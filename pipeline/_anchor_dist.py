import json
from pathlib import Path
from collections import Counter

counts = Counter()
for f in Path("../generated/anchors").glob("*.json"):
    if f.name == "_unclassified.json": continue
    data = json.loads(f.read_text(encoding="utf-8"))
    counts[data["point_id"]] = data["total"]

print(f"Total anchor files: {len(counts)}")
print(f"Total anchored problems: {sum(counts.values())}")
print()
for pid in sorted(counts.keys(), key=lambda x: (-counts[x], x)):
    print(f"  {pid:8s} → {counts[pid]:3d}")
