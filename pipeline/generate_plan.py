#!/usr/bin/env python3
"""
generate_plan.py — ЕДИН файл за перфектен учебен план.

Прави всичко:
  1. Чете 11 кл областни + National 9-12 (probs + sols)
  2. Pruning от най-старите години при token cap
  3. Един API call: analyze toolkit + design 25-week plan
  4. Валидация (критично vs warning)
  5. Backup на всичко (timestamp)
  6. Опционално apply на новия toolkit
  7. Retry с prompt caching (95% discount)

Model:  openai/gpt-6.1-sol
Effort: reasoning_effort: max
Output: max_tokens = 100,000

Usage:
    python generate_plan.py --dry-run
    python generate_plan.py
    python generate_plan.py --apply-toolkit
    python generate_plan.py --retry-from prompt_cache/last.json --extra "..."
    python generate_plan.py --force
    python generate_plan.py --restore
    python generate_plan.py --restore-toolkit
    python generate_plan.py --restore-all
"""
import sys
import io
import json
import re
import argparse
import hashlib
import shutil
from pathlib import Path
from datetime import date, datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = Path(__file__).parent.resolve()
ROOT = BASE.parent
DATA = ROOT / "data"
CACHE_DIR = BASE / ".pdf_text_cache"
PROMPT_CACHE = BASE / "prompt_cache"
PROMPT_CACHE.mkdir(exist_ok=True)
AUDIT_DIR = ROOT / "generated" / "audit"
STATE_DIR = ROOT / "generated" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
MODEL = "openai/gpt-6.1-sol"
REASONING_EFFORT = "max"
MAX_OUTPUT_TOKENS = 100_000
EST_OUTPUT_TOKENS = 50_000
INPUT_TOKEN_CAP = 270_000
HARD_INPUT_CAP = 900_000
HARD_COST_CAP_USD = 1.80
DOUBLE_RATE_THRESHOLD = 272_000
RATE_INPUT = 0.000002
RATE_OUTPUT = 0.000010
RATE_DOUBLE_INPUT = 0.000004
RATE_DOUBLE_OUTPUT = 0.000015
RATE_CACHED_INPUT = 0.0000001
TOTAL_WEEKS = 25


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def extract_year(name):
    m = re.search(r'(\d{4})', name)
    return int(m.group(1)) if m else 0


def timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def measure_tokens(texts):
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        return sum(len(enc.encode(t)) for t in texts)
    except ImportError:
        return sum(len(t) // 2 for t in texts)


def calc_cost(tokens, cached=0, output_tokens=EST_OUTPUT_TOKENS):
    if tokens > DOUBLE_RATE_THRESHOLD:
        in_cost = tokens * RATE_DOUBLE_INPUT
        out_cost = output_tokens * RATE_DOUBLE_OUTPUT
        label = f"DOUBLE (>{DOUBLE_RATE_THRESHOLD // 1000}K)"
    else:
        fresh = tokens - cached
        in_cost = fresh * RATE_INPUT + cached * RATE_CACHED_INPUT
        out_cost = output_tokens * RATE_OUTPUT
        label = f"standard" + (f" + {cached:,} cached" if cached else "")
    return in_cost + out_cost, label


def safe_write(path, content):
    """Записва файл с backup ако съществува."""
    path = Path(path)
    if path.exists():
        backup = path.with_suffix(f".backup-{timestamp()}{path.suffix}")
        shutil.copy2(path, backup)
        print(f"  ✓ Backup: {backup.name}")
    path.write_text(content, encoding="utf-8")


# ═══════════════════════════════════════════════════════════════
# FILE SELECTION
# ═══════════════════════════════════════════════════════════════
def collect_files(skip_probs=False):
    """Събира 11 кл областни + National 9-12 от cache."""
    files = []
    skipped = 0
    for f in CACHE_DIR.glob("*.txt"):
        stem = f.stem
        if skip_probs and "-probs" in stem:
            skipped += 1
            continue
        is_11kl_reg = "Областен" in stem and "11 кл" in stem
        is_national = "Национален" in stem and "9-12 кл" in stem
        if is_11kl_reg or is_national:
            files.append(f)
    if skipped:
        print(f"   Skipped -probs: {skipped}")
    return sorted(files, key=lambda f: (-extract_year(f.stem), f.name))


def prune(files, max_tokens, texts):
    """Реже от най-старите години докато стигне под max_tokens."""
    by_year = {}
    for f in files:
        by_year.setdefault(extract_year(f.stem), []).append(f)

    selected = list(files)
    excluded = []
    tokens = measure_tokens([texts[f] for f in selected])
    chars = sum(len(texts[f]) for f in selected)

    if tokens <= max_tokens:
        return selected, excluded, tokens, chars

    print(f"\n✂ Pruning: {tokens:,} > {max_tokens:,}")
    for year in sorted(by_year.keys()):
        if tokens <= max_tokens:
            break
        dt = measure_tokens([texts[f] for f in by_year[year]])
        dc = sum(len(texts[f]) for f in by_year[year])
        for f in by_year[year]:
            selected.remove(f)
            excluded.append(f)
        tokens -= dt
        chars -= dc
        print(f"   - {year}: {len(by_year[year])} files, "
              f"{dt:,} tok → {tokens:,} left")

    return selected, excluded, tokens, chars


# ═══════════════════════════════════════════════════════════════
# DATA LOADERS
# ═══════════════════════════════════════════════════════════════
def load_steps():
    text = (DATA / "steps.js").read_text(encoding="utf-8")
    points = []
    for m in re.finditer(
        r'\{\s*id\s*:\s*"([^"]+)"[^{}]*?title\s*:\s*"((?:\\.|[^"\\])*)"',
        text, re.DOTALL,
    ):
        points.append({
            "id": m.group(1),
            "title": m.group(2).replace('\\"', '"')[:70],
        })
    return points


def load_toolkit():
    text = (DATA / "tasks_data.js").read_text(encoding="utf-8")
    tasks = {}
    for m in re.finditer(
        r"num:\s*(\d+)[\s\S]{0,400}?toolkit:\s*\[([^\]]+)\]",
        text,
    ):
        tasks[int(m.group(1))] = re.findall(r"['\"]([^'\"]+)['\"]", m.group(2))
    return tasks


def load_prereqs():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r"const\s+PREREQS\s*=\s*\{([\s\S]*?)\n\};", html)
    if not m:
        return {}
    prereqs = {}
    for match in re.finditer(r'"([^"]+)"\s*:\s*\[([^\]]*)\]', m.group(1)):
        pid = match.group(1)
        deps = re.findall(r'"([^"]+)"', match.group(2))
        prereqs[pid] = deps
    return prereqs


# ═══════════════════════════════════════════════════════════════
# PROMPT BUILDING
# ═══════════════════════════════════════════════════════════════
def build_prompt_parts(files_data, steps, toolkit, prereqs, extra=""):
    """Cache-friendly: STATIC_PREFIX + MIDDLE (fixed order) + SUFFIX."""
    steps_str = "\n".join(f"  {p['id']:<7} {p['title']}" for p in steps)
    toolkit_str = "\n".join(
        f"  Task {n}: {', '.join(ids)}"
        for n, ids in sorted(toolkit.items())
    )
    prereqs_str = "\n".join(
        f"  {pid}: {', '.join(deps) if deps else '(none)'}"
        for pid, deps in sorted(prereqs.items())
    ) if prereqs else "(няма дефинирани)"

    # ── STATIC PREFIX (cached) ──
    static_prefix = f"""Ти си Стефан Георгиев — учител по математика с 21 години стаж в СМГ,
специализиран в олимпиадна подготовка. 3-ма твои ученици на IMO (1 сребро 2019).

═══ ЗАДАЧА ═══
Анализирай {len(files_data)} реални български олимпиади за 11 клас:
областни кръгове (11 кл) и национални кръгове (9-12 кл).
За всяка от 4-те позиции (Task 1-4) определи кои STEPS точки се използват РЕАЛНО.

После:
1. Предложи разширен toolkit за всяка Task (5-12 точки)
2. Обоснови всяка добавена/премахната точка с конкретни задачи
3. Дизайнирай 25-седмичен LEVEL-driven план

═══ 160 STEPS ТОЧКИ ═══
{steps_str}

═══ ТЕКУЩ TOOLKIT ═══
{toolkit_str}

═══ PREREQUISITES ═══
{prereqs_str}

═══ РЕАЛНИ ОЛИМПИАДИ ({len(files_data)} файла) ═══
"""

    # ── MIDDLE (fixed order by year desc, cached) ──
    sorted_exams = sorted(files_data, key=lambda fd: (-extract_year(fd["name"]), fd["name"]))
    middle = ""
    for i, fd in enumerate(sorted_exams, 1):
        middle += f"\n═══ EXAM {i}: {fd['name']} ═══\n{fd['text']}\n\n"

    # ── SUFFIX (variable, retry-safe) ──
    suffix = f"""
═══ ПРИНЦИПИ ═══
1. MINIMAL SUFFICIENT toolkit — само точки, без които ученикът НЕ МОЖЕ
2. Цитирай източници (2024-11-1, 2003-11-2)
3. LEVEL-driven:
   - PREP (2 седмици): R.1-R.15
   - REGIONAL (12 седмици): 4 Tasks по новия toolkit
   - SIMULATIONS (3 седмици): mocks + анализ
   - NATIONAL (8 седмици): advanced (2.x, 4.x, 6.7-6.10, 7.x, 9.x)
4. SPACED REPETITION: secondary трак = 30%, повтаря стари теми
5. PREREQUISITES СА СВЕЩЕНИ — никоя тема преди зависимостта си

═══ ФОРМАТ (САМО JSON, без markdown) ═══
{{
  "analysis": {{
    "exams_analyzed": {len(files_data)},
    "task_1_observed": ["5.1", ...],
    "task_2_observed": ["1.3", ...],
    "task_3_observed": ["3.3", ...],
    "task_4_observed": ["8.1", ...]
  }},
  "toolkit_review": {{
    "task_1": {{
      "current": [...],
      "suggested": [...],
      "added": [{{"id": "5.2", "reason": "среща се в 2020-11-1, 2023-11-1"}}],
      "removed": [{{"id": "5.9", "reason": "не се среща в нито една от 25 задачи"}}],
      "confidence": "high|medium|low"
    }},
    "task_2": {{"current": [...], "suggested": [...], "added": [...], "removed": [...], "confidence": "..."}},
    "task_3": {{"current": [...], "suggested": [...], "added": [...], "removed": [...], "confidence": "..."}},
    "task_4": {{"current": [...], "suggested": [...], "added": [...], "removed": [...], "confidence": "..."}}
  }},
  "plan_js": "const PLAN_PHASES = [\\n  {{num: 1, name: \\"...\\", weeks: \\"СЕДМИЦИ 1–2\\", goal: \\"...\\", dateRange: ['2026-10-23', '2026-11-05'], weeks_data: [\\n    {{week: 1, phase: \\"prep\\", taskType: 0, main: \\"... (R.1, R.2)\\", sec: \\"... (R.7, R.8)\\"}},\\n    ...\\n  ]}},\\n  ...\\n];"
}}

ВАЖНО:
- plan_js трябва да е валиден JavaScript (в JSON string)
- Точно 25 седмици (week: 1 до week: 25)
- Всяка седмица: main + sec с STEPS IDs в скоби
- dateRange: реалистични (2026-10-23 → 2027-04-06)
- taskType: 0 (prep/sim), 1 (algebra), 2 (geometry), 3 (NT), 4 (combinatorics)

═══ ДОПЪЛНИТЕЛНИ ИНСТРУКЦИИ ═══
{extra if extra else '(без допълнителни)'}
"""

    return {
        "static_prefix": static_prefix,
        "middle": middle,
        "suffix": suffix,
        "full": static_prefix + middle + suffix,
    }


# ═══════════════════════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════════════════════
def call_ai(cfg, prompt, max_tokens=MAX_OUTPUT_TOKENS):
    import requests
    print(f"\n🚀 {cfg['model']}  (reasoning: {cfg.get('reasoning_effort', 'default')})")
    print(f"   Prompt: {len(prompt):,} chars")
    print(f"   max_tokens: {max_tokens:,}")

    payload = {
        "model": cfg["model"],
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "reasoning_effort": cfg.get("reasoning_effort", "max"),
        "messages": [
            {"role": "system", "content": "Ти си опитен учител по математика. Връщаш САМО валиден JSON."},
            {"role": "user", "content": prompt},
        ],
    }

    r = requests.post(
        cfg["api_url"],
        headers={"Authorization": f"Bearer {cfg['api_key']}", "Content-Type": "application/json"},
        json=payload,
        timeout=2400,
    )

    # Fallback: ако reasoning_effort не се поддържа
    if r.status_code == 400 and "reasoning_effort" in r.text.lower():
        print(f"   ⚠ reasoning_effort не се поддържа — retry без него")
        payload.pop("reasoning_effort", None)
        r = requests.post(
            cfg["api_url"],
            headers={"Authorization": f"Bearer {cfg['api_key']}", "Content-Type": "application/json"},
            json=payload,
            timeout=2400,
        )

    if not r.ok:
        print(f"✗ API {r.status_code}: {r.text[:500]}")
        return None, None

    data = r.json()
    usage = data.get("usage", {})
    prompt_tok = usage.get("prompt_tokens", 0)
    completion_tok = usage.get("completion_tokens", 0)
    cached_tok = (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0)

    print(f"✓ {usage.get('total_tokens', 0):,} tok total")
    print(f"   prompt={prompt_tok:,}  completion={completion_tok:,}")
    if cached_tok:
        print(f"   ⚡ cached={cached_tok:,} ({cached_tok/prompt_tok*100:.1f}%)")

    # Изчисли реална цена
    in_rate = RATE_DOUBLE_INPUT if prompt_tok > DOUBLE_RATE_THRESHOLD else RATE_INPUT
    out_rate = RATE_DOUBLE_OUTPUT if prompt_tok > DOUBLE_RATE_THRESHOLD else RATE_OUTPUT
    in_cost = (prompt_tok - cached_tok) * in_rate + cached_tok * RATE_CACHED_INPUT
    out_cost = completion_tok * out_rate
    actual_cost = in_cost + out_cost
    print(f"   actual cost: ${actual_cost:.4f}  (in=${in_cost:.4f} out=${out_cost:.4f})")

    content = (data.get("choices", [{}])[0].get("message", {}).get("content", "")).strip()
    return content or None, actual_cost


def parse_json(text):
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```\s*$', '', text)
    m = re.search(r'\{[\s\S]*\}', text)
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
# VALIDATION
# ═══════════════════════════════════════════════════════════════
def validate_plan(plan_js, toolkit_review):
    """Връща (critical_issues, warnings)."""
    critical = []
    warnings = []

    # ── Critical ──
    if not plan_js:
        critical.append("plan_js е празен")
        return critical, warnings

    if "const PLAN_PHASES = [" not in plan_js:
        critical.append("липсва 'const PLAN_PHASES = ['")
        return critical, warnings

    if not plan_js.rstrip().endswith("];"):
        critical.append("plan_js не завършва с '];'")

    weeks = re.findall(r"week:\s*(\d+)", plan_js)
    if len(weeks) < 20:
        critical.append(f"само {len(weeks)} седмици (truncated output?)")

    week_nums = sorted(set(int(w) for w in weeks))
    if week_nums and week_nums[0] != 1:
        critical.append(f"първата седмица е {week_nums[0]}, не 1")

    if not toolkit_review:
        critical.append("toolkit_review е празен")

    # ── Warning ──
    if not critical:
        missing = set(range(1, TOTAL_WEEKS + 1)) - set(week_nums)
        if missing:
            warnings.append(f"липсват седмици: {sorted(missing)}")

        upper = plan_js.upper()
        if "PREP" not in upper[:1000]:
            warnings.append("PREP не е в началото")

        for t in [0, 1, 2, 3, 4]:
            if f"taskType: {t}" not in plan_js:
                warnings.append(f"липсва taskType: {t}")

        # Дати монотонни
        dates = re.findall(r"'(\d{4}-\d{2}-\d{2})'", plan_js)
        if dates:
            try:
                sorted_dates = sorted(dates)
                if dates != sorted_dates:
                    warnings.append("датите не са монотонни")
            except Exception:
                pass

    return critical, warnings


# ═══════════════════════════════════════════════════════════════
# TOOLKIT APPLY
# ═══════════════════════════════════════════════════════════════
def apply_toolkit(review):
    """Обновява toolkit: [...] в tasks_data.js."""
    tasks_file = DATA / "tasks_data.js"
    text = tasks_file.read_text(encoding="utf-8")

    changes = 0
    for task_key, r in review.items():
        if not task_key.startswith("task_"):
            continue
        num = task_key.replace("task_", "")
        suggested = r.get("suggested", [])
        if not suggested:
            continue
        ids_str = ", ".join(f"'{i}'" for i in suggested)
        pattern = rf"(num:\s*{num},[\s\S]*?toolkit:\s*)\[[^\]]*\]"
        new_text, n = re.subn(pattern, rf"\1[{ids_str}]", text, count=1)
        if n:
            text = new_text
            changes += 1
            print(f"  Task {num}: {len(suggested)} точки")

    if changes:
        safe_write(tasks_file, text)
        print(f"✓ {changes} toolkit обновени в tasks_data.js")
    else:
        print("⚠ Никакви toolkit промени не са приложени")

    return changes


# ═══════════════════════════════════════════════════════════════
# BUDGET
# ═══════════════════════════════════════════════════════════════
def track_cost(cost_usd):
    """Записва разхода в chunker_state.json."""
    state_file = STATE_DIR / "chunker_state.json"
    if not state_file.exists():
        return
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        today = str(date.today())
        if data["budget"]["date"] != today:
            data["budget"] = {"date": today, "spent_usd": 0.0, "calls": 0}
        data["budget"]["spent_usd"] += cost_usd
        data["budget"]["calls"] += 1
        safe_write(state_file, json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"⚠ Budget tracking fail: {e}")


# ═══════════════════════════════════════════════════════════════
# BACKUP / RESTORE
# ═══════════════════════════════════════════════════════════════
def restore_file(base_name):
    """Връща последния backup на файл."""
    backups = sorted(DATA.glob(f"{base_name}.backup-*"), reverse=True)
    if not backups:
        print(f"✗ Няма backup за {base_name}")
        return False
    latest = backups[0]
    shutil.copy2(latest, DATA / base_name)
    print(f"✓ {base_name} възстановен от {latest.name}")
    return True


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser(
        description="Generate study plan — един файл, един API call",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=INPUT_TOKEN_CAP)
    ap.add_argument("--skip-probs", action="store_true",
                    help="Пропусни -probs файлове (sol съдържа stmt+sol)")
    ap.add_argument("--apply-toolkit", action="store_true")
    ap.add_argument("--retry-from", type=str, default=None)
    ap.add_argument("--extra", type=str, default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--restore", action="store_true")
    ap.add_argument("--restore-toolkit", action="store_true")
    ap.add_argument("--restore-all", action="store_true")
    args = ap.parse_args()

    # ── RESTORE MODES ──
    if args.restore or args.restore_all:
        restore_file("plan_phases.js")
    if args.restore_toolkit or args.restore_all:
        restore_file("tasks_data.js")
    if args.restore or args.restore_toolkit or args.restore_all:
        return 0

    print("═" * 72)
    print("  GENERATE PLAN — един файл, един API call")
    print("═" * 72)
    print(f"  Model:       {MODEL}")
    print(f"  Effort:      {REASONING_EFFORT}")
    print(f"  max_tokens:  {MAX_OUTPUT_TOKENS:,}")
    print(f"  Input cap:   {args.max_tokens:,}")

    # ── RETRY MODE ──
    if args.retry_from:
        print(f"\n🔁 RETRY: {args.retry_from}")
        cached = json.loads(Path(args.retry_from).read_text(encoding="utf-8"))
        static_prefix = cached["static_prefix"]
        middle = cached["middle"]
        print(f"   Cached prefix: {len(static_prefix):,} chars")
        print(f"   Cached middle: {len(middle):,} chars")
        print(f"   Extra: {args.extra[:100] if args.extra else '(none)'}")

        # Rebuild suffix (не сме го запазили, защото се променя)
        suffix = f"""
═══ ПРИНЦИПИ ═══
1. MINIMAL SUFFICIENT toolkit
2. Цитирай източници
3. LEVEL-driven: PREP (2w) → REGIONAL (12w) → SIMULATIONS (3w) → NATIONAL (8w)
4. SPACED REPETITION: secondary 30%
5. PREREQUISITES СА СВЕЩЕНИ

═══ ФОРМАТ (САМО JSON) ═══
{{
  "analysis": {{...}},
  "toolkit_review": {{...}},
  "plan_js": "const PLAN_PHASES = [...]"
}}

═══ ДОПЪЛНИТЕЛНИ ИНСТРУКЦИИ ═══
{args.extra if args.extra else '(без промени)'}
"""
        prompt = static_prefix + middle + suffix
        if args.dry_run:
            print(f"\n📝 Prompt: {len(prompt):,} chars")
            return 0

        cfg = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
        ai_cfg = dict(cfg.get("escalation", cfg["generator"]))
        ai_cfg["model"] = MODEL
        ai_cfg["reasoning_effort"] = REASONING_EFFORT

        response, cost = call_ai(ai_cfg, prompt)
        if not response:
            return 1

        if cost and cost > HARD_COST_CAP_USD:
            print(f"\n🛑 Cost ${cost:.2f} > cap ${HARD_COST_CAP_USD:.2f} — не се записва")
            debug = BASE / f"plan_debug_{timestamp()}.txt"
            debug.write_text(response, encoding="utf-8")
            print(f"   Debug: {debug.name}")
            return 1

        parsed = parse_json(response)
        if not parsed or not parsed.get("plan_js"):
            debug = BASE / f"plan_debug_{timestamp()}.txt"
            debug.write_text(response, encoding="utf-8")
            print(f"✗ JSON fail. Debug: {debug.name}")
            return 1

        plan_js = parsed["plan_js"]
        review = parsed.get("toolkit_review", {})
        critical, warnings = validate_plan(plan_js, review)

        if critical:
            print("\n🔴 CRITICAL:")
            for c in critical:
                print(f"   - {c}")
            debug = BASE / f"plan_debug_{timestamp()}.txt"
            debug.write_text(response, encoding="utf-8")
            print(f"   Debug: {debug.name}")
            return 1

        if warnings:
            print("\n🟡 Warnings:")
            for w in warnings:
                print(f"   - {w}")

        safe_write(DATA / "plan_phases.js", plan_js + "\n")
        print(f"✓ Plan записан")

        if cost:
            track_cost(cost)
        return 0

    # ── NORMAL MODE ──
    print(f"  Skip probs: {'YES' if args.skip_probs else 'NO'}")

    # 1. Collect
    files = collect_files(skip_probs=args.skip_probs)
    print(f"\n📂 Relevant files: {len(files)}")
    if not files:
        print("✗ Няма файлове в .pdf_text_cache/")
        print("   Пусни: python scan_pdf_text.py")
        return 1

    is_reg = sum(1 for f in files if "Областен" in f.stem)
    print(f"   Regional: {is_reg}")
    print(f"   National: {len(files) - is_reg}")

    # 2. Check for missing cache
    all_needed = collect_files(skip_probs=False)
    missing = [f for f in all_needed if not (CACHE_DIR / f"{f.stem}.txt").exists()]
    if missing:
        print(f"\n⚠ {len(missing)} файла липсват в cache:")
        for f in missing[:5]:
            print(f"   - {f}")
        print(f"\n   Пусни: python scan_pdf_text.py")
        return 1

    # 3. Load texts + prune
    texts = {f: f.read_text(encoding="utf-8") for f in files}
    selected, excluded, tokens, chars = prune(files, args.max_tokens, texts)

    cost_est, rate_label = calc_cost(tokens, 0, MAX_OUTPUT_TOKENS)
    print(f"\n{'═' * 72}")
    print(f"  SELECTION")
    print(f"{'═' * 72}")
    print(f"  Selected:  {len(selected)} files")
    print(f"  Excluded:  {len(excluded)} files")
    print(f"  Chars:     {chars:,}")
    print(f"  Tokens:    {tokens:,}")
    print(f"  Est worst: ${cost_est:.2f}  ({rate_label}, max_tokens={MAX_OUTPUT_TOKENS:,})")

    sel_years = sorted(set(extract_year(f.stem) for f in selected), reverse=True)
    if sel_years:
        print(f"  Years: {sel_years[-1]}–{sel_years[0]} ({len(sel_years)} unique)")

    if tokens > HARD_INPUT_CAP:
        print(f"\n❌ {tokens:,} > hard cap {HARD_INPUT_CAP:,}. Abort.")
        return 1

    if cost_est > HARD_COST_CAP_USD:
        print(f"\n❌ Est cost ${cost_est:.2f} > cap ${HARD_COST_CAP_USD:.2f}. Abort.")
        return 1

    # 4. Build prompt
    files_data = [{"name": f.stem, "text": texts[f]} for f in selected]
    steps = load_steps()
    toolkit = load_toolkit()
    prereqs = load_prereqs()

    parts = build_prompt_parts(files_data, steps, toolkit, prereqs, args.extra)
    print(f"\n✓ STEPS: {len(steps)}  Toolkit: {len(toolkit)} tasks  PREREQS: {len(prereqs)}")
    print(f"📝 Prompt: {len(parts['full']):,} chars")
    print(f"   static: {len(parts['static_prefix']):,}  "
          f"middle: {len(parts['middle']):,}  suffix: {len(parts['suffix']):,}")

    # 5. Save prompt for retry
    cache_file = PROMPT_CACHE / "last.json"
    cache_file.write_text(json.dumps({
        "saved_at": datetime.now().isoformat(),
        "static_prefix": parts["static_prefix"],
        "middle": parts["middle"],
        "files": [f.stem for f in selected],
        "years": sel_years,
        "tokens": tokens,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Saved for retry: prompt_cache/last.json")

    # 6. Dry run
    if args.dry_run:
        print("\n" + "=" * 72)
        print("  DRY RUN — first 3000 chars")
        print("=" * 72)
        print(parts["full"][:3000])
        print(f"\n[... {len(parts['full']) - 3000:,} chars hidden ...]")
        print("\n" + "=" * 72)
        print("  SELECTED FILES")
        print("=" * 72)
        for f in selected:
            kind = "regional" if "Областен" in f.stem else "national"
            print(f"  {extract_year(f.stem)}  {kind:<10}  {len(texts[f]):>6,}ch  {f.stem}")
        return 0

    # 7. Force check
    plan_file = DATA / "plan_phases.js"
    if plan_file.exists() and not args.force:
        today = str(date.today())
        if f"backup-{today.replace('-', '')}" in str(sorted(DATA.glob("plan_phases.backup-*"))[-1] if list(DATA.glob("plan_phases.backup-*")) else ""):
            print(f"\n⚠ plan_phases.js вече е писан днес. Ползвай --force за overwrite.")
            return 1

    # 8. API call
    cfg = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
    ai_cfg = dict(cfg.get("escalation", cfg["generator"]))
    ai_cfg["model"] = MODEL
    ai_cfg["reasoning_effort"] = REASONING_EFFORT

    response, actual_cost = call_ai(ai_cfg, parts["full"])

    if actual_cost and actual_cost > HARD_COST_CAP_USD:
        print(f"\n🛑 Cost ${actual_cost:.2f} > ${HARD_COST_CAP_USD:.2f} — не се записва")
        debug = BASE / f"plan_debug_{timestamp()}.txt"
        debug.write_text(response or "", encoding="utf-8")
        print(f"   Debug: {debug.name}")
        return 1

    if not response:
        print("✗ No response from API")
        return 1

    # 9. Parse
    parsed = parse_json(response)
    if not parsed:
        debug = BASE / f"plan_debug_{timestamp()}.txt"
        debug.write_text(response, encoding="utf-8")
        print(f"✗ JSON parse fail. Debug: {debug.name}")
        print(f"   Можеш да го поправиш ръчно или да пуснеш retry")
        return 1

    plan_js = parsed.get("plan_js", "")
    review = parsed.get("toolkit_review", {})

    # 10. Validate
    critical, warnings = validate_plan(plan_js, review)

    if critical:
        print("\n🔴 CRITICAL ISSUES:")
        for c in critical:
            print(f"   - {c}")
        debug = BASE / f"plan_debug_{timestamp()}.txt"
        debug.write_text(response, encoding="utf-8")
        print(f"\n   💾 Debug saved: {debug.name}")
        print(f"   Можеш да го поправиш ръчно или да пуснеш retry с --extra")
        return 1

    if warnings:
        print("\n🟡 Warnings (продължавам):")
        for w in warnings:
            print(f"   - {w}")

    # 11. Save files
    print(f"\n{'═' * 72}")
    print(f"  SAVING")
    print(f"{'═' * 72}")

    # Toolkit review
    review_file = DATA / f"toolkit_review_{date.today()}.json"
    review_file.write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✓ toolkit_review: {review_file.name}")

    # Toolkit changes summary
    for task_key in sorted(review.keys()):
        r = review[task_key]
        added = r.get("added", [])
        removed = r.get("removed", [])
        conf = r.get("confidence", "?")
        print(f"\n  {task_key} ({conf}): +{len(added)} / -{len(removed)}")
        for a in added:
            print(f"    + {a['id']}: {a['reason'][:70]}")
        for rm in removed:
            print(f"    - {rm['id']}: {rm['reason'][:70]}")

    # Plan
    safe_write(DATA / "plan_phases.js", plan_js + "\n")
    print(f"\n✓ plan_phases.js записан")

    # Metadata
    audit_today = AUDIT_DIR / str(date.today())
    audit_today.mkdir(parents=True, exist_ok=True)
    meta = {
        "generated_at": datetime.now().isoformat(),
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "max_tokens": MAX_OUTPUT_TOKENS,
        "exams_analyzed": len(selected),
        "years": sel_years,
        "input_tokens": tokens,
        "cost_usd": actual_cost,
        "critical_issues": critical,
        "warnings": warnings,
    }
    (audit_today / "plan_generation.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DATA / "plan_metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✓ audit/<date>/plan_generation.json")
    print(f"✓ plan_metadata.json")

    # 12. Track cost
    if actual_cost:
        track_cost(actual_cost)
        print(f"\n💰 Cost: ${actual_cost:.4f} tracked")

    # 13. Apply toolkit
    if args.apply_toolkit:
        print(f"\n{'═' * 72}")
        print(f"  APPLY TOOLKIT")
        print(f"{'═' * 72}")
        apply_toolkit(review)

    # 14. Summary
    print(f"\n{'═' * 72}")
    print(f"  SUMMARY")
    print(f"{'═' * 72}")

    # Phase breakdown
    by_phase = {}
    for m in re.finditer(r'week:\s*(\d+)[^}]*?phase:\s*"([^"]+)"', plan_js):
        by_phase.setdefault(m.group(2), []).append(int(m.group(1)))
    for ph, wks in sorted(by_phase.items()):
        print(f"  {ph:12s}  weeks {sorted(wks)}")

    print(f"\n💡 Retry (ако не ти хареса):")
    print(f"   python generate_plan.py --retry-from prompt_cache/last.json \\")
    print(f"       --extra \"Нова инструкция\"")
    print(f"   (cache hit → ~$0.20 вместо ~$1.00)")

    return 0


if __name__ == "__main__":
    sys.exit(main())