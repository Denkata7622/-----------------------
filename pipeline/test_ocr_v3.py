#!/usr/bin/env python3
import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import base64, json, re, requests
from pathlib import Path

cfg = json.loads(Path("config.json").read_text(encoding="utf-8"))
ocr = cfg["ocr"]
base = Path("..").resolve()

targets = ["2018-11", "2020-10", "2016-11"]

for target in targets:
    pdf = next((p for p in base.rglob("*.pdf") if target in p.name and "probs" in p.name), None)
    if not pdf:
        print(f"\n[X] Не намирам: {target}")
        continue

    b64 = base64.b64encode(pdf.read_bytes()).decode()
    print()
    print("=" * 70)
    print(pdf.name)
    print("=" * 70)

    r = requests.post(
        ocr["api_url"],
        headers={"Authorization": f"Bearer {ocr['api_key']}", "Content-Type": "application/json"},
        json={
            "model": ocr["model"],
            "document": {"type": "document_url", "document_url": f"data:application/pdf;base64,{b64}"},
            "include_image_base64": True,
        },
        timeout=300,
    )

    if not r.ok:
        print(f"FAIL: {r.status_code} {r.text[:200]}")
        continue

    d = r.json()
    for p in d.get("pages", []):
        md = p.get("markdown", "")
        task_nums = re.findall(r"Задача\s+\d+\.\d+\.", md)
        print(f"\n{len(md)} chars | {len(task_nums)} задачи: {task_nums}")
        print(f"\n... КРАЙ: ...{md[-300:]}")
