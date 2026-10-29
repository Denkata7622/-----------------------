#!/usr/bin/env python3
"""
scan_articles.py — класифицира статиите като old/new.

Пише:
  generated/articles/_manifest.json   (пълен списък с метаданни)
  generated/articles/_to_regenerate.json  (списък за regen)
"""
import sys, io, re, json
from pathlib import Path
from datetime import date

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ARTICLES = Path(__file__).parent.parent / "generated" / "articles"

# Прагове от новия prompt
NEW_PROMPT_MIN_WORDS = 2500
NEW_PROMPT_MIN_SECTIONS = 7   # трябва да е 9, но 7 е "приемливо"
NEW_PROMPT_MIN_CHECKS = 2     # трябва да е 3, но 2 е OK
NEW_PROMPT_MIN_EXAMPLES = 4


def classify_article(deep_file: Path, metadata_file: Path) -> dict:
    """Връща {status, reasons, ...}."""
    text = deep_file.read_text(encoding="utf-8")
    words = len(text.split())

    # Metadata check
    meta_status = "missing"
    meta_version = None
    meta_gen_date = None
    if metadata_file.exists():
        try:
            meta = json.loads(metadata_file.read_text(encoding="utf-8"))
            meta_status = "present"
            meta_version = meta.get("prompt_version")
            meta_gen_date = meta.get("generated_at")
        except Exception:
            pass

    # Structural metrics
    sections = re.findall(r'^## \d+\.', text, re.MULTILINE)
    checks = text.count(">>> CHECK:")
    examples = re.findall(r'\*\*Пример \d+', text)
    has_historical = "## Исторически контекст" in text
    has_why_important = "## 1. Защо е важно" in text

    # Decision
    reasons = []

    if has_historical:
        reasons.append("old_structure_historical_section")

    if has_why_important:
        reasons.append("new_structure_why_important")

    if words < NEW_PROMPT_MIN_WORDS:
        reasons.append(f"too_short_{words}w")

    if len(sections) < NEW_PROMPT_MIN_SECTIONS:
        reasons.append(f"too_few_sections_{len(sections)}")

    if checks < NEW_PROMPT_MIN_CHECKS:
        reasons.append(f"missing_checks_{checks}")

    if len(examples) < NEW_PROMPT_MIN_EXAMPLES:
        reasons.append(f"too_few_examples_{len(examples)}")

    # Decide: old, new, or suspicious
    # - If explicit prompt_version == "v5" → NEW
    # - If has historical section → OLD
    # - If has 3+ "old" signals → OLD
    # - If has 3+ "new" signals → NEW
    # - Else → SUSPICIOUS

    old_signals = sum([
        has_historical,
        words < NEW_PROMPT_MIN_WORDS,
        len(sections) < NEW_PROMPT_MIN_SECTIONS,
        checks < NEW_PROMPT_MIN_CHECKS,
    ])

    new_signals = sum([
        has_why_important,
        words >= NEW_PROMPT_MIN_WORDS,
        len(sections) >= NEW_PROMPT_MIN_SECTIONS,
        checks >= NEW_PROMPT_MIN_CHECKS,
    ])

    if meta_version == "v5":
        status = "new"
    elif old_signals >= 3:
        status = "old"
    elif new_signals >= 3:
        status = "new"
    else:
        status = "suspicious"

    return {
        "point_id": deep_file.parent.name.replace("_", "."),
        "status": status,
        "words": words,
        "sections": len(sections),
        "checks": checks,
        "examples": len(examples),
        "has_historical": has_historical,
        "has_why_important": has_why_important,
        "meta_status": meta_status,
        "meta_version": meta_version,
        "meta_gen_date": meta_gen_date,
        "reasons": reasons,
    }


def main():
    if not ARTICLES.exists():
        print(f"✗ {ARTICLES} не съществува")
        return 1

    print(f"📂 Scanning {ARTICLES}\n")

    results = []
    for point_dir in sorted(ARTICLES.iterdir()):
        if not point_dir.is_dir():
            continue
        deep = point_dir / "deep.md"
        meta = point_dir / "metadata.json"
        if not deep.exists():
            continue
        results.append(classify_article(deep, meta))

    # Summary
    by_status = {"old": [], "new": [], "suspicious": []}
    for r in results:
        by_status[r["status"]].append(r)

    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Total articles:  {len(results)}")
    print(f"  Old:             {len(by_status['old'])}")
    print(f"  New:             {len(by_status['new'])}")
    print(f"  Suspicious:      {len(by_status['suspicious'])}")
    print()

    # Sample old
    if by_status["old"]:
        print(f"  Old (first 5):")
        for r in by_status["old"][:5]:
            print(f"    {r['point_id']:6s}  {r['words']:4d}w  "
                  f"{r['sections']}s  {r['checks']}c  "
                  f"({', '.join(r['reasons'][:2])})")
        if len(by_status["old"]) > 5:
            print(f"    ... и {len(by_status['old']) - 5} още")

    if by_status["suspicious"]:
        print(f"\n  Suspicious (first 5):")
        for r in by_status["suspicious"][:5]:
            print(f"    {r['point_id']:6s}  {r['words']:4d}w  "
                  f"{r['sections']}s  {r['checks']}c")

    # Write manifest
    manifest = {
        "scanned_at": date.today().isoformat(),
        "total": len(results),
        "by_status": {
            "old": len(by_status["old"]),
            "new": len(by_status["new"]),
            "suspicious": len(by_status["suspicious"]),
        },
        "articles": results,
    }
    (ARTICLES / "_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Write regenerate queue (old + suspicious)
    to_regen = {
        "generated_at": date.today().isoformat(),
        "reason": "old_prompt_structure",
        "priority_order": [],  # стар → най-нов
        "points": [],
    }
    # Сортирай по мета-gen-date (по-старите първо)
    combined = by_status["old"] + by_status["suspicious"]
    combined.sort(key=lambda r: r.get("meta_gen_date") or "9999")
    for r in combined:
        to_regen["points"].append({
            "point_id": r["point_id"],
            "status": r["status"],
            "words": r["words"],
            "sections": r["sections"],
            "reasons": r["reasons"],
        })

    (ARTICLES / "_to_regenerate.json").write_text(
        json.dumps(to_regen, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n✓ Manifest → generated/articles/_manifest.json")
    print(f"✓ Queue    → generated/articles/_to_regenerate.json "
          f"({len(to_regen['points'])} articles)")

    return 0


if __name__ == "__main__":
    sys.exit(main())