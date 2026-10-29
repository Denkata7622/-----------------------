#!/usr/bin/env python3
"""
Olympiad Prep — AI Pipeline (clean v7)

Structure:
  1. CONFIG + logging
  2. Exceptions
  3. Data models (QueueItem)
  4. State       — thread-safe persistent state + budget
  5. Queue       — JSONL loading, sort, pending filter
  6. AIClient    — HTTP wrapper with retries, cost tracking
  7. Writer      — filesystem output (text.md, deep.md, metadata.json, verify.md)
  8. Pipeline    — orchestration (generation + verification + retry loop)
  9. CLI

Changes in v7 (vs v6):
  • REGEN prompt rewritten: includes previous article as context,
    correct per-section math (ceil), self-check before return
  • IMPROVE prompt uses same ceil math (no more 9×250=2250<2800 bug)
  • All hardcoded prompt values moved to CONFIG (article_structure,
    real_problem_truncation, source_problem_truncation, max_real_problems)
  • load_config deep-merges ALL dict keys (not just generator/verifier)
  • AIClient always sends reasoning_effort if set (not just for GLM);
    on 400, tries removing response_format, then reasoning_effort
  • Fixed improve_threshold_pct fallback mismatch (0.3 everywhere)
  • Removed dead code in _build_regen_prompt
  • Removed unused MASTER_PERSONA import
  • _extract_summary_section uses article_header_pattern from CONFIG
  • Added --check-config CLI command
"""
import os
import sys
import json
import time
import signal
import logging
import argparse
import re
import threading
from pathlib import Path
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

def _atomic_write(path: Path, content: str) -> None:
    """
    Атомарен запис + fsync — оцелява при внезапно изключване на лаптопа.
    Уникален .tmp per-thread за избягване на PermissionError при concurrent writes.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Уникален tmp за всеки thread — иначе Windows дава PermissionError
    import threading
    tid = threading.current_thread().ident or 0
    tmp = path.with_suffix(f"{path.suffix}.{tid}.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        try:
            os.fsync(f.fileno())
        except (OSError, AttributeError):
            pass
    try:
        tmp.replace(path)
    except (OSError, PermissionError):
        path.write_text(content, encoding="utf-8")
        try:
            tmp.unlink()
        except Exception:
            pass


# ─── Windows UTF-8 fix ───
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import requests
except ImportError:
    print("Инсталирай requests: pip install requests")
    sys.exit(1)

try:
    from personas import ARTICLE_REVIEWER, ARTICLE_WRITER
except ImportError as e:
    print(f"⚠ Грешка при импорт от personas.py: {e}")
    sys.exit(1)

try:
    from prompts import (
        format_prompt,
        ARTICLE_PROMPT,
        ARTICLE_VERIFICATION_PROMPT,
    )
except ImportError as e:
    print(f"⚠ Грешка при импорт от prompts.py: {e}")
    sys.exit(1)

try:
    from scan_queue import scan_and_merge
    AUTO_SCAN_AVAILABLE = True
except ImportError:
    AUTO_SCAN_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent.resolve()

# ── cost tracker init ──
from cost_tracker import init as _ct_init, track_call as _track_call
_ct_init(BASE_DIR.parent / "generated" / "costs" / "ledger.jsonl")


DEFAULT_CONFIG = {
    "generator": {
        "provider": "openai-compatible",
        "api_url": "https://ai.hackclub.com/proxy/v1/chat/completions",
        "api_key": "",
        "model": "openai/gpt-6.1-sol",
        "max_tokens": 32000,
        "temperature": 0.3,
        "cost_per_call_usd": 0.015,
    },
    "verifier": {
        "provider": "openai-compatible",
        "api_url": "https://ai.hackclub.com/proxy/v1/chat/completions",
        "api_key": "",
        "model": "deepseek/deepseek-v3.2",
        "max_tokens": 12000,
        "temperature": 0.1,
        "cost_per_call_usd": 0.008,
    },
    "daily_budget_usd": 5.00,
    "max_verification_retries": 1,
    "min_verification_score": 7,
    "enable_verification": True,
    "max_retries": 3,
    "retry_delay_sec": 8,
    "request_timeout_sec": 600,   # 10 min — Sol с reasoning може да е бавен
    "max_concurrent": 2,
    "tick_interval_sec": 6,
    "batch_size": 2,
    "budget_stop_pct": 0.80,
    "log_level": "INFO",
    "auto_scan": True,
    "scan_every_ticks": 10,
    "html_path": "",
    "pdf_root": "",
    "scan_only_with_pdf": False,
    "scan_skip_with_explanation": False,
    "min_word_count": 2500,
    "target_word_count_min": 2800,
    "target_word_count_max": 3400,
    "improve_threshold_pct": 0.3,
    "perfect_score_threshold": 10,   # При score >= това → изтрий temp. -1 = забранено

    # ─── Prompt configuration (no more hardcoded values) ───
    "article_structure": {
        "expand_ranges": "3.1-3.6, 4.1-4.3",
        "min_words_per_section": 300,
        "total_sections": 9,
    },
    "max_real_problems": 4,
    "real_problem_truncation": {
        "statement_chars": 600,
        "solution_chars": 1500,
    },
    "source_problem_truncation": {
        "explanation_chars": 1500,
        "desc_chars": 800,
    },
    "article_header_pattern": r"(?m)^##\s+(\d+\.\s*[^\n]+)",
}


def load_config() -> dict:
    cfg_file = BASE_DIR / "config.json"
    if cfg_file.exists():
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            merged = DEFAULT_CONFIG.copy()
            for key in user_cfg:
                # Deep merge за ВСИЧКИ dict ключове (не само generator/verifier)
                if isinstance(DEFAULT_CONFIG.get(key), dict) and isinstance(user_cfg[key], dict):
                    merged[key] = {**DEFAULT_CONFIG[key], **user_cfg[key]}
                else:
                    merged[key] = user_cfg[key]
            return merged
        except Exception as e:
            print(f"⚠ Грешка при четене на config.json: {e}")
    with open(cfg_file, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
    return DEFAULT_CONFIG.copy()


CONFIG = load_config()


# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, CONFIG["log_level"], logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"pipeline_{date.today()}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("pipeline")


# ═══════════════════════════════════════════════════════════════
# EXCEPTIONS
# ═══════════════════════════════════════════════════════════════
class BudgetExhausted(Exception):
    """HTTP 402 или локален budget cap — спира целия run."""


# ═══════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════
@dataclass
class QueueItem:
    id: str
    title: str
    desc: str = ""
    source: str = ""
    pdf: str = ""
    page: int = 1
    explanation: str = ""
    step_title: str = ""
    status: str = "pending"
    attempts: int = 0
    error: str = ""
    result: str = ""
    deep_result: str = ""
    verification: Optional[dict] = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    started_at: Optional[float] = None
    finished_at: Optional[float] = None


# ═══════════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════════
class State:
    def __init__(self):
        self.file = BASE_DIR / "state.json"
        self._lock = threading.RLock()
        self.data = self._load()

    def _load(self) -> dict:
        if self.file.exists():
            try:
                with open(self.file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log.warning(f"Не мога да прочета state: {e}")
        return {
            "processed": {},
            "budget": {"date": str(date.today()), "spent_usd": 0.0, "calls": 0},
            "started_at": time.time(),
            "total_calls": 0,
            "total_cost_usd": 0.0,
        }

    def save(self):
        with self._lock:
            text = json.dumps(self.data, indent=2, ensure_ascii=False)
            tmp = self.file.with_suffix(".tmp")
            try:
                tmp.write_text(text, encoding="utf-8")
            except PermissionError:
                self.file.write_text(text, encoding="utf-8")
                return
            for attempt in range(6):
                try:
                    tmp.replace(self.file)
                    return
                except PermissionError:
                    if attempt < 5:
                        time.sleep(0.3 * (attempt + 1))
                    else:
                        self.file.write_text(text, encoding="utf-8")
                        try:
                            tmp.unlink()
                        except Exception:
                            pass
                        return

    def check_budget_reset(self):
        today = str(date.today())
        with self._lock:
            if self.data["budget"]["date"] != today:
                log.info(f"Нов ден — рестарт на бюджета (предишен: ${self.data['budget']['spent_usd']:.3f})")
                self.data["budget"] = {"date": today, "spent_usd": 0.0, "calls": 0}
                self.save()

    def budget_remaining(self) -> float:
        self.check_budget_reset()
        with self._lock:
            return CONFIG["daily_budget_usd"] - self.data["budget"]["spent_usd"]

    def budget_exceeded(self) -> bool:
        self.check_budget_reset()
        limit = CONFIG["daily_budget_usd"] * CONFIG["budget_stop_pct"]
        with self._lock:
            return self.data["budget"]["spent_usd"] >= limit

    def add_cost(self, usd: float, tokens: int = 0):
        self.check_budget_reset()
        with self._lock:
            self.data["budget"]["spent_usd"] += usd
            self.data["budget"]["calls"] += 1
            self.data["total_calls"] += 1
            self.data["total_cost_usd"] += usd
            self.save()

    def mark(self, item_id: str, status: str, cost: float = 0.0, tokens: int = 0, **extra):
        with self._lock:
            entry = {
                "status": status, "cost": cost, "tokens": tokens, "ts": time.time(),
            }
            # Merge any extra metadata (score, verdict, word_count, generator_model, retries...)
            for k, v in extra.items():
                if v is not None:
                    entry[k] = v
            self.data["processed"][item_id] = entry
            self.save()

    def is_done(self, item_id: str) -> bool:
        with self._lock:
            return self.data["processed"].get(item_id, {}).get("status") == "done"

    def stats(self) -> dict:
        with self._lock:
            procs = self.data["processed"]
            done = sum(1 for v in procs.values() if v["status"] == "done")
            err = sum(1 for v in procs.values() if v["status"] == "error")
            return {
                "done": done, "error": err, "total": len(procs),
                "today_spent": self.data["budget"]["spent_usd"],
                "today_calls": self.data["budget"]["calls"],
                "total_cost": self.data["total_cost_usd"],
            }


# ═══════════════════════════════════════════════════════════════
# QUEUE
# ═══════════════════════════════════════════════════════════════
def point_sort_key(point_id: str) -> tuple:
    """R.1 → R.15 → 1.1 → 1.15 → 2.1 → ... → 13.4"""
    if point_id.startswith("R."):
        return (0, int(point_id[2:]))
    major, minor = point_id.split(".")
    return (int(major), int(minor))


class Queue:
    def __init__(self):
        self.file = BASE_DIR / "queue.jsonl"
        self.items: list[QueueItem] = []
        self._load()

    def _load(self):
        if not self.file.exists():
            log.warning(f"Няма {self.file.name} — създавам примерен")
            self._create_sample()
        self.items = []
        with open(self.file, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    obj = json.loads(line)
                    allowed = {f.name for f in QueueItem.__dataclass_fields__.values()}
                    clean = {k: v for k, v in obj.items() if k in allowed}
                    self.items.append(QueueItem(**clean))
                except Exception as e:
                    log.error(f"Ред {i}: невалиден JSON — {e}")

    def _create_sample(self):
        sample = [
            {"id": "1.1", "title": "Теорема на Менелай",
             "desc": "Колинеарни точки върху страните на триъгълник",
             "source": "OT_2012", "pdf": "Материали_БГ/OT_2012", "page": 67},
        ]
        with open(self.file, "w", encoding="utf-8") as f:
            for item in sample:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def pending(self, state: State, only_id: Optional[str] = None) -> list[QueueItem]:
        items = [
            it for it in self.items
            if it.status in ("pending", "error")
            and not state.is_done(it.id)
            and it.attempts < CONFIG["max_retries"]
        ]
        if only_id:
            return [it for it in items if it.id == only_id]
        return sorted(items, key=lambda it: point_sort_key(it.id))

    def get(self, item_id: str) -> Optional[QueueItem]:
        return next((it for it in self.items if it.id == item_id), None)

    def reload(self):
        self._load()

    def total(self) -> int:
        return len(self.items)


# ═══════════════════════════════════════════════════════════════
# AI CLIENT
# ═══════════════════════════════════════════════════════════════
class AIClient:
    def __init__(self, cfg: dict, name: str = "AI"):
        self.name = name
        self.url = cfg["api_url"]
        self.model = cfg["model"]
        self.max_tokens = cfg["max_tokens"]
        self.temperature = cfg["temperature"]
        self.reasoning_effort = cfg.get("reasoning_effort")  # per-client
        self.cost_per_call_fallback = cfg.get("cost_per_call_usd", 0.0) or 0.0
        self.is_anthropic = (
            "anthropic" in self.url.lower()
            or cfg.get("provider", "").lower() == "anthropic"
        )
        self.headers = {"Content-Type": "application/json"}
        if self.is_anthropic:
            self.headers["x-api-key"] = cfg["api_key"]
            self.headers["anthropic-version"] = "2023-06-01"
        elif cfg.get("api_key"):
            self.headers["Authorization"] = f"Bearer {cfg['api_key']}"

    def _payload(self, system: str, user: str, force_json: bool = False) -> dict:
        if self.is_anthropic:
            return {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            }
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
        # Винаги подавай reasoning_effort ако е зададен — независимо от модела.
        # Ако моделът не го поддържа, 400 handler-ът ще го махне.
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort
        return payload

    def _extract_text(self, data: dict) -> str:
        if self.is_anthropic:
            blocks = data.get("content", [])
            parts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
            return "\n".join(parts).strip()
        content = data.get("choices", [{}])[0].get("message", {}).get("content")
        return (content or "").strip()

    def _extract_usage(self, data: dict) -> tuple[int, float]:
        """Връща (tokens, cost).
        
        Приоритет:
          1. usage.cost / usage.total_cost / usage.cost_usd (реално от API)
          2. Compute от input_tokens + output_tokens × model_pricing
          3. Fallback cost_per_call_usd
        """
        usage = data.get("usage", {}) or {}
        
        # ─── Tokens ───
        if self.is_anthropic:
            input_t = usage.get("input_tokens", 0) or 0
            output_t = usage.get("output_tokens", 0) or 0
        else:
            input_t = usage.get("prompt_tokens", 0) or 0
            output_t = usage.get("completion_tokens", 0) or 0
        tokens = usage.get("total_tokens", 0) or (input_t + output_t)
        
        # ─── Cost: try multiple fields ───
        cost = (
            usage.get("cost") or
            usage.get("total_cost") or
            usage.get("cost_usd") or
            0.0
        )
        
        # ─── If API didn't return cost, compute from pricing ───
        if cost == 0.0 and tokens > 0:
            pricing = CONFIG.get("model_pricing", {}).get(self.model)
            if pricing:
                in_p = pricing.get("input", 0)
                out_p = pricing.get("output", 0)
                if in_p > 0 or out_p > 0:
                    cost = (input_t * in_p + output_t * out_p) / 1_000_000
        
        # ─── Fallback config ───
        if cost == 0.0 and tokens > 0 and self.cost_per_call_fallback > 0:
            cost = self.cost_per_call_fallback
        
        return tokens, cost

    def call(self, system: str, user: str, item_id: str = "?", force_json: bool = False):
        """
        Връща (text, tokens, cost).
        При грешка: (None, 0, 0).
        При 402: хвърля BudgetExhausted.
        """
        payload = self._payload(system, user, force_json=force_json)
        for attempt in range(1, CONFIG["max_retries"] + 1):
            try:
                timeout = CONFIG.get("request_timeout_sec", 600)
                t0 = time.time()
                r = requests.post(self.url, headers=self.headers, json=payload, timeout=timeout)
                if r.status_code == 400:
                    # Опитай да махнеш ВСИЧКИ "risk" параметри наведнъж.
                    # Ако сме махнали нещо — retry БЕЗ да броим за attempt
                    # (използваме while-подобен pattern с ръчен контрол).
                    removed = []
                    if "response_format" in payload:
                        payload.pop("response_format", None)
                        removed.append("response_format")
                    if "reasoning_effort" in payload:
                        payload.pop("reasoning_effort", None)
                        removed.append("reasoning_effort")

                    if removed:
                        log.warning(
                            f"[{item_id}/{self.name}] 400 — махам {', '.join(removed)}, retry"
                        )
                        # Не вдигай attempt — това е "fix", не "retry"
                        # Използваме същия цикъл, но с намален брояч
                        attempt -= 1
                        continue

                    log.error(f"[{item_id}/{self.name}] 400 без fixable param: {r.text[:400]}")
                    return None, 0, 0
                if r.status_code == 429:
                    log.warning(f"[{item_id}/{self.name}] 429 — чакам 30с")
                    time.sleep(30)
                    continue
                if r.status_code == 402:
                    raise BudgetExhausted(f"[{item_id}/{self.name}] 402: {r.text[:200]}")
                if r.status_code >= 500:
                    log.warning(f"[{item_id}/{self.name}] {r.status_code} — retry {attempt}")
                    time.sleep(CONFIG["retry_delay_sec"] * attempt)
                    continue
                if r.status_code >= 400:
                    log.error(f"[{item_id}/{self.name}] {r.status_code}: {r.text[:400]}")
                    return None, 0, 0
                data = r.json()
                tokens, cost = self._extract_usage(data)
                _track_call("pipeline", self.name, self.model, data,
                            item_id=item_id, is_anthropic=self.is_anthropic, t0=t0)
                return self._extract_text(data), tokens, cost
            except BudgetExhausted:
                raise
            except requests.Timeout:
                log.warning(f"[{item_id}/{self.name}] Timeout — НЕ retry-вам (риск от двойно таксуване)")
                return None, 0, 0
            except requests.RequestException as e:
                log.warning(f"[{item_id}/{self.name}] Network грешка — опит {attempt}: {e}")
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                log.error(f"[{item_id}/{self.name}] Лош отговор — {e}")
                return None, 0, 0
            if attempt < CONFIG["max_retries"]:
                time.sleep(CONFIG["retry_delay_sec"] * attempt)
        return None, 0, 0


# ═══════════════════════════════════════════════════════════════
# WRITER
# ═══════════════════════════════════════════════════════════════
def _strip_dup_header(content: str) -> str:
    """parts[i+1] започва с ' Заглавие\n\nтекст' — маха първия ред."""
    content = content.lstrip()
    if "\n" in content:
        _, rest = content.split("\n", 1)
        return rest
    return ""


class Writer:
    def __init__(self):
        self.dir = BASE_DIR.parent / "generated" / "articles"
        self.dir.mkdir(parents=True, exist_ok=True)

    def save_attempt(self, item_id: str, attempt_num: int, article_md: str,
                     word_count: int, score: Optional[int] = None,
                     verdict: Optional[str] = None, label: str = "initial") -> Path:
        """
        Запазва опит в temp/ директория — за сигурност при crash / budget out.
        Създава: generated/articles/{id}/temp/attempt-XX-{label}.md
        При повторно извикване със същите (attempt_num, label), презаписва
        файла (за да добави score след верификация).
        """
        safe_id = item_id.replace(".", "_")
        folder = self.dir / safe_id / "temp"
        folder.mkdir(parents=True, exist_ok=True)

        filename = f"attempt-{attempt_num:02d}-{label}.md"
        filepath = folder / filename

        score_str = f"{score}/10" if score is not None else "— (непроверена)"
        verdict_str = verdict or "—"
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        header = (
            f"# {item_id} — опит {attempt_num} ({label})\n\n"
            f"**Score:** {score_str}  \n"
            f"**Verdict:** {verdict_str}  \n"
            f"**Word count:** {word_count}  \n"
            f"**Saved:** {ts}\n\n"
            f"---\n\n"
        )
        _atomic_write(filepath, header + article_md)
        log.info(
            f"[{item_id}] 💾 Temp: {filename} "
            f"({word_count}w, score {score if score is not None else '?'})"
        )
        return filepath

    def cleanup_temp(self, item_id: str) -> bool:
        """Изтрива temp/ директорията за item. Връща True ако е изтрита."""
        safe_id = item_id.replace(".", "_")
        temp_dir = self.dir / safe_id / "temp"
        if not temp_dir.exists():
            return False
        try:
            import shutil
            shutil.rmtree(temp_dir)
            log.info(f"[{item_id}] 🗑️  Temp изтрит")
            return True
        except Exception as e:
            log.warning(f"[{item_id}] Не мога да изтрия temp: {e}")
            return False

    def list_temp(self, item_id: str) -> list:
        """Връща списък с temp файловете за item."""
        safe_id = item_id.replace(".", "_")
        temp_dir = self.dir / safe_id / "temp"
        if not temp_dir.exists():
            return []
        return sorted(temp_dir.glob("*.md"))

    def save_verification(self, item_id: str, attempt_num: int,
                          label: str, verification: dict) -> Path:
        """
        Записва ПЪЛНИЯ verification dict в temp/ — за crash recovery.
        Извиква се веднага след всяко _verify(). Ако crash-не, файлът
        остава и може да бъде прочетен без нова Sol заявка.
        """
        safe_id = item_id.replace(".", "_")
        folder = self.dir / safe_id / "temp"
        folder.mkdir(parents=True, exist_ok=True)
        filepath = folder / f"attempt-{attempt_num:02d}-{label}-verify.json"
        _atomic_write(filepath, json.dumps(verification, ensure_ascii=False, indent=2))
        return filepath

    def _extract_summary_section(self, article_md: str) -> str:
        r"""
        Извлича първите 2 секции от статията за text.md.

        Използва article_header_pattern от CONFIG. Паттернът ТРЯБВА да има
        capture group за заглавието, напр. r'(?m)^##\s+(\d+\.\s*[^\n]+)'.
        Ако няма capture group, fallback-ва към split-а без headers.
        """
        pattern = CONFIG.get("article_header_pattern", r"(?m)^##\s+(\d+\.\s*[^\n]+)")

        # Използваме finditer, за да запазим и позициите, и заглавията
        matches = list(re.finditer(pattern, article_md))
        if not matches:
            words = article_md.split()
            if len(words) <= 400:
                return article_md
            return " ".join(words[:400]) + "..."

        # Разделяме на секции ръчно (finditer → между началото на match i+1)
        sections = []
        for i, m in enumerate(matches):
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(article_md)
            body = article_md[start:end].strip()

            # Ако pattern-ът има capture group, ползвай го; иначе вземи целия match
            if m.groups():
                title = m.group(1).strip()
            else:
                # Fallback: вземи текста след ## и до края на реда
                title = re.sub(r"^[#\s]+", "", m.group(0)).strip()

            sections.append((title, body))

        # Вземи първите 2 секции
        out = []
        for title, body in sections[:2]:
            out.append(f"## {title}\n{body}")

        summary = "\n".join(out).strip()
        if summary:
            return summary

        words = article_md.split()
        if len(words) <= 400:
            return article_md
        return " ".join(words[:400]) + "..."

    def write(self, item: QueueItem, parsed: dict) -> Path:
        safe_id = item.id.replace(".", "_")
        folder = self.dir / safe_id
        folder.mkdir(exist_ok=True)

        v = len(list(folder.glob("text-v*.md"))) + 1
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        title = parsed.get("title", item.title)
        article_md = parsed.get("article_markdown", "").strip()
        word_count = parsed.get("word_count", len(article_md.split()))
        learning_objectives = parsed.get("learning_objectives", [])
        common_mistakes = parsed.get("common_mistakes", [])
        self_quiz = parsed.get("self_quiz", [])

        gen_model = CONFIG["generator"]["model"]
        ver_model = CONFIG["verifier"]["model"] if CONFIG.get("enable_verification") else None

        # 1. text.md — кратко резюме
        summary_md = f"""# {title}

**ID:** `{item.id}`
**Източник:** {item.source}
**Генерирано:** {ts}
**Версия:** v{v}
**Думи:** {word_count}

---

{self._extract_summary_section(article_md)}
"""
        (folder / f"text-v{v}.md").write_text(summary_md, encoding="utf-8")
        (folder / "text.md").write_text(summary_md, encoding="utf-8")

        # 2. deep.md
        if article_md:
            deep_md = f"""# {title} — Пълна статия

**ID:** `{item.id}`
**Генерирано:** {ts}
**Версия:** v{v}
**Думи:** {word_count}
**Generator:** {gen_model}
**Verifier:** {ver_model or 'disabled'}

---

{article_md}
"""
            (folder / f"deep-v{v}.md").write_text(deep_md, encoding="utf-8")
            (folder / "deep.md").write_text(deep_md, encoding="utf-8")

        # 3. metadata.json
        meta = {
            "title": title,
            "point_id": item.id,
            "generated_at": ts,
            "version": v,
            "word_count": word_count,
            "learning_objectives": learning_objectives,
            "common_mistakes": common_mistakes,
            "self_quiz": self_quiz,
            "generator_model": gen_model,
            "verifier_model": ver_model if item.verification else None,
        }
        (folder / "metadata.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        # 4. verify.md + verify-vN.json
        if item.verification:
            self._write_verification(folder, item, ts, v)

        log.info(f"[{item.id}] Записано: {folder.relative_to(BASE_DIR.parent)} ({word_count} думи)")
        return folder

    def _write_verification(self, folder: Path, item: QueueItem, ts: str, v: int):
        vf = item.verification
        ver_model = CONFIG["verifier"]["model"]

        strengths = "\n".join(f"- {s}" for s in vf.get("strengths", [])) or "-"
        issues = "\n".join(
            f"- [{i.get('severity','?')}] **{i.get('section','')}**: {i.get('description','')}"
            for i in vf.get("issues", [])
        ) or "-"
        math_err = "\n".join(
            f"- `{m.get('formula','')}` — {m.get('problem','')} → {m.get('fix','')}"
            for m in vf.get("math_errors", [])
        ) or "-"
        missing = "\n".join(f"- {m}" for m in vf.get("missing_topics", [])) or "-"
        suggestions = "\n".join(f"- {s}" for s in vf.get("suggestions", [])) or "-"

        verify_md = f"""# Verification report — {item.title}

**ID:** `{item.id}`
**Дата:** {ts}
**Verifier:** {ver_model}

## Verdict: {vf.get('verdict', '?')} — Score: {vf.get('score', '?')}/10

**Reasoning:** {vf.get('verdict_reasoning', '—')}

## Strengths
{strengths}

## Issues
{issues}

## Math errors
{math_err}

## Missing topics
{missing}

## Suggestions
{suggestions}
"""
        (folder / "verify.md").write_text(verify_md, encoding="utf-8")
        vf_with_model = dict(vf, _model=ver_model)
        (folder / f"verify-v{v}.json").write_text(
            json.dumps(vf_with_model, ensure_ascii=False, indent=2), encoding="utf-8"
        )


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def find_html_path(cli_path: Optional[str] = None) -> Optional[Path]:
    candidates = []
    if cli_path:
        candidates.append(Path(cli_path).resolve())
    if CONFIG.get("html_path"):
        cfg_path = Path(CONFIG["html_path"])
        if not cfg_path.is_absolute():
            cfg_path = (BASE_DIR / cfg_path).resolve()
        candidates.append(cfg_path)
    candidates.extend([
        BASE_DIR / "index.html",
        BASE_DIR.parent / "index.html",
        BASE_DIR.parent.parent / "index.html",
        Path.cwd() / "index.html",
    ])
    for c in candidates:
        if c and c.exists() and c.is_file():
            return c
    return None


# ═══════════════════════════════════════════════════════════════
# PIPELINE
# ═══════════════════════════════════════════════════════════════
class Pipeline:
    def __init__(self, html_path: Optional[Path] = None, only_id: Optional[str] = None):
        self.state = State()
        self.queue = Queue()
        self.generator = AIClient(CONFIG["generator"], name="gen")
        self.verifier = (
            AIClient(CONFIG["verifier"], name="ver")
            if CONFIG.get("enable_verification") and CONFIG["verifier"].get("api_key")
            else None
        )
        self.writer = Writer()
        self.running = True
        self.processed_count = 0
        self.error_count = 0
        self.html_path = html_path
        self.only_id = only_id
        self.scan_enabled = AUTO_SCAN_AVAILABLE and CONFIG.get("auto_scan", True)

        self._html_cache: Optional[str] = None
        self._steps_ids: Optional[list] = None
        self.progress_file = BASE_DIR / "progress.json"
        self._session_started = datetime.now().isoformat()

        if self.verifier is None and CONFIG.get("enable_verification"):
            log.warning("Verification е включена, но липсва api_key — пропускам верификация")

        if self.scan_enabled and not self.html_path:
            self.html_path = find_html_path()
            if self.html_path:
                log.info(f"Auto-scan: HTML намерен → {self.html_path}")
            else:
                log.warning("Auto-scan: HTML НЕ е намерен. Ползвай --html")
        elif not AUTO_SCAN_AVAILABLE:
            log.warning("Auto-scan: scan_queue.py липсва — само ръчен queue")

    def stop(self, signum=None, frame=None):
        log.info("Получен SIGTERM/SIGINT — спирам след текущите задачи...")
        self.running = False

    def _load_progress(self) -> dict:
        """Чете progress.json — за resume след crash."""
        if not self.progress_file.exists():
            return {}
        try:
            return json.loads(self.progress_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save_progress(self, **updates) -> None:
        """Атомарно обновява progress.json. Merge-ва с текущия."""
        data = self._load_progress()
        data.setdefault("session_started", self._session_started)
        data["updated_at"] = datetime.now().isoformat()
        data.update(updates)
        _atomic_write(self.progress_file, json.dumps(data, indent=2, ensure_ascii=False))

    def _detect_and_recover_interrupted(self) -> list:
        """
        На старт: намира items със status 'running' в state.json (значи crash).
        Reset-ва ги на 'pending' и логва какво е било прекъснато.
        """
        interrupted = [
            pid for pid, data in self.state.data.get("processed", {}).items()
            if data.get("status") == "running"
        ]
        progress = self._load_progress()
        if interrupted:
            log.warning("═" * 60)
            log.warning(f"⚠ Открити {len(interrupted)} прекъснати items от предишна сесия:")
            for pid in interrupted:
                safe_id = pid.replace(".", "_")
                temp_dir = BASE_DIR.parent / "generated" / "articles" / safe_id / "temp"
                temp_files = list(temp_dir.glob("attempt-*.md")) if temp_dir.exists() else []
                verify_files = list(temp_dir.glob("attempt-*-verify.json")) if temp_dir.exists() else []

                best_score = None
                for tf in temp_files:
                    try:
                        head = tf.read_text(encoding="utf-8")[:500]
                        m = re.search(r'\*\*Score:\*\*\s*(\d+)/10', head)
                        if m:
                            sc = int(m.group(1))
                            if best_score is None or sc > best_score:
                                best_score = sc
                    except Exception:
                        pass

                hint = f" (best score: {best_score})" if best_score is not None else ""
                log.warning(f"   • {pid}: {len(temp_files)} статии, "
                            f"{len(verify_files)} verify JSON-а{hint}")
                if temp_files:
                    for tf in temp_files:
                        log.warning(f"       → {tf.relative_to(BASE_DIR.parent)}")
                log.warning(f"     💡 За възстановяване без нова генерация:")
                log.warning(f"        python recover_point.py {pid}")
                self.state.mark(pid, "pending")
            log.warning("  Дефинирани като pending → ще опита отново.")
            log.warning("═" * 60)

        step = progress.get("step")
        if step:
            log.info(f"📍 Предишна стъпка при crash: {step}")

        if progress.get("updated_at"):
            last_done = progress.get("last_completed", {})
            if last_done:
                log.info(f"📋 Предишна сесия: последно завършено {last_done.get('id')} "
                         f"({last_done.get('at')}, score {last_done.get('score')})")
            log.info(f"📋 Предишна сесия: обновено {progress['updated_at']}")

        return interrupted

    # ─── HTML / STEPS ───
    def _get_html(self) -> Optional[str]:
        if self._html_cache is None:
            if not self.html_path or not self.html_path.exists():
                return None
            try:
                self._html_cache = self.html_path.read_text(encoding="utf-8")
            except Exception as e:
                log.warning(f"Не мога да прочета HTML: {e}")
                return None
        return self._html_cache

    def _get_steps_ids(self) -> list:
        if self._steps_ids is not None:
            return self._steps_ids
        steps_js = BASE_DIR.parent / "data" / "steps.js"
        text = steps_js.read_text(encoding="utf-8") if steps_js.exists() else (self._get_html() or "")
        if not text:
            return []
        raw_ids = re.findall(r'\{\s*id\s*:\s*"([^"]+)"', text)
        self._steps_ids = [i for i in raw_ids if re.match(r'^(\d+\.\d+|R\.\d+)$', i)]
        return self._steps_ids

    def try_scan(self, reason: str = "manual") -> int:
        if not self.scan_enabled or not self.html_path or not self.html_path.exists():
            return 0
        try:
            pdf_root = None
            if CONFIG.get("pdf_root"):
                pdf_root = Path(CONFIG["pdf_root"])
                if not pdf_root.is_absolute():
                    pdf_root = (BASE_DIR / pdf_root).resolve()
            stats = scan_and_merge(
                html_path=self.html_path,
                queue_path=BASE_DIR / "queue.jsonl",
                pdf_root=pdf_root,
                only_with_pdf=CONFIG.get("scan_only_with_pdf", False),
                skip_with_explanation=CONFIG.get("scan_skip_with_explanation", True),
                dry_run=False,
            )
            added = stats.get("added", 0)
            if added > 0:
                log.info(f"[scan/{reason}] ➕ Добавени {added} нови items в queue")
                self.queue.reload()
                self._html_cache = None
                self._steps_ids = None
            return added
        except Exception as e:
            log.error(f"[scan/{reason}] Грешка: {e}", exc_info=True)
            return 0

    # ─── JSON parsing ───
    def _parse_json(self, text: str) -> Optional[dict]:
        if not text:
            return None
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```\s*$', '', text).strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        start, end = text.find('{'), text.rfind('}')
        if start == -1 or end == -1 or end <= start:
            return None
        candidate = text[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            fixed = re.sub(r',\s*([}\]])', r'\1', candidate)
            try:
                return json.loads(fixed)
            except Exception:
                return None

    # ─── Prompt loading ───
    def _load_real_problems(self, point_id: str) -> str:
        real_file = BASE_DIR.parent / "generated" / "anchors" / f"{point_id.replace('.', '_')}.json"
        if not real_file.exists():
            return ("(няма заредени реални задачи — генерирай по темата, "
                    "но маркирай ясно примерите като '**Пример (типичен, не от минала олимпиада):**')")
        try:
            all_problems = json.loads(real_file.read_text(encoding="utf-8")).get("problems", [])
        except Exception as e:
            log.warning(f"[{point_id}] real_problems read fail: {e}")
            return "(грешка при четене — генерирай по темата)"

        try:
            from pdf_chunker import _validate_problem
        except ImportError:
            _validate_problem = lambda p: (True, "ok")

        valid = [p for p in all_problems if _validate_problem(p)[0]]
        if not valid:
            return ("(няма валидни реални задачи с решения — генерирай типични примери, "
                    "но ВСЕКИ пример маркирай ясно с '**Пример (типичен, не от минала олимпиада):**')")

        max_real = CONFIG.get("max_real_problems", 8)
        trunc = CONFIG.get("real_problem_truncation", {})
        stmt_chars = trunc.get("statement_chars", 1200)
        sol_chars = trunc.get("solution_chars", 3500)

        # не режи решения: предпочитай задачи, които се побират цели
        fit = [p for p in valid
               if len(p.get("statement") or "") <= stmt_chars
               and len(p.get("solution") or "") <= sol_chars]
        pool = fit or valid
        by_diff = {"easy": [], "medium": [], "hard": []}
        for p in pool:
            by_diff.get(p.get("difficulty"), by_diff["medium"]).append(p)
        picked = []
        for d, q in (("easy", 3), ("medium", 3), ("hard", 2)):
            picked += by_diff[d][:q]
        for p in pool:
            if len(picked) >= max_real:
                break
            if p not in picked:
                picked.append(p)
        picked = picked[:max_real]

        lines = []
        for i, p in enumerate(picked, 1):
            lines.append(
                f"  {i}. [{p.get('source', '?')}]\n"
                f"     Условие: {(p.get('statement') or '')[:stmt_chars]}\n"
                f"     Реално решение (ИЗПОЛЗВАЙ ГО КАТО КОПИЕ):\n"
                f"     {(p.get('solution') or '')[:sol_chars]}"
            )
        log.info(f"[{point_id}] {len(valid)} валидни real problems (от {len(all_problems)}, показвам {min(max_real, len(valid))})")
        return "\n\n".join(lines)

    def _load_prereqs(self, point_id: str) -> str:
        html = self._get_html()
        if not html:
            return "(няма)"
        try:
            m = re.search(r'const\s+PREREQS\s*=\s*\{(.*?)\n?\};', html, re.DOTALL)
            if not m:
                return "(няма)"
            p = re.search(r'"' + re.escape(point_id) + r'"\s*:\s*\[([^\]]*)\]', m.group(1))
            if not p:
                return "(няма)"
            ids = re.findall(r'"([^"]+)"', p.group(1))
            return ", ".join(ids) if ids else "(няма)"
        except Exception as e:
            log.debug(f"[{point_id}] prereqs read fail: {e}")
            return "(няма)"

    def _load_source_problems(self, item: QueueItem) -> str:
        trunc = CONFIG.get("source_problem_truncation", {})
        expl_chars = trunc.get("explanation_chars", 1500)
        desc_chars = trunc.get("desc_chars", 800)
        if item.explanation:
            return item.explanation[:expl_chars]
        if item.desc:
            return item.desc[:desc_chars]
        return "(няма)"

    def _load_next_topic(self, point_id: str) -> str:
        ids = self._get_steps_ids()
        if not ids:
            return "(няма)"
        try:
            idx = ids.index(point_id)
            return ids[idx + 1] if idx + 1 < len(ids) else "(няма)"
        except ValueError:
            return "(няма)"

    # ─── Verification ───
    def _verify(self, item, article_markdown: str):
        if self.verifier is None:
            return None, 0.0
        user = format_prompt(
            ARTICLE_VERIFICATION_PROMPT,
            title=item.title,
            point_id=item.id,
            desc=item.desc or "(няма описание)",
            article_markdown=article_markdown or "(няма статия)",
        )
        text, tokens, cost = self.verifier.call(ARTICLE_REVIEWER, user, item.id, force_json=True)
        if text is None:
            log.warning(f"[{item.id}] Верификация неуспешна (API) — продължавам без нея")
            return None, cost

        # Empty response — retry once with truncated article (reasoning loop / max_tokens hit)
        if not text.strip():
            log.warning(f"[{item.id}] Verifier върна празен отговор — retry със съкратена статия")
            if len(article_markdown) > 10000:
                short_article = article_markdown[:10000] + "\n\n[...съкратено за верификация...]"
                short_user = format_prompt(
                    ARTICLE_VERIFICATION_PROMPT,
                    title=item.title,
                    point_id=item.id,
                    desc=item.desc or "(няма описание)",
                    article_markdown=short_article,
                )
                text, tokens2, cost2 = self.verifier.call(
                    ARTICLE_REVIEWER, short_user, item.id, force_json=True
                )
                cost += cost2
                tokens += tokens2
                if not text or not text.strip():
                    log.error(f"[{item.id}] Verifier пак празен — пропускам верификация")
                    return None, cost
            else:
                log.error(f"[{item.id}] Verifier празен и без съкращаване — пропускам")
                return None, cost

        parsed = self._parse_json(text)
        if parsed is None:
            log.warning(f"[{item.id}] Verifier JSON парсване неуспешно")
            log.warning(f"[{item.id}] Verifier RAW (first 800): {text[:800]!r}")
            return None, cost
        parsed["_tokens"] = tokens
        return parsed, cost

    def _format_feedback(self, vf: dict) -> str:
        lines = [f"ОЦЕНКА: {vf.get('score', '?')}/10 — {vf.get('verdict', '?')}"]
        lines.append(f"ПРИЧИНА: {vf.get('verdict_reasoning', '—')}")
        if vf.get("math_errors"):
            lines.append("\nМАТЕМАТИЧЕСКИ ГРЕШКИ (ЗАДЪЛЖИТЕЛНО ПОПРАВИ):")
            for err in vf["math_errors"]:
                lines.append(f"  • {err.get('formula','')}: {err.get('problem','')} → {err.get('fix','')}")
        if vf.get("issues"):
            lines.append("\nПРОБЛЕМИ:")
            for iss in vf["issues"]:
                lines.append(f"  • [{iss.get('severity','?')}] {iss.get('section','')}: {iss.get('description','')}")
        if vf.get("missing_topics"):
            lines.append("\nЛИПСВАЩИ ТЕМИ:")
            for m in vf["missing_topics"]:
                lines.append(f"  • {m}")
        if vf.get("suggestions"):
            lines.append("\nПРЕДЛОЖЕНИЯ:")
            for s in vf["suggestions"]:
                lines.append(f"  • {s}")
        return "\n".join(lines)

    # ─── Retry prompt builders ───
    def _compute_sections_min(self, min_target: int) -> tuple[int, int]:
        """
        Изчислява per-section минимум, който ГАРАНТИРА че сумата >= min_target.

        Връща (sections_min, total_sections).

        Проблемът с naive (9 × 250 = 2250 < 2800) е решен чрез ceil division:
            computed = ceil(min_target / total_sections)
            sections_min = max(configured_min, computed)
        """
        struct = CONFIG.get("article_structure", {})
        configured_min = struct.get("min_words_per_section", 300)
        total_sections = struct.get("total_sections", 9)
        computed = (min_target + total_sections - 1) // total_sections
        return max(configured_min, computed), total_sections

    def _build_improve_prompt(self, gen_user, article_md, actual_wc, min_target, max_target, feedback):
        """
        IMPROVE prompt — моделът ЗАПАЗВА статията и я РАЗШИРЯВА.

        Разлики от v6:
          • per-section минимум е ceil(2800/9) = 312, не 250 (иначе 2250 < 2800)
          • expand_ranges идва от CONFIG, не е hardcoded
        """
        word_deficit = max_target - actual_wc
        struct = CONFIG.get("article_structure", {})
        expand_ranges = struct.get("expand_ranges", "3.1-3.6, 4.1-4.3")
        sections_min, total_sections = self._compute_sections_min(min_target)

        # Handle negative deficit (статията е по-дълга от max_target)
        if word_deficit > 0:
            deficit_line = f"ЛИПСВАТ ~{word_deficit} думи."
            deficit_action = f"Трябва да ДОБАВИШ ~{word_deficit} думи."
        else:
            deficit_line = f"Статията е с {abs(word_deficit)} думи НАД меката цел."
            deficit_action = (
                f"ПРИОРИТЕТ: поправи проблемите от одита. Дължината е ВТОРИЧНА. "
                f"Статия от 4000-5500 думи е напълно приемлива, стига да е плътна. "
                f"Ако трябва да избираш между 'поправи грешка' и 'съкрати', "
                f"ВИНАГИ поправяй грешката. НЕ добавяй нови секции без причина, "
                f"но и НЕ съкращавай насила — ако е дълга, нека е дълга."
            )

        return gen_user + f"""

═══ ПРЕДИШНАТА ТИ СТАТИЯ ═══
(Текуща дължина: {actual_wc} думи. ЦЕЛ: {min_target}-{max_target} думи.
{deficit_line})

{article_md}

═══ ОДИТ ОТ РЕЦЕНЗЕНТ ═══

{feedback}

═══ ТВОЯТА ЗАДАЧА ═══

ТОВА Е РАЗШИРЯВАНЕ, НЕ ПРЕПИСВАНЕ.

⚠️ КРИТИЧНО: Статията е с {actual_wc} думи, но трябва да е {min_target}-{max_target}.
{deficit_action}

КАК ДА ПОПРАВИШ (не разширявай изкуствено):
1. Поправи ВСЯКА формула или стъпка, посочена в одита
2. Ако липсва пример — добави САМО ако имаш реален от real_problems,
   иначе добави typical, изрично маркиран
3. Ако одитът казва "неясно" — препиши САМО тази част, не цялата секция
4. Запази дължината — не добавяй пълнеж, не изхвърляй съществено

ЗАПАЗИ цялата структура и съдържание на предишната статия.
ДОБАВИ към нея, не я преписвай.

ТОВА Е РЕВИЗИЯ, НЕ ПРЕПИСВАНЕ. Надгради върху предишната статия:
1. ЗАПАЗИ всичко, което работи
2. ПОПРАВИ само проблемите, посочени в одита
3. РАЗШИРИ секциите, които са твърде кратки
4. ДОБАВИ липсващите теми
5. ИЗТРИЙ само очевидно сгрешеното

НЕ започвай от нулата.
Целева дължина: {min_target}-{max_target} думи. Всяка от {total_sections}-те секции минимум {sections_min} думи.

Върни САМО новия JSON.
"""

    def _build_regen_prompt(self, gen_user, article_md, actual_wc, feedback):
        """
        REGEN prompt — моделът пише ОТ НУЛАТА, но ВИЖДА предишната статия.

        Ключови разлики от v6:
          1. Включва article_md като контекст (не започва сляпо)
          2. Изрична инструкция "не копирай" (за да не дублира грешки)
          3. Правилен per-section минимум (ceil, не hardcoded 250)
          4. Self-check преди връщане (моделът брои думите си)
        """
        min_target = CONFIG.get("target_word_count_min", 2800)
        max_target = CONFIG.get("target_word_count_max", 3400)
        struct = CONFIG.get("article_structure", {})
        expand_ranges = struct.get("expand_ranges", "3.1-3.6, 4.1-4.3")
        sections_min, total_sections = self._compute_sections_min(min_target)

        word_deficit = max_target - actual_wc
        deficit_text = (
            f"липсват ~{word_deficit}" if word_deficit > 0
            else "над лимита — преценявай"
        )

        return gen_user + f"""

═══ ПРЕДИШЕН ОПИТ (КОНТЕКСТ — НЕ КОПИРАЙ) ═══

Предишната ти статия беше САМО {actual_wc} думи.
ЦЕЛ: {min_target}-{max_target} думи ({deficit_text}).

Ето я за референция — какво си написал преди:

---НАЧАЛО НА ПРЕДИШНАТА СТАТИЯ---
{article_md}
---КРАЙ НА ПРЕДИШНАТА СТАТИЯ---

═══ ОДИТ ОТ РЕЦЕНЗЕНТ ═══

{feedback}

═══ ТВОЯТА ЗАДАЧА ═══

НАПИШИ НОВА СТАТИЯ ОТ НУЛАТА.
НЕ копирай предишната — тя е твърде кратка ({actual_wc} < {min_target}) и има проблеми от одита.
Но я прегледай — за да знаеш какво НЕ правиш отново.

⚠️ ЗАДЪЛЖИТЕЛНА ДЪЛЖИНА:

  • ОБЩО: минимум {min_target} думи (максимум {max_target})
  • Секции {expand_ranges}: минимум {sections_min} думи ВСЯКА
  • Общо {total_sections} секции — не сливай, не съкращавай

КАК ДА ПОСТИГНЕШ ДЪЛЖИНАТА:

  1. Всяка формула → обясни "Защо работи" (2-3 изречения контекст)
  2. Всяка теорема → 2 конкретни примера с числа
  3. Всяка техника → кога НЕ работи (edge cases)
  4. Всяка секция → завърши с "Чести грешки в тази секция"
  5. Свържи темите → как тази техника се отнася към предишни/следващи

ПРЕДИ ДА ВЪРНЕШ — ПРОВЕРИ:

  ✓ Преброй думите в article_markdown.
    Ако < {min_target} → ПРОДЪЛЖИ ДА ПИШЕШ. Не връщай къса статия.
  ✓ Провери всяка секция {expand_ranges} е >= {sections_min} думи.
  ✓ Провери няма празни секции, "TBD", "...", "оставям за читателя".
  ✓ Провери няма съкратени доказателства ("очевидно е", "лесно се вижда").

Върни САМО JSON с поле article_markdown.
"""

    # ─── Generation + verification loop ───
    def _generate_and_verify(self, item, gen_user):
        """
        Прави generation + verification с retry loop.

        Връща (parsed, article_md, verification, total_cost, total_tokens, err).
        err = None при успех.
        """
        min_target = CONFIG.get("target_word_count_min", 2800)
        max_target = CONFIG.get("target_word_count_max", 3400)
        min_acceptable = CONFIG.get("min_word_count", 2500)

        # 💾 Snapshot на стъпката — за crash диагностика
        self._save_progress(in_flight=[item.id], step="generating_initial")
        text, tokens, cost = self.generator.call(ARTICLE_WRITER, gen_user, item.id, force_json=True)
        if text is None:
            return None, None, None, cost, tokens, "Generator не върна отговор"

        parsed = self._parse_json(text)
        if parsed is None:
            return None, None, None, cost, tokens, "JSON парсване неуспешно"

        article_md = parsed.get("article_markdown", "").strip()
        if not article_md:
            return None, None, None, cost, tokens, "AI не върна article_markdown"

        actual_wc = len(article_md.split())
        parsed["word_count"] = actual_wc

        # 💾 Запази в temp ВЕДНАГА — преди verification и преди retry-и,
        # за да не се загуби статията ако бюджетът свърши по средата.
        self.writer.save_attempt(
            item.id, attempt_num=1, article_md=article_md,
            word_count=actual_wc, score=None, verdict=None, label="initial"
        )

        if actual_wc < min_acceptable:
            log.warning(f"[{item.id}] ⚠ Статията е само {actual_wc} думи (цел: {min_target}-{max_target})")
        elif actual_wc > max_target + 500:
            log.warning(f"[{item.id}] ⚠ Статията е {actual_wc} думи (над {max_target})")
        else:
            log.info(f"[{item.id}] Статия: {actual_wc} думи")

        total_cost, total_tokens = cost, tokens
        verification = None

        if self.verifier is not None:
            self._save_progress(in_flight=[item.id], step="verifying_initial")
            verification, ver_cost = self._verify(item, article_md)
            total_cost += ver_cost
            if verification:
                total_tokens += verification.get("_tokens", 0)

                # 💾 Обнови temp файла с резултата от верификацията
                self.writer.save_attempt(
                    item.id, attempt_num=1, article_md=article_md,
                    word_count=actual_wc,
                    score=verification.get("score"),
                    verdict=verification.get("verdict"),
                    label="initial"
                )
                # 💾 И запази ПЪЛНИЯ verification dict — оцелява при crash
                self.writer.save_verification(
                    item.id, attempt_num=1, label="initial",
                    verification=verification
                )

                # Fallback matches DEFAULT_CONFIG (0.3), not 0.7
                improve_threshold = int(min_acceptable * CONFIG.get("improve_threshold_pct", 0.3))

                for retry in range(CONFIG["max_verification_retries"]):
                    score = verification.get("score", 10)
                    if score >= CONFIG["min_verification_score"]:
                        break
                    use_improve = actual_wc >= improve_threshold
                    log.info(
                        f"↻ [{item.id}] retry (score {score}, "
                        f"{'IMPROVE' if use_improve else 'REGEN'}) — "
                        f"опит {retry + 1}/{CONFIG['max_verification_retries']}"
                    )
                    feedback = self._format_feedback(verification)

                    retry_prompt = (
                        self._build_improve_prompt(gen_user, article_md, actual_wc, min_target, max_target, feedback)
                        if use_improve
                        else self._build_regen_prompt(gen_user, article_md, actual_wc, feedback)
                    )

                    self._save_progress(
                        in_flight=[item.id],
                        step=f"retry_{retry + 1}_generating",
                    )
                    text2, tokens2, cost2 = self.generator.call(
                        ARTICLE_WRITER, retry_prompt, item.id, force_json=True
                    )
                    if text2 is None:
                        break
                    p2 = self._parse_json(text2)
                    if p2 is None or not p2.get("article_markdown", "").strip():
                        break

                    # Store current (best) state before evaluating retry
                    prev_parsed = parsed
                    prev_article_md = article_md
                    prev_wc = actual_wc
                    prev_verification = verification
                    prev_score = verification.get("score", 0) if verification else 0

                    # Evaluate retry
                    new_wc = len(p2["article_markdown"].strip().split())
                    p2["word_count"] = new_wc

                    # 💾 Запази retry опита в temp — преди verification
                    self.writer.save_attempt(
                        item.id, attempt_num=retry + 2,
                        article_md=p2["article_markdown"].strip(),
                        word_count=new_wc, score=None, verdict=None,
                        label=f"retry-{retry + 1}"
                    )

                    self._save_progress(
                        in_flight=[item.id],
                        step=f"retry_{retry + 1}_verifying",
                    )
                    new_verification, ver_cost = self._verify(item, p2["article_markdown"].strip())
                    total_cost += cost2 + ver_cost
                    total_tokens += tokens2
                    if new_verification is None:
                        log.warning(f"[{item.id}] Retry verification failed — keeping previous article")
                        parsed, article_md, actual_wc, verification = (
                            prev_parsed, prev_article_md, prev_wc, prev_verification
                        )
                        break
                    total_tokens += new_verification.get("_tokens", 0)

                    # 💾 Обнови retry temp файла с score
                    self.writer.save_attempt(
                        item.id, attempt_num=retry + 2,
                        article_md=p2["article_markdown"].strip(),
                        word_count=new_wc,
                        score=new_verification.get("score"),
                        verdict=new_verification.get("verdict"),
                        label=f"retry-{retry + 1}"
                    )
                    # 💾 И запази ПЪЛНИЯ verification dict за retry
                    self.writer.save_verification(
                        item.id, attempt_num=retry + 2,
                        label=f"retry-{retry + 1}",
                        verification=new_verification
                    )

                    new_score = new_verification.get("score", 0)
                    # Дължината е ВТОРИЧНА. Основен критерий е score.
                    def is_reasonable_length(wc):
                        # 2600-5500 е ОК. Само абсурдно къси/дълги се отхвърлят.
                        return 2600 <= wc <= 5500

                    keep_retry = (
                        new_score > prev_score or
                        (new_score == prev_score and is_reasonable_length(new_wc)
                         and not is_reasonable_length(prev_wc)) or
                        (new_score == prev_score and is_reasonable_length(new_wc)
                         and is_reasonable_length(prev_wc)
                         and abs(new_wc - 3100) < abs(prev_wc - 3100))
                    )
                    # Ако new_score > prev_score → ВИНАГИ приемай, дори при лоша дължина
                    if keep_retry:
                        parsed = p2
                        article_md = p2["article_markdown"].strip()
                        actual_wc = new_wc
                        verification = new_verification
                        log.info(f"[{item.id}] Retry accepted: {prev_score}→{new_score}, {prev_wc}→{new_wc}w")
                    else:
                        parsed = prev_parsed
                        article_md = prev_article_md
                        actual_wc = prev_wc
                        verification = prev_verification
                        log.info(f"[{item.id}] Retry rejected: {prev_score}→{new_score}, keeping {prev_wc}w")

        return parsed, article_md, verification, total_cost, total_tokens, None

    def process_item(self, item: QueueItem) -> bool:
        if self.state.budget_exceeded():
            log.warning(f"Бюджет достигнат (${self.state.stats()['today_spent']:.3f})")
            return False

        item.status = "running"
        item.attempts += 1
        item.started_at = time.time()
        log.info(f"▶ [{item.id}] {item.title} (опит {item.attempts})")

        # 💾 Persist 'running' status → crash detection при следващ старт
        self.state.mark(item.id, "running", attempts=item.attempts)
        self._save_progress(in_flight=[item.id])

        gen_user = format_prompt(
            ARTICLE_PROMPT,
            title=item.title,
            point_id=item.id,
            desc=item.desc or "(няма описание)",
            prereqs=self._load_prereqs(item.id),
            source_problems=self._load_source_problems(item),
            real_problems=self._load_real_problems(item.id),
            next_topic=self._load_next_topic(item.id),
        )

        parsed, article_md, verification, cost, tokens, err = self._generate_and_verify(item, gen_user)
        if err is not None:
            item.status = "error"
            item.error = err
            self.error_count += 1
            self.state.mark(item.id, "error")
            self._save_progress(
                in_flight=[],
                last_completed={
                    "id": item.id,
                    "at": datetime.now().isoformat(),
                    "error": err,
                },
            )
            log.error(f"✗ [{item.id}] {err}")
            return False

        item.result = article_md[:800]
        item.deep_result = article_md
        item.verification = verification
        item.tokens_used = tokens
        item.cost_usd = cost
        item.status = "done"
        item.finished_at = time.time()

        self.writer.write(item, parsed)
        sc = verification.get("score") if verification else None
        verdict = verification.get("verdict") if verification else None
        low = sc is not None and sc < CONFIG["min_verification_score"]

        # 🗑️ Ако score е перфектен → изтрий temp (вече няма нужда от backup)
        perfect_threshold = CONFIG.get("perfect_score_threshold", 10)
        if perfect_threshold > 0 and sc is not None and sc >= perfect_threshold:
            self.writer.cleanup_temp(item.id)

        # 💾 Progress snapshot
        self._save_progress(
            in_flight=[],
            last_completed={
                "id": item.id,
                "at": datetime.now().isoformat(),
                "score": sc,
                "verdict": verdict,
                "word_count": len(article_md.split()),
            },
        )

        # Persist full result metadata for --report
        self.state.mark(
            item.id, "done", cost, tokens,
            score=sc,
            verdict=verdict,
            word_count=len(article_md.split()),
            generator_model=CONFIG["generator"]["model"],
            verifier_model=CONFIG["verifier"]["model"],
            attempts=item.attempts,
            math_errors=len(verification.get("math_errors", [])) if verification else 0,
            issues=len(verification.get("issues", [])) if verification else 0,
        )
        self.state.add_cost(cost, tokens)
        if low:
            log.warning(f"[{item.id}] score {sc} < {CONFIG['min_verification_score']} — записано, но с нисък score (няма auto-retry)")
        self.processed_count += 1
        
        dur = item.finished_at - item.started_at
        score = verification.get("score", "—") if verification else "—"
        verdict = verification.get("verdict", "—") if verification else "no-verify"
        log.info(f"✓ [{item.id}] {dur:.1f}s | ${cost:.4f} | {tokens} tok | score {score} ({verdict})")
        return True

    def run_once(self, allow_scan: bool = True) -> int:
        self.state.check_budget_reset()
        pending = self.queue.pending(self.state, only_id=self.only_id)

        if not pending and allow_scan and not self.only_id:
            if self.try_scan(reason="empty-queue") > 0:
                pending = self.queue.pending(self.state, only_id=self.only_id)

        if not pending:
            return 0

        batch = pending[:CONFIG["batch_size"]]
        log.info(f"Batch: {len(batch)} items | остават {len(pending) - len(batch)} | бюджет ${self.state.budget_remaining():.2f}")

        # 📋 Snapshot на какво предстои (за resume)
        self._save_progress(
            current_batch=[it.id for it in batch],
            pending_count=len(pending),
            budget_spent=self.state.stats()["today_spent"],
        )

        processed = 0
        budget_hit = False
        with ThreadPoolExecutor(max_workers=CONFIG["max_concurrent"]) as pool:
            futures = {pool.submit(self.process_item, it): it for it in batch}
            for fut in as_completed(futures):
                try:
                    if fut.result():
                        processed += 1
                except BudgetExhausted as e:
                    budget_hit = True
                    log.warning(f"⚠ Budget exhausted: {e}")
                except Exception as e:
                    it = futures[fut]
                    log.exception(f"[{it.id}] Exception: {e}")
                    self.state.mark(it.id, "error")

        if budget_hit:
            self.running = False
        return processed

    def run_forever(self):
        log.info("═" * 60)
        log.info("Pipeline стартиран 24/7")
        log.info(f"Generator:      {CONFIG['generator']['model']}")
        log.info(f"Verifier:       {CONFIG['verifier']['model'] if self.verifier else 'DISABLED'}")
        log.info(f"Бюджет/ден:     ${CONFIG['daily_budget_usd']:.2f}")
        log.info(f"Batch:          {CONFIG['batch_size']} items")
        log.info(f"Concurrent:     {CONFIG['max_concurrent']}")
        log.info(f"Auto-scan:      {'ON' if self.scan_enabled else 'OFF'}")
        if self.only_id:
            log.info(f"Point filter:   {self.only_id}")
        if self.html_path:
            log.info(f"HTML:           {self.html_path}")
        log.info("═" * 60)

        # 🚨 Crash recovery — намери прекъснати items от предишна сесия
        self._detect_and_recover_interrupted()

        self.try_scan(reason="startup")
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        empty_ticks = 0
        while self.running:
            try:
                n = self.run_once(allow_scan=False)
                if n == 0:
                    empty_ticks += 1
                    if self.scan_enabled and empty_ticks % CONFIG["scan_every_ticks"] == 0:
                        if self.try_scan(reason=f"periodic-{empty_ticks}") > 0:
                            empty_ticks = 0
                            continue
                    if empty_ticks == 1 and not self.queue.pending(self.state, only_id=self.only_id):
                        log.info("Няма pending items. Чакам нови задачи...")
                else:
                    empty_ticks = 0

                if self.state.budget_exceeded():
                    log.warning(f"⚠ {CONFIG['budget_stop_pct']*100:.0f}% от бюджета изразходван — пауза 1 час")
                    for _ in range(600):
                        if not self.running:
                            break
                        time.sleep(CONFIG["tick_interval_sec"])
                    continue

                time.sleep(CONFIG["tick_interval_sec"])
            except BudgetExhausted as e:
                log.warning(f"⚠ Budget exhausted: {e}")
                self.running = False
            except KeyboardInterrupt:
                break
            except Exception as e:
                log.exception(f"Грешка в main loop: {e}")
                time.sleep(30)

        self.print_summary()

    def print_summary(self):
        s = self.state.stats()
        log.info("═" * 60)
        log.info("КРАЙ")
        log.info(f"  Обработени тази сесия: {self.processed_count}")
        log.info(f"  Грешки тази сесия:     {self.error_count}")
        log.info(f"  Общо done:             {s['done']}")
        log.info(f"  Общо error:            {s['error']}")
        log.info(f"  Днес:                  ${s['today_spent']:.3f} / ${CONFIG['daily_budget_usd']:.2f}")
        log.info(f"  Всичко похарчено:      ${s['total_cost']:.3f}")
        log.info("═" * 60)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════
def cmd_stats():
    state = State()
    queue = Queue()
    s = state.stats()
    total = queue.total()
    pending = len(queue.pending(state))
    pct = round(s["done"] / total * 100, 1) if total else 0
    print()
    print("═" * 55)
    print(f"  QUEUE:      {total} общо | {pending} pending | {s['done']} done ({pct}%)")
    print(f"  ERRORS:     {s['error']}")
    print(f"  ДНЕС:       ${s['today_spent']:.4f} / ${CONFIG['daily_budget_usd']:.2f}")
    print(f"  ДНЕС calls: {s['today_calls']}")
    print(f"  TOTAL:      ${s['total_cost']:.4f}")
    print("═" * 55)
    print()


def cmd_report():
    """Показва таблица с резултатите от всички обработени статии."""
    state = State()
    procs = state.data.get("processed", {})

    if not procs:
        print("Няма обработени статии.")
        return

    # Sort by score descending, then by id
    rows = []
    for pid, data in procs.items():
        if data.get("status") != "done":
            continue
        rows.append({
            "id": pid,
            "score": data.get("score"),
            "verdict": data.get("verdict", "?"),
            "wc": data.get("word_count"),
            "attempts": data.get("attempts"),
            "cost": data.get("cost", 0),
            "math_err": data.get("math_errors", 0),
            "issues": data.get("issues", 0),
            "gen": (data.get("generator_model") or "?").split("/")[-1],
        })

    if not rows:
        print("Няма завършени статии.")
        return

    # Sort by score ascending (worst first — to prioritize fixes)
    rows.sort(key=lambda r: (r["score"] or 0, r["id"]))

    print()
    print("═" * 95)
    print(f"  PIPELINE REPORT — {len(rows)} статии")
    print("═" * 95)
    print(f"  {'ID':<6} {'Score':>5} {'Verdict':<8} {'Words':>6} {'Att':>4} {'Cost':>8} {'MathErr':>7} {'Issues':>6} {'Gen':<20}")
    print("─" * 95)

    total_cost = 0
    total_words = 0
    low_scores = []
    with_math_errors = []

    for r in rows:
        score_str = f"{r['score']}/10" if r["score"] is not None else "—"
        wc_str = str(r["wc"]) if r["wc"] is not None else "—"
        cost_str = f"${r['cost']:.4f}"
        math_str = f"❌ {r['math_err']}" if r["math_err"] else "✓"
        issues_str = str(r["issues"])

        att_str = str(r['attempts']) if r['attempts'] is not None else "—"
        print(f"  {r['id']:<6} {score_str:>5} {r['verdict']:<8} {wc_str:>6} {att_str:>4} {cost_str:>8} {math_str:>7} {issues_str:>6} {r['gen']:<20}")

        total_cost += r["cost"]
        if r["wc"]:
            total_words += r["wc"]
        if r["score"] is not None and r["score"] < CONFIG["min_verification_score"]:
            low_scores.append((r["id"], r["score"]))
        if r["math_err"]:
            with_math_errors.append(r["id"])

    print("─" * 95)
    print(f"  ОБЩО: {len(rows)} статии | ${total_cost:.4f} | {total_words} думи | ~{total_words // len(rows) if rows else 0} думи/статия")
    print()

    if low_scores:
        print(f"  ⚠ Score < {CONFIG['min_verification_score']}: {len(low_scores)} статии")
        for pid, sc in low_scores:
            print(f"      {pid} — score {sc}")
        print()

    if with_math_errors:
        print(f"  ❌ Math errors: {len(with_math_errors)} статии")
        for pid in with_math_errors:
            print(f"      {pid}")
        print()

    # Score distribution
    dist = {}
    for r in rows:
        if r["score"] is not None:
            dist[r["score"]] = dist.get(r["score"], 0) + 1
    if dist:
        print("  Score distribution:")
        for sc in sorted(dist.keys(), reverse=True):
            bar = "█" * dist[sc]
            print(f"      {sc:>2}/10: {bar} ({dist[sc]})")
    print()


def cmd_reset(point_id: Optional[str] = None):
    state_file = BASE_DIR / "state.json"
    if not state_file.exists():
        print("Няма state.json")
        return
    if point_id:
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            if point_id in data.get("processed", {}):
                del data["processed"][point_id]
                state_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"✓ {point_id} изтрит от state.json")
            else:
                print(f"{point_id} не е в state.json")
        except Exception as e:
            print(f"✗ Грешка: {e}")
    else:
        state_file.unlink()
        print("✓ state.json изтрит")


def cmd_scan(html_arg: Optional[str] = None):
    if not AUTO_SCAN_AVAILABLE:
        print("✗ scan_queue.py липсва в тази папка")
        sys.exit(1)
    html_path = find_html_path(html_arg)
    if not html_path:
        print("✗ HTML не е намерен. Подай с --html /path/to/index.html")
        sys.exit(1)
    print(f"📖 HTML: {html_path}")
    pdf_root = None
    if CONFIG.get("pdf_root"):
        pdf_root = Path(CONFIG["pdf_root"])
        if not pdf_root.is_absolute():
            pdf_root = (BASE_DIR / pdf_root).resolve()
    scan_and_merge(
        html_path=html_path,
        queue_path=BASE_DIR / "queue.jsonl",
        pdf_root=pdf_root,
        only_with_pdf=CONFIG.get("scan_only_with_pdf", False),
        skip_with_explanation=CONFIG.get("scan_skip_with_explanation", True),
    )


def cmd_once(html_arg: Optional[str] = None, point_id: Optional[str] = None):
    p = Pipeline(html_path=find_html_path(html_arg), only_id=point_id)
    p._detect_and_recover_interrupted()   # ← crash recovery и за --once
    n = p.run_once(allow_scan=True)
    print(f"\nОбработени: {n}")
    p.print_summary()


def cmd_add(args):
    item = {
        "id": args.id, "title": args.title, "desc": args.desc or "",
        "source": args.source or "", "pdf": args.pdf or "", "page": args.page,
    }
    with open(BASE_DIR / "queue.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"✓ Добавен: {args.id} — {args.title}")


def main():
    parser = argparse.ArgumentParser(
        description="Olympiad Prep AI Pipeline v7",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--once", action="store_true", help="Обработи 1 batch и излез")
    parser.add_argument("--point", default=None, help="Само една точка (напр. 1.4)")
    parser.add_argument("--stats", action="store_true", help="Покажи статистика")
    parser.add_argument("--report", action="store_true", help="Покажи таблица с всички статии")
    parser.add_argument("--scan", action="store_true", help="Само сканирай HTML → queue")
    parser.add_argument("--reset", action="store_true", help="Изчисти state.json")
    parser.add_argument("--reset-point", default=None, help="Изчисти само една точка")
    parser.add_argument("--html", default=None, help="Път до index.html")
    parser.add_argument("--no-scan", action="store_true", help="Изключи auto-scan")
    parser.add_argument("--no-verify", action="store_true", help="Изключи verification")
    parser.add_argument("--check-config", action="store_true", help="Покажи merged config и излез")

    sub = parser.add_subparsers(dest="cmd")
    p_add = sub.add_parser("add", help="Ръчно добави item в queue")
    p_add.add_argument("id")
    p_add.add_argument("title")
    p_add.add_argument("--desc", default="")
    p_add.add_argument("--source", default="")
    p_add.add_argument("--pdf", default="")
    p_add.add_argument("--page", type=int, default=1)

    args = parser.parse_args()

    if args.no_scan:
        CONFIG["auto_scan"] = False
    if args.no_verify:
        CONFIG["enable_verification"] = False

    if args.check_config:
        print(json.dumps(CONFIG, indent=2, ensure_ascii=False))
        return

    if args.stats:
        cmd_stats()
        return

    if args.report:
        cmd_report()
        return

    if args.reset_point:
        cmd_reset(args.reset_point)
        return

    if args.reset:
        cmd_reset(None)
        return

    if args.scan:
        cmd_scan(args.html)
        return

    if args.cmd == "add":
        cmd_add(args)
        return

    # ─── Batch mode detection ───
    if CONFIG["generator"]["model"].endswith(":batch"):
        try:
            from batch_pipeline import run_batch
        except ImportError as e:
            print(f"⚠ Не мога да импортирам batch_pipeline.py: {e}")
            sys.exit(1)
        sys.exit(run_batch(only_id=args.point))

    if args.once:
        cmd_once(args.html, args.point)
        return

    # Default: 24/7 mode
    Pipeline(html_path=find_html_path(args.html), only_id=args.point).run_forever()


if __name__ == "__main__":
    main()