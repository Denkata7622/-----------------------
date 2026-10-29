import json
from pathlib import Path

# 1. Къде е 2001/2 в anchors?
print("═══ В ANCHORS ═══")
for pid in ["5.10", "1.6"]:
    f = Path(f"../generated/anchors/{pid.replace('.', '_')}.json")
    if not f.exists():
        print(f"{pid}: файл НЕ съществува")
        continue
    data = json.loads(f.read_text(encoding="utf-8"))
    print(f"\n{pid}: {data['total']} problems")
    for p in data["problems"]:
        if "2001" in (p.get("source") or ""):
            print(f"  ★ {p.get('source')}")

# 2. Къде е 2001/2 в classified/ (търси навсякъде)?
print("\n═══ В CLASSIFIED (всички файлове) ═══")
marker = "AE = 3CE"
for f in Path("../generated/cache/classified").glob("*/all_problems.json"):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    for p in data["problems"]:
        if marker in (p.get("statement") or ""):
            print(f"  {data['pdf']} · num={p.get('num')} · pid={p.get('point_id')!r} · year={p.get('year')}")

# 3. Провери dedupe — има ли друг проблем с year=2001, num=2?
print("\n═══ Всички с year=2001, num=2 ═══")
for f in Path("../generated/cache/classified").glob("*/all_problems.json"):
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    for p in data["problems"]:
        if p.get("year") == 2001 and p.get("num") == 2:
            stmt = (p.get("statement") or "")[:80]
            print(f"  {data['pdf']} · pid={p.get('point_id')!r}")
            print(f"    stmt[:80]={stmt!r}")
            print(f"    sol_len={len((p.get('solution') or '').strip())}")
