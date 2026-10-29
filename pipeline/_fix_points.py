import json
from pathlib import Path

BASE = Path("../generated/cache/classified")

FIXES = [
    ("OLI-2-Областен кръг-2004-11 кл", "последователни членове на геометрична прогресия", "5.11", "R.6"),
    ("OLI-2-Областен кръг-2001-11 кл", "AE = 3CE", "5.10", "1.6"),
    ("OLI-2-Областен кръг-2013-11 кл", "Допирателната към k в точка C пресича лъча BA", "1.4", "1.5"),
    ("OLI-2-Областен кръг-2022-11 кл", "ъглополовящата BL", "2.6", "1.6"),
]

total_fixed = 0
for folder, marker, old_pid, new_pid in FIXES:
    f = BASE / folder / "all_problems.json"
    if not f.exists():
        print(f"⚠ ЛИПСВА: {folder}")
        continue
    data = json.loads(f.read_text(encoding="utf-8"))
    hits = 0
    for p in data["problems"]:
        stmt = p.get("statement") or ""
        if marker in stmt:
            hits += 1
            cur = p.get("point_id")
            if cur == old_pid:
                p["point_id"] = new_pid
                print(f"  ✓ {folder}: {old_pid} → {new_pid}")
                total_fixed += 1
            elif cur == new_pid:
                print(f"  · {folder}: вече е {new_pid} (нищо не правя)")
            else:
                print(f"  ⚠ {folder}: намерих stmt, но point_id е {cur!r} (очаквах {old_pid!r})")
    if hits == 0:
        print(f"  ✗ {folder}: statement НЕ е намерен")
        print(f"     Първи statement в файла: {(data['problems'][0].get('statement') or '')[:80]!r}")
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"\n═══ Общо поправени: {total_fixed}/4 ═══")
