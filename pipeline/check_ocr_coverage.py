#!/usr/bin/env python3
"""check_ocr_coverage.py — колко от target PDF-ите имат OCR cache."""
import sys, io, re
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = Path(__file__).parent.resolve()
ROOT = BASE.parent
OCR_CACHE = ROOT / "generated" / "cache" / "ocr"

WATCH = [
    ROOT / "Задачи_Минали_Години" / "Областен",
    ROOT / "Задачи_Минали_Години" / "Национален",
]


def safe_name(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()


def main():
    print("═" * 70)
    print("  OCR CACHE COVERAGE")
    print("═" * 70)

    if not OCR_CACHE.exists():
        print(f"✗ {OCR_CACHE} не съществува")
        return 1

    # Build cache index: stem → file
    cache_files = {}
    for f in OCR_CACHE.glob("*__v2.json"):
        # Format: "OLI-2-Областен кръг-2003-10 кл-sol__v2.json"
        stem = f.name.replace("__v2.json", "")
        cache_files[stem] = f

    print(f"\n📁 Cache: {len(cache_files)} OCR-нати PDF-а")
    print(f"   Path: {OCR_CACHE}")

    # Scan target PDFs
    target_pdfs = []
    for folder in WATCH:
        if not folder.exists():
            continue
        for pdf in folder.rglob("*.pdf"):
            target_pdfs.append(pdf)

    print(f"\n📄 Target PDFs: {len(target_pdfs)}")

    # Match cache
    covered = []
    not_covered = []

    for pdf in target_pdfs:
        stem = safe_name(pdf.stem)
        if stem in cache_files:
            # Check size (bytes) — да знаем дали е пълен
            cache_size = cache_files[stem].stat().st_size
            covered.append((pdf, cache_size))
        else:
            not_covered.append(pdf)

    print(f"\n✓ Covered:     {len(covered)}")
    print(f"✗ Not covered: {len(not_covered)}")
    print(f"  Coverage:    {len(covered) / len(target_pdfs) * 100:.1f}%")

    # Breakdown by type
    print(f"\n📊 Covered by type:")
    cov_sol = sum(1 for p, _ in covered if "-sol" in p.stem)
    cov_probs = sum(1 for p, _ in covered if "-probs" in p.stem)
    cov_other = len(covered) - cov_sol - cov_probs
    print(f"  -sol:    {cov_sol}")
    print(f"  -probs:  {cov_probs}")
    print(f"  other:   {cov_other}")

    print(f"\n📊 Not covered by type:")
    nc_sol = sum(1 for p in not_covered if "-sol" in p.stem)
    nc_probs = sum(1 for p in not_covered if "-probs" in p.stem)
    nc_other = len(not_covered) - nc_sol - nc_probs
    print(f"  -sol:    {nc_sol}")
    print(f"  -probs:  {nc_probs}")
    print(f"  other:   {nc_other}")

    # List covered -sol files (най-важни)
    print(f"\n📋 Covered -sol files (first 20):")
    for p, size in sorted(covered, key=lambda x: x[0].name)[:20]:
        if "-sol" in p.stem:
            size_kb = size / 1024
            print(f"  {p.name:<60} ({size_kb:.1f} KB cache)")

    # Estimate costs
    n_text = 0
    n_scanned = 0
    import pdfplumber
    try:
        for pdf in not_covered:
            try:
                with pdfplumber.open(pdf) as p:
                    chars = sum(len(pg.chars) for pg in p.pages[:1])
                    if chars > 50:
                        n_text += 1
                    else:
                        n_scanned += 1
            except Exception:
                n_scanned += 1
    except ImportError:
        print("\n⚠ pdfplumber не е инсталиран - пропускам текстов/сканиран анализ")
        return 0

    print(f"\n💰 COST ESTIMATE (за оставащите {len(not_covered)}):")
    print(f"  Текстови (pdfplumber): {n_text} × $0.05 = ${n_text * 0.05:.2f}")
    print(f"  Сканирани (need OCR):  {n_scanned} × $0.055 = ${n_scanned * 0.055:.2f}")
    print(f"  TOTAL extract:         ${n_text * 0.05 + n_scanned * 0.055:.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())