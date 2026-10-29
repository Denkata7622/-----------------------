#!/usr/bin/env python3
"""
scan_pdf_text.py — чете всички PDF-и с pdfplumber (локално, безплатно).
Показва дължина на текста. НЕ пипа AI, НЕ пише файлове (освен cache).

Употреба:
    python scan_pdf_text.py             # всички PDF-и
    python scan_pdf_text.py --scope regional
    python scan_pdf_text.py --scope national
    python scan_pdf_text.py --stats-only  # само обобщение
    python scan_pdf_text.py --save-text   # записва текста за преглед
"""
import sys, io, re, json, argparse, time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = Path(__file__).parent.resolve()
ROOT = BASE.parent
GEN = ROOT / "generated"
OCR_CACHE = GEN / "cache" / "ocr"

WATCH = [
    ("Областен", ROOT / "Задачи_Минали_Години" / "Областен"),
    ("Национален", ROOT / "Задачи_Минали_Години" / "Национален"),
]

CACHE_DIR = BASE / ".pdf_text_cache"
CACHE_DIR.mkdir(exist_ok=True)


def safe_name(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()


def dedupe(pdfs):
    """Dedupe по base stem (без "(1)", "- копие")."""
    seen = {}
    for pdf in pdfs:
        stem = pdf.stem
        m = re.match(r'^(.*?)(?:\s*\(\d+\)|\s*-\s*копие|\s*-\s*copy)?$', stem)
        base = m.group(1).strip() if m else stem
        if base not in seen or stem == base:
            seen[base] = pdf
    return list(seen.values())


def read_pdf(pdf_path):
    """Връща (source, text) или (None, None)."""
    stem = safe_name(pdf_path.stem)

    # 1. Cache check (наш собствен)
    cache_file = CACHE_DIR / f"{stem}.txt"
    if cache_file.exists():
        try:
            text = cache_file.read_text(encoding="utf-8")
            return ("cache", text)
        except Exception:
            pass

    # 2. pdfplumber
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    parts.append(page.extract_text() or "")
                except Exception:
                    parts.append("")
        text = "\n\n".join(parts).strip()
        if len(text) >= 500:
            cache_file.write_text(text, encoding="utf-8")
            return ("pdfplumber", text)
    except Exception as e:
        return ("pdfplumber_error", str(e))

    # 3. OCR cache (ако има)
    ocr_file = OCR_CACHE / f"{stem}__v2.json"
    if ocr_file.exists():
        try:
            pages = json.loads(ocr_file.read_text(encoding="utf-8"))
            text = "\n\n".join(
                f"[Стр. {p['page']}]\n{p['text']}" for p in pages
            ).strip()
            if len(text) >= 500:
                cache_file.write_text(text, encoding="utf-8")
                return ("ocr_cache", text)
        except Exception:
            pass

    return (None, None)


def classify_pdf(pdf_path):
    """Извлича метаданни от името."""
    stem = pdf_path.stem
    m = re.search(r'(\d{4})', stem)
    year = int(m.group(1)) if m else 0

    kind = "other"
    if "-sol" in stem:
        kind = "sol"
    elif "-probs" in stem:
        kind = "probs"

    grade = "?"
    m = re.search(r'-(\d{1,2})\s*кл', stem)
    if m:
        grade = m.group(1)
    else:
        m = re.search(r'-(\d{1,2})-(\d{1,2})\s*кл', stem)
        if m:
            grade = f"{m.group(1)}-{m.group(2)}"

    return {"year": year, "kind": kind, "grade": grade}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=["all", "regional", "national"],
                    default="all")
    ap.add_argument("--stats-only", action="store_true")
    ap.add_argument("--save-text", action="store_true",
                    help="Записва всеки PDF текст като .txt в .pdf_text_cache/")
    ap.add_argument("--max-chars", type=int, default=None,
                    help="Спри след N chars (за preview)")
    args = ap.parse_args()

    print("═" * 78)
    print("  PDF TEXT SCANNER — локално, без AI")
    print("═" * 78)

    # Collect
    all_pdfs = []
    for scope_name, folder in WATCH:
        if args.scope not in ("all", scope_name.lower()):
            continue
        if not folder.exists():
            print(f"⚠ Липсва: {folder}")
            continue
        all_pdfs.extend(folder.rglob("*.pdf"))

    print(f"\n📂 Scanned: {len(all_pdfs)} PDF-а (преди dedupe)")
    pdfs = dedupe(all_pdfs)
    print(f"   Deduped: {len(pdfs)}")

    # Sort by year desc, kind (sol first), scope
    def sort_key(p):
        meta = classify_pdf(p)
        kind_order = {"sol": 0, "probs": 1, "other": 2}
        return (-meta["year"], kind_order.get(meta["kind"], 3), p.name)

    pdfs.sort(key=sort_key)

    # Process
    results = []
    total_time = 0

    for i, pdf in enumerate(pdfs, 1):
        meta = classify_pdf(pdf)
        t0 = time.time()
        source, text = read_pdf(pdf)
        dur = time.time() - t0
        total_time += dur

        if text:
            chars = len(text)
            words = len(text.split())
            results.append({
                "pdf": pdf,
                "meta": meta,
                "source": source,
                "chars": chars,
                "words": words,
                "status": "ok",
                "dur": dur,
            })
            if not args.stats_only:
                print(f"  [{i:>3}/{len(pdfs)}] {pdf.name:<55} "
                      f"{chars:>7}ch {words:>6}w  {source:<11} {dur:.1f}s")
        else:
            results.append({
                "pdf": pdf,
                "meta": meta,
                "chars": 0,
                "words": 0,
                "status": "no_text",
                "dur": dur,
            })
            if not args.stats_only:
                print(f"  [{i:>3}/{len(pdfs)}] {pdf.name:<55} "
                      f"NO TEXT (scanned, need OCR?)")

    # Summary
    ok = [r for r in results if r["status"] == "ok"]
    no_text = [r for r in results if r["status"] == "no_text"]

    print(f"\n{'═' * 78}")
    print(f"  SUMMARY")
    print(f"{'═' * 78}")
    print(f"  Total processed:    {len(results)}")
    print(f"  Readable (≥500ch):  {len(ok)}")
    print(f"  Empty/scanned:      {len(no_text)}")
    print(f"  Total text:         {sum(r['chars'] for r in ok):,} chars")
    print(f"  Total words:        {sum(r['words'] for r in ok):,}")
    print(f"  Processing time:    {total_time:.1f}s")

    # Group by source
    print(f"\n  By source:")
    sources = {}
    for r in ok:
        sources.setdefault(r["source"], 0)
        sources[r["source"]] += 1
    for src, n in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"    {src:<20} {n}")

    # By kind
    print(f"\n  By kind:")
    kinds = {}
    for r in ok:
        kinds.setdefault(r["meta"]["kind"], {"count": 0, "chars": 0})
        kinds[r["meta"]["kind"]]["count"] += 1
        kinds[r["meta"]["kind"]]["chars"] += r["chars"]
    for kind, data in sorted(kinds.items()):
        print(f"    {kind:<10} {data['count']:>3} files, "
              f"{data['chars']:>8,} chars ({data['chars']//data['count']:,} avg)")

    # By year
    print(f"\n  By year (top 15):")
    years = {}
    for r in ok:
        y = r["meta"]["year"]
        if y:
            years.setdefault(y, {"count": 0, "chars": 0})
            years[y]["count"] += 1
            years[y]["chars"] += r["chars"]
    for y in sorted(years.keys(), reverse=True)[:15]:
        d = years[y]
        print(f"    {y}  {d['count']:>3} files, {d['chars']:>8,} chars")

    # Size buckets
    print(f"\n  By size (chars):")
    buckets = {"< 5K": 0, "5-10K": 0, "10-15K": 0, "15-20K": 0, "20-30K": 0, "> 30K": 0}
    for r in ok:
        c = r["chars"]
        if c < 5000: buckets["< 5K"] += 1
        elif c < 10000: buckets["5-10K"] += 1
        elif c < 15000: buckets["10-15K"] += 1
        elif c < 20000: buckets["15-20K"] += 1
        elif c < 30000: buckets["20-30K"] += 1
        else: buckets["> 30K"] += 1
    for bucket, n in buckets.items():
        if n:
            print(f"    {bucket:<10} {n}")

    # Recommended for AI analysis
    print(f"\n{'═' * 78}")
    print(f"  ПРЕПОРЪКА ЗА AI АНАЛИЗ")
    print(f"{'═' * 78}")

    # Best candidates: -sol, year >= 2015, chars 5K-25K
    best = [r for r in ok
            if r["meta"]["kind"] == "sol"
            and r["meta"]["year"] >= 2015
            and 5000 <= r["chars"] <= 25000]
    best.sort(key=lambda r: (-r["meta"]["year"], r["pdf"].name))

    print(f"\n  Top кандидати: {len(best)} файла")
    print(f"  {'Year':<6} {'Grade':<8} {'Chars':<8} {'File'}")
    print(f"  {'─'*6} {'─'*8} {'─'*8} {'─'*50}")

    total_chars = 0
    for r in best[:30]:
        total_chars += r["chars"]
        print(f"  {r['meta']['year']:<6} {r['meta']['grade']:<8} "
              f"{r['chars']:>7,}  {r['pdf'].name}")

    # Token estimate
    if total_chars:
        print(f"\n  Общо chars (top {min(30, len(best))}): {total_chars:,}")
        print(f"  Est tokens (chars/4): {total_chars // 4:,}")

        for limit in [3, 5, 10, 20, 30]:
            n_files = min(limit, len(best))
            chars = sum(r["chars"] for r in best[:n_files])
            tokens = chars // 4
            cost_in = tokens * 0.000003
            cost_out = 15000 * 0.000015  # ~15K output
            total_cost = cost_in + cost_out
            print(f"  {n_files:>2} files: {tokens:>7,} in-tok → "
                  f"${total_cost:.3f}")

    # Save text preview за ръчен преглед
    if args.save_text:
        print(f"\n💾 Save text preview → .pdf_text_cache/")
        preview_dir = CACHE_DIR
        print(f"   {len(ok)} text files вече са в {preview_dir}")
        print(f"   Разгледай с: Get-ChildItem {preview_dir}")

    # Machine-readable output
    summary_file = BASE / "pdf_scan_results.json"
    summary_data = {
        "scanned_at": str(__import__("datetime").date.today()),
        "total": len(results),
        "readable": len(ok),
        "empty": len(no_text),
        "files": [
            {
                "name": r["pdf"].name,
                "year": r["meta"]["year"],
                "kind": r["meta"]["kind"],
                "grade": r["meta"]["grade"],
                "chars": r["chars"],
                "words": r["words"],
                "source": r.get("source"),
                "status": r["status"],
            }
            for r in results
        ],
    }
    summary_file.write_text(
        json.dumps(summary_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✓ Machine-readable: {summary_file.name}")


if __name__ == "__main__":
    main()