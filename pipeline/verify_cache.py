#!/usr/bin/env python3
"""
verify_cache.py — проверява дали cached text е пълен.

За всеки избран файл:
  1. Отваря оригиналния PDF с pdfplumber
  2. Брои страници
  3. Сравнява chars от cache vs chars от PDF
  4. Флагва suspicious (chars/page < 200 или 30%+ missing)
"""
import sys, io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pdfplumber

BASE = Path(__file__).parent.resolve()
ROOT = BASE.parent
CACHE_DIR = BASE / ".pdf_text_cache"

WATCH = [
    ROOT / "Задачи_Минали_Години" / "Областен",
    ROOT / "Задачи_Минали_Години" / "Национален",
]

# Прагове
MIN_CHARS_PER_PAGE = 200   # под това → suspicious
MIN_PDF_BYTES = 5000       # под това → skip (няма смисъл)


def collect_targets():
    """Събира 11 кл + National 9-12 sols (както generate_plan)."""
    files = []
    for folder in WATCH:
        if not folder.exists():
            continue
        for pdf in folder.rglob("*.pdf"):
            stem = pdf.stem
            if "-probs" in stem:
                continue
            is_11kl_reg = "Областен" in stem and "11 кл" in stem
            is_national = "Национален" in stem and "9-12 кл" in stem
            if is_11kl_reg or is_national:
                files.append(pdf)
    return sorted(files, key=lambda p: p.name)


def main():
    print("═" * 80)
    print("  VERIFY CACHE — проверка за truncation")
    print("═" * 80)

    pdfs = collect_targets()
    print(f"\n📂 Target PDFs: {len(pdfs)}")

    suspicious = []
    empty = []
    missing_cache = []

    for i, pdf in enumerate(pdfs, 1):
        stem = pdf.stem

        # Cache check
        cache_file = CACHE_DIR / f"{stem}.txt"
        if not cache_file.exists():
            missing_cache.append(pdf)
            print(f"  [{i:>2}/{len(pdfs)}] {stem:<55} NO CACHE")
            continue

        cached_text = cache_file.read_text(encoding="utf-8")
        cached_chars = len(cached_text)

        # PDF size
        pdf_size = pdf.stat().st_size
        if pdf_size < MIN_PDF_BYTES:
            print(f"  [{i:>2}/{len(pdfs)}] {stem:<55} "
                  f"{cached_chars:>7,}ch  (tiny PDF {pdf_size}B, skip)")
            continue

        # Extract from PDF fresh (just count)
        try:
            with pdfplumber.open(pdf) as p:
                pages = len(p.pages)
                fresh_chars = 0
                empty_pages = 0
                for page in p.pages:
                    try:
                        t = (page.extract_text() or "").strip()
                        fresh_chars += len(t)
                        if len(t) < 50:
                            empty_pages += 1
                    except Exception:
                        empty_pages += 1
        except Exception as e:
            print(f"  [{i:>2}/{len(pdfs)}] {stem:<55} PDF FAIL: {e}")
            continue

        # Compare
        chars_per_page_cache = cached_chars / pages if pages else 0
        chars_per_page_fresh = fresh_chars / pages if pages else 0

        # Detection
        if cached_chars == 0:
            empty.append(pdf)
            status = "❌ EMPTY"
        elif chars_per_page_cache < MIN_CHARS_PER_PAGE:
            suspicious.append((pdf, pages, cached_chars, empty_pages))
            status = f"⚠  SUSPICIOUS ({chars_per_page_cache:.0f}ch/p, {empty_pages}/{pages} empty p)"
        elif abs(cached_chars - fresh_chars) / max(fresh_chars, 1) > 0.1:
            suspicious.append((pdf, pages, cached_chars, empty_pages))
            status = f"⚠  MISMATCH (cache={cached_chars}, fresh={fresh_chars})"
        else:
            status = f"✓  OK ({pages}p, {chars_per_page_cache:.0f}ch/p)"

        print(f"  [{i:>2}/{len(pdfs)}] {stem:<55} {status}")

    # Summary
    print(f"\n{'═' * 80}")
    print(f"  SUMMARY")
    print(f"{'═' * 80}")
    print(f"  Total checked:    {len(pdfs)}")
    print(f"  ✓ OK:             {len(pdfs) - len(suspicious) - len(empty) - len(missing_cache)}")
    print(f"  ⚠  Suspicious:    {len(suspicious)}")
    print(f"  ❌ Empty:         {len(empty)}")
    print(f"  📭 Missing cache: {len(missing_cache)}")

    if suspicious:
        print(f"\n⚠ SUSPICIOUS FILES:")
        print(f"  {'File':<55} {'Pages':>5} {'Chars':>8} {'Ch/p':>6} {'Empty p':>8}")
        for pdf, pages, chars, empty_p in suspicious:
            ch_pp = chars / pages if pages else 0
            print(f"  {pdf.stem:<55} {pages:>5} {chars:>8,} {ch_pp:>6.0f} {empty_p:>8}")

    if empty:
        print(f"\n❌ EMPTY FILES (cache 0 chars):")
        for pdf in empty:
            print(f"  {pdf.stem}")

    if missing_cache:
        print(f"\n📭 MISSING CACHE:")
        for pdf in missing_cache:
            print(f"  {pdf.stem}")

    # Recommendation
    print(f"\n{'═' * 80}")
    if suspicious or empty:
        print(f"  ⚠️  ПРЕПОРЪКА: {len(suspicious) + len(empty)} файла може да са сгрешени")
        print(f"  Options:")
        print(f"    1. Пусни ги пак: python scan_pdf_text.py (но ще презапише всичко)")
        print(f"    2. Изключи ги от generate_plan: --exclude \"{suspicious[0][0].stem}\" (TODO флаг)")
        print(f"    3. Приеми че са малки — те заемат <10% от prompt-а")
    else:
        print(f"  ✓ Всички файлове изглеждат OK")
    print(f"{'═' * 80}")


if __name__ == "__main__":
    main()