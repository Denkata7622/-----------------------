"""
build_merged_v3.py — lenient grounding + file-level safety.
"""
import json, re, hashlib, shutil, sys, argparse
from pathlib import Path
from collections import Counter

EXTRACTED = Path('../generated/cache/extracted')
MERGED = Path('../generated/cache/merged')
STAGING = Path('../generated/cache/merged_staging')
PDF_FOLDERS = ['../Задачи_Минали_Години/Областен', '../Задачи_Минали_Години/Национален']
OCR_CACHE = Path('../generated/cache/ocr')

MIN_CONFIDENCE_KEEP = 0.15   # was 0.4
MIN_CONFIDENCE_FLAG = 0.4     # below this = flag for review
MIN_LEN_PROBLEM = 50
MAX_LEN_STATEMENT = 3000
FILE_SAFETY_RATIO = 0.6       # if <60% kept, keep all, flag file
DEDUPE_JACCARD = 0.90
COMPILATION_PATTERNS = ('BMC_', 'BMO_', 'NOM_', 'OT_')  # skip grounding


def normalize(s):
    if not s: return ""
    s = re.sub(r'[\$\\{}^_]', ' ', s)
    s = s.translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉', '01234567890123456789'))
    s = re.sub(r'[\u0000-\u001f\u007f-\u00ff]{5,}', '', s)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s


def fuzzy_score(needle, haystack):
    """Lenient matching: any 20-char match OR token overlap."""
    norm_n = normalize(needle)
    norm_h = normalize(haystack)
    if len(norm_n) < 10 or not norm_h:
        return 0.0
    # Fast path: any 20-char fragment matches
    if len(norm_n) >= 20:
        for i in range(0, len(norm_n) - 20 + 1, 10):
            if norm_n[i:i+20] in norm_h:
                return 1.0
    # Short text: exact match
    elif norm_n in norm_h:
        return 1.0
    # Token overlap fallback
    tn = set(norm_n.split())
    th = set(norm_h.split())
    if tn and len(tn) >= 5:
        overlap = len(tn & th) / len(tn)
        return overlap * 0.8  # 50% overlap → 0.4
    return 0.0


def get_sources(pdf_name):
    sources = []
    for folder in PDF_FOLDERS:
        p = Path(folder) / f'{pdf_name}.pdf'
        if p.exists():
            try:
                import fitz
                doc = fitz.open(str(p))
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
                if len(text) > 300:
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
    if not sources:
        return 0.5, 'unverifiable'  # KEEP if can't verify
    best = 0.0
    best_field = None
    for field in ('statement', 'solution', 'answer'):
        text = problem.get(field, '')
        if not text or len(normalize(text)) < 10:
            continue
        for _, src_text, _ in sources:
            score = fuzzy_score(text, src_text)
            if score > best:
                best = score
                best_field = field
    return best, best_field


def quality_check(problem):
    stmt = (problem.get('statement') or '').strip()
    sol = (problem.get('solution') or '').strip()
    if len(stmt) + len(sol) < MIN_LEN_PROBLEM:
        return False, f"too_short"
    if len(stmt) > MAX_LEN_STATEMENT:
        return False, f"stmt_too_long"
    if not re.search(r'[а-яА-Яa-zA-Z]', stmt + sol):
        return False, "no_letters"
    if re.search(r'(.{10,})\1{5,}', stmt + sol):
        return False, "repeated_text"
    return True, "ok"


def dedupe(problems):
    kept = []
    for p in problems:
        h = hashlib.md5(normalize(p.get('statement', '')).encode()).hexdigest()[:16]
        key = (p.get('grade'), p.get('num'), h)
        found = False
        for i, ex in enumerate(kept):
            ex_h = hashlib.md5(normalize(ex.get('statement', '')).encode()).hexdigest()[:16]
            if (ex.get('grade'), ex.get('num'), ex_h) == key:
                e_s = len((ex.get('statement') or '') + (ex.get('solution') or ''))
                n_s = len((p.get('statement') or '') + (p.get('solution') or ''))
                if n_s > e_s: kept[i] = p
                found = True
                break
        if not found:
            kept.append(p)
    return kept


def split_base_kind(name):
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
    if kind is None: return None
    target = 'sol' if kind == 'probs' else 'probs'
    for cand in all_keys:
        if cand == name: continue
        cb, ck = split_base_kind(cand)
        if cb == base and ck == target:
            return cand
    return None


def key_counter(problems):
    return Counter((p.get('grade'), p.get('num')) for p in problems if p.get('num') is not None)


def merge_pair(probs, sols):
    sols_by = {(p.get('grade'), p.get('num')): p for p in sols}
    out = []
    for pr in probs:
        k = (pr.get('grade'), pr.get('num'))
        so = sols_by.get(k, {})
        stmt = (pr.get('statement') or so.get('statement') or '').strip()
        sol = (so.get('solution') or pr.get('solution') or '').strip()
        ans = so.get('answer') or pr.get('answer')
        if not stmt and not sol: continue
        conf = min(pr.get('_confidence', 0.5), so.get('_confidence', 0.5))
        out.append({
            'num': k[1], 'grade': k[0],
            'year': pr.get('year') or so.get('year'),
            'round': pr.get('round') or so.get('round'),
            'statement': stmt or None, 'solution': sol or None,
            'answer': ans, 'page': pr.get('page') or so.get('page'),
            '_confidence': round(conf, 2),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    mode = "APPLY" if args.apply else "DRY RUN"
    print("=" * 70)
    print(f"  BUILD_MERGED v3 — {mode}")
    print("=" * 70)

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

    print(f"\nLoaded {len(extracted)} files, {sum(len(p) for p in extracted.values())} problems\n")

    # Layer 1+2
    print("─── Layer 1+2: Grounding + Quality ───")
    cleaned = {}
    stats = Counter()
    drops = []
    flags = []

    for name in sorted(extracted.keys()):
        problems = extracted[name]
        is_compilation = any(pat in name for pat in COMPILATION_PATTERNS)
        sources = [] if is_compilation else get_sources(name)
        
        kept = []
        for p in problems:
            ok, reason = quality_check(p)
            if not ok:
                stats['drop_quality'] += 1
                drops.append({'file': name, 'num': p.get('num'),
                              'reason': reason, 'type': 'quality'})
                continue
            if is_compilation:
                # Skip grounding for compilations
                p['_confidence'] = 0.5
                p['_flag'] = 'compilation'
                kept.append(p)
                stats['kept'] += 1
                continue
            conf, field = grounding_confidence(p, sources)
            if conf < MIN_CONFIDENCE_KEEP:
                stats['drop_halluc'] += 1
                drops.append({'file': name, 'num': p.get('num'),
                              'reason': f'conf={conf:.2f}',
                              'type': 'hallucination',
                              'stmt_preview': (p.get('statement') or '')[:60]})
                if args.verbose:
                    print(f"  ✗ [{name}] num={p.get('num')}: conf={conf:.2f}")
                continue
            p['_confidence'] = round(conf, 2)
            if conf < MIN_CONFIDENCE_FLAG:
                p['_flag'] = f'low_confidence:{conf:.2f}'
                flags.append({'file': name, 'num': p.get('num'), 'conf': conf})
            kept.append(p)
            stats['kept'] += 1
        
        # File-level safety
        if len(kept) < FILE_SAFETY_RATIO * len(problems) and len(problems) >= 3:
            stats['file_safety_triggered'] += 1
            print(f"  ⚠ FILE SAFETY {name}: only {len(kept)}/{len(problems)} kept → restoring all")
            for p in problems:
                p['_confidence'] = 0.3
                p['_flag'] = 'file_safety_restore'
            kept = problems
            stats['kept'] += (len(problems) - len(kept))
        
        cleaned[name] = kept
        dropped_here = len(problems) - len(kept)
        if dropped_here > 0:
            src_type = sources[0][2] if sources else ('compilation' if is_compilation else 'none')
            print(f"  {name}: kept {len(kept)}/{len(problems)} (src={src_type})")

    print(f"\n  Kept: {stats['kept']} / {sum(len(p) for p in extracted.values())}")
    print(f"  Dropped: {stats['drop_halluc']} halluc + {stats['drop_quality']} quality")
    print(f"  File safety triggers: {stats['file_safety_triggered']}")
    print(f"  Low-confidence flags: {len(flags)}")

    # Layer 3
    print("\n─── Layer 3: Pair-aware merge ───")
    if args.apply:
        if STAGING.exists(): shutil.rmtree(STAGING)
        STAGING.mkdir(parents=True)

    processed = set()
    m_stats = Counter()
    splits = []

    for name in sorted(cleaned.keys()):
        if name in processed: continue
        probs = cleaned[name]
        pair = find_pair(name, cleaned.keys())

        if pair and pair not in processed:
            if name.endswith('-probs'):
                pn, sn = name, pair
            else:
                pn, sn = pair, name
            pa, sa = cleaned[pn], cleaned[sn]
            base, _ = split_base_kind(pn)

            pk, sk = key_counter(pa), key_counter(sa)
            if pk == sk and pk:
                out = dedupe(merge_pair(pa, sa))
                conf_avg = sum(p.get('_confidence', 0.5) for p in out) / len(out) if out else 0
                m_stats['merged'] += 1
                m_stats['merged_problems'] += len(out)
                print(f"  ✓ MERGE  {base}: {len(out)} problems (avg conf {conf_avg:.2f})")
                if args.apply:
                    out_dir = STAGING / base
                    out_dir.mkdir(parents=True, exist_ok=True)
                    json.dump({'pdf': base, 'problems': out},
                              open(out_dir / 'all_problems.json', 'w', encoding='utf-8'),
                              ensure_ascii=False, indent=2)
            else:
                pd, sd = dedupe(pa), dedupe(sa)
                m_stats['split'] += 1
                m_stats['split_problems'] += len(pd) + len(sd)
                splits.append({'base': base, 'probs': len(pd), 'sols': len(sd)})
                print(f"  ⚠ SPLIT  {base}: probs={len(pd)}, sols={len(sd)}")
                if args.apply:
                    for suffix, arr in [('-probs', pd), ('-sol', sd)]:
                        if not arr: continue
                        out_dir = STAGING / f'{base}{suffix}'
                        out_dir.mkdir(parents=True, exist_ok=True)
                        json.dump({'pdf': f'{base}{suffix}', 'problems': arr},
                                  open(out_dir / 'all_problems.json', 'w', encoding='utf-8'),
                                  ensure_ascii=False, indent=2)
            processed.add(pn)
            processed.add(sn)
        else:
            arr = dedupe(probs)
            base, _ = split_base_kind(name)
            m_stats['standalone'] += 1
            m_stats['standalone_problems'] += len(arr)
            print(f"  ─ STANDALONE  {base}: {len(arr)} problems")
            if args.apply:
                out_dir = STAGING / base
                out_dir.mkdir(parents=True, exist_ok=True)
                json.dump({'pdf': base, 'problems': arr},
                          open(out_dir / 'all_problems.json', 'w', encoding='utf-8'),
                          ensure_ascii=False, indent=2)
            processed.add(name)

    total_out = m_stats['merged_problems'] + m_stats['split_problems'] + m_stats['standalone_problems']
    print(f"\n─── Verification ───")
    print(f"  Total output: {total_out} problems")
    print(f"  Files: {m_stats['merged']} merged + {m_stats['split']} split + {m_stats['standalone']} standalone")

    report = {
        'mode': mode,
        'extracted_problems': sum(len(p) for p in extracted.values()),
        'kept_problems': stats['kept'],
        'dropped_halluc': stats['drop_halluc'],
        'dropped_quality': stats['drop_quality'],
        'file_safety_triggered': stats['file_safety_triggered'],
        'flags': flags,
        'drops': drops,
        'splits': splits,
        'merge_stats': dict(m_stats),
        'total_output': total_out,
    }

    if args.apply:
        staging_files = list(STAGING.rglob('all_problems.json'))
        verify = sum(len(json.load(open(f, encoding='utf-8')).get('problems', [])) for f in staging_files)
        report['staging_verified'] = verify
        (STAGING / '_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        old = MERGED.parent / 'merged_old'
        if old.exists(): shutil.rmtree(old)
        if MERGED.exists(): MERGED.rename(old)
        STAGING.rename(MERGED)
        if old.exists(): shutil.rmtree(old)
        print(f"\n✓ APPLIED → {MERGED}")
    else:
        print(f"\n DRY RUN — no files written.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
