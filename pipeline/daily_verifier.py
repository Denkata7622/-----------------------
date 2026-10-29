#!/usr/bin/env python3
"""
daily_verifier.py — дневен качествен одит на anchors, articles, problems.

Работи като Стефан Георгиев — строг, но справедлив.

═══════════════════════════════════════════════════════════════════
  АРХИТЕКТУРА
═══════════════════════════════════════════════════════════════════

  Дневен цикъл:
    orchestrator (00:01) → extract → merge → classify → aggregate
    orchestrator (22:00) → daily_verifier
                            ↓
                          audit/<date>/
                            ├── report.json          (пълен)
                            ├── report.md            (human-readable)
                            ├── anchors.json         (за classifications)
                            ├── articles.json
                            ├── problems.json
                            ├── overall.json
                            └── reclassify.json      ← orchestrator утре
                                                       re-classify с
                                                       gpt-6.1-sol

  Модули:
    anchors    — point_id correct? stmt complete? sol valid?
                 ⚠ НАЙ-ВАЖНИЯТ — грешен anchor → грешна статия
    articles   — математическа коректност, педагогика, структура
    problems   — solvable? correct? difficulty calibrated?
    gaps       — real topic? duplicate? level appropriate? (TODO)
    overall    — pattern detection + препоръки

═══════════════════════════════════════════════════════════════════
  УПОТРЕБА
═══════════════════════════════════════════════════════════════════

  # Автоматично (от orchestrator в края на деня)
  python daily_verifier.py

  # Ръчно — конкретен модул
  python daily_verifier.py --module anchors
  python daily_verifier.py --module anchors,articles

  # Дълбок одит (20+ samples на модул)
  python daily_verifier.py --module all --deep

  # Конкретна точка
  python daily_verifier.py --point 1.4

  # Без AI (проверка на plumbing-а, 0 API calls)
  python daily_verifier.py --dry-run

  # С конкретни samples
  python daily_verifier.py --samples-anchors 15 --samples-articles 5

  # Re-run днес (ако вече е минал)
  python daily_verifier.py --force

═══════════════════════════════════════════════════════════════════
"""

import sys
import io
import os
import re
import json
import time
import logging
import argparse
import random
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import requests

from personas import (
    ARTICLE_REVIEWER, PROBLEM_REVIEWER,
    GAP_REVIEWER, OVERALL_REVIEWER,
)
from config import (
    PIPELINE_DIR as BASE_DIR,
    GENERATED_ROOT,
    ARTICLES_DIR,
    ANCHORS_DIR,
    EXTRACTED_DIR,
    CLASSIFIED_DIR,
    LOGS_DIR,
    STATE_DIR,
    STEPS_FILE,
    HTML_FILE,
)


# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════
AUDIT_DIR = GENERATED_ROOT / "audit"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

GAP_OUTPUT_DIR = BASE_DIR / "gap_output"
PROBLEMS_DIR = BASE_DIR / "problems"

# 4-те state файла — за точен budget tracking
STATE_FILES = [
    STATE_DIR / "chunker_state.json",
    BASE_DIR / "state.json",  # ← pipeline.py пише тук
    STATE_DIR / "problem_state.json",
    STATE_DIR / "gap_state.json",
]

# Hard cap — verifier-ът никога не надхвърля това за ден
VERIFIER_DAILY_CAP_USD = 0.35

# Global cap — не пипаме последните $0.30 от $3
GLOBAL_SAFE_LIMIT_USD = 2.70

DEFAULT_SAMPLES = {
    "anchors":  10,
    "articles": 2,
    "problems": 3,
    "gaps":     2,
    "overall":  1,
}

DEEP_SAMPLES = {
    "anchors":  20,
    "articles": 5,
    "problems": 8,
    "gaps":     5,
    "overall":  1,
}

# Оценка cost/call за всеки модул (за budget-safe проверка)
EST_COST = {
    "anchors":  0.015,
    "articles": 0.090,
    "problems": 0.040,
    "gaps":     0.040,
    "overall":  0.050,
}


# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [VERIFIER] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / f"verifier_{date.today()}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("verifier")


# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
def load_config() -> dict:
    cfg_file = BASE_DIR / "config.json"
    with open(cfg_file, "r", encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_config()

# ── cost tracker init ──
from cost_tracker import init as _ct_init, track_call as _track_call
_ct_init(BASE_DIR.parent / "generated" / "costs" / "ledger.jsonl")


# ═══════════════════════════════════════════════════════════════
# BUDGET EXHAUSTED
# ═══════════════════════════════════════════════════════════════
class BudgetExhausted(Exception):
    """HTTP 402 или локален cap — спира целия run."""


# ═══════════════════════════════════════════════════════════════
# AI CLIENT (with 402 awareness)
# ═══════════════════════════════════════════════════════════════
class AIClient:
    def __init__(self, cfg: dict, name: str = "verifier"):
        self.name = name
        self.url = cfg["api_url"]
        self.model = cfg["model"]
        self.max_tokens = cfg["max_tokens"]
        self.temperature = cfg["temperature"]
        self.headers = {"Content-Type": "application/json"}
        if cfg.get("api_key"):
            self.headers["Authorization"] = f"Bearer {cfg['api_key']}"

    def call(self, system: str, user: str, item_id: str = "?") -> Optional[str]:
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }
        for attempt in range(1, 4):
            try:
                t0 = time.time()
                r = requests.post(self.url, headers=self.headers, json=payload, timeout=180)
                if r.status_code == 429:
                    time.sleep(30); continue
                if r.status_code == 400:
                    log.warning(f"[{item_id}] 400 — махам response_format")
                    payload.pop("response_format", None)
                    continue
                if r.status_code == 402:
                    raise BudgetExhausted(f"[{item_id}] 402: {r.text[:120]}")
                if r.status_code >= 500:
                    time.sleep(8 * attempt); continue
                if r.status_code >= 400:
                    log.error(f"[{item_id}] {r.status_code}: {r.text[:300]}")
                    return None
                data = r.json()
                _track_call("daily_verifier", self.name, self.model, data,
                            item_id=item_id, t0=t0)
                return (data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content") or "").strip() or None
            except BudgetExhausted:
                raise
            except Exception as e:
                log.warning(f"[{item_id}] {e}")
                time.sleep(8 * attempt)
        return None


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def parse_since(s: str) -> int:
    """'24h' → 24, '7d' → 168, '30m' → 0.5"""
    m = re.match(r"^(\d+)([hdm])$", s.strip().lower())
    if not m:
        return 24
    n, unit = int(m.group(1)), m.group(2)
    return n if unit == "h" else n * 24 if unit == "d" else n / 60


def parse_compare_date(s: Optional[str]) -> Optional[date]:
    """'yesterday' | '2026-10-15' → date object"""
    if not s:
        return None
    if s.lower() == "yesterday":
        return date.today() - timedelta(days=1)
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


_PLAN_PHASES_CACHE = None

def _phase_from_week(week: int) -> tuple:
    """Чете PLAN_PHASES от data/plan_phases.js, връща (phase_num, focus_label)."""
    global _PLAN_PHASES_CACHE
    if _PLAN_PHASES_CACHE is None:
        phases = []
        try:
            src = (BASE_DIR.parent / "data" / "plan_phases.js").read_text(encoding="utf-8")
            m = re.search(r'const\s+PLAN_PHASES\s*=\s*\[', src)
            if m:
                start = m.end() - 1
                depth = 0
                in_str = False
                quote = None
                escape = False
                end = len(src)
                for i in range(start, len(src)):
                    c = src[i]
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
                            end = i + 1
                            break
                phases_src = src[start:end]
                for pm in re.finditer(
                    r'\{\s*num\s*:\s*(\d+)[\s\S]*?name\s*:\s*"([^"]*)"[\s\S]*?weeks_data\s*:\s*\[([\s\S]*?)\]\s*\}\s*\}',
                    phases_src
                ):
                    num = int(pm.group(1))
                    name = pm.group(2)
                    weeks = [int(w) for w in re.findall(r'week\s*:\s*(\d+)', pm.group(3))]
                    phases.append({"num": num, "name": name, "weeks": weeks})
        except Exception as e:
            log.warning(f"[_phase_from_week] {e}")
        _PLAN_PHASES_CACHE = phases

    for ph in _PLAN_PHASES_CACHE:
        if week in ph["weeks"]:
            name = ph["name"].lower()
            if "prep" in name:
                focus = "Task 0 (PREP)"
            elif "regional" in name:
                focus = "Task 1+2"
            elif "simulation" in name:
                focus = "Simulations"
            elif "national" in name:
                focus = "Task 3+4"
            else:
                focus = ph["name"]
            return ph["num"], focus
    if week <= 6: return 1, "Task 1"
    if week <= 12: return 2, "Task 2"
    if week <= 15: return 3, "Task 3+4"
    if week <= 17: return 4, "Simulations"
    return 5, "National"

def get_plan_context() -> dict:
    """Извлича контекст от HTML — текуща фаза, седмица, дни до изпит."""
    try:
        html = HTML_FILE.read_text(encoding="utf-8")
    except Exception:
        return _empty_plan()

    m = re.search(r"planStartDate:\s*new Date\('([^']+)'", html)
    if not m:
        return _empty_plan()

    start = datetime.fromisoformat(m.group(1))
    now = datetime.now()
    days_since = (now - start).days
    week = max(1, days_since // 7 + 1)

    exam_dates = {}
    for name in ["regional", "nationalStart"]:
        m2 = re.search(rf"{name}:\s*new Date\('([^']+)'", html)
        if m2:
            exam_dates[name] = datetime.fromisoformat(m2.group(1))

    days_reg = (exam_dates.get("regional", now) - now).days if "regional" in exam_dates else 0
    days_nat = (exam_dates.get("nationalStart", now) - now).days if "nationalStart" in exam_dates else 0

    # Derived from PLAN_PHASES (не hardcode)
    phase, focus = _phase_from_week(week)

    return {
        "week": week, "phase": phase, "focus": focus,
        "days_to_regional": max(0, days_reg),
        "days_to_national": max(0, days_nat),
    }


def _empty_plan() -> dict:
    return {"week": 0, "phase": 0, "days_to_regional": 0,
            "days_to_national": 0, "focus": "unknown"}


def load_previous_audit(compare_date: Optional[date] = None) -> Optional[dict]:
    """Зарежда вчерашния (или конкретен) audit report."""
    target = compare_date or (date.today() - timedelta(days=1))
    f = AUDIT_DIR / str(target) / "report.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def find_recent_files(folder: Path, hours: int = 24) -> list[Path]:
    """Файлове, променени в последните N часа."""
    if not folder.exists():
        return []
    cutoff = time.time() - hours * 3600
    return [f for f in folder.rglob("*")
            if f.is_file() and f.stat().st_mtime >= cutoff]


def load_steps_for_context(max_points: int = 160) -> str:
    """
    Зарежда STEPS IDs + titles за prompt.

    Само IDs и titles (не desc) — намалява prompt-а с ~70%,
    без да губи семантична информация.
    """
    try:
        content = STEPS_FILE.read_text(encoding="utf-8")
    except Exception:
        return "(STEPS не е налично)"

    # Извлича всички {id: "X.Y", title: "..."}
    pattern = re.compile(
        r'\{\s*id\s*:\s*"([^"]+)"[^{}]*?title\s*:\s*"((?:\\.|[^"\\])*)"',
        re.DOTALL,
    )
    points = []
    for m in pattern.finditer(content):
        pid = m.group(1)
        title = m.group(2).replace('\\"', '"').replace("\\'", "'")
        points.append(f"  {pid}: {title}")

    return "\n".join(points[:max_points])


# ═══════════════════════════════════════════════════════════════
# DAILY VERIFIER
# ═══════════════════════════════════════════════════════════════
class DailyVerifier:
    """Дневен одит. Един lifecycle, много модули, actionable output."""

    def __init__(
        self,
        target_point: Optional[str] = None,
        since_hours: int = 24,
        compare_date: Optional[date] = None,
        seed: Optional[int] = None,
    ):
        # Auditor model — по-евтин от claude-opus ($0.15 → $0.02)
        auditor_cfg = dict(CONFIG.get("auditor", {}))
        if not auditor_cfg:
            # Fallback — ползваме gpt-6.1-sol с разумни defaults
            generator = CONFIG["generator"]
            auditor_cfg = {
                "api_url": generator["api_url"],
                "api_key": generator["api_key"],
                "model": "openai/gpt-6.1-sol",
                "max_tokens": 800,
                "temperature": 0.05,
            }
        self.ai = AIClient(auditor_cfg, "auditor")

        self.plan_ctx = get_plan_context()
        self.results: dict[str, dict] = {}
        self.target_point = target_point
        self.since_hours = since_hours
        self.compare_date = compare_date
        self.previous = load_previous_audit(compare_date)

        # Session budget tracking
        self._session_cost = 0.0
        self._budget_start = self._budget_used()

        # Deterministic sampling
        if seed is not None:
            random.seed(seed)

        # STEPS cache за prompts
        self._steps_context = load_steps_for_context()

    # ─── BUDGET ───────────────────────────────────────────────
    def _budget_used(self) -> float:
        """Сума от всички state файлове за днес."""
        total = 0.0
        today = str(date.today())
        for f in STATE_FILES:
            if not f.exists():
                continue
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                b = d.get("budget", {})
                if b.get("date") == today:
                    total += float(b.get("spent_usd", 0.0))
            except Exception:
                pass
        return total

    def _can_afford(self, est_cost: float) -> bool:
        """Проверява и локалния, и глобалния cap."""
        # 1. Локален cap за verifier
        if self._session_cost + est_cost > VERIFIER_DAILY_CAP_USD:
            return False
        # 2. Глобален cap за деня
        if self._budget_used() + est_cost > GLOBAL_SAFE_LIMIT_USD:
            return False
        return True

    def _charge_budget(self, usd: float, reason: str = "verifier"):
        """Добавя разход към chunker_state (глобалния бюджет)."""
        self._session_cost += usd
        state_file = STATE_DIR / "chunker_state.json"
        if not state_file.exists():
            return
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            today = str(date.today())
            if data["budget"]["date"] != today:
                data["budget"] = {"date": today, "spent_usd": 0.0, "calls": 0}
            data["budget"]["spent_usd"] += usd
            data["budget"]["calls"] += 1
            # Atomic save с retry (същата логика като chunker)
            text = json.dumps(data, ensure_ascii=False, indent=2)
            tmp = state_file.with_suffix(".tmp")
            try:
                tmp.write_text(text, encoding="utf-8")
            except PermissionError:
                state_file.write_text(text, encoding="utf-8")
                return
            for attempt in range(6):
                try:
                    tmp.replace(state_file)
                    return
                except PermissionError:
                    if attempt < 5:
                        time.sleep(0.3 * (attempt + 1))
                    else:
                        state_file.write_text(text, encoding="utf-8")
                        try:
                            tmp.unlink()
                        except Exception:
                            pass
                        return
        except Exception as e:
            log.warning(f"[budget] charge failed: {e}")

    # ─── AI WRAPPER ───────────────────────────────────────────
    def _audit_call(
        self,
        system: str,
        user: str,
        item_id: str,
        est_cost: float,
    ) -> Optional[dict]:
        """AI call с budget check + cost tracking + JSON parse."""
        if not self._can_afford(est_cost):
            raise BudgetExhausted(
                f"Budget cap: session ${self._session_cost:.3f} + "
                f"est ${est_cost:.3f} > local ${VERIFIER_DAILY_CAP_USD:.2f}"
            )
        raw = self.ai.call(system, user, item_id)
        if not raw:
            return None
        self._charge_budget(est_cost)
        return self._parse_json(raw)

    def _parse_json(self, text: Optional[str]) -> Optional[dict]:
        if not text:
            return None
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except Exception:
            try:
                return json.loads(re.sub(r",\s*([}\]])", r"\1", m.group(0)))
            except Exception:
                return None

    # ═══════════════════════════════════════════════════════════
    # MODULE: ANCHORS (— най-важният)
    # ═══════════════════════════════════════════════════════════
    def audit_anchors(self, samples: int = 10) -> dict:
        """
        Проверява anchor задачите в generated/anchors/*.json.

        За всяка sampled задача:
          1. Правилен ли е point_id?
          2. Statement пълен ли е (без OCR garbage)?
          3. Solution валидно ли е (математически коректно)?
          4. Difficulty калибриран ли е?

        Flags за orchestrator (утре):
          - flagged_sources → reclassify с gpt-6.1-sol
          - flagged_points  → ръчна проверка / reclassify цяла точка
        """
        if not ANCHORS_DIR.exists():
            return {"score": 0, "audited": 0, "error": "no anchors dir"}

        # ─── Събери всички anchor problems ───
        anchors: list[dict] = []
        for f in ANCHORS_DIR.glob("*.json"):
            if f.name == "_unclassified.json":
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            pid = data.get("point_id")
            if not pid:
                continue
            for p in data.get("problems", []):
                anchors.append({
                    "assigned_pid": pid,
                    "source": p.get("source", "?"),
                    "statement": (p.get("statement") or "").strip(),
                    "solution": (p.get("solution") or "").strip(),
                    "difficulty": p.get("difficulty"),
                })

        if not anchors:
            return {"score": 0, "audited": 0, "error": "no anchor problems"}

        # ─── Филтър по точка ако е зададена ───
        if self.target_point:
            anchors = [a for a in anchors if a["assigned_pid"] == self.target_point]
            if not anchors:
                return {"score": 0, "audited": 0,
                        "error": f"no anchors for point {self.target_point}"}

        # ─── Sample ───
        sample = random.sample(anchors, min(samples, len(anchors)))

        results: list[dict] = []
        flagged_sources: list[dict] = []
        wrong_by_point: dict[str, list[dict]] = {}

        for item in sample:
            user = f"""═══ КОНТЕКСТ ═══
Фаза: {self.plan_ctx['phase']} ({self.plan_ctx['focus']}), седмица {self.plan_ctx['week']}/25
Източник: {item['source']}

═══ ЗАДАЧА ═══
{('Условие: ' + item['statement'][:1500]) if item['statement'] else '(без условие)'}

{('Решение: ' + item['solution'][:1500]) if item['solution'] else '(без решение)'}

═══ КЛАСИФИЦИРАНА КАТО ═══
Point {item['assigned_pid']} (ниво: {item['difficulty'] or '?'})

═══ ВСИЧКИ STEPS ТОЧКИ ═══
{self._steps_context}

═══ ТВОЯТА ЗАДАЧА ═══
Провери 4 неща:

1. POINT_ID: Каква е ОСНОВНАТА техника за решаване?
   Съвпада ли с Point {item['assigned_pid']}?
   Ако не — коя точка е по-точна?

2. STATEMENT: Пълен ли е? Има ли OCR garbage (символи, неразчетени части)?
   Може ли ученик да реши задачата от това условие?

3. SOLUTION: Математически коректно ли е?
   Провери с конкретни числа ако можеш. Има ли скипнати стъпки?

4. DIFFICULTY: Калибриран ли е ({item['difficulty']})?
   Easy = 5-8 мин, Medium = 15-20, Hard = 30+

Върни САМО JSON:
{{
  "assigned_pid": "{item['assigned_pid']}",
  "point_correct": true|false,
  "correct_pid": "X.Y" или null,
  "statement_ok": true|false,
  "statement_issues": ["..."] или [],
  "solution_ok": true|false,
  "solution_issues": ["..."] или [],
  "difficulty_ok": true|false,
  "suggested_difficulty": "easy|medium|hard" или null,
  "reasoning": "1-2 изречения общо",
  "can_be_anchor": true|false
}}"""

            try:
                parsed = self._audit_call(
                    "Ти си строг проверител на олимпиадни задачи. "
                    "Проверяваш математическа коректност и точност на класификацията.",
                    user,
                    f"anchor-{item['source'][:30]}",
                    EST_COST["anchors"],
                )
            except BudgetExhausted:
                raise

            if not parsed:
                log.warning(f"[anchor] {item['source']}: no response")
                continue

            parsed["source"] = item["source"]
            parsed["assigned_pid"] = item["assigned_pid"]
            results.append(parsed)

            # Flag за reclassify
            if not parsed.get("point_correct", True):
                wrong_by_point.setdefault(item["assigned_pid"], []).append({
                    "source": item["source"],
                    "correct_pid": parsed.get("correct_pid"),
                    "reasoning": parsed.get("reasoning"),
                })
                flagged_sources.append({
                    "source": item["source"],
                    "assigned_pid": item["assigned_pid"],
                    "correct_pid": parsed.get("correct_pid"),
                    "reasoning": parsed.get("reasoning"),
                })

            status = "✓" if parsed.get("can_be_anchor") else "✗"
            log.info(
                f"[anchor/{item['source'][:40]}] {status} "
                f"pid_ok={parsed.get('point_correct')} "
                f"stmt_ok={parsed.get('statement_ok')} "
                f"sol_ok={parsed.get('solution_ok')}"
            )

        if not results:
            return {"score": 0, "audited": 0, "error": "all audits failed"}

        # ─── Aggregated metrics ───
        n = len(results)
        point_correct = sum(1 for r in results if r.get("point_correct"))
        stmt_ok = sum(1 for r in results if r.get("statement_ok"))
        sol_ok = sum(1 for r in results if r.get("solution_ok"))
        can_anchor = sum(1 for r in results if r.get("can_be_anchor"))

        # Точки с 2+ грешки → цяла точка за ръчна проверка
        flagged_points = [
            pid for pid, wrongs in wrong_by_point.items()
            if len(wrongs) >= 2
        ]

        score = round(can_anchor / n * 10, 1) if n else 0

        return {
            "score": score,
            "audited": n,
            "point_accuracy_pct": round(point_correct / n * 100, 1),
            "statement_ok_pct": round(stmt_ok / n * 100, 1),
            "solution_ok_pct": round(sol_ok / n * 100, 1),
            "can_anchor_pct": round(can_anchor / n * 100, 1),
            "flagged_sources": flagged_sources,
            "flagged_points": flagged_points,
            "wrong_by_point": wrong_by_point,
            "details": results,
        }

    # ═══════════════════════════════════════════════════════════
    # MODULE: ARTICLES
    # ═══════════════════════════════════════════════════════════
    def audit_articles(self, samples: int = 2) -> dict:
        """Проверява генерирани статии в generated/articles/*/deep.md."""
        if not ARTICLES_DIR.exists():
            return {"score": 0, "audited": 0, "error": "no articles dir"}

        if self.target_point:
            point_dirs = [ARTICLES_DIR / self.target_point.replace(".", "_")]
        else:
            recent = find_recent_files(ARTICLES_DIR, hours=self.since_hours)
            deep_files = [f for f in recent if f.name == "deep.md"]
            point_dirs = list({f.parent for f in deep_files})
            if not point_dirs:
                all_deep = list(ARTICLES_DIR.rglob("deep.md"))
                if not all_deep:
                    return {"score": 0, "audited": 0, "error": "no deep.md files"}
                all_dirs = list({f.parent for f in all_deep})
                point_dirs = random.sample(all_dirs, min(samples, len(all_dirs)))

        point_dirs = point_dirs[:samples]
        results: list[dict] = []
        flagged_points: list[str] = []

        for pd in point_dirs:
            deep_file = pd / "deep.md"
            if not deep_file.exists():
                continue

            point_id = pd.name.replace("_", ".")
            try:
                deep_text = deep_file.read_text(encoding="utf-8")
                title = re.sub(r"^#\s*", "", deep_text.split("\n")[0]) if deep_text else point_id

                # Previous version (за diff)
                previous = ""
                prev_files = sorted(pd.glob("deep-v*.md"))
                if len(prev_files) >= 2:
                    previous = prev_files[-2].read_text(encoding="utf-8")[:3000]

                user = ARTICLE_REVIEWER + f"""

═══ КОНТЕКСТ ═══
Тема: {title}
Точка: {point_id}
Фаза: {self.plan_ctx['phase']} ({self.plan_ctx['focus']}), седмица {self.plan_ctx['week']}/25
Дни до областен: {self.plan_ctx['days_to_regional']}
Дни до национален: {self.plan_ctx['days_to_national']}

═══ СТАТИЯ ЗА ОЦЕНКА ═══
{deep_text[:15000]}

{("═══ ПРЕДИШНА ВЕРСИЯ (за сравнение) ═══" + chr(10) + previous) if previous else ""}

Оцени като Стефан Георгиев. Върни САМО JSON:
{{
  "score": 1-10,
  "verdict": "excellent|good|acceptable|needs_work|unusable",
  "strengths": ["..."],
  "critical_issues": [{{"formula": "...", "problem": "...", "fix": "..."}}],
  "pedagogical_gaps": ["..."],
  "ai_smell": ["..."],
  "plan_alignment": "aligned|partial|off",
  "comparison_with_previous": {{"improved": [...], "regressed": [...], "delta": -2 to +2}},
  "specific_recommendations": ["..."],
  "can_ship": true|false
}}"""

                parsed = self._audit_call(
                    ARTICLE_REVIEWER, user, point_id, EST_COST["articles"]
                )
                if parsed:
                    parsed["point_id"] = point_id
                    results.append(parsed)
                    if not parsed.get("can_ship", True):
                        flagged_points.append(point_id)
                    log.info(f"[article/{point_id}] "
                             f"score={parsed.get('score')} "
                             f"verdict={parsed.get('verdict')}")
            except BudgetExhausted:
                raise
            except Exception as e:
                log.exception(f"[article/{point_id}] {e}")

        if not results:
            return {"score": 0, "audited": 0, "error": "all audits failed"}

        avg = sum(r.get("score", 0) for r in results) / len(results)
        return {
            "score": round(avg, 1),
            "audited": len(results),
            "details": results,
            "critical_issues": sum(1 for r in results if r.get("critical_issues")),
            "can_ship": sum(1 for r in results if r.get("can_ship")),
            "flagged_points": flagged_points,
        }

    # ═══════════════════════════════════════════════════════════
    # MODULE: PROBLEMS
    # ═══════════════════════════════════════════════════════════
    def audit_problems(self, samples: int = 3) -> dict:
        """Проверява генерирани задачи в pipeline/problems/*/."""
        if not PROBLEMS_DIR.exists():
            return {"score": 0, "audited": 0, "error": "no problems dir"}

        if self.target_point:
            point_dirs = [PROBLEMS_DIR / self.target_point.replace(".", "_")]
        else:
            recent = find_recent_files(PROBLEMS_DIR, hours=self.since_hours)
            pf_list = [f for f in recent if f.name == "problems.json"]
            point_dirs = list({f.parent for f in pf_list})
            if not point_dirs:
                all_pf = list(PROBLEMS_DIR.rglob("problems.json"))
                if not all_pf:
                    return {"score": 0, "audited": 0, "error": "no problems.json"}
                all_dirs = list({f.parent for f in all_pf})
                point_dirs = random.sample(all_dirs, min(samples, len(all_dirs)))

        point_dirs = point_dirs[:samples]
        results: list[dict] = []
        flagged_points: list[str] = []

        for pd in point_dirs:
            pf = pd / "problems.json"
            if not pf.exists():
                continue
            point_id = pd.name.replace("_", ".")

            try:
                data = json.loads(pf.read_text(encoding="utf-8"))
                sols_file = pd / "solutions.json"
                sols = (json.loads(sols_file.read_text(encoding="utf-8"))
                        if sols_file.exists() else {})
                problems = data.get("problems", [])
                if not problems:
                    continue

                for p in random.sample(problems, min(2, len(problems))):
                    pid = p.get("id", "?")
                    sol = sols.get(pid, {})

                    user = PROBLEM_REVIEWER + f"""

═══ КОНТЕКСТ ═══
Точка: {point_id}
Ниво: {p.get('difficulty', '?')}
Фаза: {self.plan_ctx['phase']}, седмица {self.plan_ctx['week']}/25

═══ ЗАДАЧА ═══
{p.get('problem', '')}

═══ РЕШЕНИЕ ═══
{sol.get('solution', '')}

═══ ОТГОВОР ═══
{sol.get('answer', '')}

═══ HINTS ═══
""" + "\n".join(f"- {h}" for h in sol.get("hints", [])) + """

Оцени като Стефан Георгиев. Първо РЕШИ ЗАДАЧАТА САМ. Върни САМО JSON:
{
  "score": 1-10,
  "verdict": "...",
  "my_solution_matches": true|false,
  "solvable": true|false,
  "solution_correct": true|false,
  "topic_match": "exact|partial|off",
  "difficulty_calibrated": true|false,
  "hints_quality": 1-10,
  "critical_issues": [],
  "ai_smell": [],
  "recommendation": "keep|revise|regenerate",
  "can_ship": true|false
}"""

                    parsed = self._audit_call(
                        PROBLEM_REVIEWER, user, pid, EST_COST["problems"]
                    )
                    if parsed:
                        parsed["problem_id"] = pid
                        parsed["point_id"] = point_id
                        results.append(parsed)
                        if not parsed.get("can_ship", True):
                            if point_id not in flagged_points:
                                flagged_points.append(point_id)
                        log.info(f"[problem/{pid}] "
                                 f"score={parsed.get('score')} "
                                 f"solvable={parsed.get('solvable')}")
            except BudgetExhausted:
                raise
            except Exception as e:
                log.exception(f"[problem/{point_id}] {e}")

        if not results:
            return {"score": 0, "audited": 0, "error": "all audits failed"}

        avg = sum(r.get("score", 0) for r in results) / len(results)
        return {
            "score": round(avg, 1),
            "audited": len(results),
            "details": results,
            "unsolvable": sum(1 for r in results if not r.get("solvable")),
            "wrong_solutions": sum(1 for r in results if not r.get("solution_correct")),
            "topic_off": sum(1 for r in results if r.get("topic_match") == "off"),
            "flagged_points": flagged_points,
        }

    # ═══════════════════════════════════════════════════════════
    # MODULE: GAPS (stub — за в бъдеще)
    # ═══════════════════════════════════════════════════════════
    def audit_gaps(self, samples: int = 2) -> dict:
        """Проверява gap candidates. TODO: имплементирай когато gap_worker работи."""
        if not GAP_OUTPUT_DIR.exists():
            return {"score": 0, "audited": 0, "note": "gap_worker not active"}
        return {"score": 0, "audited": 0, "note": "not implemented yet"}

    # ═══════════════════════════════════════════════════════════
    # MODULE: OVERALL
    # ═══════════════════════════════════════════════════════════
    def audit_overall(self) -> dict:
        """Синтезира всички модули + сравнява с вчера."""
        today_summary = {
            k: {
                "score": v.get("score", 0),
                "audited": v.get("audited", 0),
                "flagged_count": len(v.get("flagged_sources", [])) +
                                 len(v.get("flagged_points", [])),
            }
            for k, v in self.results.items() if k != "overall"
        }
        yesterday_summary = (self.previous or {}).get("results", {})

        user = OVERALL_REVIEWER + f"""

═══ ДАННИ ДНЕС ═══
{json.dumps(today_summary, ensure_ascii=False, indent=2)}

═══ ДАННИ ВЧЕРА ═══
{json.dumps(yesterday_summary, ensure_ascii=False, indent=2)[:3000]}

═══ ПЛАН ═══
Седмица: {self.plan_ctx['week']}/25
Фаза: {self.plan_ctx['phase']} ({self.plan_ctx['focus']})
Дни до областен: {self.plan_ctx['days_to_regional']}
Дни до национален: {self.plan_ctx['days_to_national']}
Очаквано покритие: {min(100, int(self.plan_ctx['week'] / 25 * 100))}%

═══ BUDGET ═══
Похарчено днес: ${self._budget_used():.2f}
Verifier session: ${self._session_cost:.2f}

Оцени като Стефан Георгиев. Върни САМО JSON:
{{
  "overall_score": 1-10,
  "verdict": "on_track|behind|way_behind|ahead",
  "modules_health": {{
    "anchors":  {{"score": N, "trend": "up|down|stable"}},
    "articles": {{"score": N, "trend": "..."}},
    "problems": {{"score": N, "trend": "..."}}
  }},
  "critical_alerts": ["..."],
  "comparison_yesterday": {{"improved": [...], "regressed": [...], "delta": -2 to +2}},
  "recommendations_for_human": ["..."],
  "should_pause_and_review": true|false,
  "reasoning": "..."
}}"""

        try:
            parsed = self._audit_call(
                OVERALL_REVIEWER, user, "overall", EST_COST["overall"]
            )
        except BudgetExhausted:
            return {"error": "budget exhausted"}

        if not parsed:
            return {"error": "AI failed"}
        return parsed

    # ═══════════════════════════════════════════════════════════
    # REPORT
    # ═══════════════════════════════════════════════════════════
    def save_report(self) -> Path:
        today_dir = AUDIT_DIR / str(date.today())
        today_dir.mkdir(parents=True, exist_ok=True)

        report = {
            "date": str(date.today()),
            "run_at": datetime.now().isoformat(),
            "manual_run": bool(self.target_point or self.compare_date),
            "target_point": self.target_point,
            "since_hours": self.since_hours,
            "compare_date": str(self.compare_date) if self.compare_date else None,
            "plan_context": self.plan_ctx,
            "budget": {
                "before": round(self._budget_start, 4),
                "after": round(self._budget_used(), 4),
                "session_cost": round(self._session_cost, 4),
                "local_cap": VERIFIER_DAILY_CAP_USD,
                "global_cap": GLOBAL_SAFE_LIMIT_USD,
            },
            "results": self.results,
        }
        (today_dir / "report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # Per-module files (за orchestrator да чете само нужното)
        for mod, data in self.results.items():
            if mod == "overall":
                continue
            (today_dir / f"{mod}.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        # Reclassify file (orchestrator утре)
        self._write_reclassify(today_dir)

        # Markdown
        md = self._build_markdown()
        (today_dir / "report.md").write_text(md, encoding="utf-8")

        log.info(f"\n📄 {today_dir / 'report.md'}")
        return today_dir

    def _write_reclassify(self, today_dir: Path) -> None:
        """Пише reclassify.json за orchestrator."""
        anchors = self.results.get("anchors", {})
        flagged = anchors.get("flagged_sources", [])
        flagged_pts = anchors.get("flagged_points", [])

        if not flagged and not flagged_pts:
            return

        payload = {
            "date": str(date.today()),
            "generated_at": datetime.now().isoformat(),
            "reason": "anchor_audit",
            "accuracy_pct": anchors.get("point_accuracy_pct"),
            "sample_size": anchors.get("audited"),
            "flagged_sources": flagged,
            "flagged_points": flagged_pts,
        }
        (today_dir / "reclassify.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        log.info(f"⚠ {len(flagged)} flagged sources → reclassify.json")

    def _build_markdown(self) -> str:
        md = f"# Audit — {date.today()}\n\n"
        md += f"**Run:** {datetime.now().strftime('%H:%M:%S')}\n"
        md += f"**Budget:** ${self._budget_start:.2f} → ${self._budget_used():.2f} "
        md += f"(session ${self._session_cost:.2f})\n\n"

        if self.target_point:
            md += f"**Target point:** `{self.target_point}`\n\n"

        md += f"**Week {self.plan_ctx['week']}/25** · "
        md += f"Phase {self.plan_ctx['phase']} ({self.plan_ctx['focus']})\n"
        md += f"**Days to regional:** {self.plan_ctx['days_to_regional']} · "
        md += f"**to national:** {self.plan_ctx['days_to_national']}\n\n"

        for module, data in self.results.items():
            if module == "overall":
                continue
            md += f"## {module.upper()}\n"
            md += f"- Score: **{data.get('score', '?')}/10**\n"
            md += f"- Audited: {data.get('audited', 0)}\n"

            # Module-specific metrics
            if "point_accuracy_pct" in data:
                md += f"- Point accuracy: **{data['point_accuracy_pct']}%**\n"
            if "statement_ok_pct" in data:
                md += f"- Statement OK: {data['statement_ok_pct']}%\n"
            if "solution_ok_pct" in data:
                md += f"- Solution OK: {data['solution_ok_pct']}%\n"
            if "can_anchor_pct" in data:
                md += f"- Can be anchor: **{data['can_anchor_pct']}%**\n"
            if data.get("unsolvable"):
                md += f"- ⚠️ Unsolvable: {data['unsolvable']}\n"
            if data.get("wrong_solutions"):
                md += f"- ⚠️ Wrong solutions: {data['wrong_solutions']}\n"
            if data.get("topic_off"):
                md += f"- ⚠️ Topic off: {data['topic_off']}\n"
            if data.get("flagged_sources"):
                md += f"- 🔁 Flagged for reclassify: {len(data['flagged_sources'])}\n"
            if data.get("flagged_points"):
                md += f"- 🔁 Flagged points: {data['flagged_points']}\n"
            if data.get("error"):
                md += f"- ❌ Error: {data['error']}\n"
            md += "\n"

        # Overall
        if "overall" in self.results and "error" not in self.results["overall"]:
            ov = self.results["overall"]
            md += "## OVERALL\n"
            md += f"- Score: **{ov.get('overall_score', '?')}/10**\n"
            md += f"- Verdict: **{ov.get('verdict', '?')}**\n"
            md += f"- Reasoning: {ov.get('reasoning', '')}\n\n"

            if ov.get("critical_alerts"):
                md += "### ⚠️ Critical alerts\n"
                for a in ov["critical_alerts"]:
                    md += f"- {a}\n"
                md += "\n"

            if ov.get("recommendations_for_human"):
                md += "### Recommendations\n"
                for r in ov["recommendations_for_human"]:
                    md += f"- {r}\n"
                md += "\n"

            if ov.get("should_pause_and_review"):
                md += "\n🛑 **Human review recommended**\n"

        return md

    # ─── PRINT ────────────────────────────────────────────────
    def print_summary(self) -> None:
        log.info("═" * 60)
        log.info("SUMMARY")
        for mod, data in self.results.items():
            if mod == "overall":
                continue
            extra = ""
            if "point_accuracy_pct" in data:
                extra = f" (accuracy {data['point_accuracy_pct']}%)"
            log.info(f"  {mod:12s}  score {data.get('score', '?'):>4}/10  "
                     f"audited {data.get('audited', 0)}{extra}")

        if "overall" in self.results and "error" not in self.results["overall"]:
            ov = self.results["overall"]
            log.info(f"  {'OVERALL':12s}  score {ov.get('overall_score', '?'):>4}/10  "
                     f"{ov.get('verdict', '?')}")

        log.info(f"\n  Session cost: ${self._session_cost:.4f}")
        log.info(f"  Budget: ${self._budget_start:.2f} → ${self._budget_used():.2f}")
        log.info("═" * 60)

    # ─── DRY RUN ──────────────────────────────────────────────
    def dry_run(self) -> None:
        """Показва какво би се направило. Без API calls, без save."""
        log.info("🔍 DRY RUN — без AI calls")
        log.info(f"Plan: Week {self.plan_ctx['week']}/25, Phase {self.plan_ctx['phase']}")
        log.info(f"Budget: ${self._budget_used():.2f} / ${GLOBAL_SAFE_LIMIT_USD:.2f}")
        log.info(f"Verifier cap: ${VERIFIER_DAILY_CAP_USD:.2f}")
        log.info(f"Previous audit: {self.compare_date or 'yesterday'}")

        if self.previous:
            log.info("\nВчерашни резултати:")
            for mod, data in self.previous.get("results", {}).items():
                if mod == "overall":
                    continue
                log.info(f"  {mod:12s}  {data.get('score', '?')}/10")

        # Какво ще се проверява
        if ANCHORS_DIR.exists():
            count = sum(len(json.loads(f.read_text(encoding="utf-8")).get("problems", []))
                        for f in ANCHORS_DIR.glob("*.json")
                        if f.name != "_unclassified.json")
            log.info(f"\nAnchors:    {count} problems available")
        if ARTICLES_DIR.exists():
            count = len([d for d in ARTICLES_DIR.iterdir() if d.is_dir()])
            log.info(f"Articles:   {count} available")
        if PROBLEMS_DIR.exists():
            count = len([d for d in PROBLEMS_DIR.iterdir() if d.is_dir()])
            log.info(f"Problems:   {count} available")

        # Какво е ново
        new_articles = [f for f in find_recent_files(ARTICLES_DIR, self.since_hours)
                        if f.name == "deep.md"]
        new_problems = [f for f in find_recent_files(PROBLEMS_DIR, self.since_hours)
                        if f.name == "problems.json"]
        log.info(f"\nНови за последните {self.since_hours}h:")
        log.info(f"  Articles: {len(new_articles)}")
        log.info(f"  Problems: {len(new_problems)}")


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser(
        description="Дневен верификатор — audit anchors, articles, problems",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примери:
  python daily_verifier.py                              # default (small samples)
  python daily_verifier.py --deep                       # 20 samples на модул
  python daily_verifier.py --module anchors             # само anchors
  python daily_verifier.py --module anchors,articles    # 2 модула
  python daily_verifier.py --point 1.4                  # конкретна точка
  python daily_verifier.py --samples-anchors 15         # override за 1 модул
  python daily_verifier.py --dry-run                    # без API
  python daily_verifier.py --force                      # rerun днес
        """,
    )
    ap.add_argument("--module", default=None,
                    help="Списък модули: anchors, articles, problems, gaps, all")
    ap.add_argument("--point", default=None, help="Конкретна STEPS точка")
    ap.add_argument("--since", default="24h", help="Времеви прозорец (24h, 7d)")
    ap.add_argument("--compare", default=None, help="Сравни с дата или 'yesterday'")
    ap.add_argument("--deep", action="store_true", help="20 samples на модул")
    ap.add_argument("--sample", type=int, default=None,
                    help="Override за всички модули")
    ap.add_argument("--samples-anchors", type=int, default=None)
    ap.add_argument("--samples-articles", type=int, default=None)
    ap.add_argument("--samples-problems", type=int, default=None)
    ap.add_argument("--seed", type=int, default=None,
                    help="Seed за deterministic sampling")
    ap.add_argument("--dry-run", action="store_true",
                    help="Само показва, без AI calls")
    ap.add_argument("--force", action="store_true",
                    help="Rerun дори ако днес вече е минавал")
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args()

    # Проверка за rerun
    today_dir = AUDIT_DIR / str(date.today())
    if (today_dir / "report.json").exists() and not args.force and not args.dry_run:
        log.error(f"❌ Днес вече е минавал ({today_dir}). "
                  f"Ползвай --force за rerun.")
        return 1

    v = DailyVerifier(
        target_point=args.point,
        since_hours=parse_since(args.since),
        compare_date=parse_compare_date(args.compare),
        seed=args.seed,
    )

    if args.dry_run:
        v.dry_run()
        return 0

    # Кои модули
    if args.module:
        modules = [m.strip() for m in args.module.split(",")]
        if "all" in modules:
            modules = ["anchors", "articles", "problems", "gaps", "overall"]
    else:
        modules = ["anchors", "articles", "problems", "overall"]

    # Samples
    base_samples = DEEP_SAMPLES if args.deep else DEFAULT_SAMPLES
    sample_map = dict(base_samples)
    if args.sample is not None:
        sample_map = {k: args.sample for k in sample_map}
    if args.samples_anchors is not None:
        sample_map["anchors"] = args.samples_anchors
    if args.samples_articles is not None:
        sample_map["articles"] = args.samples_articles
    if args.samples_problems is not None:
        sample_map["problems"] = args.samples_problems

    # Изпълни
    log.info(f"\n▶ Audit start — budget ${v._budget_used():.2f}")
    try:
        for mod in modules:
            if mod == "overall":
                continue
            method = getattr(v, f"audit_{mod}", None)
            if not method:
                log.warning(f"Непознат модул: {mod}")
                continue
            log.info(f"\n▶ Модул: {mod.upper()} ({sample_map.get(mod, 3)} samples)")
            try:
                v.results[mod] = method(samples=sample_map.get(mod, 3))
            except BudgetExhausted as e:
                log.warning(f"⚠ Budget exhausted при {mod}: {e}")
                break

        # Overall — винаги последен
        if "overall" in modules and not v.results.get("overall"):
            log.info("\n▶ Модул: OVERALL")
            try:
                v.results["overall"] = v.audit_overall()
            except BudgetExhausted as e:
                log.warning(f"⚠ Budget exhausted при overall: {e}")

    except KeyboardInterrupt:
        log.warning("\n⚠ Прекъснато от потребител")
    except Exception as e:
        log.exception(f"❌ Грешка: {e}")

    # Отчет
    v.print_summary()
    if not args.no_save:
        v.save_report()

    return 0


if __name__ == "__main__":
    sys.exit(main())