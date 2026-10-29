#!/usr/bin/env python3
"""Проверява, че cost_tracker записва в ledger. Прави 1 мини call."""
import json, time, sys
from pathlib import Path
import requests
from cost_tracker import init, track_call

BASE = Path(__file__).parent.resolve()
init(BASE.parent / "generated" / "costs" / "ledger.jsonl")

cfg = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
model = cfg.get("chunker", {}).get("classify_model", "openai/gpt-oss-120b")
url = cfg["generator"]["api_url"]
key = cfg["generator"]["api_key"]

payload = {
    "model": model,
    "max_tokens": 50,
    "temperature": 0,
    "messages": [
        {"role": "system", "content": "Reply with exactly one word: OK."},
        {"role": "user", "content": "Say OK."},
    ],
}

print(f"→ POST {url}  model={model}")
t0 = time.time()
r = requests.post(url, json=payload, timeout=60,
                  headers={"Authorization": f"Bearer {key}",
                           "Content-Type": "application/json"})

if not r.ok:
    print(f"✗ HTTP {r.status_code}: {r.text[:300]}")
    sys.exit(1)

data = r.json()
content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
usage = data.get("usage", {})
print(f"✓ response: {content!r}")
print(f"✓ usage: {usage}")

track_call("smoke_test", "test", model, data, item_id="smoke-1", t0=t0)

ledger = BASE.parent / "generated" / "costs" / "ledger.jsonl"
if ledger.exists():
    lines = ledger.read_text(encoding="utf-8").strip().splitlines()
    print(f"\n✓ ledger: {ledger}  ({len(lines)} entries)")
    print(f"  last: {lines[-1]}")
else:
    print(f"\n✗ ledger не е създаден: {ledger}")
    sys.exit(2)