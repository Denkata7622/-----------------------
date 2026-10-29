#!/usr/bin/env python3
"""test_ocr_quality.py — OCR качество на 3 различни сканирани PDF-а."""
import sys
import io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import pdf_chunker

# Промени имената според това, което виждаш в --scan
targets = [
    '2023-11 кл-probs',
    '2019-10 кл-probs',
    '2015-11 кл-probs',
]

base = pdf_chunker.BASE_DIR.parent
for t in targets:
    matches = [p for p in base.rglob('*.pdf') if t in p.name]
    if not matches:
        print(f'\n✗ Не намирам: {t}')
        continue
    pdf = matches[0]
    print('\n' + '=' * 70)
    print(f'PDF: {pdf.name} ({pdf.stat().st_size/1024:.0f}KB)')
    print('=' * 70)
    pages = pdf_chunker._ocr_pdf(pdf)
    if not pages:
        print('✗ OCR върна 0 страници')
        continue
    for p in pages:
        print(f'\n--- Стр. {p["page"]} ({len(p["text"])} chars) ---')
        print(p['text'][:700])