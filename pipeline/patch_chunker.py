#!/usr/bin/env python3
"""patch_chunker.py — прилага 7 patch-а към pdf_chunker.py атомарно."""
import sys, io
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = Path(__file__).parent / "pdf_chunker.py"
src = P.read_text(encoding="utf-8")
orig_len = len(src)

# ─── Patch 1: imports → config ───
OLD_1 = '''BASE_DIR = Path(__file__).parent.resolve()
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)
logging.getLogger("pypdf").setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PDF_CHUNKER] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"chunker_{date.today()}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("chunker")

EXTRACTED_DIR = BASE_DIR / "extracted"
EXTRACTED_DIR.mkdir(exist_ok=True)
MERGED_DIR = BASE_DIR / "merged"
MERGED_DIR.mkdir(exist_ok=True)
CLASSIFIED_DIR = BASE_DIR / "classified"
CLASSIFIED_DIR.mkdir(exist_ok=True)
REAL_PROBLEMS_DIR = BASE_DIR / "real_problems"
REAL_PROBLEMS_DIR.mkdir(exist_ok=True)

HTML_FILE = BASE_DIR.parent / "index.html"
STEPS_FILE = BASE_DIR.parent / "data" / "steps.js"
STATE_FILE = BASE_DIR / "chunker_state.json"'''

NEW_1 = '''from config import (
    PIPELINE_DIR       as BASE_DIR,
    LOGS_DIR           as LOG_DIR,
    EXTRACTED_DIR,
    MERGED_DIR,
    CLASSIFIED_DIR,
    ANCHORS_DIR        as REAL_PROBLEMS_DIR,
    HTML_FILE,
    STEPS_FILE,
    CHUNKER_STATE_FILE as STATE_FILE,
    OCR_CACHE_DIR,
)

logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)
logging.getLogger("pypdf").setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PDF_CHUNKER] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"chunker_{date.today()}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("chunker")'''

# ─── Patch 2: BudgetExhausted ───
OLD_2 = '''# ═══════════════════════════════════════════════════════════════
# AI CLIENT
# ═══════════════════════════════════════════════════════════════
class AIClient:'''

NEW_2 = '''# ═══════════════════════════════════════════════════════════════
# BUDGET EXHAUSTED
# ═══════════════════════════════════════════════════════════════
class BudgetExhausted(Exception):
    """HTTP 402 — спира целия run."""


# ═══════════════════════════════════════════════════════════════
# AI CLIENT
# ═══════════════════════════════════════════════════════════════
class AIClient:'''

# ─── Patch 3: 402 handling в AIClient ───
OLD_3 = '''                if r.status_code >= 500:
                    time.sleep(8 * attempt); continue
                if r.status_code >= 400:
                    log.error(f"[{item_id}] {r.status_code}: {r.text[:300]}")
                    return None'''

NEW_3 = '''                if r.status_code == 402:
                    raise BudgetExhausted(f"[{item_id}] 402: {r.text[:120]}")
                if r.status_code >= 500:
                    time.sleep(8 * attempt); continue
                if r.status_code >= 400:
                    log.error(f"[{item_id}] {r.status_code}: {r.text[:300]}")
                    return None'''

# ─── Patch 4: OCR cache dir ───
OLD_4 = '_OCR_CACHE_DIR = BASE_DIR / ".ocr_cache"'
NEW_4 = '_OCR_CACHE_DIR = OCR_CACHE_DIR'

# ─── Patch 5: save() retry за WinError 5 ───
OLD_5 = '''    def save(self):
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(STATE_FILE)'''

NEW_5 = '''    def save(self):
        text = json.dumps(self.data, ensure_ascii=False, indent=2)
        tmp = STATE_FILE.with_suffix(".tmp")
        try:
            tmp.write_text(text, encoding="utf-8")
        except PermissionError:
            STATE_FILE.write_text(text, encoding="utf-8")
            return
        for attempt in range(6):
            try:
                tmp.replace(STATE_FILE)
                return
            except PermissionError:
                if attempt < 5:
                    time.sleep(0.3 * (attempt + 1))
                else:
                    log.warning("[save] replace fails → direct write")
                    STATE_FILE.write_text(text, encoding="utf-8")
                    try: tmp.unlink()
                    except Exception: pass
                    return'''

# ─── Patch 6: extract cost $0.008 → $0.05 ───
OLD_6 = '''        problems = parsed["problems"]
        self.state.add_cost(0.008)
        log.info(f"[{pdf_name}] chunk {chunk['start']}-{chunk['end']}: {len(problems)} problems ({dur}s)")'''

NEW_6 = '''        problems = parsed["problems"]
        self.state.add_cost(0.05)  # реален ~cost на gpt-6.1-sol
        log.info(f"[{pdf_name}] chunk {chunk['start']}-{chunk['end']}: {len(problems)} problems ({dur}s)")'''

# ─── Patch 7: BudgetExhausted catch в run_extract ───
OLD_7 = '''            log.info(f"\\n[{i}/{len(pdfs)}] {pdf.name}")
            try:
                self.process_pdf(pdf)
            except Exception as e:
                log.exception(f"[{pdf.name}] {e}")'''

NEW_7 = '''            log.info(f"\\n[{i}/{len(pdfs)}] {pdf.name}")
            try:
                self.process_pdf(pdf)
            except BudgetExhausted as e:
                log.error(f"⚠ Бюджет достигнат: {e} — спирам extract")
                break
            except Exception as e:
                log.exception(f"[{pdf.name}] {e}")'''

PATCHES = [
    ("1. imports → config",     OLD_1, NEW_1),
    ("2. BudgetExhausted",      OLD_2, NEW_2),
    ("3. 402 raise",            OLD_3, NEW_3),
    ("4. OCR cache dir",        OLD_4, NEW_4),
    ("5. save() retry",         OLD_5, NEW_5),
    ("6. cost $0.008 → $0.05",  OLD_6, NEW_6),
    ("7. 402 catch in extract", OLD_7, NEW_7),
]

ok = 0
fail = 0
for name, old, new in PATCHES:
    if old not in src:
        print(f"✗ MISS: {name}")
        fail += 1
        continue
    if src.count(old) > 1:
        print(f"⚠ AMBIGUOUS ({src.count(old)}x): {name} — skip")
        fail += 1
        continue
    src = src.replace(old, new, 1)
    print(f"✓ {name}")
    ok += 1

if fail > 0:
    print(f"\n✗ {fail} patch-а не са приложени. Файлът НЕ е записан.")
    sys.exit(1)

P.write_text(src, encoding="utf-8")
print(f"\n✓ {P.name} patched ({orig_len:,} → {len(src):,} bytes)")