#!/usr/bin/env python3
# parse_dashboard.py
"""
Парсва Dashboard.txt (provider activity log).

Употреба:
    python parse_dashboard.py Dashboard.txt                     # само текстов отчет
    python parse_dashboard.py Dashboard.txt provider_costs.json # + JSON за dashboard
    python parse_dashboard.py Dashboard.txt out.json --now 2026-10-28T12:00
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

COST_RE   = re.compile(r"\$([0-9]+(?:\.[0-9]+)?)")
TOKENS_RE = re.compile(r"([\d,]+)\s+in\s*/\s*([\d,]+)\s*out")
REL_RE    = re.compile(r"^(\d+)\s*([hdm])\s+ago$", re.I)
ABS_RE    = re.compile(r"^(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})$")
BULLET    = "●"

_MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"]
)}


def _parse_latency_ms(text):
    total = 0
    m = re.search(r"(\d+)\s*h", text)
    if m: total += int(m.group(1)) * 3_600_000
    m = re.search(r"(\d+)\s*m(?!s)", text)
    if m: total += int(m.group(1)) * 60_000
    m = re.search(r"(\d+(?:\.\d+)?)\s*s(?!\w)", text)
    if m: total += int(float(m.group(1)) * 1000)
    m = re.search(r"(\d+(?:\.\d+)?)\s*ms", text)
    if m: total += int(float(m.group(1)))
    return total


def _parse_time(text, ref_now):
    """'13h ago' | '6d ago' | '21 Oct 2026' -> datetime | None"""
    text = text.strip()
    m = REL_RE.match(text)
    if m:
        n, unit = int(m.group(1)), m.group(2).lower()
        delta = {"h": timedelta(hours=n),
                 "d": timedelta(days=n),
                 "m": timedelta(minutes=n)}[unit]
        return ref_now - delta
    m = ABS_RE.match(text)
    if m:
        mo = _MONTHS.get(m.group(2).lower()[:3])
        if mo:
            try:
                return datetime(int(m.group(3)), mo, int(m.group(1)))
            except ValueError:
                return None
    return None


def _time_kind(text):
    text = text.strip()
    if REL_RE.match(text): return "relative"
    if ABS_RE.match(text): return "absolute"
    return None


def _split_tab_row(line):
    """Returns (bi, parts) or (None, None) if unusable."""
    if "\t" not in line:
        return None, None
    parts = [p.strip() for p in line.split("\t")]
    bi = next((i for i, p in enumerate(parts) if BULLET in p), None)
    if bi is None or bi + 3 >= len(parts):
        return None, None
    return bi, parts


def parse_line(line, ref_now):
    """
    Парсва един ред -> dict | None
    Полета: ts, model, in_tokens, out_tokens, tokens, cost(Decimal),
            status('ok'|'error'), latency_ms
    """
    line = line.rstrip("\n")
    if BULLET not in line:
        return None

    bi, parts = _split_tab_row(line)
    if parts is None:
        return None

    time_cell   = parts[bi].replace(BULLET, "").strip()
    model       = parts[bi + 1]
    tokens_cell = parts[bi + 2]
    cost_cell   = parts[bi + 3]
    result_cell = parts[bi + 4] if bi + 4 < len(parts) else ""

    if not model:
        return None

    ts = _parse_time(time_cell, ref_now)
    if ts is None:
        return None

    # --- tokens + status ---
    if tokens_cell.lower().startswith("no usage"):
        in_tokens = out_tokens = 0
        status = "error"
    else:
        tm = TOKENS_RE.search(tokens_cell)
        if not tm:
            return None
        in_tokens  = int(tm.group(1).replace(",", ""))
        out_tokens = int(tm.group(2).replace(",", ""))
        status = "ok"

    # --- cost ---
    if cost_cell.lower() == "free" or cost_cell in ("–", "-", ""):
        cost = Decimal("0")
    else:
        cm = COST_RE.search(cost_cell)
        if not cm:
            return None
        cost = Decimal(cm.group(1))

    if result_cell.lower().startswith("error"):
        status = "error"
        cost = Decimal("0")

    return {
        "ts":         ts.isoformat(timespec="seconds"),
        "model":      model,
        "in_tokens":  in_tokens,
        "out_tokens": out_tokens,
        "tokens":     in_tokens + out_tokens,
        "cost":       cost,
        "status":     status,
        "latency_ms": _parse_latency_ms(result_cell),
    }


def auto_calibrate_now(lines):
    """
    Оценява референтно 'сега' от самите данни.
    Ако файлът има и относителни, и абсолютни дати — приема, че най-новата
    абсолютна дата е денят преди най-стария относителен запис ('6d ago').
    """
    rel_max_days = 0
    abs_dates = []

    for line in lines:
        bi, parts = _split_tab_row(line)
        if parts is None:
            continue
        tcell = parts[bi].replace(BULLET, "").strip()
        kind = _time_kind(tcell)
        if kind == "relative":
            m = REL_RE.match(tcell)
            n, u = int(m.group(1)), m.group(2).lower()
            days = n * {"h": 1 / 24, "d": 1, "m": 1 / 1440}[u]
            rel_max_days = max(rel_max_days, days)
        elif kind == "absolute":
            m = ABS_RE.match(tcell)
            mo = _MONTHS.get(m.group(2).lower()[:3])
            if mo:
                try:
                    abs_dates.append(datetime(int(m.group(3)), mo, int(m.group(1))))
                except ValueError:
                    pass

    if abs_dates and rel_max_days > 0:
        newest_abs = max(abs_dates)
        return newest_abs + timedelta(days=int(rel_max_days) + 1), "auto"

    return datetime.now(), "system clock"


def _json_default(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError(f"Not JSON serializable: {type(o)}")


def main():
    ap = argparse.ArgumentParser(description="Parse provider Dashboard.txt")
    ap.add_argument("input",   help="Dashboard.txt")
    ap.add_argument("output",  nargs="?", help="provider_costs.json (optional)")
    ap.add_argument("--now",   default=None,
                    help="ISO reference time for relative dates "
                         "(e.g. '2026-10-28T12:00'). Default: auto.")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        lines = f.readlines()

    if args.now:
        ref_now = datetime.fromisoformat(args.now.replace(" ", "T"))
        now_src = "--now"
    else:
        ref_now, now_src = auto_calibrate_now(lines)

    total        = Decimal("0")
    counted_rows = 0
    skipped_rows = 0
    entries      = []
    by_model     = defaultdict(lambda: {"cost": Decimal("0"), "rows": 0})

    for line in lines:
        if BULLET not in line:
            continue
        parsed = parse_line(line, ref_now)
        if parsed is None:
            skipped_rows += 1
            continue

        by_model[parsed["model"]]["cost"] += parsed["cost"]
        by_model[parsed["model"]]["rows"] += 1
        total += parsed["cost"]
        counted_rows += 1
        entries.append(parsed)

    # --- текстов отчет (същият като преди) ---
    print(f"Общо: ${total:.6f}")
    print(f"Редове с цена: {counted_rows}")
    print(f"Пропуснати редове без цена/грешка: {skipped_rows}")
    print(f"Референтно време: {ref_now.isoformat(sep=' ')} ({now_src})")
    print()
    print(f"{'Модел':55} {'Редове':>7} {'Цена':>14}")
    print("-" * 80)
    for model, d in sorted(by_model.items(),
                           key=lambda kv: kv[1]["cost"], reverse=True):
        print(f"{model:55} {d['rows']:7d} ${d['cost']:13.6f}")

    # --- JSON за dashboard ---
    if args.output:
        entries.sort(key=lambda x: x["ts"], reverse=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False,
                      indent=2, default=_json_default)
        print(f"\n→ {args.output}  ({len(entries)} entries)")


if __name__ == "__main__":
    main()