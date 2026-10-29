import json
import time
from pathlib import Path
from datetime import date

GEN = Path("../generated")
cutoff = time.time() - 86400

print("=" * 60)
print("ARTICLES")
print("=" * 60)
articles = GEN / "articles"
if articles.exists():
    dirs = [d for d in articles.iterdir() if d.is_dir()]
    with_deep = [d for d in dirs if (d / "deep.md").exists()]
    fresh = [d for d in with_deep if d.joinpath("deep.md").stat().st_mtime > cutoff]
    print(f"  Total folders: {len(dirs)}")
    print(f"  With deep.md: {len(with_deep)}")
    print(f"  Generated last 24h: {len(fresh)}")
    if fresh:
        for d in sorted(fresh, key=lambda x: x.name):
            print(f"    {d.name}")

print()
print("=" * 60)
print("ANCHORS")
print("=" * 60)
anchors = GEN / "anchors"
if anchors.exists():
    files = list(anchors.glob("*.json"))
    total = 0
    for f in files:
        if f.name == "_unclassified.json":
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            total += d.get("total", 0)
        except Exception:
            pass
    print(f"  Files: {len(files)}")
    print(f"  Total problems: {total}")

print()
print("=" * 60)
print("STATE BUDGET")
print("=" * 60)
state = Path("../pipeline/state.json")
if state.exists():
    d = json.loads(state.read_text(encoding="utf-8"))
    b = d.get("budget", {})
    print(f"  Date: {b.get('date')}")
    print(f"  Spent: ${b.get('spent_usd', 0):.4f}")
