#!/usr/bin/env python3
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import base64
import json
import requests
from pathlib import Path

cfg = json.loads(Path("config.json").read_text(encoding="utf-8"))
ocr = cfg["ocr"]
base = Path("..").resolve()

for target in ["2019-10", "2015-11"]:
    pdf = next((p for p in base.rglob("*.pdf") if target in p.name and "probs" in p.name), None)
    if not pdf:
        print(f"Не намирам: {target}")
        continue

    b64 = base64.b64encode(pdf.read_bytes()).decode()

    print()
    print("=" * 70)
    print(pdf.name)
    print("=" * 70)

    r = requests.post(
        ocr["api_url"],
        headers={
            "Authorization": f"Bearer {ocr['api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": ocr["model"],
            "document": {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{b64}",
            },
            "include_image_base64": True,
        },
        timeout=300,
    )

    if not r.ok:
        print(f"FAIL: {r.status_code}")
        print(r.text[:300])
        continue

    d = r.json()
    for p in d.get("pages", []):
        md = p.get("markdown", "")
        print(f"\n({len(md)} chars)")
        print(md)
        print(f"\n... КРАЙ: ...{md[-400:]}")