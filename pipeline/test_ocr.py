#!/usr/bin/env python3
"""test_ocr.py — тест на Mistral OCR на 1-2 PDF-а. Не пипа pipeline-а."""
import base64
import json
import sys
from pathlib import Path

import requests

# Вземи API key от config
cfg = json.loads(Path("config.json").read_text(encoding="utf-8"))
ocr_cfg = cfg.get("ocr", {})
if not ocr_cfg.get("enabled"):
    print("OCR не е enabled в config.json")
    sys.exit(1)

API_URL = ocr_cfg["api_url"]
API_KEY = ocr_cfg["api_key"]
MODEL = ocr_cfg["model"]

BASE = Path("..").resolve()


def find_pdf(keyword: str) -> Path | None:
    for p in BASE.rglob("*.pdf"):
        if keyword.lower() in p.name.lower():
            return p
    return None


def run_ocr(pdf: Path, save_path: Path | None = None) -> dict:
    print(f"\n{'='*70}")
    print(f"PDF: {pdf.name}")
    print(f"Size: {pdf.stat().st_size:,} bytes")
    print(f"{'='*70}")

    b64 = base64.b64encode(pdf.read_bytes()).decode()
    print("Calling Mistral OCR...")

    r = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "document": {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{b64}",
            },
            "include_image_base64": False,
        },
        timeout=300,
    )

    print(f"Status: {r.status_code}")
    if not r.ok:
        print(f"Error: {r.text[:500]}")
        return {}

    data = r.json()
    pages = data.get("pages", [])
    usage = data.get("usage_info", {})
    print(f"Pages: {len(pages)}")
    print(f"Usage: {usage}")

    if save_path:
        save_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Saved → {save_path}")

    print(f"\n{'─'*70}")
    for p in pages:
        idx = p.get("index", 0) + 1
        md = p.get("markdown", "")
        print(f"\n### Стр. {idx} ({len(md)} chars) ###")
        print(md)
    print(f"{'─'*70}")

    return data


if __name__ == "__main__":
    # 1. Намери probs файла
    probs = find_pdf("2024-11 кл-probs")
    if not probs:
        print("Не намирам 2024-11-probs.pdf")
        sys.exit(1)

    # 2. OCR него
    save1 = Path("test_ocr_probs.json")
    run_ocr(probs, save1)

    # 3. Опционално — sol файла
    sol = find_pdf("2024-11 кл-sol")
    if sol:
        print("\n\n" + "=" * 70)
        print("И сега sol файла (за сравнение)")
        print("=" * 70)
        save2 = Path("test_ocr_sol.json")
        run_ocr(sol, save2)