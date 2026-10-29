import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
import pdf_chunker, pdfplumber

pdfs = []
for folder in pdf_chunker.CONFIG.get('watch_folders', []):
    path = (pdf_chunker.BASE_DIR / folder).resolve()
    if path.exists():
        pdfs.extend(path.rglob('*.pdf'))

scanned = []
for pdf in pdfs:
    try:
        with pdfplumber.open(pdf) as p:
            chars = sum(len(pg.chars) for pg in p.pages)
        if chars < 50:
            scanned.append(pdf)
    except Exception:
        pass

print(f'OCR-вам {len(scanned)} PDF-а (~${len(scanned) * 2 * 0.001:.2f})...')
print()
for i, pdf in enumerate(scanned, 1):
    print(f'[{i}/{len(scanned)}] {pdf.name[:60]}')
    pages = pdf_chunker._ocr_pdf(pdf)
    if pages:
        total = sum(len(p['text']) for p in pages)
        print(f'  → {len(pages)}p, {total} chars')
