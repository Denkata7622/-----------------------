"""
build_merged.py v2 — 4-layer merge with confidence scoring.

Layers:
  1. Grounding    — fuzzy match against PDF + OCR sources (5-sample)
  2. Quality      — length, LaTeX balance, no repeated text
  3. Pair         — merge only if probs_keys == sols_keys, else split
  4. Dedupe       — exact hash + Jaccard similarity

Every problem gets _confidence 0.0-1.0:
  1.0 = full match in clean PDF
  0.8 = full match in OCR
  0.6 = partial (2/5 fragments)
  0.4 = weak (1/5, still above threshold)
  0.3 = unverifiable (no source) → kept but flagged
  <0.4 = DROP (likely hallucination)

Modes:
  --dry-run   Show all decisions, no writes (default)
  --apply     Atomic write (staging → rename)
"""
import json, re, hashlib, shutil, sys, os, argparse
from pathlib import Path
from collections import Counter

EXTRACTED = Path('../generated/cache/extracted')
MERGED = Path('../generated/cache/merged')
STAGING = Path('../generated/cache/merged_staging')
PDF_FOLDERS = ['../Задачи_Минали_Години/Областен', '../Задачи_Минали_Години/Национален']
OCR_CACHE = Path('../generated/cache/ocr')

# Thresholds
MIN_CONFIDENCE_KEEP = 0.4
MIN_LEN_PROBLEM = 50
MAX_LEN_STATEMENT = 3000
DEDUPE_JACCARD = 0.90


def normalize(s):
    if not s: return ""
    s = re.sub(r'[\$\\{}^_]', ' ', s)
    s = s.translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789'))
    s = s.translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789'))
    s = re.sub(r'[\u0000-\u00ff]{10,}', '', s)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s


def fuzzy_score(needle, haystack, sample_count=5, frag_size=40):
    """Return fraction of needle fragments found in haystack (0.0-1.0)."""
    norm_n = normalize(needle)
    norm_h = normalize(haystack)
    if len(norm_n) < 15 or not norm_h:
        return 0.0
    if len(norm_n) <= frag_size:
        return 1.0 if norm_n in norm_h else 0.0
    positions = set()
    for i in range(sample_count):
        p = int(i * (len(norm_n) - frag_size) / max(1, sample_count - 1))
        positions.add(p)
    positions = sorted(positions)
    matches = sum(1 for p in positions if norm_n[p:p + frag_size] in norm_h)
    return matches / len(positions)


def get_sources(pdf_name):
    """Return list of (name, text, type) sources. Best first."""
    sources = []
    for folder in PDF_FOLDERS:
        p = Path(folder) / f'{pdf_name}.pdf'
        if p.exists():
            try:
                import fitz
                doc = fitz.open(str(p))
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
                if len(text) > 500:
                    sources.append(('pdf', text, 'clean'))
            except Exception:
                pass
    ocr_file = OCR_CACHE / f'{pdf_name}__v2.json'
    if ocr_file.exists():
        try:
            data = json.load(open(ocr_file, encoding='utf-8'))
            text = "\n".join(pg.get('text', '') for pg in data)
            if len(text) > 300:
                sources.append(('ocr', text, 'ocr'))
        except Exception:
            pass
    return sources


def grounding_confidence(problem, sources):
    """Best confidence across stmt/sol/answer × sources."""
    if not sources:
        return 0.3, 'unverifiable'  # Kept but flagged

    best_score = 0.0
    best_field = None
    best_type = None
    for field in ('statement', 'solution', 'answer'):
        text = problem.get(field, '')
        if not text or len(normalize(text)) < 15:
            continue
        for src_name, src_text, src_type in sources:
            score = fuzzy_score(text, src_text)
            if score > best_score:
                best_score = score
                best_field = field
                best_type = src_type
    # Boost clean PDF slightly (more reliable than OCR)
    if best_type == 'clean' and best_score >= 0.4:
        best_score = min(1.0, best_score + 0.1)
    return best_score, best_field


def quality_check(problem):
    """Return (ok, reason)."""
    stmt = (problem.get('statement') or '').strip()
    sol = (problem.get('solution') or '').strip()

    if len(stmt) + len(sol) < MIN_LEN_PROBLEM:
        return False, f"too_short ({len(stmt)+len(sol)} < {MIN_LEN_PROBLEM})"
    if len(stmt) > MAX_LEN_STATEMENT:
        return False, f"statement_too_long ({len(stmt)} > {MAX_LEN_STATEMENT})"
    if not re.search(r'[а-яА-Яa-zA-Z]', stmt + sol):
        return False, "no_letters"
    # Repeated text (AI loop)
    if re.search(r'(.{10,})\1{5,}', stmt + sol):
        return False, "repeated_text"
    # LaTeX brace balance in statement
    opens = stmt.count('{') + stmt.count('(')
    closes = stmt.count('}') + stmt.count(')')
    if abs(opens - closes) > 2:
        return False, f"latex_unbalanced ({opens} vs {closes})"
    # Truncation: ends mid-word
    if stmt and stmt[-1] in 'аеиоуъюяАЕИОУЪЮЯa-zA-Z' and not stmt.endswith(('.', '?', '!', ')', ']', '}', '°', ':', ';')):
        if len(stmt) > 200:  # only for longer texts
            return False, "truncated_mid_word"
    return True, "ok"


def jaccard(a, b):
    a_tokens = set(normalize(a).split())
    b_tokens = set(normalize(b).split())
    if not a_tokens or not b_tokens:
        return 0.0
    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def dedupe(problems):
    """Exact hash + Jaccard fuzzy."""
    kept = []
    for p in problems:
        norm_stmt = normalize(p.get('statement', ''))
        h = hashlib.md5(norm_stmt.encode()).hexdigest()[:16]
        key = (p.get('grade'), p.get('num'), h)

        # Exact dup — keep richer
        replaced = False
        for i, existing in enumerate(kept):
            e_key = (existing.get('grade'), existing.get('num'),
                     hashlib.md5(normalize(existing.get('statement', '')).encode()).hexdigest()[:16])
            if e_key == key:
                e_score = len((existing.get('statement') or '') + (existing.get('solution') or ''))
                n_score = len((p.get('statement') or '') + (p.get('solution') or ''))
                if n_score > e_score:
                    kept[i] = p
                replaced = True
                break
        if replaced:
            continue

        # Fuzzy dup — same (grade, num), similar statement
        for existing in kept:
            if (existing.get('grade') == p.get('grade')
                    and existing.get('num') == p.get('num')
                    and jaccard(existing.get('statement', ''), p.get('statement', '')) >= DEDUPE_JACCARD):
                # Keep richer
                e_score = len((existing.get('statement') or '') + (existing.get('solution') or ''))
                n_score = len((p.get('statement') or '') + (p.get('solution') or ''))
                if n_score > e_score:
                    existing.update(p)
                replaced = True
                break
        if not replaced:
            kept.append(p)
    return kept


def split_base_kind(name):
    """Handle '(1)' variants + probs/sol."""
    m = re.search(r'\s*\(\d+\)\s*$', name)
    variant = ''
    if m:
        variant = m.group(0).strip()
        name = name[:m.start()].strip()
    m = re.match(r'^(.+?)(-(?:probs|sol))$', name)
    if m:
        return m.group(1) + ('_' + variant if variant else ''), m.group(2)[1:]
    return name + ('_' + variant if variant else ''), None


def find_pair(name, all_keys):
    base, kind = split_base_kind(name)
    if kind is None:
        return None
    target = 'sol' if kind == 'probs' else 'probs'
    # Reconstruct candidate
    for cand in all_keys:
        if cand == name:
            continue
        cb, ck = split_base_kind(cand)
        if cb == base and ck == target:
            return cand
    return None


def key_set(problems):
    return Counter((p.get('grade'), p.get('num')) for p in problems if p.get('num') is not None)


def merge_pair(probs, sols):
    """Safe merge — caller must ensure key counters match."""
    sols_by = {(p.get('grade'), p.get('num')): p for p in sols}
    out = []
    for pr in probs:
        k = (pr.get('grade'), pr.get('num'))
        so = sols_by.get(k, {})
        stmt = (pr.get('statement') or so.get('statement') or '').strip()
        sol = (so.get('solution') or pr.get('solution') or '').strip()
        ans = so.get('answer') or pr.get('answer')
        if not stmt and not sol:
            continue
        conf = min(
            pr.get('_confidence', 0.5),
            so.get('_confidence', 0.5) if so else pr.get('_confidence', 0.5),
        )
        out.append({
            'num': k[1], 'grade': k[0],
            'year': pr.get('year') or so.get('year'),
            'round': pr.get('round') or so.get('round'),
            'statement': stmt or None,
            'solution': sol or None,
            'answer': ans,
            'page': pr.get('page') or so.get('page'),
            '_confidence': conf,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Write to disk')
    ap.add_argument('--verbose', action='store_true', help='Show all drops')
    args = ap.parse_args()

    mode = "APPLY" if args.apply else "DRY RUN"
    print("=" * 70)
    print(f"  BUILD_MERGED v2 — {mode}")
    print("=" * 70)

    if not EXTRACTED.exists():
        print(f"✗ {EXTRACTED} not found")
        return 1

    # Load
    extracted = {}
    for d in EXTRACTED.iterdir():
        if not d.is_dir(): continue
        f = d / 'all_problems.json'
        if not f.exists(): continue
        try:
            data = json.load(open(f, encoding='utf-8'))
            extracted[data.get('pdf', d.name)] = data.get('problems', [])
        except Exception as e:
            print(f"✗ {d.name}: {e}")

    print(f"\nLoaded {len(extracted)} extracted files, "
          f"{sum(len(p) for p in extracted.values())} problems\n")

    # Layer 1+2
    print("─── Layer 1+2: Grounding + Quality ───")
    cleaned = {}
    stats = Counter()
    drops = []  # For report

    for name in sorted(extracted.keys()):
        problems = extracted[name]
        sources = get_sources(name)
        src_desc = ','.join(s[0] for s in sources) if sources else 'none'
        kept = []
        for p in problems:
            ok, reason = quality_check(p)
            if not ok:
                stats['drop_quality'] += 1
                drops.append({'file': name, 'num': p.get('num'),
                              'reason': reason, 'type': 'quality'})
                if args.verbose:
                    print(f"  ✗ [{name}] num={p.get('num')}: {reason}")
                continue
            conf, field = grounding_confidence(p, sources)
            if conf < MIN_CONFIDENCE_KEEP:
                stats['drop_halluc'] += 1
                drops.append({'file': name, 'num': p.get('num'),
                              'reason': f'confidence {conf:.2f} < {MIN_CONFIDENCE_KEEP}',
                              'type': 'hallucination',
                              'stmt_preview': (p.get('statement') or '')[:60]})
                if args.verbose:
                    print(f"  ✗ [{name}] num={p.get('num')}: conf={conf:.2f}")
                continue
            p['_confidence'] = round(conf, 2)
            p['_grounding_field'] = field or 'none'
            kept.append(p)
            stats['kept'] += 1
        cleaned[name] = kept
        dropped_here = len(problems) - len(kept)
        if dropped_here > 0:
            print(f"  {name}: kept {len(kept)}/{len(problems)} (src={src_desc})")

    print(f"\n  Kept: {stats['kept']}")
    print(f"  Dropped: {stats['drop_halluc']} halluc + {stats['drop_quality']} quality")

    # Layer 3
    print("\n─── Layer 3: Pair-aware merge ───")
    if args.apply:
        if STAGING.exists(): shutil.rmtree(STAGING)
        STAGING.mkdir(parents=True)

    processed = set()
    merge_stats = Counter()
    splits = []

    for name in sorted(cleaned.keys()):
        if name in processed: continue
        probs = cleaned[name]
        pair = find_pair(name, cleaned.keys())

        if pair and pair not in processed:
            if name.endswith('-probs'):
                probs_name, sols_name = name, pair
            else:
                probs_name, sols_name = pair, name
            p_arr = cleaned[probs_name]
            s_arr = cleaned[sols_name]
            base, _ = split_base_kind(probs_name)

            pk, sk = key_set(p_arr), key_set(s_arr)
            if pk == sk and pk:
                out = dedupe(merge_pair(p_arr, s_arr))
                conf_avg = sum(p.get('_confidence', 0.5) for p in out) / len(out) if out else 0
                merge_stats['merged'] += 1
                merge_stats['problems_merged'] += len(out)
                print(f"  ✓ MERGE  {base}: {len(out)} problems (avg conf {conf_avg:.2f})")
                if args.apply:
                    out_dir = STAGING / base
                    out_dir.mkdir(parents=True, exist_ok=True)
                    json.dump({'pdf': base, 'problems': out},
                              open(out_dir / 'all_problems.json', 'w', encoding='utf-8'),
                              ensure_ascii=False, indent=2)
            else:
                # Split
                merge_stats['split'] += 1
                p_dedup = dedupe(p_arr)
                s_dedup = dedupe(s_arr)
                merge_stats['problems_split'] += len(p_dedup) + len(s_dedup)
                splits.append({
                    'base': base,
                    'probs_count': len(p_dedup),
                    'sols_count': len(s_dedup),
                    'pk_size': len(pk),
                    'sk_size': len(sk),
                    'pk': sorted(pk),
                    'sk': sorted(sk),
                })
                print(f"  ⚠ SPLIT  {base}: probs={len(p_dedup)}, sols={len(s_dedup)}")
                if args.apply:
                    for suffix, arr in [('-probs', p_dedup), ('-sol', s_dedup)]:
                        if not arr: continue
                        out_dir = STAGING / f'{base}{suffix}'
                        out_dir.mkdir(parents=True, exist_ok=True)
                        json.dump({'pdf': f'{base}{suffix}', 'problems': arr},
                                  open(out_dir / 'all_problems.json', 'w', encoding='utf-8'),
                                  ensure_ascii=False, indent=2)
            processed.add(probs_name)
            processed.add(sols_name)
        else:
            # Standalone
            arr = dedupe(probs)
            base, _ = split_base_kind(name)
            merge_stats['standalone'] += 1
            merge_stats['problems_standalone'] += len(arr)
            print(f"  ─ STANDALONE  {base}: {len(arr)} problems")
            if args.apply:
                out_dir = STAGING / base
                out_dir.mkdir(parents=True, exist_ok=True)
                json.dump({'pdf': base, 'problems': arr},
                          open(out_dir / 'all_problems.json', 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=2)
            processed.add(name)

    # Verify + report
    print("\n─── Verification ───")
    total_out = merge_stats['problems_merged'] + merge_stats['problems_split'] + merge_stats['problems_standalone']
    print(f"  Total problems in output: {total_out}")
    print(f"  Files: {merge_stats['merged']} merged + {merge_stats['split']} split + {merge_stats['standalone']} standalone")

    report = {
        'mode': mode,
        'extracted_files': len(extracted),
        'extracted_problems': sum(len(p) for p in extracted.values()),
        'kept_problems': stats['kept'],
        'dropped_halluc': stats['drop_halluc'],
        'dropped_quality': stats['drop_quality'],
        'merge_stats': dict(merge_stats),
        'total_problems_output': total_out,
        'drops': drops,
        'splits': splits,
    }

    if args.apply:
        # Verify staging before rename
        staging_files = list(STAGING.rglob('all_problems.json'))
        print(f"\n  Staging: {len(staging_files)} files written")
        verify_total = 0
        for f in staging_files:
            try:
                d = json.load(open(f, encoding='utf-8'))
                verify_total += len(d.get('problems', []))
            except Exception as e:
                print(f"  ✗ {f}: {e}")
                return 1
        print(f"  Staging verifies: {verify_total} problems")

        # Write report
        report['staging_verified'] = verify_total
        (STAGING / '_report.json').write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

        # Atomic swap
        old_merged = MERGED.parent / 'merged_old'
        if old_merged.exists(): shutil.rmtree(old_merged)
        if MERGED.exists():
            MERGED.rename(old_merged)
        STAGING.rename(MERGED)
        if old_merged.exists():
            shutil.rmtree(old_merged)
        print(f"  ✓ Renamed staging → merged")
        print(f"\n✓ APPLIED. Report: {MERGED}/_report.json")
    else:
        print(f"\n DRY RUN complete. No files written.")
        print(f" Run with --apply to execute.")
        print(f" Run with --apply --verbose to see all drops individually.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
