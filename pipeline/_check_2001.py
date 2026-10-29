import json
from pathlib import Path

f = Path("../generated/cache/classified/OLI-2-Областен кръг-2001-11 кл/all_problems.json")
data = json.loads(f.read_text(encoding="utf-8"))

print(f"Total problems: {len(data['problems'])}\n")
for i, p in enumerate(data["problems"], 1):
    pid = p.get("point_id")
    num = p.get("num")
    stmt_short = (p.get("statement") or "")[:60]
    has_sol = "YES" if (p.get("solution") or "").strip() else "no"
    has_ae = "★" if "AE = 3CE" in (p.get("statement") or "") else " "
    print(f"[{i}] num={num:>2} pid={pid!r:<8} sol={has_sol} {has_ae}  {stmt_short}")

# Брой по point_id
from collections import Counter
pids = Counter(p.get("point_id") for p in data["problems"])
print(f"\nПо point_id: {dict(pids)}")

# Дали има дубликати на 2001/2
ae_matches = [p for p in data["problems"] if "AE = 3CE" in (p.get("statement") or "")]
print(f"\nЗадачи с 'AE = 3CE': {len(ae_matches)}")
for m in ae_matches:
    print(f"  num={m.get('num')}, point_id={m.get('point_id')!r}, has_sol={'YES' if m.get('solution') else 'no'}")
