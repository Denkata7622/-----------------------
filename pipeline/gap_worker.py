#!/usr/bin/env python3
"""
pdf_gap_worker.py — 24/7 PDF gap analyzer
==========================================
Следи за нови PDF-ове в зададени папки, анализира ги с AI, намира
липсващи концепции в STEPS масива, верифицира ги и произвежда списък
с нови теми за добавяне.

Употреба:
    python pdf_gap_worker.py                 # 24/7
    python pdf_gap_worker.py --once          # 1 batch и излиза
    python pdf_gap_worker.py --scan          # само сканира
    python pdf_gap_worker.py --verify        # verifier + излиза
    python pdf_gap_worker.py --aggregate     # aggregation + излиза
    python pdf_gap_worker.py --reanalyze-all # пре-анализ на всички
    python pdf_gap_worker.py --reanalyze 2016-10
    python pdf_gap_worker.py --stats
    python pdf_gap_worker.py --reset
"""
import os
import re
import sys
import json
import time
import signal
import hashlib
import logging
import argparse
import traceback
from pathlib import Path
from datetime import datetime, date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from personas import MASTER_PERSONA

try:
    import requests
except ImportError:
    print("pip install requests"); sys.exit(1)

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

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


# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent.resolve()

DEFAULT_GAP_CONFIG = {
    "enabled": True,
    "daily_budget_usd": 0.50,
    "max_concurrent": 2,
    "poll_interval_sec": 60,
    "max_retries": 3,
    "retry_delay_sec": 8,
    "reanalyze_interval_days": 3,
    "reanalyze_batch_per_hour": 5,
    "verify_threshold": 10,
    "verify_interval_hours": 24,
    "aggregate_threshold": 5,
    "min_frequency_for_candidate": 2,
    "watch_folders": [
        "../Задачи_Минали_Години/",
        "../Материали_БГ/",
    ],
    "ignore_patterns": ["*_old*", "*_backup*", "*.tmp", "*.bak", "*~*"],
    "log_level": "INFO",
}


def load_config():
    cfg_file = BASE_DIR / "config.json"
    if not cfg_file.exists():
        print(f"✗ {cfg_file} не съществува"); sys.exit(1)
    with open(cfg_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Deep merge на gap_analysis секцията
    gap = DEFAULT_GAP_CONFIG.copy()
    if "gap_analysis" in cfg:
        gap.update(cfg["gap_analysis"])
    cfg["gap_analysis"] = gap
    return cfg


CONFIG = load_config()

# ── cost tracker init ──
from cost_tracker import init as _ct_init, track_call as _track_call
_ct_init(BASE_DIR.parent / "generated" / "costs" / "ledger.jsonl")


# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, CONFIG["gap_analysis"]["log_level"], logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"pdf_gap_worker_{date.today()}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("gap")


# ═══════════════════════════════════════════════════════════════
# PROMPTS
# ═══════════════════════════════════════════════════════════════
ANALYSIS_PROMPT = MASTER_PERSONA + """
Получаваш задачи и (ако има) решения от олимпиада.
Извлечи ВСИЧКИ концепции, които ученик трябва да знае, за да ги реши.

═══ ФОРМАТ НА ОТГОВОРА ═══
Върни САМО JSON (без markdown обвивка, без ```json):
{
  "problems": [
    {
      "num": 1,
      "topic": "geometry|algebra|number_theory|combinatorics|mixed",
      "theorems": ["Menelaus", "Ptolemy", ...],
      "techniques": ["substitution", "contradiction", ...],
      "concepts": ["cyclic quadrilaterals", "power of a point", ...],
      "difficulty": "standard|hard|olympic",
      "notes": "..."
    }
  ],
  "unique_concepts": ["...", "..."],
  "confidence": 0.0-1.0
}

═══ ПРАВИЛА ═══
- "theorems" — конкретни имена (Menelaus, Чева, AM-GM, Jensen, LTE, ...)
- "techniques" — похвати (индукция, противоречие, заместване, ...)
- "concepts" — какво трябва да знаеш (вписани ъгли, power of point, ...)
- "unique_concepts" — обединени уникални концепти от всички задачи
- Ако задачата е нестандартна — сложи го в notes
- Ако не разпознаваш задачата — сложи по-нисък confidence

═══ ВАЖНО ═══
Не измисляй неща. Ако задачата е просто стандартна — кажи го.
Не ползвай backticks освен в LaTeX формули.
"""


AGGREGATION_PROMPT = MASTER_PERSONA + """
Имаш концепции, извлечени от много минали олимпиади, и съществуващ
учебен план. Трябва да класифицираш всяка концепция:

1. WELL_COVERED — покрита е от съществуваща тема
2. PARTIALLY_COVERED — спомената е, но не задълбочено
3. MISSING — изобщо не е в плана

═══ КОНЦЕПЦИИ ОТ ОЛИМПИАДИ ═══
__CONCEPTS_LIST__

═══ СЪЩЕСТВУВАЩ УЧЕБЕН ПЛАН (145 теми) ═══
__EXISTING_TOPICS__

═══ ФОРМАТ ═══
Върни САМО JSON:
{
  "well_covered": [
    { "concept": "Menelaus", "frequency": 15, "topics": ["1.1"] }
  ],
  "partially_covered": [
    {
      "concept": "Ptolemy's inequality",
      "frequency": 8,
      "existing_topic": "1.3",
      "gap_description": "current text only shows equality case"
    }
  ],
  "missing_candidates": [
    {
      "concept": "Injective functional equations",
      "frequency": 6,
      "suggested_id": "R.16",
      "suggested_title": "ФУ: доказване на инжективност",
      "suggested_level": 2,
      "why": "Среща се в 6 задачи, никъде не е обяснено",
      "related_existing": ["7.5"],
      "examples": ["ОИ 2017/11 Зад 4", "..."],
      "confidence": 0.0-1.0
    }
  ]
}

═══ ПРАВИЛА ═══
- Само концепции с frequency >= 2 влизат в missing_candidates
- suggested_id: започвай с R. за преговорни, продължи номерацията
- suggested_level: 0=преговор, 1=областен, 2=национален, 3=IMO
- confidence < 0.6 = AI не е сигурен (ще го маркираме за ръчен преглед)
- Не давай повече от 10 кандидата наведнъж
"""


VERIFIER_PROMPT = MASTER_PERSONA + """
Проверяваш дали кандидат-тема е реална, уникална и заслужава собствена статия.

═══ ФОРМАТ ═══
Върни САМО JSON:
{
  "candidate_id": "R.16",
  "is_duplicate": false,
  "duplicate_of": null,
  "is_real_topic": true,
  "correct_level": 2,
  "worthy_of_article": true,
  "examples_valid": true,
  "score": 8,
  "verdict": "approve|revise|reject",
  "reason": "...",
  "suggested_changes": "...",
  "confidence": 0.0-1.0
}

═══ КРИТЕРИИ ═══
- is_duplicate: същата тема ли е като друга?
- is_real_topic: реална олимпиадна тема или sub-case на друга?
- worthy_of_article: >1000 думи материал? Или само 200-300 думи?
- score >= 7 → approve
- score 4-6 → revise
- score < 4 → reject
"""


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def pdf_hash(path: Path) -> str:
    """Бърз hash — първи 8KB + последни 8KB + размер."""
    try:
        st = path.stat()
        with open(path, "rb") as f:
            first = f.read(8192)
            if st.st_size > 8192:
                f.seek(-8192, 2)
                last = f.read(8192)
            else:
                last = b""
        h = hashlib.md5(first + last + str(st.st_size).encode()).hexdigest()
        return h
    except Exception as e:
        log.debug(f"hash fail {path}: {e}")
        return ""


def extract_pdf_text(path: Path) -> str:
    """Извлича текст от PDF. Опитва pdfplumber, после pypdf."""
    text = ""
    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(path) as pdf:
                parts = []
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    parts.append(t)
                text = "\n\n".join(parts)
        except Exception as e:
            log.debug(f"pdfplumber fail {path.name}: {e}")

    if not text.strip() and HAS_PYPDF:
        try:
            reader = PdfReader(str(path))
            parts = []
            for page in reader.pages:
                t = page.extract_text() or ""
                parts.append(t)
            text = "\n\n".join(parts)
        except Exception as e:
            log.debug(f"pypdf fail {path.name}: {e}")

    return text.strip()


def classify_level(path: Path) -> int:
    """Определя ниво по пътя на файла."""
    p = str(path).lower().replace("\\", "/")
    if "областен" in p or "regional" in p:
        return 1
    if "национален" in p or "national" in p:
        return 2
    if "материали_бг" in p:
        if "/ot_" in p or "ot_20" in p:
            return 3
        return 2
    if "материали_en" in p:
        return 3
    return 2  # default


def detect_type(filename: str) -> str:
    """probs / sol / combined"""
    low = filename.lower()
    if "-probs" in low or "_probs" in low:
        return "probs"
    if "-sol" in low or "_sol" in low or "solution" in low:
        return "sol"
    return "combined"


def olympiad_key(filename: str) -> str:
    """Извлича общ ключ за pairing (напр. '2016-10')."""
    name = Path(filename).stem
    # Махни suffix -probs, -sol, _probs, _sol
    name = re.sub(r"[-_](probs?|sol|solutions?)$", "", name, flags=re.IGNORECASE)
    # Извлечи година + клас
    m = re.search(r"(\d{4})[-_ ]?(\d{2})?\s*кл", name, re.IGNORECASE)
    if m:
        year, grade = m.group(1), m.group(2) or "00"
        return f"{year}-{grade}"
    m = re.search(r"(\d{4})", name)
    if m:
        return m.group(1)
    return name


def extract_steps_from_html(html_path: Path) -> list[dict]:
    """Извлича всички теми от STEPS масива в index.html."""
    if not html_path.exists():
        log.warning(f"HTML не е намерен: {html_path}")
        return []
    text = html_path.read_text(encoding="utf-8")
    pattern = re.compile(r'id\s*:\s*"([\d.]+)"\s*,\s*title\s*:\s*"([^"]+)"')
    steps = []
    for m in pattern.finditer(text):
        pid, title = m.group(1), m.group(2)
        steps.append({"id": pid, "title": title})
    log.info(f"Заредени {len(steps)} теми от index.html")
    return steps


# ═══════════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════════
class GapState:
    def __init__(self):
        self.file = BASE_DIR / "gap_state.json"
        self.data = self._load()

    def _load(self) -> dict:
        if self.file.exists():
            try:
                with open(self.file, "r", encoding="utf-8") as f:
                    d = json.load(f)
                # Migration — ensure keys
                d.setdefault("pdfs", {})
                d.setdefault("pairing", {})
                d.setdefault("queue", [])
                d.setdefault("candidates", [])
                d.setdefault("aggregation", {"last_run": 0})
                d.setdefault("budget", {"date": str(date.today()), "spent_usd": 0.0, "calls": 0})
                d.setdefault("last_full_recheck", 0)
                d.setdefault("last_verify", 0)
                d.setdefault("created_at", time.time())
                return d
            except Exception as e:
                log.warning(f"Не мога да прочета gap_state: {e}")
        return {
            "pdfs": {},
            "pairing": {},
            "queue": [],
            "candidates": [],
            "aggregation": {"last_run": 0},
            "budget": {"date": str(date.today()), "spent_usd": 0.0, "calls": 0},
            "last_full_recheck": 0,
            "last_verify": 0,
            "created_at": time.time(),
        }

    def save(self):
        tmp = self.file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        tmp.replace(self.file)

    def budget_reset_if_new_day(self):
        today = str(date.today())
        if self.data["budget"]["date"] != today:
            log.info(f"Нов ден — рестарт на gap бюджета")
            self.data["budget"] = {"date": today, "spent_usd": 0.0, "calls": 0}
            self.save()

    def budget_remaining(self) -> float:
        self.budget_reset_if_new_day()
        limit = CONFIG["gap_analysis"]["daily_budget_usd"]
        return limit - self.data["budget"]["spent_usd"]

    def add_cost(self, usd: float):
        self.data["budget"]["spent_usd"] += usd
        self.data["budget"]["calls"] += 1
        self.save()


# ═══════════════════════════════════════════════════════════════
# AI CLIENT (reuse pattern от pipeline.py)
# ═══════════════════════════════════════════════════════════════
class AIClient:
    def __init__(self, cfg: dict, name: str = "AI"):
        self.name = name
        self.url = cfg["api_url"]
        self.model = cfg["model"]
        self.max_tokens = cfg["max_tokens"]
        self.temperature = cfg["temperature"]
        self.headers = {"Content-Type": "application/json"}
        if cfg.get("api_key"):
            self.headers["Authorization"] = f"Bearer {cfg['api_key']}"

    def call(self, system: str, user: str, item_id: str = "?", force_json: bool = True) -> Optional[str]:
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

        for attempt in range(1, CONFIG["gap_analysis"]["max_retries"] + 1):
            try:
                t0 = time.time()
                r = requests.post(self.url, headers=self.headers, json=payload, timeout=180)
                if r.status_code == 429:
                    log.warning(f"[{item_id}/{self.name}] 429 — чакам 30с")
                    time.sleep(30); continue
                if r.status_code == 400 and force_json:
                    log.warning(f"[{item_id}/{self.name}] 400 — махам response_format")
                    payload.pop("response_format", None)
                    force_json = False
                    continue
                if r.status_code >= 500:
                    time.sleep(CONFIG["gap_analysis"]["retry_delay_sec"] * attempt)
                    continue
                if r.status_code >= 400:
                    log.error(f"[{item_id}/{self.name}] {r.status_code}: {r.text[:300]}")
                    return None
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    log.warning(f"[{item_id}/{self.name}] празен content")
                    continue
                _track_call("gap_worker", self.name, self.model, data, item_id=item_id, t0=t0)
                return content.strip()
            except requests.Timeout:
                log.warning(f"[{item_id}/{self.name}] timeout — опит {attempt}")
            except Exception as e:
                log.warning(f"[{item_id}/{self.name}] {e}")
            if attempt < CONFIG["gap_analysis"]["max_retries"]:
                time.sleep(CONFIG["gap_analysis"]["retry_delay_sec"] * attempt)
        return None


# ═══════════════════════════════════════════════════════════════
# PDF SCANNER
# ═══════════════════════════════════════════════════════════════
def scan_watch_folders() -> list[Path]:
    """Сканира всички watch папки и връща списък от PDF-ове."""
    result = []
    ignore_pats = CONFIG["gap_analysis"]["ignore_patterns"]

    for rel in CONFIG["gap_analysis"]["watch_folders"]:
        folder = (BASE_DIR / rel).resolve()
        if not folder.exists():
            log.debug(f"Папка не съществува: {folder}")
            continue
        for pdf in folder.rglob("*.pdf"):
            name = pdf.name.lower()
            if any(pat.strip("*").lower() in name for pat in ignore_pats):
                continue
            result.append(pdf)
    return result


def find_new_or_changed(state: GapState) -> list[Path]:
    """Намира PDF-ове, които не са в state или са с променен hash."""
    result = []
    for pdf in scan_watch_folders():
        rel_key = str(pdf.relative_to(BASE_DIR.parent)).replace("\\", "/")
        info = state.data["pdfs"].get(rel_key)
        current_hash = pdf_hash(pdf)
        if not current_hash:
            continue
        if not info or info.get("hash") != current_hash:
            result.append(pdf)
    return result


# ═══════════════════════════════════════════════════════════════
# ANALYSIS PIPELINE
# ═══════════════════════════════════════════════════════════════
def parse_json(text: str) -> Optional[dict]:
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```\s*$', '', text)
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end+1])
    except Exception:
        try:
            fixed = re.sub(r',\s*([}\]])', r'\1', text[start:end+1])
            return json.loads(fixed)
        except Exception:
            return None


class Analyzer:
    def __init__(self, state: GapState):
        self.state = state
        self.ai = AIClient(CONFIG["generator"], name="gap-gen")
        self.out_dir = BASE_DIR / "gap_output"
        self.out_dir.mkdir(exist_ok=True)
        (self.out_dir / "olympiads").mkdir(exist_ok=True)
        (self.out_dir / "_history").mkdir(exist_ok=True)

    def analyze_pdf(self, pdf: Path) -> bool:
        """Анализира 1 PDF (или двойка probs+sol)."""
        rel_key = str(pdf.relative_to(BASE_DIR.parent)).replace("\\", "/")
        info = self.state.data["pdfs"].get(rel_key, {})

        # Ако вече анализиран със същия hash → skip
        current_hash = pdf_hash(pdf)
        if info.get("hash") == current_hash and info.get("status") == "done":
            return False

        # Извлечи текст
        text = extract_pdf_text(pdf)
        if len(text) < 200:
            log.warning(f"[{pdf.name}] само {len(text)} символа — вероятно сканиран PDF")
            self.state.data["pdfs"][rel_key] = {
                **info,
                "hash": current_hash,
                "size": pdf.stat().st_size,
                "mtime": pdf.stat().st_mtime,
                "status": "error",
                "error": "text extraction too short",
                "last_analyzed": time.time(),
            }
            self.state.save()
            return False

        # Намери pair
        key = olympiad_key(pdf.name)
        ptype = detect_type(pdf.name)
        paired_text = ""
        paired_path = None

        if ptype == "probs":
            # Потърси sol
            sol_path = self._find_sol_for(pdf, key)
            if sol_path and sol_path != pdf:
                paired_text = extract_pdf_text(sol_path)
                paired_path = sol_path

        # Сглоби prompt
        user_msg = f"""═══ МЕТАДАННИ ═══
Файл: {pdf.name}
Олимпиада: {key}
Ниво: {classify_level(pdf)}
Тип: {ptype}

═══ ЗАДАЧИ ═══
{text[:30000]}

"""
        if paired_text:
            user_msg += f"""
═══ РЕШЕНИЯ ═══
{paired_text[:30000]}
"""

        user_msg += "\n\nИзвлечи концепции. Върни САМО JSON."

        # AI call
        log.info(f"→ [{pdf.name}] изпращам {len(user_msg)} символа")
        result = self.ai.call(ANALYSIS_PROMPT, user_msg, pdf.name)
        if not result:
            log.error(f"✗ [{pdf.name}] AI не отговори")
            self.state.data["pdfs"][rel_key] = {
                **info,
                "hash": current_hash,
                "size": pdf.stat().st_size,
                "mtime": pdf.stat().st_mtime,
                "status": "error",
                "error": "AI no response",
                "last_analyzed": time.time(),
            }
            self.state.save()
            return False

        parsed = parse_json(result)
        if not parsed:
            log.error(f"✗ [{pdf.name}] JSON парсване неуспешно")
            self.state.data["pdfs"][rel_key] = {
                **info,
                "hash": current_hash,
                "size": pdf.stat().st_size,
                "mtime": pdf.stat().st_mtime,
                "status": "error",
                "error": "JSON parse failed",
                "last_analyzed": time.time(),
            }
            self.state.save()
            return False

        # Запиши резултат
        out_file = self.out_dir / "olympiads" / f"{key}-{ptype}.json"
        # Ако вече има → архивирай
        if out_file.exists():
            old_ver = self._next_version(key, ptype)
            archive = self.out_dir / "_history" / f"{key}-{ptype}-v{old_ver}.json"
            out_file.rename(archive)

        out_data = {
            "_meta": {
                "pdf": str(pdf),
                "paired_with": str(paired_path) if paired_path else None,
                "level": classify_level(pdf),
                "type": ptype,
                "analyzed_at": datetime.now().isoformat(),
                "model": CONFIG["generator"]["model"],
                "text_length": len(text),
                "paired_text_length": len(paired_text),
            },
            **parsed,
        }
        out_file.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding="utf-8")

        # Update state
        self.state.data["pdfs"][rel_key] = {
            "hash": current_hash,
            "size": pdf.stat().st_size,
            "mtime": pdf.stat().st_mtime,
            "level": classify_level(pdf),
            "type": ptype,
            "olympiad_key": key,
            "first_seen": info.get("first_seen", time.time()),
            "last_analyzed": time.time(),
            "status": "done",
            "result_file": str(out_file.relative_to(BASE_DIR)),
            "error": None,
            "version": info.get("version", 0) + 1,
        }
        if paired_path:
            paired_rel = str(paired_path.relative_to(BASE_DIR.parent)).replace("\\", "/")
            if paired_rel not in self.state.data["pdfs"]:
                self.state.data["pdfs"][paired_rel] = {
                    "hash": pdf_hash(paired_path),
                    "size": paired_path.stat().st_size,
                    "mtime": paired_path.stat().st_mtime,
                    "level": classify_level(paired_path),
                    "type": "sol",
                    "olympiad_key": key,
                    "first_seen": time.time(),
                    "last_analyzed": time.time(),
                    "status": "done",
                    "result_file": str(out_file.relative_to(BASE_DIR)),
                    "error": None,
                    "version": 1,
                }

        self.state.data["pairing"][key] = {
            "probs": rel_key if ptype == "probs" else None,
            "sol": str(paired_path.relative_to(BASE_DIR.parent)).replace("\\", "/") if paired_path else None,
            "analyzed_as": str(out_file.relative_to(BASE_DIR)),
        }

        self.state.add_cost(0.005)  # груба оценка
        self.state.save()

        concepts = parsed.get("unique_concepts", [])
        log.info(f"✓ [{pdf.name}] {len(concepts)} концепции")
        return True

    def _find_sol_for(self, probs_pdf: Path, key: str) -> Optional[Path]:
        """Търси sol файл за probs файл."""
        folder = probs_pdf.parent
        name = probs_pdf.stem
        # Замени -probs с -sol
        for suffix in ["-probs", "_probs", "-PROBS", "-Probs"]:
            if suffix in name:
                sol_name = name.replace(suffix, suffix.replace("probs", "sol").replace("PROBS", "SOL"))
                for ext in [".pdf", ".PDF"]:
                    candidate = folder / (sol_name + ext)
                    if candidate.exists():
                        return candidate
        # Fallback — търси всеки файл с -sol в името
        for pdf in folder.glob("*-sol*.pdf"):
            if olympiad_key(pdf.name) == key:
                return pdf
        return None

    def _next_version(self, key: str, ptype: str) -> int:
        history = self.out_dir / "_history"
        count = len(list(history.glob(f"{key}-{ptype}-v*.json")))
        return count + 1


# ═══════════════════════════════════════════════════════════════
# AGGREGATOR
# ═══════════════════════════════════════════════════════════════
class Aggregator:
    def __init__(self, state: GapState):
        self.state = state
        self.ai = AIClient(CONFIG["generator"], name="gap-agg")
        self.out_dir = BASE_DIR / "gap_output"

    def run(self):
        log.info("═══ Aggregation стартира ═══")
        olympiads_dir = self.out_dir / "olympiads"
        if not olympiads_dir.exists():
            log.warning("Няма анализирани олимпиади")
            return

        # Събери всички концепции с честоти
        concept_freq = {}
        concept_examples = {}
        for f in olympiads_dir.glob("*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            olym = f.stem
            for prob in d.get("problems", []):
                for c in prob.get("concepts", []) + prob.get("theorems", []):
                    cnorm = c.strip().lower()
                    if not cnorm: continue
                    concept_freq[cnorm] = concept_freq.get(cnorm, 0) + 1
                    if cnorm not in concept_examples:
                        concept_examples[cnorm] = []
                    if len(concept_examples[cnorm]) < 3:
                        concept_examples[cnorm].append(f"{olym} Зад {prob.get('num')}")

        # Филтрирай само тези над threshold
        min_freq = CONFIG["gap_analysis"]["min_frequency_for_candidate"]
        top = sorted(
            [(c, f) for c, f in concept_freq.items() if f >= min_freq],
            key=lambda x: -x[1]
        )[:100]

        if not top:
            log.info("Няма достатъчно концепции за aggregation")
            return

        # Зареди STEPS от HTML
        steps = extract_steps_from_html(BASE_DIR.parent / "index.html")
        if not steps:
            log.warning("Няма STEPS — пропускам aggregation")
            return

        steps_str = "\n".join(f"{s['id']}: {s['title']}" for s in steps[:150])
        concepts_str = "\n".join(f"- {c} (freq={f}, examples: {', '.join(concept_examples[c])})" for c, f in top)

        user_msg = (AGGREGATION_PROMPT
            .replace("__CONCEPTS_LIST__", concepts_str)
            .replace("__EXISTING_TOPICS__", steps_str)
        )

        log.info(f"→ Aggregation call с {len(top)} концепции срещу {len(steps)} теми")
        result = self.ai.call(AGGREGATION_PROMPT, user_msg, "aggregate")
        if not result:
            log.error("✗ Aggregation AI не отговори")
            return

        parsed = parse_json(result)
        if not parsed:
            log.error("✗ Aggregation JSON парсване неуспешно")
            return

        # Запиши aggregated
        agg_file = self.out_dir / "_aggregated.json"
        agg_data = {
            "_meta": {
                "generated_at": datetime.now().isoformat(),
                "olympiads_analyzed": len(list(olympiads_dir.glob("*.json"))),
                "concepts_total": len(concept_freq),
                "concepts_above_threshold": len(top),
                "min_frequency": min_freq,
            },
            **parsed,
        }
        agg_file.write_text(json.dumps(agg_data, indent=2, ensure_ascii=False), encoding="utf-8")

        # Обнови candidates
        new_candidates = parsed.get("missing_candidates", [])
        existing_ids = {c.get("suggested_id") for c in self.state.data["candidates"]}
        added = 0
        for cand in new_candidates:
            cid = cand.get("suggested_id", "")
            if cid and cid not in existing_ids:
                cand["status"] = "pending"
                cand["added_at"] = time.time()
                cand["verification"] = None
                self.state.data["candidates"].append(cand)
                added += 1

        self.state.data["aggregation"] = {
            "last_run": time.time(),
            "well_covered": len(parsed.get("well_covered", [])),
            "partial": len(parsed.get("partially_covered", [])),
            "missing": len(new_candidates),
            "candidates_total": len(self.state.data["candidates"]),
        }
        self.state.add_cost(0.01)
        self.state.save()

        log.info(f"✓ Aggregation готов: {len(parsed.get('well_covered', []))} well, "
                 f"{len(parsed.get('partially_covered', []))} partial, "
                 f"{len(new_candidates)} missing ({added} нови)")


# ═══════════════════════════════════════════════════════════════
# VERIFIER
# ═══════════════════════════════════════════════════════════════
class Verifier:
    def __init__(self, state: GapState):
        self.state = state
        self.ai = AIClient(CONFIG["verifier"], name="gap-ver")
        self.out_dir = BASE_DIR / "gap_output"

    def run(self):
        log.info("═══ Verifier стартира ═══")
        pending = [c for c in self.state.data["candidates"] if c.get("status") == "pending"]
        if not pending:
            log.info("Няма pending кандидати")
            return

        # Зареди STEPS
        steps = extract_steps_from_html(BASE_DIR.parent / "index.html")
        steps_str = "\n".join(f"{s['id']}: {s['title']}" for s in steps[:150])

        verified_count = 0
        for cand in pending:
            user_msg = f"""═══ КАНДИДАТ-ТЕМА ═══
ID: {cand.get('suggested_id')}
Заглавие: {cand.get('suggested_title')}
Концепт: {cand.get('concept')}
Честота: {cand.get('frequency')}
Ниво: {cand.get('suggested_level')}
Защо: {cand.get('why')}
Свързани: {cand.get('related_existing', [])}
Примери: {cand.get('examples', [])}

═══ СЪЩЕСТВУВАЩИ ТЕМИ ═══
{steps_str}

Провери кандидата. Върни САМО JSON."""

            result = self.ai.call(VERIFIER_PROMPT, user_msg, cand.get("suggested_id", "?"))
            if not result:
                log.warning(f"⚠ Verifier не отговори за {cand.get('suggested_id')}")
                continue

            parsed = parse_json(result)
            if not parsed:
                log.warning(f"⚠ Verifier JSON парсване неуспешно за {cand.get('suggested_id')}")
                continue

            cand["verification"] = parsed
            verdict = parsed.get("verdict", "?")
            score = parsed.get("score", "?")
            cand["status"] = "verified" if verdict == "approve" else "rejected"
            verified_count += 1
            log.info(f"  {cand.get('suggested_id')}: {verdict} (score {score})")

        self.state.add_cost(0.008 * verified_count)
        self.state.data["last_verify"] = time.time()
        self.state.save()

        # Запиши verified report
        approved = [c for c in self.state.data["candidates"]
                    if c.get("verification") and c["verification"].get("verdict") == "approve"]
        revise = [c for c in self.state.data["candidates"]
                  if c.get("verification") and c["verification"].get("verdict") == "revise"]
        rejected = [c for c in self.state.data["candidates"]
                    if c.get("verification") and c["verification"].get("verdict") == "reject"]

        report = {
            "_meta": {
                "generated_at": datetime.now().isoformat(),
                "total": len(self.state.data["candidates"]),
                "approved": len(approved),
                "needs_review": len(revise),
                "rejected": len(rejected),
            },
            "approved": approved,
            "needs_review": revise,
            "rejected": rejected,
        }
        (self.out_dir / "_suggested_topics_verified.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        log.info(f"✓ Verifier готов: {len(approved)} approve, {len(revise)} revise, {len(rejected)} reject")


# ═══════════════════════════════════════════════════════════════
# MAIN WORKER
# ═══════════════════════════════════════════════════════════════
class Worker:
    def __init__(self):
        self.state = GapState()
        self.analyzer = Analyzer(self.state)
        self.aggregator = Aggregator(self.state)
        self.verifier = Verifier(self.state)
        self.running = True

    def stop(self, *args):
        log.info("Получен SIGTERM — спирам след текущите задачи...")
        self.running = False

    def scan_and_queue(self):
        """Сканира за нови PDF-ове и ги добавя в queue."""
        new_pdfs = find_new_or_changed(self.state)
        queued_keys = set(self.state.data["queue"])
        for pdf in new_pdfs:
            rel_key = str(pdf.relative_to(BASE_DIR.parent)).replace("\\", "/")
            if rel_key not in queued_keys:
                self.state.data["queue"].append(rel_key)
                # Запиши в pdfs с first_seen ако нов
                if rel_key not in self.state.data["pdfs"]:
                    self.state.data["pdfs"][rel_key] = {
                        "hash": pdf_hash(pdf),
                        "size": pdf.stat().st_size,
                        "mtime": pdf.stat().st_mtime,
                        "level": classify_level(pdf),
                        "type": detect_type(pdf.name),
                        "olympiad_key": olympiad_key(pdf.name),
                        "first_seen": time.time(),
                        "last_analyzed": 0,
                        "status": "pending",
                        "error": None,
                        "version": 0,
                    }
        if new_pdfs:
            log.info(f"➕ {len(new_pdfs)} нови/променени PDF-а в queue")
            self.state.save()
        return len(new_pdfs)

    def process_queue(self):
        """Обработва PDF-ове от queue."""
        if not self.state.data["queue"]:
            return 0
        if self.state.budget_remaining() < 0.02:
            log.warning(f"⚠ Gap бюджетът е изчерпан (${self.state.budget_remaining():.2f})")
            return 0

        batch = self.state.data["queue"][:CONFIG["gap_analysis"]["max_concurrent"]]
        processed = 0

        for rel_key in batch:
            pdf = (BASE_DIR.parent / rel_key).resolve()
            if not pdf.exists():
                log.warning(f"PDF изчезна: {rel_key}")
                self.state.data["queue"].remove(rel_key)
                continue
            try:
                if self.analyzer.analyze_pdf(pdf):
                    processed += 1
            except Exception as e:
                log.exception(f"Грешка при {rel_key}: {e}")
            finally:
                if rel_key in self.state.data["queue"]:
                    self.state.data["queue"].remove(rel_key)
                self.state.save()
        return processed

    def should_reanalyze(self) -> bool:
        """Проверява дали да пуснем scheduled re-analysis."""
        days = CONFIG["gap_analysis"]["reanalyze_interval_days"]
        last = self.state.data["last_full_recheck"]
        if last == 0:
            # Първи път — не re-analyze
            self.state.data["last_full_recheck"] = time.time()
            self.state.save()
            return False
        return (time.time() - last) > days * 86400

    def queue_reanalysis_batch(self):
        """Добавя N стари PDF-а в queue за re-analysis."""
        batch_size = CONFIG["gap_analysis"]["reanalyze_batch_per_hour"]
        old = []
        for rel_key, info in self.state.data["pdfs"].items():
            if info.get("status") == "done" and info.get("type") == "probs":
                old.append((rel_key, info.get("last_analyzed", 0)))
        old.sort(key=lambda x: x[1])  # най-старите първи
        added = 0
        for rel_key, _ in old[:batch_size]:
            if rel_key not in self.state.data["queue"]:
                self.state.data["queue"].append(rel_key)
                added += 1
        if added:
            log.info(f"↻ Re-analysis: {added} PDF-а в queue")
            self.state.save()

        # Ако всички са обходени → маркирай
        if len(old) <= batch_size:
            self.state.data["last_full_recheck"] = time.time()
            self.state.save()

    def should_aggregate(self) -> bool:
        last = self.state.data["aggregation"].get("last_run", 0)
        if last == 0:
            return True
        # Ако има нови анализи след последния aggregation
        new_count = sum(1 for info in self.state.data["pdfs"].values()
                        if info.get("status") == "done" and info.get("last_analyzed", 0) > last)
        return new_count >= CONFIG["gap_analysis"]["aggregate_threshold"]

    def should_verify(self) -> bool:
        pending = [c for c in self.state.data["candidates"] if c.get("status") == "pending"]
        threshold = CONFIG["gap_analysis"]["verify_threshold"]
        if len(pending) >= threshold:
            return True
        hours = CONFIG["gap_analysis"]["verify_interval_hours"]
        last = self.state.data.get("last_verify", 0)
        if pending and (time.time() - last) > hours * 3600:
            return True
        return False

    def run_forever(self):
        log.info("═" * 60)
        log.info("PDF Gap Worker стартиран 24/7")
        log.info(f"  Generator:    {CONFIG['generator']['model']}")
        log.info(f"  Verifier:     {CONFIG['verifier']['model']}")
        log.info(f"  Budget/ден:   ${CONFIG['gap_analysis']['daily_budget_usd']:.2f}")
        log.info(f"  Watch:        {', '.join(CONFIG['gap_analysis']['watch_folders'])}")
        log.info(f"  Reanalyze:    всеки {CONFIG['gap_analysis']['reanalyze_interval_days']} дни")
        log.info("═" * 60)

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        # Initial scan
        self.scan_and_queue()

        while self.running:
            try:
                # 1. Scan
                self.scan_and_queue()

                # 2. Process queue
                n = self.process_queue()

                # 3. Scheduled re-analysis
                if self.should_reanalyze() and not self.state.data["queue"]:
                    self.queue_reanalysis_batch()

                # 4. Aggregation
                if self.should_aggregate() and not self.state.data["queue"]:
                    try:
                        self.aggregator.run()
                    except Exception as e:
                        log.exception(f"Aggregation грешка: {e}")

                # 5. Verifier
                if self.should_verify():
                    try:
                        self.verifier.run()
                    except Exception as e:
                        log.exception(f"Verifier грешка: {e}")

                time.sleep(CONFIG["gap_analysis"]["poll_interval_sec"])

            except KeyboardInterrupt:
                break
            except Exception as e:
                log.exception(f"Main loop грешка: {e}")
                time.sleep(30)

        log.info("Worker спрян")

    def run_once(self):
        """1 batch и излиза."""
        self.scan_and_queue()
        n = self.process_queue()
        if self.should_aggregate():
            self.aggregator.run()
        if self.should_verify():
            self.verifier.run()
        log.info(f"Обработени: {n}")

    def print_stats(self):
        pdfs = self.state.data["pdfs"]
        done = sum(1 for p in pdfs.values() if p.get("status") == "done")
        err = sum(1 for p in pdfs.values() if p.get("status") == "error")
        pending = len(self.state.data["queue"])
        agg = self.state.data.get("aggregation", {})
        cands = self.state.data.get("candidates", [])
        approved = sum(1 for c in cands if c.get("verification", {}) and c["verification"].get("verdict") == "approve")

        print()
        print("═" * 55)
        print(f"  PDFs total:      {len(pdfs)}")
        print(f"  ✓ Analyzed:      {done}")
        print(f"  ✗ Errors:        {err}")
        print(f"  ⏳ Pending:       {pending}")
        print(f"  Aggregation:     {datetime.fromtimestamp(agg.get('last_run', 0)).strftime('%Y-%m-%d %H:%M') if agg.get('last_run') else 'never'}")
        print(f"  Candidates:      {len(cands)}")
        print(f"  ✓ Approved:      {approved}")
        print(f"  Budget today:    ${self.state.data['budget']['spent_usd']:.4f} / ${CONFIG['gap_analysis']['daily_budget_usd']:.2f}")
        print("═" * 55)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════
def main():
    if not HAS_PDFPLUMBER and not HAS_PYPDF:
        print("✗ Инсталирай pdfplumber: pip install pdfplumber")
        sys.exit(1)

    ap = argparse.ArgumentParser(description="PDF Gap Worker")
    ap.add_argument("--once", action="store_true", help="1 batch и излиза")
    ap.add_argument("--scan", action="store_true", help="Само сканирай")
    ap.add_argument("--verify", action="store_true", help="Verifier + излиза")
    ap.add_argument("--aggregate", action="store_true", help="Aggregation + излиза")
    ap.add_argument("--reanalyze-all", action="store_true", help="Re-analyze всички")
    ap.add_argument("--reanalyze", type=str, help="Re-analyze конкретна олимпиада")
    ap.add_argument("--stats", action="store_true", help="Статистика")
    ap.add_argument("--reset", action="store_true", help="Изчисти gap_state.json")

    args = ap.parse_args()

    if args.reset:
        f = BASE_DIR / "gap_state.json"
        if f.exists():
            f.unlink()
            print("✓ gap_state.json изтрит")
        return

    worker = Worker()

    if args.stats:
        worker.print_stats()
        return
    if args.scan:
        n = worker.scan_and_queue()
        print(f"Намерени {n} нови/променени PDF-а")
        worker.print_stats()
        return
    if args.verify:
        worker.verifier.run()
        return
    if args.aggregate:
        worker.aggregator.run()
        return
    if args.reanalyze_all:
        for rel_key in worker.state.data["pdfs"]:
            if rel_key not in worker.state.data["queue"]:
                worker.state.data["queue"].append(rel_key)
        worker.state.save()
        worker.run_once()
        return
    if args.reanalyze:
        key = args.reanalyze
        added = 0
        for rel_key in worker.state.data["pdfs"]:
            if key in rel_key and rel_key not in worker.state.data["queue"]:
                worker.state.data["queue"].append(rel_key)
                added += 1
        worker.state.save()
        print(f"Добавени {added} PDF-а с ключ '{key}' в queue")
        worker.run_once()
        return
    if args.once:
        worker.run_once()
        return

    # Default: 24/7
    worker.run_forever()


if __name__ == "__main__":
    main()