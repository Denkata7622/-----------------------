#!/usr/bin/env python3
"""Възстановява state.json от успешно генерираните output/ папки."""
import json
from pathlib import Path
from datetime import date
import time

BASE = Path(__file__).parent
OUTPUT = BASE / "output"
STATE = BASE / "state.json"

def main():
    if not OUTPUT.exists():
        print("✗ Няма output/ папка")
        return

    done = {}
    for folder in sorted(OUTPUT.iterdir()):
        if not folder.is_dir():
            continue
        has_deep = (folder / "deep.md").exists()
        has_text = (folder / "text.md").exists()
        if not has_deep and not has_text:
            continue
        pid = folder.name.replace("_", ".")
        done[pid] = {
            "status": "done" if has_deep else "error",
            "cost": 0.013 if has_deep else 0.005,
            "tokens": 15000 if has_deep else 5000,
            "ts": time.time(),
        }

    # Backup на стария state, ако съществува
    if STATE.exists():
        backup = STATE.with_suffix(f".json.broken-{int(time.time())}")
        STATE.rename(backup)
        print(f"💾 Стар state → {backup.name}")

    state = {
        "processed": done,
        "budget": {"date": str(date.today()), "spent_usd": 0.0, "calls": 0},
        "started_at": time.time(),
        "total_calls": len(done),
        "total_cost_usd": len(done) * 0.013,
    }

    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Възстановени {len(done)} точки в state.json")
    print()
    print("Точки:")
    for pid in sorted(done.keys(), key=lambda x: [int(p) for p in x.split(".")]):
        print(f"  {pid} ({done[pid]['status']})")

if __name__ == "__main__":
    main()