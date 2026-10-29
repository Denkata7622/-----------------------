#!/usr/bin/env python3
"""
pdf_chunker.py v3.2 — извлича задачи от PDF-и, слива probs+sol двойки,
класифицира към STEPS точки и агрегира по точка.

v3.2:
- Mistral OCR fallback с include_image_base64 (fix за truncation)
- Cache v2 (__v2.json)
- AI separation на stmt/solution (без regex евристики)
- Classify с евтин модел (chunker.classify_model)
- По-мек _topics_match (само очевидно сгрешени)
- Merge приема sols verbatim при празен probs
"""
import os, re, sys, json, time, logging, argparse, threading, shutil, hashlib
from pathlib import Path
from datetime import datetime, date
from typing import Optional

import requests

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("ЛИПСВА pdfplumber. Инсталирай: pip install pdfplumber pypdf")
    sys.exit(1)

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    import fitz  # pymupdf
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from personas import EXTRACTION_PERSONA, CLASSIFIER_PERSONA
except ImportError as e:
    print(f"ЛИПСВА personas.py или липсват роли в него: {e}")
    sys.exit(1)

from config import (
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
log = logging.getLogger("chunker")


def load_config():
    with open(BASE_DIR / "config.json", "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config()

# ── cost tracker init ──
from cost_tracker import init as _ct_init, track_call as _track_call, log_call as _ct_log
_ct_init(BASE_DIR.parent / "generated" / "costs" / "ledger.jsonl")


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def safe_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()


def format_prompt(template: str, **kwargs) -> str:
    if not kwargs:
        return template
    pattern = re.compile(r'\{(' + '|'.join(re.escape(k) for k in kwargs) + r')\}')
    return pattern.sub(lambda m: str(kwargs[m.group(1)]), template)


def heartbeat(item_id: str, label: str, interval: int = 30):
    stop = threading.Event()
    def run():
        t0 = time.time()
        while not stop.wait(interval):
            log.info(f"[{item_id}] {label}... {int(time.time()-t0)}s")
    threading.Thread(target=run, daemon=True).start()
    return stop


def parse_json(text: str) -> Optional[dict]:
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```\s*$', '', text)
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        try:
            return json.loads(re.sub(r',\s*([}\]])', r'\1', m.group(0)))
        except Exception:
            return None


# ═══════════════════════════════════════════════════════════════
# NAME PARSING — structural, не semantic
# ═══════════════════════════════════════════════════════════════
def split_pdf_name(stem: str) -> dict:
    variant = ""
    m_var = re.search(r'\s*(\(\d+\)|- копие|- copy)\s*$', stem, re.IGNORECASE)
    if m_var:
        variant = m_var.group(1).strip()
        stem = stem[:m_var.start()].strip()

    m = re.search(r'^(.*?)[\s\-]*(probs|sol)$', stem, re.IGNORECASE)
    if m:
        return {
            'base': m.group(1).strip(),
            'kind': m.group(2).lower(),
            'variant': variant,
        }
    return {'base': stem, 'kind': None, 'variant': variant}


def infer_metadata_from_filename(pdf_name: str) -> dict:
    name = pdf_name.lower()
    meta = {"year": None, "grade": None, "grade_range": None, "round": "unknown"}

    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})\s*кл", name)
    if m:
        meta["year"] = int(m.group(1))
        meta["grade_range"] = (int(m.group(2)), int(m.group(3)))
        meta["grade"] = None
        meta["round"] = "nacionalen"
        return meta

    m = re.search(r"(\d{4})-(\d{1,2})\s*кл", name)
    if m:
        meta["year"] = int(m.group(1))
        meta["grade"] = int(m.group(2))
        meta["round"] = "oblasten"
        return meta

    m = re.search(r"nom[_\-\s]*(\d{4})", name)
    if m:
        meta["year"] = int(m.group(1))
        meta["round"] = "nacionalen"
    m = re.search(r"ot[_\-\s]*(\d{4})", name)
    if m:
        meta["year"] = int(m.group(1))
        meta["round"] = "ot"

    if "bmo" in name:
        meta["round"] = "bmo"
    elif "bms" in name:
        meta["round"] = "bms"
    elif "bmc" in name:
        meta["round"] = "bmc"

    return meta


# ═══════════════════════════════════════════════════════════════
# VALIDATION — минимална, доверяваме се на AI
# ═══════════════════════════════════════════════════════════════
def _validate_problem(p: dict) -> tuple:
    """Само structural checks. AI-ят разделя stmt/solution в extraction."""
    stmt = (p.get("statement") or "").strip()
    sol = (p.get("solution") or "").strip()
    if len(stmt) < 20:
        return False, "statement_too_short"
    if not sol or len(sol) < 30:
        return False, "no_solution"
    return True, "ok"


def _topics_match(stmt: str, sol: str) -> bool:
    """Само ОЧЕВИДНО сгрешени: 3+ сигнала в stmt, 0 в sol, И различна тема."""
    if not stmt or not sol:
        return True
    s, so = stmt.lower(), sol.lower()

    geo_kw = ['окръжност', 'триъгълник', 'допирателна', 'ъглополовяща', 'хорда',
              'вписан', 'подобни', 'ортоцентър', 'медиана', 'височина']
    nt_kw = ['делител', 'просто число', 'остатък', 'mod', 'дели се', 'четно',
             'нечетно', 'нод', 'нок', 'естествени', 'цяло число']
    trig_kw = ['cos', 'sin', 'tan', 'cot']
    para_kw = ['парабола', 'a^2', 'a²', 'b^2', 'b²', '(a,', '(b,']
    func_kw = ['f(x)', 'f(m,n)', 'функция']

    def count(text, kws):
        return sum(1 for k in kws if k in text)

    s_geo, s_nt, s_trig = count(s, geo_kw), count(s, nt_kw), count(s, trig_kw)
    so_geo, so_nt, so_trig = count(so, geo_kw), count(so, nt_kw), count(so, trig_kw)
    so_para, so_func = count(so, para_kw), count(so, func_kw)

    # Само силни mismatch-и
    if s_geo >= 3 and so_geo == 0 and (so_nt >= 2 or so_func >= 1):
        return False
    if s_trig >= 2 and so_trig == 0 and so_para >= 2:
        return False
    if s_nt >= 2 and so_nt == 0 and so_geo >= 3:
        return False
    return True


# ═══════════════════════════════════════════════════════════════
# BUDGET EXHAUSTED
# ═══════════════════════════════════════════════════════════════
class BudgetExhausted(Exception):
    """HTTP 402 — спира целия run."""


# ═══════════════════════════════════════════════════════════════
# AI CLIENT
# ═══════════════════════════════════════════════════════════════
class AIClient:
    def __init__(self, cfg, name="chunker"):
        self.name = name
        self.url = cfg["api_url"]
        self.model = cfg["model"]
        self.max_tokens = cfg["max_tokens"]
        self.temperature = cfg["temperature"]
        self.headers = {"Content-Type": "application/json"}
        if cfg.get("api_key"):
            self.headers["Authorization"] = f"Bearer {cfg['api_key']}"

    def call(self, system, user, item_id="?", force_json=True):
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if force_json:
            payload["response_format"] = {"type": "json_object"}

        for attempt in range(1, 4):
            try:
                t0 = time.time()
                r = requests.post(self.url, headers=self.headers, json=payload, timeout=600)
                if r.status_code == 429:
                    log.warning(f"[{item_id}] 429 — чакам 30с")
                    time.sleep(30); continue
                if r.status_code == 400 and force_json:
                    log.warning(f"[{item_id}] 400 — махам response_format")
                    payload.pop("response_format", None)
                    force_json = False
                    continue
                if r.status_code == 402:
                    raise BudgetExhausted(f"[{item_id}] 402: {r.text[:120]}")
                if r.status_code >= 500:
                    time.sleep(8 * attempt); continue
                if r.status_code >= 400:
                    log.error(f"[{item_id}] {r.status_code}: {r.text[:300]}")
                    return None
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                _track_call("pdf_chunker", self.name, self.model, data, item_id=item_id, t0=t0)
                return (content or "").strip() or None
            except BudgetExhausted:
                raise
            except Exception as e:
                log.warning(f"[{item_id}] {e}")
                time.sleep(8 * attempt)
        return None


# ═══════════════════════════════════════════════════════════════
# OCR (Mistral) — fallback за сканирани PDF-и
# ═══════════════════════════════════════════════════════════════
_OCR_CACHE_DIR = OCR_CACHE_DIR
_ocr_state_singleton = None

def _ocr_state_charge(usd: float):
    """Таксува OCR в текущия ChunkerState (ако съществува)."""
    global _ocr_state_singleton
    if _ocr_state_singleton is not None:
        _ocr_state_singleton.add_cost(usd)


def _ocr_pdf(pdf_path: Path) -> list:
    """OCR-ва PDF чрез Mistral. Кешира резултата (v2 с include_image_base64)."""
    cfg = CONFIG.get("ocr", {})
    if not cfg.get("enabled"):
        return []

    _OCR_CACHE_DIR.mkdir(exist_ok=True)
    cache_file = _OCR_CACHE_DIR / f"{safe_name(pdf_path.stem)}__v2.json"
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            if cached:
                log.info(f"[{pdf_path.name}] OCR cache: {len(cached)}p")
                return cached
        except Exception:
            pass

    import base64
    if pdf_path.stat().st_size > 30 * 1024 * 1024:
        log.warning(f"[{pdf_path.name}] >30MB, OCR skip")
        return []

    b64 = base64.b64encode(pdf_path.read_bytes()).decode()
    log.info(f"[{pdf_path.name}] Mistral OCR ({pdf_path.stat().st_size/1024:.0f}KB)")

    hb = heartbeat(pdf_path.stem, "OCR", interval=15)
    t0 = time.time()
    try:
        r = requests.post(
            cfg["api_url"],
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": cfg["model"],
                "document": {
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{b64}",
                },
                "include_image_base64": True,
            },
            timeout=600,
        )
    except Exception as e:
        hb.set()
        log.error(f"[{pdf_path.name}] OCR fail: {e}")
        return []
    finally:
        hb.set()

    dur = int(time.time() - t0)
    if not r.ok:
        log.error(f"[{pdf_path.name}] OCR {r.status_code} ({dur}s): {r.text[:200]}")
        return []

    data = r.json()
    pages_raw = data.get("pages", [])
    if not pages_raw:
        return []

    pages = []
    for p in pages_raw:
        md = (p.get("markdown") or "").strip()
        # Изчисти garbage от вида "гггггггггг"
        md = re.sub(r'(.)\1{9,}', r'\1', md)
        md = re.sub(r'\n{3,}', '\n\n', md)
        pages.append({"page": int(p.get("index", 0)) + 1, "text": md.strip()})

    total = sum(len(p["text"]) for p in pages)
    cost = len(pages) * cfg.get("cost_per_page_usd", 0.001)
    log.info(f"[{pdf_path.name}] OCR: {len(pages)}p, {total}chars, {dur}s, ${cost:.4f}")
    _ocr_state_charge(cost)
    _ct_log(module="pdf_chunker", role="ocr",
            model=cfg.get("model", "mistral-ocr-latest"),
            in_tokens=0, out_tokens=0, cost=cost, status="ok",
            item_id=pdf_path.stem, latency_ms=dur * 1000)

    try:
        cache_file.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

    return pages


# ═══════════════════════════════════════════════════════════════
# PDF PAGE EXTRACTION
# ═══════════════════════════════════════════════════════════════
def extract_pdf_pages(pdf_path: Path) -> list:
    """Опитва pdfplumber → pypdf → pymupdf → Mistral OCR."""
    candidates = []

    if HAS_PDFPLUMBER:
        try:
            pages = []
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    try:
                        text = (page.extract_text() or "").strip()
                    except Exception:
                        text = ""
                    pages.append({"page": i, "text": text})
            total = sum(len(p["text"]) for p in pages)
            candidates.append((total, "pdfplumber", pages))
        except Exception as e:
            log.warning(f"[{pdf_path.name}] pdfplumber fail: {e}")

    if HAS_PYPDF:
        try:
            reader = PdfReader(str(pdf_path))
            pages = []
            for i, page in enumerate(reader.pages, 1):
                try:
                    text = (page.extract_text() or "").strip()
                except Exception:
                    text = ""
                pages.append({"page": i, "text": text})
            total = sum(len(p["text"]) for p in pages)
            candidates.append((total, "pypdf", pages))
        except Exception as e:
            log.warning(f"[{pdf_path.name}] pypdf fail: {e}")

    if HAS_PYMUPDF:
        try:
            import fitz
            pages = []
            doc = fitz.open(str(pdf_path))
            for i, page in enumerate(doc, 1):
                try:
                    text = page.get_text().strip()
                except Exception:
                    text = ""
                pages.append({"page": i, "text": text})
            doc.close()
            total = sum(len(p["text"]) for p in pages)
            candidates.append((total, "pymupdf", pages))
        except Exception as e:
            log.warning(f"[{pdf_path.name}] pymupdf fail: {e}")

    min_chars = CONFIG.get("ocr", {}).get("min_text_chars_for_skip", 500)
    ocr_enabled = CONFIG.get("ocr", {}).get("enabled", False)

    best_chars = 0
    best_pages = []
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_chars, method, best_pages = candidates[0]
        log.info(f"[{pdf_path.name}] {method}: {len(best_pages)}p, {best_chars} chars")

    chars_per_page = best_chars / len(best_pages) if best_pages else 0
    if best_chars >= min_chars and chars_per_page >= 100:
        return best_pages

    log.info(f"[{pdf_path.name}] {best_chars} chars ({chars_per_page:.0f}/p) → OCR fallback")

    if not ocr_enabled:
        return best_pages

    ocr_pages = _ocr_pdf(pdf_path)
    if not ocr_pages:
        return best_pages

    ocr_chars = sum(len(p["text"]) for p in ocr_pages)
    log.info(f"[{pdf_path.name}] OCR: {ocr_chars} chars (vs Python: {best_chars})")

    return ocr_pages if ocr_chars > best_chars else best_pages


# ═══════════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════════
class ChunkerState:
    def __init__(self):
        if STATE_FILE.exists():
            try:
                self.data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                self.data = self._default()
        else:
            self.data = self._default()

    def _default(self):
        return {
            "extracted": {},
            "merged": {},
            "classified": {},
            "budget": {"date": str(date.today()), "spent_usd": 0.0, "calls": 0},
        }

    def save(self):
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
                    return

    def check_budget_reset(self):
        today = str(date.today())
        if self.data["budget"]["date"] != today:
            log.info("Нов ден — рестарт на бюджета")
            self.data["budget"] = {"date": today, "spent_usd": 0.0, "calls": 0}
            self.save()

    def add_cost(self, usd: float):
        self.check_budget_reset()
        self.data["budget"]["spent_usd"] += usd
        self.data["budget"]["calls"] += 1
        self.save()

    def budget_remaining(self) -> float:
        self.check_budget_reset()
        budget = CONFIG.get("chunker", {}).get("daily_budget_usd", 3.0)
        return budget - self.data["budget"]["spent_usd"]

    def budget_exceeded(self) -> bool:
        self.check_budget_reset()
        budget = CONFIG.get("chunker", {}).get("daily_budget_usd", 3.0)
        stop = CONFIG.get("chunker", {}).get("budget_stop_pct", 0.9)
        return self.data["budget"]["spent_usd"] >= budget * stop

    def is_extracted(self, name: str) -> bool:
        return self.data["extracted"].get(name, {}).get("status") == "done"

    def mark_extracted(self, name: str, problems: int):
        self.data["extracted"].setdefault(name, {})["status"] = "done"
        self.data["extracted"][name]["problems"] = problems
        self.save()

    def mark_extraction_failed(self, name: str, failed: int, total: int):
        pdf = self.data["extracted"].setdefault(name, {})
        pdf["status"] = "partial"
        pdf["failed_chunks"] = failed
        pdf["total_chunks"] = total
        self.save()

    def is_chunk_done(self, name: str, chunk_num: int) -> bool:
        chunks = self.data["extracted"].get(name, {}).get("chunks_done", {})
        return str(chunk_num) in chunks

    def mark_chunk_done(self, name: str, chunk_num: int, problems: int):
        pdf = self.data["extracted"].setdefault(name, {})
        pdf.setdefault("chunks_done", {})[str(chunk_num)] = problems
        self.save()

    def is_classified(self, key: str) -> bool:
        return key in self.data["classified"]

    def mark_classified(self, key: str, data: dict):
        self.data["classified"][key] = data
        self.save()

    def get_classification(self, key: str) -> dict:
        return self.data["classified"].get(key, {})


# ═══════════════════════════════════════════════════════════════
# PROMPTS
# ═══════════════════════════════════════════════════════════════
EXTRACT_PROMPT = EXTRACTION_PERSONA + """

═══ КОНТЕКСТ ═══
PDF: {pdf_name}
Страници: {page_start}-{page_end}

═══ ТЕКСТ ОТ PDF-А ═══
{text}

═══ ТВОЯТА ЗАДАЧА ═══
Извлечи ВСИЧКИ задачи от този текст.

За всяка задача попълни:
1. num — номерът ("Зад. 2" → 2). Ако няма → null
2. year — годината (2018, 1997). Ако не е ясна → null
3. grade — класът (10, 11, 12). Ако не е ясен → null
4. round — "oblasten"/"nacionalen"/"bmo"/"bms"/"bmc"/"nom"/"ot"
5. statement — пълното условие (копирано от текста, БЕЗ решение)
6. solution — пълното решение АКО е в текста, иначе null
7. answer — крайният отговор (ако има)
8. page — приблизителна страница в PDF

═══ ВАЖНИ ПРАВИЛА ═══

1. STMT vs SOLUTION — как да различиш:
   - STATEMENT = условието на задачата („Да се намери", „Да се докаже", „Намерете", „Докажете")
   - SOLUTION = пълното решение (започва с „Решение.", „Proof.", „Доказателство:", или директно с логически стъпки)
   - Ако не можеш да различиш със сигурност → сложи в statement, solution: null
   - Ако solution е само частично (hints, скица) → solution: null (не отдавай частични)

2. Ако PDF-ът съдържа САМО условия:
   - Извлечи всички задачи с statement, solution: null
   - НЕ ВРЪЩАЙ празен масив

3. Ако PDF-ът съдържа решения, със или без условия (смесен файл):
   - Ако има и условие, и решение → попълни и двете
   - Ако има само решение → statement: null, solution: <текста>
   - Ако има само условие → solution: null
   - "Problem N." / "Solution." и "Задача N." / "Решение." са еквивалентни
   - НЕ ВРЪЩАЙ празен масив, ако има поне една разпознаваема задача

4. Примери:
   ✅ STMT: „Да се намерят стойностите на реалния параметър $a$, за които уравнението... има три различни реални корена."
   ✅ SOLUTION: „Решение. Тъй като от схемата на Хорнер се вижда, че $x=-1$ е решение..."
   ✅ STMT: „Даден е триъгълник $ABC$ с ъгъл $\\angle C = 90°$. Да се докаже, че..."
   ❌ STMT: „Решение. Тъй като..." (това е solution, не statement)
   ❌ STMT: „Нека $M$ е средата на $AB$." (това е част от решение, не начало на задача)

5. Други правила:
   - Ако не разчиташ част от текста → "[неразчетено]" в statement, НЕ измисляй
   - Ако задача продължава на следваща страница → свържи я
   - За книги с много години (BMO, NOM) → сложи year към всяка задача отделно
   - АКО PDF-ът съдържа задачи от РАЗЛИЧНИ КЛАСОВЕ:
     * Гледай номерацията: „Задача 11.3" означава grade=11, num=3
     * „Задача 12.1" означава grade=12, num=1
     * НЕ оставяй grade=null — винаги го попълни от номера
   - НЕ включвай съдържание, заглавия, автори, индекси — само задачи

6. СТРИКТНО ЗАБРАНЕНО:
   - НЕ добавяй задачи от твоята памет или knowledge за конкретни години/кръгове
   - Извличай САМО това, което е ЛИТЕРАЛНО написано в текста по-горе
   - Ако текстът е частичен или неразбираем → извличай каквото можеш, но НЕ допълвай
   - Ако в текста има 4 задачи → върни 4 задачи, не 8
   - Ако не можеш да разчетеш заглавието на задача → "[неразчетено]", но НЕ я подменяй

═══ ФОРМАТ (САМО JSON) ═══
{{
  "problems": [
    {{
      "num": 2,
      "year": 2018,
      "grade": 11,
      "round": "oblasten",
      "statement": "Пълен текст...",
      "solution": "Пълно решение..." или null,
      "answer": "x=2" или null,
      "page": 7
    }}
  ]
}}

Ако в текста няма задачи → {{"problems": []}}
"""


CLASSIFY_PROMPT = CLASSIFIER_PERSONA + """

═══ ЗАДАЧА ═══
Условие: {statement}

Решение: {solution}

═══ STEPS ТОЧКИ (от плана) ═══
{steps_list}

═══ ТВОЯТА ЗАДАЧА ═══
1. Към коя STEPS точка принадлежи? (1 главна)
2. Каква е трудността? (easy/medium/hard)
3. Кои техники се използват? (списък, snake_case)
4. Увереност: exact / partial / multiple / off

═══ ФОРМАТ (САМО JSON) ═══
{{
  "point_id": "1.4",
  "point_confidence": "exact",
  "alternative_points": [],
  "difficulty": "medium",
  "techniques": ["power_of_point", "similar_triangles"],
  "reasoning": "Задачата изисква степен на точка като основна техника."
}}

Ако не можеш да класифицираш (задача от тематична книга, не олимпиада):
{{"point_id": null, "point_confidence": "off", "difficulty": null, "techniques": [], "reasoning": "не е олимпиадна задача"}}
"""

PAIRED_CLASSIFY_PROMPT = CLASSIFIER_PERSONA + """

═══ КОНТЕКСТ ═══
Олимпиада: {base_name}
Очакван клас: {expected_grade} (от filename — може да е грешен)

═══ СТАТИСТИКА ═══
Условия (probs): {n_probs}
Решения (sol): {n_sols}
Съвпадение 1:1 не е задължително.

═══════════════════════════════════════
УСЛОВИЯ (probs) — {n_probs} задачи
═══════════════════════════════════════
{statements_list}

═══════════════════════════════════════
РЕШЕНИЯ (sol) — {n_sols} записа
═══════════════════════════════════════
{solutions_list}

═══ STEPS ТОЧКИ ═══
{steps_list}

═══ ТВОЯТА ЗАДАЧА ═══

TASK 1 — СВЪРЗВАНЕ
За всяко решение от SOLUTIONS, намери съответстващото условие от STATEMENTS.
- Свързвай само при ЯСНО съвпадение: същата задача, същите числа, същата структура
- Номерата НЕ са надеждни (може да са различни или грешни)
- Ако решението не пасва на нито едно условие → "orphan"

TASK 2 — КЛАСИФИКАЦИЯ
За всяка свързана двойка (условие + решение):
- point_id: коя STEPS точка (1 главна)
- difficulty: easy / medium / hard
- techniques: списък (snake_case)

TASK 3 — ORPHAN РЕШЕНИЯ
За всяко решение без съответстващо условие:
a) Ако решението ИМА вградено условие (в statement полето или в началото на solution):
   → третирай го като отделна задача, класифицирай
   → НЕ определяй grade — той идва от filename или от explicit text markers
b) Ако решението НЯМА условие (само математика) → "orphan_sols_without_statement"

TASK 4 — UNMATCHED УСЛОВИЯ
За условия без решение: класифицирай по самото условие.

═══ АМБИГВЪТЕТЕН СЛУЧАЙ (n_sols > n_probs) ═══
ТОВА Е НОРМАЛНО. Файлът sol може да съдържа задачи от различни класове или варианти.
- Свържи КОЛКОТО МОЖЕШ (обикновено n_probs свързвания)
- Всички останали sols СЕ ОБРАБОТВАТ като orphan, НЕ ги изхвърляй
- Пример: 4 probs + 8 sols → ~4 matched + ~4 orphans = 8 entries в резултата

═══ ЗАДЪЛЖИТЕЛНО ═══
1. ВИНАГИ връщай валиден JSON, дори когато си несигурен
2. НЕ връщай {{}}, празен обект или текст вместо JSON
3. НЕ отказвай задачата — върни каквото можеш, остави несигурните с null point_id
4. Ако не можеш да определиш point_id за някого → "point_id": null (НЕ пропускай entry)
5. Ако не можеш да свържеш нещо → сложи го в orphan_sols_* или unmatched_probs

═══ ФОРМАТ (САМО JSON) ═══
{{
  "matched": [
    {{"stmt_num": 1, "sol_num": 3, "point_id": "1.4", "difficulty": "medium", "techniques": ["..."], "reasoning": "..."}}
  ],
  "orphan_sols_with_statement": [
    {{"sol_num": 1, "point_id": "2.3", "difficulty": "medium", "techniques": ["..."], "reasoning": "..."}}
  ],
  "orphan_sols_without_statement": [
    {{"sol_num": 5, "reason": "no statement found"}}
  ],
  "unmatched_probs": [
    {{"stmt_num": 4, "point_id": "3.2", "difficulty": "hard", "techniques": ["..."], "reasoning": "..."}}
  ]
}}

ВАЖНО:
- stmt_num и sol_num са 1-indexed (първото условие = 1)
- Всяко условие трябва да е в matched ИЛИ unmatched_probs — не и двете
- Всяко решение трябва да е в matched ИЛИ orphan_sols_* — не и двете
- Ако output-ът ти е голям → съкрати reasoning полетата, но запази структурата
"""

# ═══════════════════════════════════════════════════════════════
# STEPS PARSER
# ═══════════════════════════════════════════════════════════════
def load_steps_info() -> dict:
    """Връща {point_id: {"title": ..., "desc": ...}} от data/steps.js."""
    candidates = [STEPS_FILE, HTML_FILE]
    html = None
    for f in candidates:
        try:
            if f.exists():
                html = f.read_text(encoding="utf-8")
                if "const STEPS" in html:
                    break
        except Exception:
            continue

    if not html:
        return {}

    marker = "const STEPS = ["
    start = html.find(marker)
    if start == -1:
        return {}
    start += len("const STEPS = ")

    depth = 0; in_str = False; quote = None; escape = False; end = len(html)
    for i in range(start, len(html)):
        c = html[i]
        if escape: escape = False; continue
        if in_str:
            if c == '\\': escape = True
            elif c == quote: in_str = False
            continue
        if c in ('"', "'", '`'):
            in_str = True; quote = c; continue
        if c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                end = i
                break

    steps_str = html[start:end+1]

    # Match: {id: "X.Y", ... title: "...", desc: "..."}
    points = {}
    for m in re.finditer(
        r'\{\s*id\s*:\s*"([^"]+)"[^{}]*?title\s*:\s*"((?:\\.|[^"\\])*)"[^{}]*?desc\s*:\s*"((?:\\.|[^"\\])*)"',
        steps_str, re.DOTALL,
    ):
        pid = m.group(1)
        title = m.group(2).replace('\\"', '"').replace("\\'", "'")
        desc = m.group(3).replace('\\"', '"').replace("\\'", "'")
        points[pid] = {"title": title, "desc": desc}

    # Fallback за точки без desc
    for m in re.finditer(r'\{\s*id\s*:\s*"([^"]+)"[^{}]*?title\s*:\s*"([^"]+)"', steps_str, re.DOTALL):
        pid, title = m.group(1), m.group(2)
        if pid not in points:
            points[pid] = {"title": title, "desc": ""}

    return points

# ═══════════════════════════════════════════════════════════════
# PDF CHUNKER
# ═══════════════════════════════════════════════════════════════
class PDFChunker:
    def __init__(self):
        global _ocr_state_singleton
        self.state = ChunkerState()
        _ocr_state_singleton = self.state
        self.steps_info = load_steps_info()
        self.steps_titles = {pid: info["title"] for pid, info in self.steps_info.items()}
        log.info(f"Заредени {len(self.steps_info)} STEPS точки")

        # Extract — Sol (не R1 — R1 е лош за extraction)
        ext_cfg = dict(CONFIG["generator"])
        chunker_cfg = CONFIG.get("chunker", {})
        if chunker_cfg.get("extract_model"):
            ext_cfg["model"] = chunker_cfg["extract_model"]
        ext_cfg["max_tokens"] = 8000
        ext_cfg["temperature"] = 0.05
        self.ai_extract = AIClient(ext_cfg, "extract")

        # Classify — евтин модел (gpt-oss-120b по подразбиране)
        chunker_cfg = CONFIG.get("chunker", {})
        cls_cfg = dict(CONFIG["verifier"])
        if chunker_cfg.get("classify_model"):
            cls_cfg["model"] = chunker_cfg["classify_model"]
        cls_cfg["max_tokens"] = 8000
        cls_cfg["temperature"] = 0.05
        self.ai_classify = AIClient(cls_cfg, "classify")
        self.classify_cost = chunker_cfg.get("classify_cost_per_call_usd", 0.005)
        log.info(f"Classify model: {cls_cfg['model']} (${self.classify_cost}/call)")

    def _write_classified(self, base: str, entries: list, extra: dict = None):
        """Записва classified файл с metadata за модела."""
        payload = {
            "pdf": base,
            "classify_model": self.ai_classify.model,
            "classified_at": datetime.now().isoformat(),
            "problems": entries,
        }
        if extra:
            payload.update(extra)
        out_dir = CLASSIFIED_DIR / safe_name(base)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "all_problems.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ═══════════════════════════════════════════════════════════
    # SCAN + DEDUPE
    # ═══════════════════════════════════════════════════════════
    def _dedupe(self, pdfs: list) -> list:
        groups = {}
        others = []

        for pdf in pdfs:
            info = split_pdf_name(pdf.stem)
            if info['kind']:
                key = (info['base'], info['kind'])
                groups.setdefault(key, []).append((info['variant'], pdf))
            else:
                others.append(pdf)

        result = []
        for key, variants in groups.items():
            no_variant = [p for v, p in variants if not v]
            if no_variant:
                result.append(no_variant[0])
            else:
                result.append(variants[0][1])

        return sorted(result + others, key=lambda p: p.name)

    def scan_pdfs(self) -> list:
        pdfs = []
        for folder in CONFIG.get("watch_folders", []):
            path = (BASE_DIR / folder).resolve()
            if not path.exists():
                log.warning(f"Липсва: {path}")
                continue
            for pdf in path.rglob("*.pdf"):
                pdfs.append(pdf)
        return self._dedupe(pdfs)

    # ═══════════════════════════════════════════════════════════
    # CHUNKING
    # ═══════════════════════════════════════════════════════════
    def _chunk_size_for(self, pdf_name: str, total_pages: int) -> tuple:
        if total_pages <= 10:
            return total_pages, 0

        lower = pdf_name.lower()
        if any(x in lower for x in ['bmo', 'bmc', 'bms', 'nom', 'ot']):
            return 4, 1

        return 8, 1

    def chunk_pdf(self, pdf_path: Path) -> list:
        pages = extract_pdf_pages(pdf_path)
        if not pages:
            log.error(f"[{pdf_path.name}] не прочетох PDF (сканиран?)")
            return []

        chunk_size, overlap = self._chunk_size_for(pdf_path.stem, len(pages))

        chunks = []
        i = 0
        while i < len(pages):
            end = min(i + chunk_size, len(pages))
            chunks.append({
                "pages": pages[i:end],
                "start": i + 1,
                "end": end,
            })
            if end >= len(pages):
                break
            i += chunk_size - overlap
        return chunks

    # ═══════════════════════════════════════════════════════════
    # EXTRACT
    # ═══════════════════════════════════════════════════════════
    def extract_from_chunk(self, pdf_name: str, chunk: dict) -> Optional[list]:
        text = "\n\n".join(
            f"─── Стр. {p['page']} ───\n{p['text']}"
            for p in chunk["pages"]
        )

        user = format_prompt(
            EXTRACT_PROMPT,
            pdf_name=pdf_name,
            page_start=chunk["start"],
            page_end=chunk["end"],
            text=text,
        )

        hb = heartbeat(f"{pdf_name}-{chunk['start']}", "extract")
        t0 = time.time()
        try:
            raw = self.ai_extract.call(EXTRACT_PROMPT, user, f"{pdf_name}-{chunk['start']}")
        finally:
            hb.set()
        dur = int(time.time() - t0)

        if not raw:
            log.error(f"[{pdf_name}] chunk {chunk['start']}-{chunk['end']} — no response ({dur}s)")
            return None

        parsed = parse_json(raw)
        if not parsed or "problems" not in parsed:
            log.error(f"[{pdf_name}] chunk {chunk['start']}-{chunk['end']} — JSON fail ({dur}s)")
            return None

        problems = parsed["problems"]
        self.state.add_cost(0.03)  # средна ~cost на gpt-6.1-sol
        log.info(f"[{pdf_name}] chunk {chunk['start']}-{chunk['end']}: {len(problems)} problems ({dur}s)")
        return problems

    def _dedupe_problems(self, problems: list) -> list:
        """Dedupe по (year, grade, num, page). Запазва по-валидната версия."""
        by_key = {}
        for p in problems:
            key = (
                p.get('year'),
                p.get('grade') or p.get('grade_range'),
                p.get('num'),
                p.get('page'),
            )
            ok, _ = _validate_problem(p)
            stmt = (p.get('statement') or '').strip()
            sol = (p.get('solution') or '').strip()
            score = (1 if ok else 0, len(stmt) + len(sol))
            existing = by_key.get(key)
            if existing is None or score > existing[0]:
                by_key[key] = (score, p)
        return [p for _, p in by_key.values()]

    def process_pdf(self, pdf_path: Path):
        name = pdf_path.stem
        if self.state.is_extracted(name):
            log.info(f"[{name}] skip (done)")
            return

        log.info(f"\n═══ {name} ═══")
        chunks = self.chunk_pdf(pdf_path)
        if not chunks:
            return

        log.info(f"[{name}] {len(chunks)} chunks, {sum(len(c['pages']) for c in chunks)} pages")

        out_dir = EXTRACTED_DIR / safe_name(name)
        out_dir.mkdir(parents=True, exist_ok=True)
        all_file = out_dir / "all_problems.json"

        all_problems = []
        if all_file.exists():
            try:
                existing = json.loads(all_file.read_text(encoding="utf-8"))
                all_problems = existing.get("problems", [])
                log.info(f"[{name}] {len(all_problems)} existing problems")
            except Exception:
                pass

        meta = infer_metadata_from_filename(name)
        success = 0
        failed = 0

        for i, chunk in enumerate(chunks, 1):
            if self.state.is_chunk_done(name, i):
                log.info(f"[{name}] chunk {i} skip")
                success += 1
                continue

            if self.state.budget_exceeded():
                log.warning(f"⚠ Бюджет достигнат. Спирам.")
                return

            problems = self.extract_from_chunk(name, chunk)
            if problems is None:
                failed += 1
                log.error(f"[{name}] chunk {i} FAILED — ще retry следващия път")
                continue

            for p in problems:
                p["pdf"] = name
                p["chunk"] = i
                if not p.get("year"):
                    p["year"] = meta["year"]
                if not p.get("grade") and not p.get("grade_range"):
                    p["grade"] = meta["grade"]
                    p["grade_range"] = meta["grade_range"]
                if not p.get("round") or p["round"] == "unknown":
                    p["round"] = meta["round"]
                all_problems.append(p)

            self.state.mark_chunk_done(name, i, len(problems))
            success += 1

            all_file.write_text(
                json.dumps({
                    "pdf": name,
                    "extraction_model": self.ai_extract.model,
                    "extracted_at": datetime.now().isoformat(),
                    "problems": all_problems,
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        if failed > 0:
            self.state.mark_extraction_failed(name, failed, len(chunks))
            log.warning(f"[{name}] {failed}/{len(chunks)} chunks failed — status=partial")
            return

        # 🗂️ Versioning — запази старата версия като -vN
        new_ver = 1
        if all_file.exists():
            try:
                old_data = json.loads(all_file.read_text(encoding="utf-8"))
                old_ver = old_data.get("version", 1)
                old_path = out_dir / f"all_problems-v{old_ver}.json"
                if not old_path.exists():
                    all_file.rename(old_path)
                    log.info(f"[{name}] Стар файл → all_problems-v{old_ver}.json")
                new_ver = old_ver + 1
            except Exception as e:
                log.warning(f"[{name}] versioning fail: {e}")

        all_problems = self._dedupe_problems(all_problems)
        all_file.write_text(
            json.dumps({
                "pdf": name,
                "version": new_ver,
                "extraction_model": self.ai_extract.model,
                "extracted_at": datetime.now().isoformat(),
                "problems": all_problems,
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log.info(f"[{name}] Записан v{new_ver} ({len(all_problems)} problems)")

        # Quality gate: ако 0 задачи от PDF с много страници → не маркирай done
        pages_count = sum(len(c['pages']) for c in chunks)
        ratio = len(all_problems) / pages_count if pages_count else 0

        if pages_count > 5 and len(all_problems) == 0:
            log.error(
                f"[{name}] ❌ QUALITY GATE: 0 problems from {pages_count} pages — "
                f"NOT marking as done (will retry)"
            )
            self.state.mark_extraction_failed(name, 0, len(chunks))
            return

        if pages_count > 5 and ratio < 0.15:
            log.warning(
                f"[{name}] ⚠ QUALITY: only {len(all_problems)} problems "
                f"from {pages_count} pages (ratio={ratio:.2f}) — marking done but flagged"
            )
            # Все пак маркирай, но с warning в state
            pdf_state = self.state.data["extracted"].setdefault(name, {})
            pdf_state["low_quality"] = True
            pdf_state["quality_ratio"] = round(ratio, 2)
            self.state.save()

        self.state.mark_extracted(name, len(all_problems))
        log.info(f"✓ [{name}] {len(all_problems)} problems (deduped) → {all_file}")

    def run_extract(self, limit: Optional[int] = None, pdf_pattern: Optional[str] = None):
        pdfs = self.scan_pdfs()
        log.info(f"Намерени {len(pdfs)} PDF-а")
        if pdf_pattern:
            patterns = [pat.strip().lower() for pat in pdf_pattern.split(",") if pat.strip()]
            pdfs = [p for p in pdfs if any(pat in p.name.lower() for pat in patterns)]
            log.info(f"Филтър '{pdf_pattern}': {len(pdfs)} PDF-а")
        if limit:
            pdfs = pdfs[:limit]
            log.info(f"Ограничавам до {limit}")

        for i, pdf in enumerate(pdfs, 1):
            if self.state.budget_exceeded():
                log.warning(f"⚠ Бюджет достигнат на {i}/{len(pdfs)}")
                break
            log.info(f"\n[{i}/{len(pdfs)}] {pdf.name}")
            try:
                self.process_pdf(pdf)
            except BudgetExhausted as e:
                log.error(f"⚠ Бюджет достигнат: {e} — спирам extract")
                break
            except Exception as e:
                log.exception(f"[{pdf.name}] {e}")

    # ═══════════════════════════════════════════════════════════
    # MERGE (probs + sol)
    # ═══════════════════════════════════════════════════════════
    def _find_pair(self, pdf_name: str, extracted: dict) -> Optional[str]:
        info = split_pdf_name(pdf_name)
        if not info['kind']:
            return None

        target_kind = 'sol' if info['kind'] == 'probs' else 'probs'

        for candidate in extracted.keys():
            if candidate == pdf_name:
                continue
            c_info = split_pdf_name(candidate)
            if (c_info['base'] == info['base']
                and c_info['kind'] == target_kind
                and c_info['variant'] == info['variant']):
                return candidate

        for candidate in extracted.keys():
            if candidate == pdf_name:
                continue
            c_info = split_pdf_name(candidate)
            if c_info['base'] == info['base'] and c_info['kind'] == target_kind:
                return candidate

        return None

    def _merge_pair(self, probs: list, sols: list) -> list:
        """Слива probs+sol по (grade, num). Filter-ва празните."""
        if not probs and sols:
            log.info(f"[merge] probs празен — използвам sols verbatim ({len(sols)})")
            return [s for s in sols
                    if (s.get("statement") or "").strip() or (s.get("solution") or "").strip()]
        if not sols and probs:
            log.info(f"[merge] sols празен — използвам probs verbatim ({len(probs)})")
            return [p for p in probs
                    if (p.get("statement") or "").strip() or (p.get("solution") or "").strip()]

        def norm_num(n):
            if n is None:
                return None
            try:
                return int(n)
            except (ValueError, TypeError):
                return str(n)

        def grade_of(p):
            g = p.get("grade")
            if g is None and p.get("grade_range"):
                gr = p.get("grade_range")
                if isinstance(gr, (list, tuple)) and len(gr) > 0:
                    g = gr[0]
            return g

        def key(p):
            return (grade_of(p), norm_num(p.get("num")))

        # probs: last-wins (не трябва да има дубликати)
        probs_by_key = {}
        for p in probs:
            if p.get("num") is not None:
                probs_by_key[key(p)] = p

        # sols: при дубликат с еднакъв (grade,num) → предпочети този с solution
        sols_by_key = {}
        for s in sols:
            if s.get("num") is None:
                continue
            k = key(s)
            if k not in sols_by_key:
                sols_by_key[k] = s
            else:
                existing = sols_by_key[k]
                existing_sol = (existing.get("solution") or "").strip()
                new_sol = (s.get("solution") or "").strip()
                if not existing_sol and new_sol:
                    sols_by_key[k] = s
                elif existing_sol and new_sol and len(new_sol) > len(existing_sol):
                    sols_by_key[k] = s

        all_keys = sorted(
            set(probs_by_key.keys()) | set(sols_by_key.keys()),
            key=lambda x: (
                x[0] is None, x[0] if x[0] is not None else 0,
                x[1] is None, str(x[1]) if x[1] is not None else ""
            )
        )

        merged = []
        for k in all_keys:
            p = probs_by_key.get(k, {})
            s = sols_by_key.get(k, {})

            stmt = (p.get("statement") or s.get("statement") or "").strip()
            sol = (s.get("solution") or p.get("solution") or "").strip()

            if len(stmt) < 20:
                continue

            if sol and not _topics_match(stmt, sol):
                log.warning(f"[merge] grade={k[0]} num={k[1]}: solution не пасва на statement — drop")
                sol = ""

            merged.append({
                "num": k[1],
                "year": p.get("year") or s.get("year"),
                "grade": p.get("grade") or s.get("grade"),
                "grade_range": p.get("grade_range") or s.get("grade_range"),
                "round": p.get("round") or s.get("round"),
                "statement": stmt or None,
                "solution": sol or None,
                "answer": s.get("answer") or p.get("answer"),
                "page": p.get("page") or s.get("page"),
            })

        # num=None entries — append само ако не са празни
        for p in probs:
            if p.get("num") is None and ((p.get("statement") or "").strip() or (p.get("solution") or "").strip()):
                merged.append(p)
        for s in sols:
            if s.get("num") is None and ((s.get("statement") or "").strip() or (s.get("solution") or "").strip()):
                merged.append(s)

        return merged

    def run_merge(self):
        extracted = {}
        for pdf_dir in EXTRACTED_DIR.iterdir():
            if not pdf_dir.is_dir():
                continue
            file = pdf_dir / "all_problems.json"
            if not file.exists():
                continue
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                extracted[data["pdf"]] = data["problems"]
            except Exception:
                continue

        log.info(f"Заредени {len(extracted)} извлечени PDF-а")

        processed = set()
        merged_count = 0

        for pdf_name, problems in extracted.items():
            if pdf_name in processed:
                continue

            pair = self._find_pair(pdf_name, extracted)
            if pair:
                if "-probs" in pdf_name:
                    probs_name, sols_name = pdf_name, pair
                else:
                    probs_name, sols_name = pair, pdf_name
                probs = extracted[probs_name]
                sols = extracted[sols_name]
                merged = self._merge_pair(probs, sols)
                base = split_pdf_name(probs_name)['base']
                processed.add(probs_name)
                processed.add(sols_name)
                log.info(f"  [{base}] merge {len(probs)} probs + {len(sols)} sols → {len(merged)} problems")
            else:
                merged = problems
                base = split_pdf_name(pdf_name)['base']
                processed.add(pdf_name)
                log.info(f"  [{base}] standalone ({len(merged)} problems)")

            merged = self._dedupe_problems(merged)

            out_dir = MERGED_DIR / safe_name(base)
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "all_problems.json").write_text(
                json.dumps({"pdf": base, "problems": merged}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self.state.data["merged"][base] = len(merged)
            merged_count += 1

        self.state.save()
        log.info(f"✓ {merged_count} merged olympiads → {MERGED_DIR}")

    # ═══════════════════════════════════════════════════════════
    # CLASSIFY
    # ═══════════════════════════════════════════════════════════
    def classify_problem(self, problem: dict) -> Optional[dict]:
        stmt = (problem.get("statement") or "").strip()
        sol = (problem.get("solution") or "").strip()

        if not stmt and not sol:
            return None

        steps_list = "\n".join(
            f"  {pid}: {info['title']}"
            + (f" — {info['desc'][:120]}" if info.get('desc') else "")
            for pid, info in sorted(self.steps_info.items())
        )

        user = format_prompt(
            CLASSIFY_PROMPT,
            statement=stmt[:2500] if stmt else "(без условие)",
            solution=sol[:2500] if sol else "(без решение)",
            steps_list=steps_list,
        )

        raw = self.ai_classify.call(CLASSIFY_PROMPT, user, str(problem.get("num")))
        self.state.add_cost(self.classify_cost)
        return parse_json(raw)

    def run_classify(self, limit: Optional[int] = None):
        merged_dirs = [d for d in MERGED_DIR.iterdir() if d.is_dir()]
        log.info(f"Намерени {len(merged_dirs)} merged папки")
        if limit:
            merged_dirs = merged_dirs[:limit]

        for mdir in merged_dirs:
            file = mdir / "all_problems.json"
            if not file.exists():
                continue

            data = json.loads(file.read_text(encoding="utf-8"))
            base = data["pdf"]
            problems = data["problems"]
            log.info(f"\n[{base}] класифицирам {len(problems)} задачи...")

            classified = []
            for p in problems:
                key = f"{base}:{p.get('num', '?')}:{p.get('page', '?')}"
                if self.state.is_classified(key):
                    classified.append({**p, **self.state.get_classification(key)})
                    continue

                if self.state.budget_exceeded():
                    log.warning("⚠ Бюджет достигнат")
                    break

                # Skip no-solution tasks — те ще паднат в aggregate
                sol = (p.get("solution") or "").strip()
                if not sol or len(sol) < 30:
                    skip_data = {"point_id": None, "point_confidence": "off",
                                 "difficulty": None, "techniques": [],
                                 "reasoning": "no_solution_skip"}
                    classified.append({**p, **skip_data})
                    self.state.mark_classified(key, skip_data)
                    log.info(f"  [{key}] skip (no solution)")
                    continue

                try:
                    cls = self.classify_problem(p)
                    if cls is not None:
                        merged = {**p, **cls}
                        classified.append(merged)
                        self.state.mark_classified(key, cls)
                        pid = cls.get("point_id") or "?"
                        diff = cls.get("difficulty") or "?"
                        log.info(f"  [{key}] → {pid} ({diff})")
                    else:
                        log.warning(f"  [{key}] empty (no statement, no solution) — skip")
                except Exception as e:
                    log.error(f"[{key}] {e}")

            self._write_classified(base, classified)
            log.info(f"✓ [{base}] {len(classified)} classified")

    # ═══════════════════════════════════════════════════════════
    # AGGREGATE
    # ═══════════════════════════════════════════════════════════
    def run_aggregate(self):
        # Изчисти стари anchor файлове (за да не остават stale при rerun)
        if REAL_PROBLEMS_DIR.exists():
            for f in REAL_PROBLEMS_DIR.glob("*.json"):
                try:
                    f.unlink()
                except Exception:
                    pass

        by_point = {}
        unclassified = []
        seen_keys = set()

        for cdir in CLASSIFIED_DIR.iterdir():
            if not cdir.is_dir():
                continue
            file = cdir / "all_problems.json"
            if not file.exists():
                continue
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
            except Exception:
                continue

            for p in data["problems"]:
                pid = p.get("point_id")
                stmt = (p.get("statement") or "").strip()
                sol = (p.get("solution") or "").strip()

                # Skip задачи без solution — не са полезни като anchors
                if not sol or len(sol) < 30:
                    continue

                dedupe_key = (data["pdf"], p.get("year"), p.get("num"), stmt[:100])
                if dedupe_key in seen_keys:
                    continue
                seen_keys.add(dedupe_key)

                entry = {
                    "source": f"{data['pdf']} · {p.get('year')}-{p.get('grade', '?')} · Зад. {p.get('num')}",
                    "statement": p.get("statement"),
                    "solution": p.get("solution"),
                    "answer": p.get("answer"),
                    "difficulty": p.get("difficulty"),
                    "techniques": p.get("techniques", []),
                    "confidence": p.get("point_confidence"),
                    "reasoning": p.get("reasoning"),
                }
                pid = (pid or "").strip()
                if not pid or pid not in self.steps_info:
                    if pid:
                        entry["_invalid_pid"] = pid
                    unclassified.append(entry)
                    continue
                by_point.setdefault(pid, []).append(entry)

        for pid, problems in by_point.items():
            problems.sort(key=lambda x: (
                {"easy": 0, "medium": 1, "hard": 2}.get(x.get("difficulty"), 1),
                x.get("source", ""),
            ))
            safe = pid.replace(".", "_")
            (REAL_PROBLEMS_DIR / f"{safe}.json").write_text(
                json.dumps({
                    "point_id": pid,
                    "total": len(problems),
                    "by_difficulty": {
                        "easy": sum(1 for p in problems if p["difficulty"] == "easy"),
                        "medium": sum(1 for p in problems if p["difficulty"] == "medium"),
                        "hard": sum(1 for p in problems if p["difficulty"] == "hard"),
                    },
                    "problems": problems,
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            log.info(f"✓ [{pid}] {len(problems)} real problems")

        if unclassified:
            (REAL_PROBLEMS_DIR / "_unclassified.json").write_text(
                json.dumps({
                    "total": len(unclassified),
                    "problems": unclassified,
                }, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            log.info(f"⚠ {len(unclassified)} unclassified problems → _unclassified.json")

    def _group_extracted_by_base(self):
        """Load extracted files, group probs+sol by base name."""
        grouped = {}
        for d in EXTRACTED_DIR.iterdir():
            if not d.is_dir(): continue
            f = d / 'all_problems.json'
            if not f.exists(): continue
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
            except Exception:
                continue
            name = data.get('pdf', d.name)
            info = split_pdf_name(name)
            base = info['base']
            kind = info['kind']  # 'probs' | 'sol' | None
            if kind == 'probs':
                grouped.setdefault(base, {})['probs'] = data.get('problems', [])
                grouped[base]['probs_name'] = name
            elif kind == 'sol':
                grouped.setdefault(base, {})['sols'] = data.get('problems', [])
                grouped[base]['sols_name'] = name
            else:
                grouped.setdefault(base, {})['probs'] = data.get('problems', [])
                grouped[base]['probs_name'] = name
                grouped[base]['standalone'] = True
        return grouped

    def _format_problems_list(self, problems, prefix):
        """Format problems for prompt with 1-indexed numbers."""
        parts = []
        for i, p in enumerate(problems, 1):
            stmt = (p.get('statement') or '').strip()[:1500]
            sol = (p.get('solution') or '').strip()[:2500]
            num = p.get('num', '?')
            grade = p.get('grade', '?')
            parts.append(f"[{prefix}{i}] (num={num}, grade={grade})\n"
                         f"  Условие: {stmt or '(няма)'}\n"
                         f"  Решение: {sol or '(няма)'}")
        return "\n\n".join(parts)

    def _classify_paired(self, base, probs, sols, plan_ctx=None):
        """One AI call: pair + classify."""
        expected_grade = '?'
        m = re.search(r'-(\d{1,2})\s*кл', base)
        if m:
            expected_grade = int(m.group(1))

        user = format_prompt(
            PAIRED_CLASSIFY_PROMPT,
            base_name=base,
            expected_grade=expected_grade,
            n_probs=len(probs),
            n_sols=len(sols),
            statements_list=self._format_problems_list(probs, 'S'),
            solutions_list=self._format_problems_list(sols, 'A'),
            steps_list="\n".join(
                f"  {pid}: {info['title']}"
                for pid, info in sorted(self.steps_info.items())
            ),
        )

        raw = self.ai_classify.call(PAIRED_CLASSIFY_PROMPT, user, f"{base}-paired")
        self.state.add_cost(self.classify_cost * 2)  # 2× normal (bigger prompt)
        return parse_json(raw) if raw else None

    def _grade_from_filename_or_text(self, base, problem):
        """Grade from filename, overridden only by explicit text evidence.
        Returns: (grade, source, is_uncertain)
        
        Sources priority:
          1. text_evidence — explicit "Задача 9.6" marker in text (certain)
          2. filename — specific grade from filename (certain)
          3. grade_range — "9-12 кл" in filename (certain, but grade=None;
             means same problems apply to all 9-12 grades by design)
          4. unknown — no grade info (uncertain)
        """
        meta = infer_metadata_from_filename(base)
        
        # 1. Text evidence (e.g., "Задача 9.6", "9.6.")
        sol = (problem.get('solution') or '').strip()
        stmt = (problem.get('statement') or '').strip()
        text = (stmt + ' ' + sol)[:500]
        
        m = re.search(r'^(?:Задача\s+|Зад\.?\s*)?(\d{1,2})\.\d+[\.\s]', text)
        if not m:
            m = re.search(r'(?:Задача|Зад\.?)\s+(\d{1,2})\.\d+', text)
        if m:
            g = int(m.group(1))
            if 5 <= g <= 12:
                return g, 'text_evidence', False
        
        # 2. Specific grade in filename
        if meta.get('grade'):
            return meta['grade'], 'filename', False
        
        # 3. Grade range in filename (by design — same problems for all)
        if meta.get('grade_range'):
            return None, 'grade_range', False  # NOT uncertain
        
        # 4. Unknown
        return None, 'unknown', True

    def _build_paired_entries(self, base, probs, sols, result):
        """Convert AI response into classified problem entries."""
        entries = []

        def _source(p):
            return f"{base} · {p.get('year', '?')}-{p.get('grade', '?')} · Зад. {p.get('num', '?')}"

        # Matched
        for m in result.get('matched', []):
            sn = m.get('stmt_num')
            an = m.get('sol_num')
            if not isinstance(sn, int) or not (1 <= sn <= len(probs)): continue
            if not isinstance(an, int) or not (1 <= an <= len(sols)): continue
            pr = probs[sn - 1]
            so = sols[an - 1]
            matched_grade, matched_source, matched_uncertain = self._grade_from_filename_or_text(base, pr)
            matched_entry = {
                'num': pr.get('num'),
                'grade': matched_grade,
                'year': pr.get('year'),
                'round': pr.get('round'),
                'statement': pr.get('statement'),
                'solution': so.get('solution') or pr.get('solution'),
                'answer': so.get('answer') or pr.get('answer'),
                'page': pr.get('page'),
                'source': f"{base} · {pr.get('year', '?')}-{matched_grade or '?'} · Зад. {pr.get('num', '?')}",
                'point_id': m.get('point_id'),
                'point_confidence': 'exact',
                'alternative_points': m.get('alternative_points', []),
                'difficulty': m.get('difficulty'),
                'techniques': m.get('techniques', []),
                'reasoning': m.get('reasoning'),
                '_paired': True,
                '_grade_source': matched_source,
            }
            if matched_source == 'grade_range':
                matched_entry['grade_range'] = list(infer_metadata_from_filename(base)['grade_range'])
            entries.append(matched_entry)

        # Orphan sols with statement
        meta = infer_metadata_from_filename(base)
        for o in result.get('orphan_sols_with_statement', []):
            an = o.get('sol_num')
            if not isinstance(an, int) or not (1 <= an <= len(sols)): continue
            so = sols[an - 1]
            
            inferred_grade, grade_source, grade_uncertain = self._grade_from_filename_or_text(base, so)
            
            entry = {
                'num': so.get('num'),
                'grade': inferred_grade,
                'year': so.get('year') or meta.get('year'),
                'round': so.get('round') or meta.get('round'),
                'statement': so.get('statement'),
                'solution': so.get('solution'),
                'answer': so.get('answer'),
                'page': so.get('page'),
                'source': f"{base} · {so.get('year') or meta.get('year') or '?'}-{inferred_grade or '?'} · Зад. {so.get('num', '?')}",
                'point_id': o.get('point_id'),
                'point_confidence': 'exact',
                'difficulty': o.get('difficulty'),
                'techniques': o.get('techniques', []),
                'reasoning': o.get('reasoning'),
                '_orphan': True,
                '_grade_uncertain': grade_uncertain,
                '_grade_source': grade_source,
            }
            # Keep grade_range if from filename
            if grade_source == 'grade_range':
                entry['grade_range'] = list(meta['grade_range'])
            entries.append(entry)

        # Unmatched probs
        for u in result.get('unmatched_probs', []):
            sn = u.get('stmt_num')
            if not isinstance(sn, int) or not (1 <= sn <= len(probs)): continue
            pr = probs[sn - 1]
            entries.append({
                'num': pr.get('num'),
                'grade': pr.get('grade'),
                'year': pr.get('year'),
                'round': pr.get('round'),
                'statement': pr.get('statement'),
                'solution': pr.get('solution'),
                'answer': pr.get('answer'),
                'page': pr.get('page'),
                'source': _source(pr),
                'point_id': u.get('point_id'),
                'point_confidence': 'exact',
                'difficulty': u.get('difficulty'),
                'techniques': u.get('techniques', []),
                'reasoning': u.get('reasoning'),
                '_no_solution': True,
            })

        # orphan_sols_without_statement → skip (can't classify without statement)

        return entries

    def _priority_key_paired(self, base_name):
        m = re.search(r'-(\d{4})-', base_name)
        year = int(m.group(1)) if m else 0
        is_11_oblasten = 0 if ('OLI-2' in base_name and '11 кл' in base_name and 'Областен' in base_name) else 1
        return (is_11_oblasten, -year, base_name)

    def run_classify_paired(self, limit=None, filter_fn=None, pdf_pattern=None, force=False):
        """Classify probs+sol together in one AI call per olympiad.

        force=False: пропуска вече класифицирани файлове (idempotent).
        force=True:  презаписва всичко (за rerun след промяна на промпт/модел).
        """
        grouped = self._group_extracted_by_base()
        bases = [b for b in grouped.keys() if grouped[b].get('probs') or grouped[b].get('sols')]
        if filter_fn:
            bases = [b for b in bases if filter_fn(b)]
        if pdf_pattern:
            patterns = [p.strip().lower() for p in pdf_pattern.split(',') if p.strip()]
            bases = [b for b in bases if any(pat in b.lower() for pat in patterns)]
            log.info(f"Филтър '{pdf_pattern}': {len(bases)} olympiads")
        bases.sort(key=self._priority_key_paired)
        if limit:
            bases = bases[:limit]

        log.info(f"Classify-paired: {len(bases)} olympiads (11 кл областен first, newest→oldest)")

        skipped = 0
        processed = 0
        for i, base in enumerate(bases, 1):
            if self.state.budget_exceeded():
                log.warning(f"⚠ Бюджет достигнат на {i}/{len(bases)}")
                break

            out_dir_check = CLASSIFIED_DIR / safe_name(base)
            out_file_check = out_dir_check / 'all_problems.json'
            if out_file_check.exists() and not force:
                log.info(f"\n[{i}/{len(bases)}] {base}: skip (already classified)")
                skipped += 1
                continue

            group = grouped[base]
            probs = group.get('probs', [])
            sols = group.get('sols', [])
            log.info(f"\n[{i}/{len(bases)}] {base}: {len(probs)} probs, {len(sols)} sols")
            processed += 1

            # Case: standalone (no pair)
            if group.get('standalone'):
                entries = []
                for p in probs:
                    entries.append({
                        **p,
                        'point_id': None, 'point_confidence': 'pending',
                        'difficulty': None, 'techniques': [], 'reasoning': 'standalone',
                        '_standalone': True,
                    })
                self._write_classified(base, entries)
                log.info(f"  standalone → {len(entries)} entries (needs individual classify later)")
                continue

            # Case: only probs OR only sols — fall back to single-file classify per problem
            if not probs or not sols:
                only = probs or sols
                entries = []
                for p in only:
                    cls = self.classify_problem(p)
                    if cls:
                        entries.append({**p, **cls})
                    else:
                        entries.append({**p, 'point_id': None, 'point_confidence': 'failed'})
                    if self.state.budget_exceeded():
                        break
                self._write_classified(base, entries)
                log.info(f"  single-file fallback → {len(entries)} entries")
                continue

            # Case: paired classify
            result = self._classify_paired(base, probs, sols)
            if not result:
                log.error(f"  paired classify failed")
                continue

            entries = self._build_paired_entries(base, probs, sols, result)
            matched = sum(1 for e in entries if e.get('_paired'))
            orphans = sum(1 for e in entries if e.get('_orphan'))
            no_sol = sum(1 for e in entries if e.get('_no_solution'))
            unclassified = len(result.get('orphan_sols_without_statement', []))

            self._write_classified(base, entries, extra={
                "paired": True,
                "matched": matched,
                "orphan_kept": orphans,
                "no_sol": no_sol,
                "dropped_unclassifiable": unclassified,
            })

            log.info(f"  ✓ matched={matched}, orphan_kept={orphans}, no_sol={no_sol}, "
                     f"dropped_unclassifiable={unclassified}, total={len(entries)}")

        log.info(f"\n═══ Classify-paired завърши: processed={processed}, skipped={skipped}, total={len(bases)} ═══")
        
    # ═══════════════════════════════════════════════════════════
    # STATS
    # ═══════════════════════════════════════════════════════════
    def print_stats(self):
        print()
        print("═" * 75)
        print("  PHASE 1: EXTRACTED")
        n_pdfs = 0
        n_extracted = 0
        n_partial = 0
        for pdf_dir in sorted(EXTRACTED_DIR.iterdir()):
            if not pdf_dir.is_dir():
                continue
            all_file = pdf_dir / "all_problems.json"
            if all_file.exists():
                try:
                    data = json.loads(all_file.read_text(encoding="utf-8"))
                    n = len(data.get("problems", []))
                    n_extracted += n
                    n_pdfs += 1
                    status = self.state.data["extracted"].get(data["pdf"], {}).get("status", "?")
                    if status == "partial":
                        n_partial += 1
                except Exception:
                    pass
        print(f"  PDFs: {n_pdfs}  |  problems: {n_extracted}  |  partial: {n_partial}")

        print()
        print("  PHASE 2: MERGED")
        n_merged_pdfs = 0
        n_merged = 0
        if MERGED_DIR.exists():
            for mdir in sorted(MERGED_DIR.iterdir()):
                if not mdir.is_dir():
                    continue
                file = mdir / "all_problems.json"
                if file.exists():
                    try:
                        data = json.loads(file.read_text(encoding="utf-8"))
                        n = len(data.get("problems", []))
                        n_merged += n
                        n_merged_pdfs += 1
                    except Exception:
                        pass
        print(f"  Olympiads: {n_merged_pdfs}  |  problems: {n_merged}")

        print()
        print("  PHASE 3: CLASSIFIED")
        n_cls_pdfs = 0
        n_cls = 0
        n_off = 0
        if CLASSIFIED_DIR.exists():
            for cdir in sorted(CLASSIFIED_DIR.iterdir()):
                if not cdir.is_dir():
                    continue
                file = cdir / "all_problems.json"
                if file.exists():
                    try:
                        data = json.loads(file.read_text(encoding="utf-8"))
                        n = len(data.get("problems", []))
                        n_cls += n
                        n_cls_pdfs += 1
                        n_off += sum(1 for p in data["problems"] if not p.get("point_id"))
                    except Exception:
                        pass
        print(f"  Olympiads: {n_cls_pdfs}  |  problems: {n_cls}  |  off: {n_off}")

        print()
        print("  PHASE 4: REAL_PROBLEMS (per point)")
        total_real = 0
        points_with_problems = 0
        if REAL_PROBLEMS_DIR.exists():
            for f in sorted(REAL_PROBLEMS_DIR.glob("*.json")):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    if f.name == "_unclassified.json":
                        print(f"  {'unclassified':10s}  {data['total']:3d} problems  ⚠")
                        continue
                    total_real += data["total"]
                    points_with_problems += 1
                    d = data["by_difficulty"]
                    print(f"  {data['point_id']:10s}  {data['total']:3d} problems  "
                          f"(easy={d['easy']:2d}, medium={d['medium']:2d}, hard={d['hard']:2d})")
                except Exception:
                    pass

        print("─" * 75)
        print(f"  TOTAL: {total_real} real problems across {points_with_problems} points")
        print(f"  Cost: ${self.state.data['budget']['spent_usd']:.3f}")
        print("═" * 75)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════
def cmd_scan(limit=None, pdf_pattern=None):
    chunker = PDFChunker()
    pdfs = chunker.scan_pdfs()
    if pdf_pattern:
        pdfs = [p for p in pdfs if pdf_pattern.lower() in p.name.lower()]
    if limit:
        pdfs = pdfs[:limit]
    print(f"\nНамерени {len(pdfs)} PDF-а (след dedupe):\n")
    for p in pdfs:
        meta = infer_metadata_from_filename(p.stem)
        pages = _get_page_count(p)   # ← бързо, без OCR
        grade_str = f"{meta['grade']}" if meta['grade'] else (
            f"{meta['grade_range'][0]}-{meta['grade_range'][1]}" if meta['grade_range'] else "?"
        )
        info = split_pdf_name(p.stem)
        kind_str = info['kind'] or "book"
        variant_str = f" {info['variant']}" if info['variant'] else ""
        print(f"  {p.name:55s} {pages:3d}p  {meta['round']:12s} "
              f"year={meta['year'] or '?':6} grade={grade_str:5s} [{kind_str}{variant_str}]")


def cmd_reset(stage: str = "all"):
    if stage in ("all", "extract"):
        if EXTRACTED_DIR.exists():
            shutil.rmtree(EXTRACTED_DIR)
            EXTRACTED_DIR.mkdir()
        if stage == "all":
            if STATE_FILE.exists():
                STATE_FILE.unlink()
        else:
            if STATE_FILE.exists():
                try:
                    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                    data["extracted"] = {}
                    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                except Exception:
                    pass
        print(f"✓ Reset: extract")

    if stage in ("all", "merge"):
        if MERGED_DIR.exists():
            shutil.rmtree(MERGED_DIR)
            MERGED_DIR.mkdir()
        print(f"✓ Reset: merge")

    if stage in ("all", "classify"):
        if CLASSIFIED_DIR.exists():
            shutil.rmtree(CLASSIFIED_DIR)
            CLASSIFIED_DIR.mkdir()
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                data["classified"] = {}
                STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass
        print(f"✓ Reset: classify")

    if stage in ("all", "aggregate"):
        if REAL_PROBLEMS_DIR.exists():
            shutil.rmtree(REAL_PROBLEMS_DIR)
            REAL_PROBLEMS_DIR.mkdir()
        print(f"✓ Reset: aggregate")


def _get_page_count(pdf_path):
    """Бърз page count (без text extract)."""
    if HAS_PYMUPDF:
        try:
            import fitz
            doc = fitz.open(str(pdf_path))
            n = len(doc)
            doc.close()
            return n
        except Exception:
            pass
    if HAS_PYPDF:
        try:
            return len(PdfReader(str(pdf_path)).pages)
        except Exception:
            pass
    return 0


def cmd_audit():
    """Показва за всеки PDF: pages, chars, problems, problems/page."""
    chunker = PDFChunker()
    pdfs = chunker.scan_pdfs()
    pdf_by_name = {p.stem: p for p in pdfs}

    rows = []
    for pdf_dir in sorted(EXTRACTED_DIR.iterdir()):
        if not pdf_dir.is_dir():
            continue
        all_file = pdf_dir / "all_problems.json"
        if not all_file.exists():
            # PDF не е обработен изобщо
            continue
        try:
            data = json.loads(all_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        name = data["pdf"]
        n_probs = len(data.get("problems", []))

        # Pages + chars
        pdf_path = pdf_by_name.get(name)
        if pdf_path:
            pages = _get_page_count(pdf_path)
            try:
                page_data = extract_pdf_pages(pdf_path)
                chars = sum(len(p.get("text", "")) for p in page_data)
            except Exception:
                chars = 0
        else:
            pages = 0
            chars = 0

        ratio = n_probs / pages if pages else 0
        chars_per_page = chars / pages if pages else 0

        # Status
        status = "OK"
        if pages > 5 and n_probs == 0:
            status = "❌ EMPTY"
        elif pages > 5 and ratio < 0.15:
            status = "⚠ LOW"
        elif pages > 5 and chars_per_page < 100:
            status = "⚠ NO_TEXT"
        elif pages > 5 and chars_per_page < 200 and n_probs > 0:
            status = "△ OCR?"

        # State
        st = chunker.state.data["extracted"].get(name, {})
        state_status = st.get("status", "?")

        rows.append({
            "PDF": name[:42],
            "Pages": pages,
            "Chars/Page": round(chars_per_page),
            "Problems": n_probs,
            "P/Page": round(ratio, 2),
            "Status": status,
            "State": state_status,
        })

    # Unprocessed PDFs (never in extracted)
    unprocessed = []
    for pdf in pdfs:
        if pdf.stem not in [r["PDF"] for r in rows]:
            unprocessed.append(pdf.stem)

    # Print
    print()
    print("═" * 110)
    print(f"  EXTRACTION AUDIT — {len(rows)} processed PDFs")
    print("═" * 110)
    print(f"  {'PDF':<42} {'Pg':>4} {'C/P':>5} {'Prob':>5} {'P/Pg':>5} {'Status':>10} {'State':>10}")
    print("─" * 110)

    for r in sorted(rows, key=lambda x: (x["P/Page"], -x["Pages"])):
        print(f"  {r['PDF']:<42} {r['Pages']:>4} {r['Chars/Page']:>5} "
              f"{r['Problems']:>5} {r['P/Page']:>5} {r['Status']:>10} {r['State']:>10}")

    print("─" * 110)

    empty = [r for r in rows if r["Status"] == "❌ EMPTY"]
    low = [r for r in rows if r["Status"] == "⚠ LOW"]
    no_text = [r for r in rows if r["Status"] == "⚠ NO_TEXT"]

    print(f"  OK: {len([r for r in rows if r['Status'] == 'OK'])}")
    print(f"  ⚠ LOW (<0.15 prob/page): {len(low)}")
    if low:
        for r in low[:10]:
            print(f"      {r['PDF']} — {r['Problems']} problems / {r['Pages']} pages")
    print(f"  ❌ EMPTY: {len(empty)}")
    if empty:
        for r in empty[:10]:
            print(f"      {r['PDF']} — 0 problems (has {r['Chars/Page']} chars/page)")
    print(f"  ⚠ NO_TEXT (<100 chars/page): {len(no_text)}")

    if unprocessed:
        print()
        print(f"  📄 Unprocessed PDFs ({len(unprocessed)}):")
        for name in unprocessed[:20]:
            print(f"      {name}")

    print("═" * 110)
    print()
    print("  💡 За проблемни PDF-и:")
    print("      .\\py.bat pdf_chunker.py --extract --pdf \"<name>\" --force-extract")

def main():
    ap = argparse.ArgumentParser(description="PDF Chunker v3.2 (with Mistral OCR + AI separation)")
    ap.add_argument("--scan", action="store_true", help="Покажи какво има")
    ap.add_argument("--extract", action="store_true", help="Извлечи от PDF-и")
    ap.add_argument("--merge", action="store_true", help="Слей probs+sol двойки")
    ap.add_argument("--classify", action="store_true", help="Класифицирай")
    ap.add_argument("--classify-paired", action="store_true",
                    help="Paired classify: probs+sol в 1 AI call (11 кл областен first)")
    ap.add_argument("--force", action="store_true",
                    help="Презапиши дори ако файлът е вече класифициран")
    ap.add_argument("--aggregate", action="store_true", help="Групирай по точки")
    ap.add_argument("--all", action="store_true", help="Всички фази")
    ap.add_argument("--limit", type=int, default=None, help="Максимум N PDF-а")
    ap.add_argument("--pdf", default=None, help="Само PDF-и, съдържащи текста в името")
    ap.add_argument("--force-extract", action="store_true",
                    help="Изтрий state за PDF и пре-извлечи от нулата")
    ap.add_argument("--audit", action="store_true",
                    help="Покажи quality метрики за всеки PDF")
    ap.add_argument("--stats", action="store_true",
                    help="Per-phase статистика: extracted / merged / classified / anchors")
    ap.add_argument("--reset-stage", choices=["extract", "merge", "classify", "aggregate", "all"],
                    default=None, help="Изчисти само една фаза")
    args = ap.parse_args()

    if args.force_extract and args.pdf:
        # Изтрий state за PDF-и, съдържащи pattern
        st = ChunkerState()
        patterns = [p.strip().lower() for p in args.pdf.split(",") if p.strip()]
        cleared = []
        for name in list(st.data["extracted"].keys()):
            if any(pat in name.lower() for pat in patterns):
                del st.data["extracted"][name]
                cleared.append(name)
        st.save()
        print(f"✓ Изчистен state за {len(cleared)} PDF-а")
        for c in cleared:
            print(f"    {c}")

    if args.reset_stage:
        cmd_reset(args.reset_stage); return
    if args.scan:
        cmd_scan(limit=args.limit, pdf_pattern=args.pdf); return
    if args.audit:
        cmd_audit(); return

    chunker = PDFChunker()

    if args.extract or args.all:
        chunker.run_extract(limit=args.limit, pdf_pattern=args.pdf)
    if args.merge or args.all:
        chunker.run_merge()
    if args.classify_paired:
        chunker.run_classify_paired(limit=args.limit, pdf_pattern=args.pdf, force=args.force)
    elif args.classify or args.all:
        chunker.run_classify(limit=args.limit)
    if args.aggregate or args.all:
        chunker.run_aggregate()

    if getattr(args, "stats", False) or args.all:
        chunker.print_stats()


if __name__ == "__main__":
    main()