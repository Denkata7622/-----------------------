"""
diag_extraction.py — Diagnose extraction cascade per point.

Usage:
    python diag_extraction.py R.10
    python diag_extraction.py --all          # всички точки
    python diag_extraction.py --pdf "OLI-2-Областен кръг-2025-11 кл"   # само един PDF
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pdf_chunker


POINT_KEYWORDS = {
    "R.9":  ["четириъгълник", "успоредник", "ромб", "трапец", "правoъгълник"],
    "R.10": ["окръжност", "хорда", "допирателна", "секуща", "вписан ъгъл",
             "централен ъгъл", "дъга"],
    "R.11": ["вектор", "координатна", "среда на отсечка", "колинеарни"],
    "R.12": ["делимост", "дели се", "остатък", "кратно"],
}


def extract_base_pdf(source: str) -> str:
    """'OLI-2-... · 2025-11 · Зад. 2' → 'OLI-2-...'"""
    return source.split(" · ")[0].strip()


def find_dir(parent: Path, base: str) -> Path | None:
    """Намира директория по име — exact, после startswith."""
    if not parent.exists():
        return None
    safe = pdf_chunker.safe_name(base)
    exact = parent / safe
    if exact.is_dir():
        return exact
    # Fallback: startswith
    for d in parent.iterdir():
        if d.is_dir() and (d.name.startswith(safe) or safe.startswith(d.name)):
            return d
    return None


def count_zadachi_in_ocr(ocr_dir: Path) -> int:
    """Преброява 'Задача N' срещания в OCR cache."""
    if not ocr_dir or not ocr_dir.exists():
        return 0
    all_nums = set()
    for page_file in sorted(ocr_dir.glob("*.txt")):
        text = page_file.read_text(encoding="utf-8", errors="ignore")
        nums = re.findall(r'(?:Задача|Зад\.?)\s*(\d+)', text)
        all_nums.update(nums)
    return len(all_nums)


def dump_pdf_problems(base: str, target_pid: str | None = None):
    """Показва ВСИЧКИ проблеми в даден PDF + техния point_id."""
    cls_dir = find_dir(pdf_chunker.CLASSIFIED_DIR, base)
    if not cls_dir:
        print(f"    (classified not found for {base})")
        return

    data = json.loads((cls_dir / "all_problems.json").read_text(encoding="utf-8"))
    probs = data.get("problems", [])

    print(f"    PDF: {base} — {len(probs)} problems total:")
    for p in probs:
        num = p.get("num") or "?"
        grade = p.get("grade") or "?"
        pid = p.get("point_id") or "(none)"
        stmt = (p.get("statement") or "").replace("\n", " ")[:70]
        marker = " ←TARGET" if pid == target_pid else ""
        print(f"      #{num:>2} [g{grade}] → {pid:<6}{marker}: {stmt}")


def diag_point(pid: str):
    print(f"\n{'═' * 70}")
    print(f"  Point: {pid}")
    print('═' * 70)

    anchor = pdf_chunker.REAL_PROBLEMS_DIR / f"{pid.replace('.', '_')}.json"
    if not anchor.exists():
        print(f"  ✗ No anchor file: {anchor}")
        return

    problems = json.loads(anchor.read_text(encoding="utf-8")).get("problems", [])
    print(f"\n  AGGREGATED ANCHOR: {len(problems)} problem(s)")

    if not problems:
        return

    # Групирай по base PDF
    bases = {}
    for p in problems:
        base = extract_base_pdf(p.get("source", "?"))
        bases.setdefault(base, []).append(p)

    for base, base_probs in bases.items():
        print(f"\n  ── Base PDF: {base} ({len(base_probs)} in anchor) ──")

        # Фаза 1: OCR
        ocr_dir = find_dir(pdf_chunker._OCR_CACHE_DIR, base)
        ocr_count = count_zadachi_in_ocr(ocr_dir)
        print(f"    OCR:        {ocr_count} задачи в кеша")

        # Фаза 2: Extracted
        ext_dir = find_dir(pdf_chunker.EXTRACTED_DIR, base)
        ext_count = 0
        if ext_dir:
            ext_data = json.loads((ext_dir / "all_problems.json").read_text(encoding="utf-8"))
            ext_count = len(ext_data.get("problems", []))
        print(f"    Extracted:  {ext_count} problems")

        # Фаза 3: Classified
        cls_dir = find_dir(pdf_chunker.CLASSIFIED_DIR, base)
        to_this = 0
        to_other = Counter()
        if cls_dir:
            cls_data = json.loads((cls_dir / "all_problems.json").read_text(encoding="utf-8"))
            cls_probs = cls_data.get("problems", [])
            for p in cls_probs:
                cp = p.get("point_id") or "(none)"
                if cp == pid:
                    to_this += 1
                else:
                    to_other[cp] += 1
        print(f"    Classified: {to_this} → {pid}, {sum(to_other.values())} → other")
        if to_other:
            top = ", ".join(f"{k}:{v}" for k, v in to_other.most_common(5))
            print(f"                ({top})")

        # ДИАГНОЗА
        print(f"\n    ── DIAGNOSIS ──")
        if ocr_count == 0:
            print(f"    ⚠ OCR кешът е празен/липсва — провери дали OCR е минал")
        elif ocr_count < 2:
            print(f"    ✓ OCR има {ocr_count} задача — PDF-ът наистина е малък")
            print(f"    → Data limitation, не extraction bug")
        elif ext_count < ocr_count * 0.7:
            print(f"    ⚠ OCR {ocr_count} → Extracted {ext_count} (загуба {ocr_count - ext_count})")
            print(f"    → HYPOTHESIS: extraction bug → re-extract")
        elif to_this < ocr_count * 0.7:
            print(f"    ⚠ OCR {ocr_count} → в {pid} само {to_this} (загуба {ocr_count - to_this})")
            print(f"    → HYPOTHESIS: classification bug → re-classify")
        else:
            print(f"    ✓ Cascade консистентна")

        # ДЕТАЙЛЕН ДЪМП — показва всички задачи в PDF-а
        dump_pdf_problems(base, target_pid=pid)

    # CANDIDATE SEARCH: други PDF-и с проблеми, споменаващи topic keywords
    keywords = POINT_KEYWORDS.get(pid, [])
    if keywords:
        print(f"\n  ── CANDIDATES (споменават {keywords[:3]}... в ДРУГИ PDF-и) ──")
        candidates = []
        for cls_dir in pdf_chunker.CLASSIFIED_DIR.iterdir():
            if not cls_dir.is_dir():
                continue
            cls_file = cls_dir / "all_problems.json"
            if not cls_file.exists():
                continue
            try:
                data = json.loads(cls_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            for p in data.get("problems", []):
                if p.get("point_id") == pid:
                    continue  # вече е тук
                stmt = (p.get("statement") or "").lower()
                if any(kw in stmt for kw in keywords):
                    candidates.append({
                        "pdf": cls_dir.name,
                        "num": p.get("num"),
                        "grade": p.get("grade"),
                        "pid": p.get("point_id"),
                        "stmt": (p.get("statement") or "")[:60].replace("\n", " "),
                    })
        if candidates:
            print(f"    Намерени {len(candidates)} кандидата:")
            for c in candidates[:15]:
                print(f"      · {c['pdf']} #{c['num']} [g{c['grade']}] "
                      f"→ сега {c['pid']}: {c['stmt']}...")
        else:
            print(f"    Няма кандидати в други PDF-и")


def global_summary():
    """Показва всички точки и колко anchor problems имат."""
    print(f"\n{'═' * 70}")
    print(f"  GLOBAL SUMMARY: всички точки по брой anchor problems")
    print('═' * 70)

    points = {}
    for f in pdf_chunker.REAL_PROBLEMS_DIR.glob("*.json"):
        pid = f.stem.replace("_", ".")
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            points[pid] = len(data.get("problems", []))
        except Exception:
            points[pid] = 0

    # Сортирай по брой (ascending — най-проблемните отгоре)
    for pid, n in sorted(points.items(), key=lambda x: (x[1], x[0])):
        bar = "█" * min(n, 20) + ("..." if n > 20 else "")
        flag = " ⚠ LOW" if n < 3 else ""
        print(f"  {pid:<6} {n:>3} {bar}{flag}")

    low = [p for p, n in points.items() if n < 3]
    print(f"\n  ⚠ {len(low)} точки с < 3 problems: {low}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python diag_extraction.py <pid> | --all | --pdf <name>")
        return

    if sys.argv[1] == "--all":
        global_summary()
        points = sorted(f.stem.replace("_", ".") for f in pdf_chunker.REAL_PROBLEMS_DIR.glob("*.json"))
        for pid in points:
            diag_point(pid)
    elif sys.argv[1] == "--pdf":
        base = sys.argv[2]
        print(f"\nDump for PDF: {base}")
        dump_pdf_problems(base)
    else:
        diag_point(sys.argv[1])


if __name__ == "__main__":
    main()