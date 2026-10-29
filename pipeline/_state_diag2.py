import json
from pathlib import Path

state_file = Path("../pipeline/state.json")
data = json.loads(state_file.read_text(encoding="utf-8"))

processed = data.get("processed", {})
print(f"Total processed: {len(processed)}")
print(f"Budget: {data.get('budget', {})}")
print(f"Total calls: {data.get('total_calls')}, total cost: ${data.get('total_cost_usd', 0):.3f}")
print()

from collections import Counter
status_counts = Counter(v.get("status", "?") if isinstance(v, dict) else str(v) for v in processed.values())
print(f"Status counts: {dict(status_counts)}")
print()

# Провери sample
print("Sample (first 5):")
for k, v in list(processed.items())[:5]:
    print(f"  {k}: {v}")
print()

# Провери кои имат готова статия
articles_dir = Path("../generated/articles")
done_with_article = 0
done_without_article = []
for pid, info in processed.items():
    safe = pid.replace(".", "_")
    deep_file = articles_dir / safe / "deep.md"
    has_article = deep_file.exists()
    status = info.get("status", "?") if isinstance(info, dict) else str(info)
    if status == "done":
        if has_article:
            done_with_article += 1
        else:
            done_without_article.append(pid)

print(f"Done with article: {done_with_article}")
print(f"Done WITHOUT article: {len(done_without_article)}")
if done_without_article:
    print(f"  {done_without_article[:20]}")
