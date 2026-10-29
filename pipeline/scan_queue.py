#!/usr/bin/env python3
"""
scan_queue.py — Автоматично сканира STEPS от HTML и попълва queue.jsonl.

Употреба:
    python scan_queue.py                                  # добавя всичко ново
    python scan_queue.py --step 1                         # само Step 1
    python scan_queue.py --only-with-pdf --pdf-root ../pdfs
    python scan_queue.py --only-missing                   # само без explanation
    python scan_queue.py --dry-run                        # показва без да пише
    python scan_queue.py --reset                          # изчиства queue и сканира наново

Интеграция с pipeline.py:
    from scan_queue import scan_and_merge
    scan_and_merge(html_path, queue_path, pdf_root)
"""

import os
import re
import json
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import Optional


# ═══════════════════════════════════════════════════════════════
# 1. EXTRACT STEPS ОТ HTML
# ═══════════════════════════════════════════════════════════════
def extract_steps_raw(html_path: Path) -> str:
    """Извлича суровия JS код на STEPS масива от HTML."""
    content = html_path.read_text(encoding="utf-8")

    marker = "const STEPS = "
    start = content.find(marker)
    if start == -1:
        raise ValueError(f"Не намирам 'const STEPS' в {html_path}")

    arr_start = start + len(marker)

    # Намери съответстващата ']' на top-level
    depth = 0
    in_str = False
    quote = None
    escape = False
    end = arr_start

    for i in range(arr_start, len(content)):
        c = content[i]

        if escape:
            escape = False
            continue
        if c == "\\" and in_str:
            escape = True
            continue

        if in_str:
            if c == quote:
                in_str = False
            continue

        if c in ('"', "'", "`"):
            in_str = True
            quote = c
            continue

        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end == arr_start:
        raise ValueError("Не намирам края на STEPS масива")

    return content[arr_start:end]


# ═══════════════════════════════════════════════════════════════
# 2. PARSE — Node.js (най-надеждно) или regex fallback
# ═══════════════════════════════════════════════════════════════
def parse_via_node(js_array: str) -> Optional[list]:
    """Използва Node.js да eval-не JS и върне JSON. None ако Node липсва.
    Ползва temp файл, за да заобиколи Windows command-line limit (~8191 chars)."""
    if not shutil.which("node"):
        return None

    import tempfile

    js_code = (
        "const STEPS = " + js_array + ";\n"
        "process.stdout.write(JSON.stringify(STEPS));\n"
    )

    tmp_path = None
    try:
        # Write to temp file (no length limit)
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", delete=False,
            encoding="utf-8", dir=BASE_DIR if 'BASE_DIR' in globals() else None,
        ) as f:
            f.write(js_code)
            tmp_path = f.name

        result = subprocess.run(
            ["node", tmp_path],
            capture_output=True, text=True, timeout=120, encoding="utf-8",
        )
        if result.returncode != 0:
            print(f"[Node] stderr: {result.stderr[:800]}", file=sys.stderr)
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"[Node] грешка: {e}", file=sys.stderr)
        return None
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def parse_via_regex(js_array: str) -> list:
    """Fallback: извлича точките с regex. Връща плосък списък с step_id."""
    STR = r'"((?:[^"\\]|\\.)*)"'

    # ── Стъпка 1: намери step границите ──
    step_re = re.compile(
        r'\{\s*id\s*:\s*(\d+)\s*,\s*icon\s*:\s*' + STR +
        r'\s*,\s*title\s*:\s*' + STR,
        re.DOTALL,
    )

    step_ranges = []
    for m in step_re.finditer(js_array):
        step_id = int(m.group(1))
        step_title = _unescape(m.group(3))
        start = m.start()
        end = _find_object_end(js_array, start)
        step_ranges.append({
            "id": step_id,
            "title": step_title,
            "start": start,
            "end": end,
        })

    if not step_ranges:
        # Няма стъпки — може би вече е flat. Опитай само точки.
        return _extract_flat_points(js_array, step_id=None, step_title="")

    # ── Стъпка 2: за всяка стъпка, извлечи нейните точки ──
    all_points = []
    for step in step_ranges:
        block = js_array[step["start"]:step["end"]]
        pts = _extract_flat_points(block, step["id"], step["title"])
        all_points.extend(pts)

    return all_points


def _extract_flat_points(block: str, step_id, step_title: str) -> list:
    """Извлича точки от текстов блок. Връща flat list."""
    STR = r'"((?:[^"\\]|\\.)*)"'
    point_re = re.compile(
        r'\{\s*id\s*:\s*' + STR +
        r'\s*,\s*title\s*:\s*' + STR +
        r'\s*,\s*desc\s*:\s*' + STR,
        re.DOTALL,
    )

    pts = []
    for m in point_re.finditer(block):
        pid = m.group(1)
        # Пропусни step-level IDs (без точка)
        if "." not in pid:
            continue
        title = _unescape(m.group(2))
        desc = _unescape(m.group(3))

        pstart = m.start()
        pend = _find_object_end(block, pstart)
        pblock = block[pstart:pend]

        source = _first_match(pblock, r'source\s*:\s*' + STR)
        pdf = _first_match(pblock, r'\bpdf\s*:\s*' + STR)
        page = _first_match(pblock, r'\bpage\s*:\s*(\d+)')
        expl = _first_match(pblock, r'explanation\s*:\s*' + STR)

        pts.append({
            "id": pid,
            "title": title,
            "desc": desc,
            "source": _unescape(source) if source else "",
            "pdf": _unescape(pdf) if pdf else "",
            "page": int(page) if page else 1,
            "explanation": _unescape(expl) if expl else "",
            "step_id": step_id,
            "step_title": step_title,
        })

    return pts


def _find_object_end(text: str, start: int) -> int:
    """Намира затварящата '}' на обект, започващ на start."""
    depth = 0
    in_str = False
    quote = None
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if escape:
            escape = False
            continue
        if c == "\\" and in_str:
            escape = True
            continue
        if in_str:
            if c == quote:
                in_str = False
            continue
        if c in ('"', "'", "`"):
            in_str = True
            quote = c
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return len(text)


def _first_match(text: str, pattern: str) -> Optional[str]:
    m = re.search(pattern, text)
    if not m:
        return None
    return m.group(1) if m.lastindex else ""


def _unescape(s: str) -> str:
    return (s.replace(r"\\n", "\n").replace(r"\\t", "\t")
             .replace(r"\\\"", '"').replace(r"\\\\", "\\"))


# ═══════════════════════════════════════════════════════════════
# 3. ФЛАТОСВАНЕ + ФИЛТРИ
# ═══════════════════════════════════════════════════════════════
def flatten_points(steps: list, only_step: Optional[int] = None) -> list:
    """STEPS → плосък списък от точки с добавено step_id.
    Работи и ако входът вече е плосък (от regex fallback-а)."""
    if not steps:
        return []

    # Detect: flat list (points with no 'points' key)?
    is_flat = "points" not in steps[0]
    out = []

    if is_flat:
        for p in steps:
            if only_step is not None and p.get("step_id") != only_step:
                continue
            out.append({
                "id": p.get("id", ""),
                "title": p.get("title", ""),
                "desc": p.get("desc", ""),
                "source": p.get("source", ""),
                "pdf": p.get("pdf", ""),
                "page": p.get("page", 1),
                "explanation": p.get("explanation", ""),
                "step_id": p.get("step_id", ""),
                "step_title": p.get("step_title", ""),
            })
        return out

    for step in steps:
        sid = step.get("id")
        if only_step is not None and sid != only_step:
            continue
        for p in step.get("points", []):
            out.append({
                "id": p.get("id", ""),
                "title": p.get("title", ""),
                "desc": p.get("desc", ""),
                "source": p.get("source", ""),
                "pdf": p.get("pdf", ""),
                "page": p.get("page", 1),
                "explanation": p.get("explanation", ""),
                "step_id": sid,
                "step_title": step.get("title", ""),
            })
    return out


def pdf_exists_on_disk(pdf_field: str, pdf_root: Optional[Path]) -> bool:
    if not pdf_root or not pdf_field:
        return False
    candidate = pdf_root / (pdf_field + ".pdf")
    return candidate.exists()


# ═══════════════════════════════════════════════════════════════
# 4. MERGE СЪС СЪЩЕСТВУВАЩ QUEUE
# ═══════════════════════════════════════════════════════════════
def load_existing_ids(queue_path: Path) -> set:
    if not queue_path.exists():
        return set()
    ids = set()
    with open(queue_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
                ids.add(obj.get("id", ""))
            except Exception:
                pass
    return ids


def write_queue(items: list, queue_path: Path, append: bool = True):
    mode = "a" if append else "w"
    with open(queue_path, mode, encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


# ═══════════════════════════════════════════════════════════════
# 5. MAIN SCANNER
# ═══════════════════════════════════════════════════════════════
def scan_and_merge(
    html_path: Path,
    queue_path: Path,
    pdf_root: Optional[Path] = None,
    only_step: Optional[int] = None,
    only_missing: bool = False,
    only_with_pdf: bool = False,
    skip_with_explanation: bool = True,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict:
    """Основна функция. Връща stats dict."""

    stats = {
        "total_scanned": 0,
        "already_in_queue": 0,
        "skipped_with_explanation": 0,
        "skipped_no_pdf": 0,
        "added": 0,
        "added_ids": [],
    }

    print(f"📖 Чета: {html_path}")
    from config import STEPS_FILE
    raw = extract_steps_raw(STEPS_FILE)
    print(f"   STEPS raw: {len(raw):,} символа")

    steps = parse_via_node(raw)
    parser_used = "node"
    if steps is None:
        print("   ⚠ Node.js липсва — ползвам regex fallback")
        steps = parse_via_regex(raw)
        parser_used = "regex"

    if not steps:
        print("   ✗ Не успях да парсна STEPS")
        return stats

    print(f"   Парснах {len(steps)} steps (чрез {parser_used})")

    points = flatten_points(steps, only_step)
    stats["total_scanned"] = len(points)
    print(f"   Точки: {len(points)}" + (f" (само Step {only_step})" if only_step else ""))

    existing_ids = set() if overwrite else load_existing_ids(queue_path)

    new_items = []
    for p in points:
        pid = p["id"]

        # Вече в queue?
        if pid in existing_ids:
            stats["already_in_queue"] += 1
            continue

        # Има explanation в HTML?
        if skip_with_explanation and not only_missing:
            if p.get("explanation", "").strip():
                stats["skipped_with_explanation"] += 1
                continue

        # PDF на диска?
        if only_with_pdf and not pdf_exists_on_disk(p["pdf"], pdf_root):
            stats["skipped_no_pdf"] += 1
            continue

        # Формирай queue item
        item = {
            "id": pid,
            "title": p["title"],
            "desc": p["desc"],
            "source": p["source"],
            "pdf": p["pdf"],
            "page": p["page"],
        }
        if p.get("explanation", "").strip():
            item["explanation"] = p["explanation"]

        new_items.append(item)
        stats["added_ids"].append(pid)

    stats["added"] = len(new_items)

    if dry_run:
        print(f"\n🔍 DRY-RUN — няма да пиша нищо")
        print(f"   Щеше да добавиш {len(new_items)} items:")
        for it in new_items[:20]:
            print(f"     • {it['id']:8s} {it['title'][:60]}")
        if len(new_items) > 20:
            print(f"     ... и още {len(new_items) - 20}")
        return stats

    if new_items:
        if overwrite:
            print(f"\n⚠ Overwrite режим — изчиствам {queue_path}")
            if queue_path.exists():
                queue_path.unlink()

        write_queue(new_items, queue_path, append=not overwrite)
        print(f"\n✅ Добавени {len(new_items)} нови items → {queue_path}")
    else:
        print(f"\n✅ Няма нови items за добавяне")

    print(f"\n📊 Статистика:")
    print(f"   Общо сканирани:            {stats['total_scanned']}")
    print(f"   Вече в queue:              {stats['already_in_queue']}")
    print(f"   Пропуснати (имат expl):    {stats['skipped_with_explanation']}")
    print(f"   Пропуснати (без PDF):      {stats['skipped_no_pdf']}")
    print(f"   ➕ ДОБАВЕНИ:               {stats['added']}")

    return stats


# ═══════════════════════════════════════════════════════════════
# 6. CLI
# ═══════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser(description="Сканира STEPS от HTML → queue.jsonl")
    ap.add_argument("html", nargs="?", default="index.html",
                    help="Път до HTML файла (default: index.html)")
    ap.add_argument("--queue", default="queue.jsonl",
                    help="Път до queue файла (default: queue.jsonl)")
    ap.add_argument("--pdf-root", default=None,
                    help="Папка с PDF-и (за --only-with-pdf / --check-pdf)")
    ap.add_argument("--step", type=int, default=None,
                    help="Само конкретен Step (напр. 1)")
    ap.add_argument("--only-missing", action="store_true",
                    help="Само точки БЕЗ explanation")
    ap.add_argument("--only-with-pdf", action="store_true",
                    help="Само точки, чиито PDF съществува на диска")
    ap.add_argument("--include-with-explanation", action="store_true",
                    help="Включи и точки, които вече имат explanation")
    ap.add_argument("--reset", action="store_true",
                    help="Изчисти queue и сканирай наново (overwrite)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Покажи какво ще се добави, без да пише")
    args = ap.parse_args()

    html_path = Path(args.html).resolve()
    queue_path = Path(args.queue).resolve()
    pdf_root = Path(args.pdf_root).resolve() if args.pdf_root else None

    if not html_path.exists():
        print(f"✗ Не намирам {html_path}", file=sys.stderr)
        sys.exit(1)

    scan_and_merge(
        html_path=html_path,
        queue_path=queue_path,
        pdf_root=pdf_root,
        only_step=args.step,
        only_missing=args.only_missing,
        only_with_pdf=args.only_with_pdf,
        skip_with_explanation=not args.include_with_explanation,
        overwrite=args.reset,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()