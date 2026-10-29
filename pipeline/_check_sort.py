import sys
sys.path.insert(0, ".")
from pipeline import Queue, State, CONFIG
from pathlib import Path
import json

# Temporarily point to nonexistent state — за да не skip-ва done
state = State.__new__(State)
state.file = Path("_dummy_state.json")
state.data = {"processed": {}, "budget": {"date": "2026-10-25", "spent_usd": 0.0, "calls": 0}}

queue = Queue()
pending = queue.pending(state)

print(f"Total items: {queue.total()}")
print(f"Pending: {len(pending)}")
print(f"\nFirst 10 pending (трябва да са R.1–R.10):")
for it in pending[:10]:
    print(f"  {it.id}: {it.title[:50]}")

print(f"\nNext 5 след R (трябва да са 1.1–1.5):")
for it in pending[15:20]:
    print(f"  {it.id}: {it.title[:50]}")
