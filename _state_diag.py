import json
from pathlib import Path

state_file = Path("../pipeline/state.json")
data = json.loads(state_file.read_text(encoding="utf-8"))

# Разбери структурата
print("Top-level keys:", list(data.keys()))
print()

# Намери items
items = data.get("items", data.get("articles", {}))
print(f"Total items in state: {len(items)}")

from collections import Counter
status_counts = Counter(v.get("status", "?") for v in items.values())
print(f"Status counts: {dict(status_counts)}")
print()

# Провери кои НЯМАТ article
articles_dir = Path("../generated/articles")
missing = []
for pid, info in items.items():
    safe = pid.replace(".", "_")
    deep_file = articles_dir / safe / "deep.md"
    if not deep_file.exists() and info.get("status") == "done":
        missing.append(pid)

print(f"В state 'done', но НЯМА deep.md: {len(missing)}")
if missing:
    print(f"  {missing[:20]}")
