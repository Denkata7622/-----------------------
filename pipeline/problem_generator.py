#!/usr/bin/env python3
"""
problem_generator.py — 2-фазов генератор на задачи.

Phase 1: 9 условия в 1 call (AI калибрира difficulty)
Phase 2: 9 individual call-а (1 per задача) — надеждно за hard
Verify:  Dual verification (DeepSeek + gpt-oss) + arbiter
Retry:   Паралелна регенерация на failed задачи

Употреба:
    python problem_generator.py --point 1.4
    python problem_generator.py --limit 3
    python problem_generator.py --redry
    python problem_generator.py --stats
    python problem_generator.py --reset --point 1.4
"""
import os, re, sys, json, time, logging, argparse, requests, threading
import concurrent.futures
from pathlib import Path
from datetime import datetime, date
from typing import Optional

from personas import PROBLEM_CREATOR, PROBLEM_REVIEWER, ARBITER, MASTER_PERSONA
from regen_compare import (
    regen_with_compare, diff_problems, save_old_version
)

BASE_DIR = Path(__file__).parent.resolve()
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PROBLEM_GEN] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"problem_gen_{date.today()}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("problem_gen")

PROBLEMS_DIR = BASE_DIR / "problems"
PROBLEMS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = BASE_DIR / "output"
HTML_FILE = BASE_DIR.parent / "index.html"
STATE_FILE = BASE_DIR / "problem_state.json"


def load_config():
    with open(BASE_DIR / "config.json", "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config()

# ── cost tracker init ──
from cost_tracker import init as _ct_init, track_call as _track_call
_ct_init(BASE_DIR.parent / "generated" / "costs" / "ledger.jsonl")


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def format_prompt(template: str, **kwargs) -> str:
    """Заменя САМО точно {key} за известните kwargs. Не се чупи от JSON/LaTeX."""
    if not kwargs:
        return template
    pattern = re.compile(r'\{(' + '|'.join(re.escape(k) for k in kwargs) + r')\}')
    return pattern.sub(lambda m: str(kwargs[m.group(1)]), template)


def heartbeat(item_id: str, label: str):
    """Heartbeat thread за видимост при дълги AI call-ове."""
    stop = threading.Event()
    def run():
        t0 = time.time()
        while not stop.wait(20):
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
# AI CLIENT
# ═══════════════════════════════════════════════════════════════
class AIClient:
    def __init__(self, cfg, name="gen"):
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
                if r.status_code >= 500:
                    time.sleep(8 * attempt); continue
                if r.status_code >= 400:
                    log.error(f"[{item_id}] {r.status_code}: {r.text[:300]}")
                    return None
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                _track_call("problem_generator", self.name, self.model, data, item_id=item_id, t0=t0)
                return (content or "").strip() or None
            except Exception as e:
                log.warning(f"[{item_id}] {e}")
                time.sleep(8 * attempt)
        return None


# ═══════════════════════════════════════════════════════════════
# HTML PARSER
# ═══════════════════════════════════════════════════════════════
def find_steps_array(html: str) -> Optional[str]:
    marker = "const STEPS = ["
    start = html.find(marker)
    if start == -1:
        return None
    start += len("const STEPS = ")
    depth = 0
    in_str = False
    quote = None
    escape = False
    for i in range(start, len(html)):
        c = html[i]
        if escape:
            escape = False; continue
        if in_str:
            if c == '\\': escape = True
            elif c == quote: in_str = False
            continue
        if c in ('"', "'", '`'):
            in_str = True; quote = c; continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return html[start:i+1]
    return None


def find_matching_brace(text: str, start: int) -> int:
    depth = 0
    in_str = False
    quote = None
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if escape: escape = False; continue
        if in_str:
            if c == '\\': escape = True
            elif c == quote: in_str = False
            continue
        if c in ('"', "'", '`'):
            in_str = True; quote = c; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return i + 1
    return len(text)


def extract_field(block: str, field: str) -> str:
    # Template literal (backticks)
    m = re.search(rf'\b{field}\s*:\s*`((?:\\.|[^`\\])*)`', block, re.DOTALL)
    if m:
        s = m.group(1)
        s = s.replace('\\`', '`').replace('\\$', '$')
        s = s.replace('\\\\', '\x00BSLASH\x00')
        s = s.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '')
        s = s.replace('\\"', '"').replace("\\'", "'")
        s = s.replace('\x00BSLASH\x00', '\\')
        return s
    # Двойни кавички
    m = re.search(rf'\b{field}\s*:\s*"((?:\\.|[^"\\])*)"', block, re.DOTALL)
    if m:
        s = m.group(1)
        s = s.replace('\\\\', '\x00BSLASH\x00')
        s = s.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
        s = s.replace('\x00BSLASH\x00', '\\')
        return s
    # Единични кавички
    m = re.search(rf"\b{field}\s*:\s*'((?:\\.|[^'\\])*)'", block, re.DOTALL)
    if m:
        s = m.group(1)
        s = s.replace('\\\\', '\x00BSLASH\x00')
        s = s.replace("\\'", "'").replace('\\n', '\n').replace('\\t', '\t')
        s = s.replace('\x00BSLASH\x00', '\\')
        return s
    return ""


def extract_task_labels(block: str) -> list:
    m = re.search(r'\btasks\s*:\s*\[', block)
    if not m:
        return []
    start = m.end() - 1
    depth = 0; in_str = False; quote = None; escape = False
    end = len(block)
    for i in range(start, len(block)):
        c = block[i]
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
    tasks_str = block[start:end]
    labels = re.findall(r'\blabel\s*:\s*"((?:\\.|[^"\\])*)"', tasks_str)
    if not labels:
        labels = re.findall(r"\blabel\s*:\s*'((?:\\.|[^'\\])*)'", tasks_str)
    return [re.sub(r'<[^>]+>', '', l).strip() for l in labels]


def parse_all_points(html: str) -> dict:
    steps_str = find_steps_array(html)
    if not steps_str:
        log.error("Не намерих STEPS масив в HTML")
        return {}
    points = {}
    i = 0
    while i < len(steps_str):
        m = re.search(r'\{\s*id\s*:\s*"([^"]+)"\s*,', steps_str[i:])
        if not m:
            break
        point_start = i + m.start()
        point_id = m.group(1)
        point_end = find_matching_brace(steps_str, point_start)
        block = steps_str[point_start:point_end]
        points[point_id] = {
            "id": point_id,
            "title": extract_field(block, "title"),
            "desc": extract_field(block, "desc"),
            "explanation": extract_field(block, "explanation"),
            "deep_explanation": extract_field(block, "deepExplanation"),
            "tasks": extract_task_labels(block),
        }
        i = point_end
    log.info(f"Намерени {len(points)} точки в HTML")
    return points


def enrich_with_deep_md(point: dict) -> dict:
    safe_id = point["id"].replace(".", "_")
    deep_file = OUTPUT_DIR / safe_id / "deep.md"
    if deep_file.exists():
        try:
            text = deep_file.read_text(encoding="utf-8")
            parts = text.split("---", 1)
            body = parts[1].strip() if len(parts) == 2 else text
            point["deep_explanation"] = body
        except Exception as e:
            log.warning(f"[{point['id']}] не прочетох deep.md: {e}")
    return point


# ═══════════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════════
class ProblemState:
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
            "processed": {},
            "budget": {"date": str(date.today()), "spent_usd": 0.0, "calls": 0},
            "created_at": time.time(),
        }

    def save(self):
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(STATE_FILE)

    def check_budget_reset(self):
        today = str(date.today())
        if self.data["budget"]["date"] != today:
            log.info("Нов ден — рестарт на бюджета")
            self.data["budget"] = {"date": today, "spent_usd": 0.0, "calls": 0}
            self.save()

    def budget_remaining(self) -> float:
        self.check_budget_reset()
        return CONFIG["daily_budget_usd"] - self.data["budget"]["spent_usd"]

    def budget_exceeded(self) -> bool:
        limit = CONFIG["daily_budget_usd"] * CONFIG["budget_stop_pct"]
        return self.data["budget"]["spent_usd"] >= limit

    def add_cost(self, usd: float):
        self.data["budget"]["spent_usd"] += usd
        self.data["budget"]["calls"] += 1
        self.save()

    def is_done(self, point_id: str) -> bool:
        return self.data["processed"].get(point_id, {}).get("status") == "done"

    def mark_done(self, point_id: str, cost: float, shipped: int, total: int):
        self.data["processed"][point_id] = {
            "status": "done",
            "cost": cost,
            "shipped": shipped,
            "total": total,
            "ts": time.time(),
        }
        self.save()


# ═══════════════════════════════════════════════════════════════
# PROMPTS
# ═══════════════════════════════════════════════════════════════
CONDITIONS_PROMPT = PROBLEM_CREATOR + """

═══ КОНТЕКСТ НА ПЛАНА ═══
- Тема: {title}
- ID: {point_id}
- Описание: {desc}
- Фаза: {phase} ({focus}), седмица {week}/25
- Дни до областен: {days_to_regional}
- Дни до национален: {days_to_national}

═══ ТЕОРИЯ (която ученикът вече е чел) ═══
{deep_explanation}

═══ РЕАЛНИ ОЛИМПИАДНИ ЗАДАЧИ ПО ТЕМАТА (от минали области/национални) ═══
{source_problems}

═══ КАК ДА ИЗПОЛЗВАШ ТЕЗИ ЗАДАЧИ ═══
Горните задачи са ИСТИНСКИ от български олимпиади по ТАЗИ тема. Те са твоят
камертон за стил, дължина, сложност и начин на формулиране. Генерирай своите
9 задачи така, че ученик, който е виждал реалните, да не усети разлика.

- Стил: "Да се намерят всички стойности на...", "Докажете, че...", "В триъгълник ABC с..."
- Дължина: 2-4 реда условие (колкото реалните)
- Числа: конкретни (2018, √3, 60°), не "гладки" (a=1, b=2)
- Трудност: ако реалните изискват 2-3 стъпки, твоите също

═══ ЗАДАЧА: ГЕНЕРИРАЙ САМО УСЛОВИЯТА ═══
Генерирай ТОЧНО 9 условия (без решения, без hints) с правилна калибрация:
- 3 easy (5-8 мин, 1-2 стъпки, директно приложение)
- 3 medium (15-20 мин, 2-3 стъпки, изисква insight)
- 3 hard (30+ мин, олимпиадна, може да комбинира техники)

═══ КРИТИЧНО ЗА КАЛИБРАЦИЯТА ═══
Преди да финализираш, СРАВНИ деветте задачи една с друга:
- Твоята "easy" наистина ли е по-лесна от твоята "medium"?
- Твоята "hard" наистина ли е най-трудната?
- Ако подредиш 9-те по трудност, редът съвпада ли с групите?

За всяка задача добави `difficulty_reasoning` — защо е точно това ниво.

═══ ФОРМАТ (САМО JSON) ═══
{
  "problems": [
    {
      "num": 1,
      "difficulty": "easy",
      "problem": "Условие (LaTeX между $...$)",
      "estimated_minutes": 5,
      "difficulty_reasoning": "Защо е easy спрямо останалите 8",
      "tests_misconception": "Кое недоразумение тества"
    }
  ]
}

ПРАВИЛА:
- Точно 9 задачи с nums 1..9
- 3 easy (nums 1-3), 3 medium (nums 4-6), 3 hard (nums 7-9)
- НЕ включвай решения — само условия
- НЕ слагай markdown обвивка около JSON-а
"""


SOLUTIONS_TEMPLATE = """
Получаваш {n_conditions} задачи от ниво **{difficulty}** по тема "{topic}".
Условията са вече калибрирани — НЕ ги променяй.

═══ ЗА ВСЯКА ЗАДАЧА ═══
1. Пълно решение стъпка по стъпка — ВСЯКА стъпка обоснована.
   Без „очевидно", без „следва директно", без „лесно се вижда".
2. Краен отговор, проверим с конкретни числа.
   Пусни проверката преди да го напишеш. Ако не минава — върни UNSOLVABLE.
3. Проверка на edge cases: D=0, x=0, знаменател=0, равни корени, ъгъл=90° —
   всички случаи, които чупят формулата. Спомени ги изрично в решението.
4. 3 hints, подредени по нарастваща конкретност:
   - hint 1: посока („помисли за...", без да разкрива техниката)
   - hint 2: конкретна техника/метод
   - hint 3: почти решение
   НЕ слагай цялото решение в hint 3.

═══ УСЛОВИЯ ═══
{conditions_text}

═══ ФОРМАТ (САМО JSON) ═══
{{
  "solutions": [
    {{
      "num": 1,
      "solution": "Пълно решение...",
      "answer": "Краен отговор",
      "hints": ["hint 1", "hint 2", "hint 3"]
    }}
  ]
}}

═══ АКО НЕ МОЖЕШ ДА РЕШИШ ЗАДАЧАТА ═══
Върни:
{{
  "solutions": [
    {{
      "num": 1,
      "solution": "UNSOLVABLE",
      "unsolvable_reason": "конкретна причина (не 'трудно е')",
      "answer": "N/A",
      "hints": []
    }}
  ]
}}

По-добре UNSOLVABLE, отколкото 500 реда rambling без ясен отговор.

═══ ПРАВИЛА ═══
- LaTeX: $...$ inline
- НЕ слагай markdown обвивка около JSON-а (без ```json)
- Решението валидно за ВСИЧКИ случаи
"""


REGEN_ONE_PROMPT = PROBLEM_CREATOR + """

═══ КОНТЕКСТ ═══
- Тема: {title}
- ID: {point_id}
- Описание: {desc}
- Фаза: {phase} ({focus}), седмица {week}/25

═══ ТЕОРИЯ ═══
{deep_explanation}

═══ ТЕКУЩА ЗАДАЧА (която трябва да ПОДОБРИШ) ═══
Задача #{num}, difficulty: {difficulty}.

Условие:
{original_problem}

Решение:
{original_solution}

═══ ПРОБЛЕМИ (от verifier) ═══
{issues}

═══ ИНСТРУКЦИИ ═══
НЕ преписвай от нула. Само коригирай конкретните проблеми:
- Ако проблемът е "сгрешен отговор" → поправи само решението
- Ако проблемът е "не покрива edge case" → добави липсващите случаи
- Ако проблемът е "не е по темата" → смени задачата (тук е ок от нула)
- Ако проблемът е "difficulty не е калибриран" → смени само нивото или опрости/усложни

═══ ФОРМАТ (САМО JSON) ═══
{{
  "problems": [{{
    "num": {num},
    "difficulty": "{difficulty}",
    "problem": "...",
    "estimated_minutes": N,
    "solution": "...",
    "answer": "...",
    "hints": ["h1", "h2", "h3"],
    "difficulty_reasoning": "...",
    "tests_misconception": "..."
  }}]
}}
"""

VERIFICATION_PROMPT = PROBLEM_REVIEWER + """

═══ КОНТЕКСТ ═══
Точка: {point_id} — {title}
Ниво: {difficulty_note}

═══ ЗАДАЧИ ЗА ОЦЕНКА ═══
{problems_json}

═══ ЗА ВСЯКА ЗАДАЧА ═══
1. РЕШИ Я САМ (в главата си). Провери дали твоето решение съвпада с даденото.
2. Провери отговора с конкретни числа.
3. Провери edge cases.
4. Реши я БЕЗ техниката на урока — ако може, не е по темата.
5. Виж hints: помагат ли реално?

═══ ФОРМАТ (САМО JSON) ═══
{
  "results": {
    "1": {
      "score": 8,
      "solvable": true,
      "solution_correct": true,
      "topic_match": "exact",
      "difficulty_calibrated": true,
      "hints_quality": 8,
      "issues": [],
      "can_ship": true
    },
    "2": {
      "score": 6,
      "solvable": true,
      "solution_correct": true,
      "topic_match": "partial",
      "difficulty_calibrated": false,
      "hints_quality": 5,
      "issues": ["medium е всъщност hard"],
      "can_ship": false
    }
  },
  "summary": {
    "avg_score": 7.5,
    "shipped": 7,
    "rejected": 2,
    "recommendation": "ship"
  }
}

ПРАВИЛА:
- solution_correct=false → score max 3, can_ship=false
- topic_match=off → score max 5, can_ship=false
- difficulty_calibrated=false → score max 7
- can_ship = (score>=7 AND solvable AND solution_correct AND topic_match!=off)
- СТРОГ. Не давай 8+ без основание.
"""


# ═══════════════════════════════════════════════════════════════
# GENERATION
# ═══════════════════════════════════════════════════════════════
def _build_base_context(point: dict, plan_ctx: dict) -> dict:
    deep = point.get("deep_explanation", "")[:6000]
    if not deep:
        deep = point.get("explanation", "")[:3000]
    if not deep:
        deep = "(няма теория — генерирай по заглавие и описание)"

    source = "\n".join(f"  • {t}" for t in point.get("tasks", [])[:10])
    if not source:
        source = "(няма реални задачи — генерирай типични)"

    # Real problems от pdf_chunker (anchors)
    real_problems_text = "(няма реални задачи — генерирай типични)"
    real_file = BASE_DIR.parent / "generated" / "anchors" / f"{point['id'].replace('.', '_')}.json"
    if real_file.exists():
        try:
            real_data = json.loads(real_file.read_text(encoding="utf-8"))
            probs = real_data.get("problems", [])
            if probs:
                # Взимаме до 6 (за да не взривим контекста)
                sample = probs[:6]
                lines = []
                for i, p in enumerate(sample, 1):
                    stmt = (p.get("statement") or "")[:600]
                    src = p.get("source", "?")
                    lines.append(f"  {i}. [{src}]\n     {stmt}")
                real_problems_text = "\n".join(lines)
                log.info(f"[{point['id']}] {len(probs)} real problems loaded as anchors")
        except Exception as e:
            log.warning(f"[{point['id']}] real_problems read fail: {e}")

    return {
        "title": point["title"],
        "point_id": point["id"],
        "desc": point.get("desc", "")[:500],
        "phase": plan_ctx["phase"],
        "focus": plan_ctx["focus"],
        "week": plan_ctx["week"],
        "days_to_regional": plan_ctx["days_to_regional"],
        "days_to_national": plan_ctx["days_to_national"],
        "deep_explanation": deep,
        "source_problems": real_problems_text, 
    }


def _gen_conditions(ai_gen: AIClient, point: dict, plan_ctx: dict) -> list:
    """Phase 1: 9 условия в 1 call (AI калибрира difficulty)."""
    user = format_prompt(CONDITIONS_PROMPT, **_build_base_context(point, plan_ctx))

    log.info(f"[{point['id']}] PHASE 1: генерирам 9 условия...")
    hb = heartbeat(point["id"], "phase 1")
    t0 = time.time()
    try:
        raw = ai_gen.call(CONDITIONS_PROMPT, user, f"{point['id']}-cond")
    finally:
        hb.set()
    dur = int(time.time() - t0)

    if not raw:
        log.error(f"[{point['id']}] PHASE 1 failed ({dur}s)")
        return []

    parsed = parse_json(raw)
    if not parsed or "problems" not in parsed:
        log.error(f"[{point['id']}] PHASE 1 JSON parse failed ({dur}s)")
        return []

    conditions = parsed["problems"]
    log.info(f"[{point['id']}] PHASE 1 готово: {len(conditions)} условия ({dur}s)")

    by_diff = {"easy": [], "medium": [], "hard": []}
    for c in conditions:
        by_diff.setdefault(c.get("difficulty", "?"), []).append(c.get("num", "?"))
    log.info(f"[{point['id']}] калибрация: easy={by_diff.get('easy', [])}, "
             f"medium={by_diff.get('medium', [])}, hard={by_diff.get('hard', [])}")

    expected = set(range(1, 10))
    found = {c.get("num") for c in conditions if isinstance(c.get("num"), int)}
    missing = expected - found
    if missing:
        log.warning(f"[{point['id']}] липсват nums {sorted(missing)} — генерирам ги")
        extra = _gen_missing_conditions(ai_gen, point, plan_ctx, sorted(missing), conditions)
        conditions.extend(extra)

    conditions.sort(key=lambda c: c.get("num", 999))
    return conditions


def _gen_missing_conditions(ai_gen, point, plan_ctx, missing_nums, existing):
    diff_map = {1:"easy",2:"easy",3:"easy",4:"medium",5:"medium",6:"medium",7:"hard",8:"hard",9:"hard"}
    missing_desc = ", ".join(f"{n} ({diff_map.get(n, '?')})" for n in missing_nums)

    existing_summary = "\n".join(
        f"  #{c.get('num')} ({c.get('difficulty')}): {c.get('problem', '')[:80]}"
        for c in existing[:6]
    )

    user = format_prompt(CONDITIONS_PROMPT, **_build_base_context(point, plan_ctx)) + f"""

═══ ВЕЧЕ СЪЗДАДЕНИ (не ги дублирай) ═══
{existing_summary}

═══ ЛИПСВАЩИ ЗАДАЧИ ═══
Липсват nums: {missing_desc}

Генерирай САМО тези {len(missing_nums)} задачи (със същите nums и difficulty).
Формат: {{"problems": [...]}}
"""

    log.info(f"[{point['id']}] fill missing: {missing_nums}")
    hb = heartbeat(point["id"], "fill missing")
    try:
        raw = ai_gen.call(CONDITIONS_PROMPT, user, f"{point['id']}-fill")
    finally:
        hb.set()

    if not raw:
        return []
    parsed = parse_json(raw)
    if not parsed or "problems" not in parsed:
        return []
    return parsed["problems"]


# ═══════════════════════════════════════════════════════════════
# PHASE 2: SOLUTIONS (per-problem parallel)
# ═══════════════════════════════════════════════════════════════
def _gen_one_solution(ai_gen, point, condition):
    """1 AI call за 1 задача. Не се засича от max_tokens."""
    difficulty = condition.get("difficulty", "medium")
    num = condition.get("num")

    user = SOLUTIONS_TEMPLATE.format(
        n_conditions=1,
        difficulty=difficulty,
        topic=point["title"],
        conditions_text=f"### Задача {num}\n{condition.get('problem')}",
    )

    log.info(f"[{point['id']}] PHASE 2 #{num} ({difficulty}) старт...")
    t0 = time.time()
    raw = ai_gen.call(MASTER_PERSONA, user, f"{point['id']}-{difficulty}-{num}-sol")
    dur = int(time.time() - t0)

    if not raw:
        log.error(f"[{point['id']}] PHASE 2 #{num} ({difficulty}) fail ({dur}s)")
        return None

    parsed = parse_json(raw)
    if not parsed or "solutions" not in parsed or not parsed["solutions"]:
        log.error(f"[{point['id']}] PHASE 2 #{num} JSON fail ({dur}s)")
        return None

    sol = parsed["solutions"][0]
    sol["num"] = num  # ensure correct num

    if sol.get("solution") == "UNSOLVABLE":
        log.warning(f"[{point['id']}] PHASE 2 #{num} UNSOLVABLE: {sol.get('unsolvable_reason', '?')}")
        return None

    log.info(f"[{point['id']}] PHASE 2 #{num} ({difficulty}) OK ({dur}s)")
    return sol


def _run_phase2_parallel(ai_gen, point, conditions):
    """Phase 2: 1 call per задача, всички паралелни."""
    if not conditions:
        return {}

    log.info(f"[{point['id']}] PHASE 2: {len(conditions)} individual call-а...")
    solutions_by_num = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(6, len(conditions))) as pool:
        futures = {
            pool.submit(_gen_one_solution, ai_gen, point, c): c.get("num")
            for c in conditions
        }
        for fut in concurrent.futures.as_completed(futures):
            num = futures[fut]
            try:
                sol = fut.result()
                if sol:
                    solutions_by_num[num] = sol
            except Exception as e:
                log.error(f"[{point['id']}] PHASE 2 #{num} exception: {e}")

    missing = [c for c in conditions if c.get("num") not in solutions_by_num]
    if missing:
        log.warning(f"[{point['id']}] липсват {len(missing)} решения — retry 1 "
                    f"nums {[c['num'] for c in missing]}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(missing))) as pool:
            futures = {
                pool.submit(_gen_one_solution, ai_gen, point, c): c.get("num")
                for c in missing
            }
            for fut in concurrent.futures.as_completed(futures):
                num = futures[fut]
                try:
                    sol = fut.result()
                    if sol:
                        solutions_by_num[num] = sol
                        log.info(f"[{point['id']}] PHASE 2 retry #{num} OK")
                except Exception:
                    pass

    return solutions_by_num


def generate_problems(ai_gen: AIClient, point: dict, plan_ctx: dict) -> Optional[dict]:
    """2-фазов генератор: Phase 1 (условия) + Phase 2 (решения per-problem)."""
    conditions = _gen_conditions(ai_gen, point, plan_ctx)
    if not conditions:
        return None

    solutions_by_num = _run_phase2_parallel(ai_gen, point, conditions)

    merged = []
    for c in conditions:
        num = c.get("num")
        sol = solutions_by_num.get(num, {})
        merged.append({
            "num": num,
            "difficulty": c.get("difficulty", "?"),
            "problem": c.get("problem", ""),
            "estimated_minutes": c.get("estimated_minutes", 10),
            "difficulty_reasoning": c.get("difficulty_reasoning", ""),
            "tests_misconception": c.get("tests_misconception", ""),
            "solution": sol.get("solution", ""),
            "answer": sol.get("answer", ""),
            "hints": sol.get("hints", []),
        })

    missing_sol = [p["num"] for p in merged if not p.get("solution")]
    if missing_sol:
        log.warning(f"[{point['id']}] без решение: {missing_sol}")

    log.info(f"[{point['id']}] генерирани {len(merged)} задачи (условия + решения)")
    return {"problems": merged}


# ═══════════════════════════════════════════════════════════════
# REGEN
# ═══════════════════════════════════════════════════════════════
def _regen_one_full_problem(ai_gen, point, num, difficulty, original=None, issues=""):
    """Регенерира 1 задача с конкретни инструкции от verifier."""
    user = format_prompt(
        REGEN_ONE_PROMPT,
        **_build_base_context(point, get_plan_context()),
        num=num,
        difficulty=difficulty,
        original_problem=(original.get("problem", "") if original else "(няма — генерирай нова)")[:2000],
        original_solution=(original.get("solution", "") if original else "(няма)")[:2000],
        issues=issues or "verifier не е специфицирал конкретен проблем — подобри общото качество",
    )

    log.info(f"[{point['id']}] regen #{num} ({difficulty})")
    hb = heartbeat(point["id"], f"regen #{num}")
    try:
        raw = ai_gen.call(REGEN_ONE_PROMPT, user, f"{point['id']}-regen-{num}")
    finally:
        hb.set()

    if not raw:
        return None
    parsed = parse_json(raw)
    if not parsed or "problems" not in parsed or not parsed["problems"]:
        return None
    return parsed["problems"][0]


def regenerate_failed(ai_gen, point, problems, failed_nums, plan_ctx, ver_result=None):
    """Паралелна регенерация на failed задачи. Max 4 едновременно."""
    if not failed_nums:
        return {"problems": []}

    tasks = []
    for num in failed_nums:
        old = next((p for p in problems if p.get("num") == num), None)
        difficulty = old.get("difficulty", "medium") if old else "medium"
        issues = ""
        if ver_result:
            v = ver_result.get("results", {}).get(str(num), {})
            issues_list = v.get("issues", [])
            issues = "; ".join(issues_list) if issues_list else ""
        tasks.append((num, difficulty, old, issues))

    log.info(f"[{point['id']}] регенерирам паралелно {len(tasks)} задачи: {failed_nums}")

    regenerated = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(tasks))) as pool:
        futures = {
            pool.submit(_regen_one_full_problem, ai_gen, point, num, diff, old, issues): (num, diff)
            for num, diff, old, issues in tasks
        }
        for fut in concurrent.futures.as_completed(futures):
            num, diff = futures[fut]
            try:
                new_p = fut.result()
                if new_p:
                    regenerated.append(new_p)
                    log.info(f"[{point['id']}] regen #{num} ({diff}) OK")
                else:
                    log.warning(f"[{point['id']}] regen #{num} ({diff}) failed")
            except Exception as e:
                log.error(f"[{point['id']}] regen #{num} exception: {e}")

    return {"problems": regenerated}


# ═══════════════════════════════════════════════════════════════
# DUAL VERIFICATION + ARBITER
# ═══════════════════════════════════════════════════════════════
def _arbitrate_disagreements(ai_arbiter, point, problems, disagreements):
    """1 AI call за всички разногласия. Връща {num: verdict}."""
    if not disagreements:
        return {}

    context = ""
    for d in disagreements:
        num = d["num"]
        prob = next((p for p in problems if p.get("num") == num), {})
        context += f"""

═══ ЗАДАЧА #{num} ({prob.get('difficulty', '?')}) ═══
Условие: {prob.get('problem', '')[:600]}
Решение: {prob.get('solution', '')[:1000]}
Отговор: {prob.get('answer', '')}
Hints: {prob.get('hints', [])}

Verifier 1 (DeepSeek) прецени:
  score: {d['v1'].get('score')}, can_ship: {d['v1'].get('can_ship')}
  issues: {d['v1'].get('issues', [])}

Verifier 2 (gpt-oss) прецени:
  score: {d['v2'].get('score')}, can_ship: {d['v2'].get('can_ship')}
  issues: {d['v2'].get('issues', [])}
"""

    nums_list = ", ".join(f'"{d["num"]}": {{...}}' for d in disagreements)

    user = ARBITER + f"""

═══ РАЗНОГЛАСИЯ ({len(disagreements)} задачи) ═══
{context}

═══ ТВОЯТА ЗАДАЧА ═══
За всяка задача реши кой е прав. Върни САМО JSON:
{{
  "results": {{
    {nums_list}
  }}
}}

За всяка задача:
{{
  "score": 1-10,
  "solvable": true|false,
  "solution_correct": true|false,
  "topic_match": "exact|partial|off",
  "difficulty_calibrated": true|false,
  "hints_quality": 1-10,
  "issues": [],
  "can_ship": true|false,
  "arbiter_reasoning": "Защо този verdict (1-2 изречения)"
}}

═══ КРИТИЧНО: КАК ИЗГЛЕЖДА UNSOLVABLE ═══
Ако задачата е твърде трудна за теб, ИЛИ ако не можеш да намериш чист отговор,
ИЛИ ако решението ти има противоречие — върни:

  "solution": "UNSOLVABLE",
  "answer": "N/A",
  "hints": [],
  "unsolvable_reason": "конкретна причина"

НЕ прави следното:
❌ НЕ започвай един подход, после "всъщност не работи", после друг
❌ НЕ си противоречи в рамките на решението
❌ НЕ завършвай без ясен отговор
❌ НЕ пиши "сега трябва да намерим X, но не знаем как"
❌ НЕ надвишавай 500 думи за решение

ПРАВИЛО: По-добре UNSOLVABLE, отколкото 5000 реда rambling. UNSOLVABLE означава
"не мога", а rambling означава "не мога, но ще ти губя времето".

Ако намериш отговор, но не си 100% сигурен → провери с конкретни числа.
Ако проверката не работи → UNSOLVABLE.
Ако проверката работи → пусни решението.
"""

    log.info(f"[{point['id']}] ⚖ арбитер за {len(disagreements)} разногласия...")
    hb = heartbeat(point["id"], "arbiter")
    t0 = time.time()
    try:
        raw = ai_arbiter.call(ARBITER, user, f"{point['id']}-arb")
    finally:
        hb.set()
    dur = int(time.time() - t0)

    if not raw:
        log.error(f"[{point['id']}] арбитер fail ({dur}s)")
        return {}

    parsed = parse_json(raw)
    if not parsed or "results" not in parsed:
        log.error(f"[{point['id']}] арбитер JSON parse fail ({dur}s)")
        return {}

    log.info(f"[{point['id']}] арбитер готово ({dur}s)")
    return parsed["results"]


def _finalize_verification(results_by_num, dual_meta, arbiter_used):
    """Build final verification dict with summary."""
    shipped = sum(1 for r in results_by_num.values() if r.get("can_ship"))
    rejected = len(results_by_num) - shipped
    scores = [r.get("score", 0) for r in results_by_num.values()]
    avg = round(sum(scores) / len(scores), 1) if scores else 0

    return {
        "results": results_by_num,
        "summary": {
            "avg_score": avg,
            "shipped": shipped,
            "rejected": rejected,
            "arbiter_used": arbiter_used,
            "dual_verified": True,
            **dual_meta,
        }
    }


def verify_problems_dual(ai_ver1, ai_ver2, ai_arbiter, point, problems):
    """Dual verification + arbiter при разногласие."""
    if not problems:
        return None

    log.info(f"[{point['id']}] ⚡ V1(DeepSeek) + V2(gpt-oss) паралелно...")
    t0 = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        f1 = pool.submit(verify_problems, ai_ver1, point, problems)
        f2 = pool.submit(verify_problems, ai_ver2, point, problems)

        try:
            v1 = f1.result(timeout=650)
        except Exception as e:
            log.error(f"[{point['id']}] V1 exception: {e}")
            v1 = None

        try:
            v2 = f2.result(timeout=650)
        except Exception as e:
            log.error(f"[{point['id']}] V2 exception: {e}")
            v2 = None

    dur = int(time.time() - t0)
    log.info(f"[{point['id']}] и двата verifier-а отговориха ({dur}s)")

    if not v1 and not v2:
        log.error(f"[{point['id']}] нито един verifier не отговори")
        return None
    if not v1:
        log.warning(f"[{point['id']}] само V2 — връщам V2 verdict")
        return v2
    if not v2:
        log.warning(f"[{point['id']}] само V1 — връщам V1 verdict")
        return v1

    # Сравнение per-problem
    nums = [p.get("num") for p in problems if p.get("num") is not None]
    disagreements = []
    merged_results = {}
    agree_count = 0

    for num in nums:
        r1 = v1.get("results", {}).get(str(num), {})
        r2 = v2.get("results", {}).get(str(num), {})

        if not r1 or not r2:
            merged_results[str(num)] = r1 or r2
            continue

        ship1 = r1.get("can_ship", False)
        ship2 = r2.get("can_ship", False)
        score1 = r1.get("score", 0)
        score2 = r2.get("score", 0)

        if ship1 == ship2 and abs(score1 - score2) <= 2:
            merged_results[str(num)] = {
                **r1,
                "score": round((score1 + score2) / 2, 1),
                "verifier_agreement": True,
                "v1_score": score1,
                "v2_score": score2,
            }
            agree_count += 1
        else:
            disagreements.append({"num": num, "v1": r1, "v2": r2})

    log.info(f"[{point['id']}] съгласие: {agree_count}/{len(nums)} | разногласия: {len(disagreements)}")

    if not disagreements:
        return _finalize_verification(
            merged_results,
            {"agree_count": agree_count, "disagreement_count": 0},
            arbiter_used=False,
        )

    # Арбитер
    arbiter_results = _arbitrate_disagreements(ai_arbiter, point, problems, disagreements)

    for d in disagreements:
        num_str = str(d["num"])
        arb = arbiter_results.get(num_str, {})
        if arb and "can_ship" in arb:
            merged_results[num_str] = {
                **arb,
                "arbiter_used": True,
                "v1_score": d["v1"].get("score", 0),
                "v2_score": d["v2"].get("score", 0),
            }
        else:
            # Арбитер fail → по-строгият verdict
            strict = d["v1"] if d["v1"].get("score", 10) <= d["v2"].get("score", 10) else d["v2"]
            merged_results[num_str] = {**strict, "arbiter_failed": True}

    return _finalize_verification(
        merged_results,
        {"agree_count": agree_count, "disagreement_count": len(disagreements)},
        arbiter_used=True,
    )


# ═══════════════════════════════════════════════════════════════
# VERIFY
# ═══════════════════════════════════════════════════════════════
def verify_problems(ai_ver: AIClient, point: dict, problems: list) -> Optional[dict]:
    compact = []
    for p in problems:
        compact.append({
            "num": p.get("num"),
            "difficulty": p.get("difficulty"),
            "problem": p.get("problem", ""),
            "solution": p.get("solution", ""),
            "answer": p.get("answer", ""),
            "hints": p.get("hints", []),
        })

    user = format_prompt(
        VERIFICATION_PROMPT,
        point_id=point["id"],
        title=point["title"],
        difficulty_note="easy (5-8 мин) / medium (15-20 мин) / hard (30+ мин)",
        problems_json=json.dumps(compact, ensure_ascii=False, indent=2),
    )

    log.info(f"[{point['id']}] верифицирам {len(problems)} задачи...")
    hb = heartbeat(point["id"], "verify")
    t0 = time.time()
    try:
        raw = ai_ver.call(VERIFICATION_PROMPT, user, point["id"])
    finally:
        hb.set()
    dur = int(time.time() - t0)

    if not raw:
        log.error(f"[{point['id']}] verifier — no response ({dur}s)")
        return None

    parsed = parse_json(raw)
    if not parsed or "results" not in parsed:
        log.error(f"[{point['id']}] verifier JSON parse failed ({dur}s)")
        return None

    log.info(f"[{point['id']}] verifier отговор ({dur}s)")
    return parsed


# ═══════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════
def save_outputs(point: dict, problems: list, verification: dict, meta: dict,
                 ai_evaluator=None, redry: bool = False):
    """Записва изходите с regen-compare ако има стара версия."""
    safe_id = point["id"].replace(".", "_")
    folder = PROBLEMS_DIR / safe_id
    folder.mkdir(exist_ok=True)

    # ─── Build new data (в паметта) ───
    problems_out = []
    for p in problems:
        num = p.get("num")
        v = verification.get("results", {}).get(str(num), {})
        problems_out.append({
            "id": f"{point['id']}-{p.get('difficulty', '?')[:1].upper()}{num}",
            "num": num,
            "difficulty": p.get("difficulty", "?"),
            "problem": p.get("problem", ""),
            "estimated_minutes": p.get("estimated_minutes", 10),
            "difficulty_reasoning": p.get("difficulty_reasoning", ""),
            "status": "shipped" if v.get("can_ship") else "rejected",
            "verification_score": v.get("score", 0),
        })

    new_problems_doc = {
        "point_id": point["id"],
        "point_title": point["title"],
        "generated_at": meta["generated_at"],
        "problems": problems_out,
    }

    solutions = {}
    for p in problems:
        num = p.get("num")
        pid = f"{point['id']}-{p.get('difficulty', '?')[:1].upper()}{num}"
        v = verification.get("results", {}).get(str(num), {})
        solutions[pid] = {
            "solution": p.get("solution", ""),
            "answer": p.get("answer", ""),
            "hints": p.get("hints", []),
            "tests_misconception": p.get("tests_misconception", ""),
            "verified": bool(v.get("can_ship")),
            "verification_score": v.get("score", 0),
        }
    new_solutions_doc = {"point_id": point["id"], "solutions": solutions}

    new_verification_doc = {
        "point_id": point["id"],
        "verified_at": meta.get("verified_at", meta["generated_at"]),
        "verifier_model": meta.get("verifier_model", ""),
        "results": verification.get("results", {}),
        "summary": verification.get("summary", {}),
    }

    # ─── Write functions ───
    def write_all(doc_problems=new_problems_doc,
                  doc_solutions=new_solutions_doc,
                  doc_verification=new_verification_doc):
        (folder / "problems.json").write_text(
            json.dumps(doc_problems, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        (folder / "solutions.json").write_text(
            json.dumps(doc_solutions, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        (folder / "verification.json").write_text(
            json.dumps(doc_verification, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        (folder / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ─── Compare flow (само ако redry и има стара версия) ───
    old_problems_file = folder / "problems.json"

    if redry and old_problems_file.exists() and ai_evaluator is not None:
        try:
            old_problems_doc = json.loads(
                old_problems_file.read_text(encoding="utf-8")
            )

            diff = diff_problems(old_problems_doc, new_problems_doc)

            if diff["total_changed"] == 0 and diff["old_count"] == diff["new_count"]:
                log.info(f"[{point['id']}] 🟰 няма промени — запазвам старата версия")
                shipped = sum(1 for p in problems_out if p["status"] == "shipped")
                log.info(f"✓ [{point['id']}] {shipped}/{len(problems_out)} shipped (old kept)")
                return

            log.info(f"[{point['id']}] 🔍 сравнявам стари vs нови ({diff['total_changed']} промени)...")

            from regen_compare import evaluate, apply_decision, save_old_version

            decision = evaluate(
                old_content=json.dumps(old_problems_doc, ensure_ascii=False, indent=2),
                new_content=json.dumps(new_problems_doc, ensure_ascii=False, indent=2),
                diff=diff,
                ai_client=ai_evaluator,
                context=f"Точка {point['id']} — {point['title']}. Regen сравнение.",
            )

            if decision is None:
                log.warning(f"[{point['id']}] ⚠ evaluator failed — revert")
                return

            action = apply_decision(
                decision=decision,
                folder=folder,
                write_new_fn=write_all,
                files=["problems.json", "solutions.json", "verification.json", "meta.json"],
                filename_for_compare="problems.json",
            )

            if action == "reverted":
                log.info(f"✓ [{point['id']}] ↩ върната стара версия")
                return
            else:
                log.info(f"✓ [{point['id']}] ✓ нова версия ({action})")
                return

        except Exception as e:
            log.exception(f"[{point['id']}] regen compare failed: {e} — revert to safe")
            return

    # ─── Default: записвай директно ───
    write_all()
    shipped = sum(1 for p in problems_out if p["status"] == "shipped")
    log.info(f"✓ [{point['id']}] {shipped}/{len(problems_out)} shipped → {folder}")


# ═══════════════════════════════════════════════════════════════
# PLAN CONTEXT
# ═══════════════════════════════════════════════════════════════
_PLAN_PHASES_CACHE = None

def _phase_from_week(week: int) -> tuple:
    """Чете PLAN_PHASES от data/plan_phases.js, връща (phase_num, focus_label)."""
    global _PLAN_PHASES_CACHE
    if _PLAN_PHASES_CACHE is None:
        phases = []
        try:
            src = (BASE_DIR.parent / "data" / "plan_phases.js").read_text(encoding="utf-8")
            # Намери const PLAN_PHASES = [...]
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
            # Focus label по име на phase
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
    # Fallback към стария hardcode
    if week <= 6: return 1, "Task 1"
    if week <= 12: return 2, "Task 2"
    if week <= 15: return 3, "Task 3+4"
    if week <= 17: return 4, "Simulations"
    return 5, "National"

def get_plan_context() -> dict:
    try:
        html = HTML_FILE.read_text(encoding="utf-8")
    except Exception:
        return {"week": 1, "phase": 1, "days_to_regional": 100, "days_to_national": 200, "focus": "unknown"}

    m = re.search(r"planStartDate:\s*new Date\('([^']+)'", html)
    if not m:
        return {"week": 1, "phase": 1, "days_to_regional": 100, "days_to_national": 200, "focus": "unknown"}

    start = datetime.fromisoformat(m.group(1))
    now = datetime.now()
    week = max(1, (now - start).days // 7 + 1)

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


# ═══════════════════════════════════════════════════════════════
# MAIN PROCESS
# ═══════════════════════════════════════════════════════════════
def process_point(ai_gen, ai_ver1, ai_ver2, ai_arbiter, ai_esc, point, plan_ctx, state, redry=False) -> bool:
    point_id = point["id"]

    if not redry and state.is_done(point_id):
        log.info(f"[{point_id}] skip (готово)")
        return True

    started = time.time()
    total_cost = 0.0
    calls = 0

    # Phase 1+2
    gen_result = generate_problems(ai_gen, point, plan_ctx)
    if not gen_result:
        log.error(f"[{point_id}] generation failed")
        return False
    total_cost += CONFIG["generator"]["cost_per_call_usd"] * 10  # 1 phase1 + 9 phase2
    calls += 10

    problems = gen_result["problems"]
    log.info(f"[{point_id}] {len(problems)} задачи генерирани")

    # Dual verify
    ver_result = verify_problems_dual(ai_ver1, ai_ver2, ai_arbiter, point, problems)
    if not ver_result:
        log.error(f"[{point_id}] dual verification failed")
        return False
    total_cost += CONFIG["verifier"]["cost_per_call_usd"] + CONFIG["verifier_2"]["cost_per_call_usd"]
    calls += 2
    if ver_result.get("summary", {}).get("arbiter_used"):
        total_cost += CONFIG["arbiter"]["cost_per_call_usd"]
        calls += 1

    # Retry loop — 1 път
    retries = 0
    while retries < 1:
        results = ver_result.get("results", {})
        failed_nums = [int(num) for num, r in results.items() if not r.get("can_ship", False)]
        if not failed_nums:
            break

        log.info(f"[{point_id}] retry 1/1 за задачи {failed_nums}")

        regen = regenerate_failed(ai_esc, point, problems, failed_nums, plan_ctx, ver_result)
        if not regen or not regen.get("problems"):
            break
        total_cost += CONFIG["generator"]["cost_per_call_usd"] * len(failed_nums)
        calls += len(failed_nums)

        for new_p in regen["problems"]:
            num = new_p.get("num")
            for i, old_p in enumerate(problems):
                if old_p.get("num") == num:
                    problems[i] = new_p
                    break

        re_ver = verify_problems_dual(
            ai_ver1, ai_ver2, ai_arbiter, point,
            [p for p in problems if p.get("num") in failed_nums]
        )
        if re_ver:
            total_cost += CONFIG["verifier"]["cost_per_call_usd"] + CONFIG["verifier_2"]["cost_per_call_usd"]
            calls += 2
            ver_result["results"].update(re_ver.get("results", {}))
            all_results = ver_result["results"].values()
            ver_result["summary"] = {
                "avg_score": round(sum(r.get("score", 0) for r in all_results) / len(all_results), 1),
                "shipped": sum(1 for r in all_results if r.get("can_ship")),
                "rejected": sum(1 for r in all_results if not r.get("can_ship")),
                "dual_verified": True,
            }
        retries += 1

    duration = time.time() - started
    meta = {
        "point_id": point_id,
        "generated_at": datetime.now().isoformat(),
        "verified_at": datetime.now().isoformat(),
        "model_gen": CONFIG["generator"]["model"],
        "model_ver1": CONFIG["verifier"]["model"],
        "model_ver2": CONFIG["verifier_2"]["model"],
        "model_arbiter": CONFIG["arbiter"]["model"],
        "cost_usd": round(total_cost, 4),
        "calls": calls,
        "duration_sec": round(duration, 1),
        "retries": retries,
        "arbiter_used": ver_result.get("summary", {}).get("arbiter_used", False),
    }
    save_outputs(point, problems, ver_result, meta, ai_evaluator=ai_ver1, redry=redry)

    shipped = ver_result.get("summary", {}).get("shipped", 0)
    total = len(problems)
    state.mark_done(point_id, total_cost, shipped, total)
    state.add_cost(total_cost)

    arb = " ⚖" if meta["arbiter_used"] else ""
    log.info(f"[{point_id}] Готово за {duration:.1f}s{arb} | ${total_cost:.4f} | {shipped}/{total} shipped")
    return True


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════
def cmd_stats():
    if not PROBLEMS_DIR.exists():
        print("Няма problems/ директория"); return

    folders = [f for f in PROBLEMS_DIR.iterdir() if f.is_dir()]
    total_problems = 0
    total_shipped = 0
    total_cost = 0.0

    print()
    print("═" * 65)
    print(f"  {'POINT':8s}  {'SHIPPED':>8s}  {'TOTAL':>6s}  {'COST':>8s}  STATUS")
    print("─" * 65)

    for folder in sorted(folders):
        point_id = folder.name.replace("_", ".")
        meta_file = folder / "meta.json"
        ver_file = folder / "verification.json"

        if not meta_file.exists():
            status = "no meta"; shipped, total = 0, 0
        else:
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                ver = json.loads(ver_file.read_text(encoding="utf-8")) if ver_file.exists() else {}
                summary = ver.get("summary", {})
                shipped = summary.get("shipped", 0)
                total = shipped + summary.get("rejected", 0)
                total_cost += meta.get("cost_usd", 0)
                total_problems += total
                total_shipped += shipped
                status = "✓" if shipped >= 7 else ("⚠" if shipped > 0 else "✗")
            except Exception as e:
                status = f"error: {e}"; shipped, total = 0, 0

        print(f"  {point_id:8s}  {shipped:>8d}  {total:>6d}  ${total_cost:>7.3f}  {status}")

    print("─" * 65)
    print(f"  TOTAL: {total_shipped}/{total_problems} shipped | ${total_cost:.3f}")
    print("═" * 65)


def cmd_reset(point_id: Optional[str] = None):
    if point_id:
        folder = PROBLEMS_DIR / point_id.replace(".", "_")
        if folder.exists():
            for f in folder.glob("*.json"):
                f.unlink()
            print(f"✓ Изчистени файлове за {point_id}")
        state = ProblemState()
        if point_id in state.data["processed"]:
            del state.data["processed"][point_id]
            state.save()
    else:
        if PROBLEMS_DIR.exists():
            import shutil
            shutil.rmtree(PROBLEMS_DIR)
            PROBLEMS_DIR.mkdir()
        STATE_FILE.unlink(missing_ok=True)
        print("✓ Всичко изчистено")


def main():
    ap = argparse.ArgumentParser(description="Генератор на задачи")
    ap.add_argument("--point", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--redry", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()

    if args.stats:
        cmd_stats(); return
    if args.reset:
        cmd_reset(args.point); return

    steps_js = BASE_DIR.parent / "data" / "steps.js"
    if steps_js.exists():
        log.info(f"Чета STEPS от {steps_js}")
        html = steps_js.read_text(encoding="utf-8")
    elif HTML_FILE.exists():
        log.info(f"Чета STEPS от {HTML_FILE}")
        html = HTML_FILE.read_text(encoding="utf-8")
    else:
        log.error(f"Липсва и {steps_js}, и {HTML_FILE}"); sys.exit(1)

    all_points = parse_all_points(html)
    if not all_points:
        log.error("Не намерих точки в HTML"); sys.exit(1)

    for pid in all_points:
        all_points[pid] = enrich_with_deep_md(all_points[pid])

    if args.point:
        if args.point not in all_points:
            log.error(f"Точка {args.point} не е намерена")
            sys.exit(1)
        points = [all_points[args.point]]
    else:
        points = list(all_points.values())

    if args.limit:
        points = points[:args.limit]

    log.info(f"Ще обработя {len(points)} точки")

    # Override max_tokens само за problem_generator.
    # Статиите (pipeline.py) продължават да ползват 24000 от config.json.
    gen_cfg = dict(CONFIG["generator"])
    gen_cfg["max_tokens"] = 14000
    gen_cfg["temperature"] = 0.15   # за математика — ниско
    ai_gen = AIClient(gen_cfg, "gen")

    # Two parallel verifiers
    ver1_cfg = dict(CONFIG["verifier"])
    ver1_cfg["max_tokens"] = 12000
    ver1_cfg["temperature"] = 0.1
    ai_ver1 = AIClient(ver1_cfg, "ver1")

    ver2_cfg = dict(CONFIG["verifier_2"])
    ver2_cfg["max_tokens"] = 12000
    ver2_cfg["temperature"] = 0.1
    ai_ver2 = AIClient(ver2_cfg, "ver2")

    # Arbiter
    arb_cfg = dict(CONFIG["arbiter"])
    arb_cfg["max_tokens"] = 10000
    ai_arbiter = AIClient(arb_cfg, "arb")
    esc_cfg = dict(CONFIG["escalation"])
    ai_esc = AIClient(esc_cfg, "esc")
    
    state = ProblemState()
    plan_ctx = get_plan_context()

    log.info(f"Plan: Week {plan_ctx['week']}/25, Phase {plan_ctx['phase']} ({plan_ctx['focus']})")
    log.info(f"Дни до областен: {plan_ctx['days_to_regional']}, до национален: {plan_ctx['days_to_national']}")
    log.info(f"Бюджет днес: ${state.budget_remaining():.2f} / ${CONFIG['daily_budget_usd']:.2f}")
    log.info("═" * 60)

    success = 0
    failed = 0

    for i, point in enumerate(points, 1):
        if state.budget_exceeded():
            log.warning(f"⚠ Бюджет достигнат. Спирам.")
            break

        log.info(f"\n[{i}/{len(points)}] {point['id']} — {point['title']}")
        try:
            if process_point(ai_gen, ai_ver1, ai_ver2, ai_arbiter, ai_esc, point, plan_ctx, state, redry=args.redry):
                success += 1
            else:
                failed += 1
        except Exception as e:
            log.exception(f"[{point['id']}] {e}")
            failed += 1

    log.info("\n" + "═" * 60)
    log.info(f"КРАЙ: {success} успешни, {failed} грешки")
    log.info(f"Бюджет: ${state.data['budget']['spent_usd']:.3f} / ${CONFIG['daily_budget_usd']:.2f}")
    log.info("═" * 60)

    cmd_stats()


if __name__ == "__main__":
    main()