#!/usr/bin/env python3
"""
analyze_all.py — всички 11 кл областни + всички National 9-12.
Ако над token limit → реже от най-старите автоматично.

Промени:
  v1.1: skip -probs (sol съдържа stmt+sol, probs е дубликат)
  v1.1: коректна цена с 272K double-rate threshold

Usage:
    python analyze_all.py --dry-run --max-tokens 270000
    python analyze_all.py --max-tokens 270000           # с API
    python analyze_all.py --no-skip-probs --max-tokens 250000  # стария режим
"""
import sys
import io
import json
import re
import argparse
from pathlib import Path
from datetime import date

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = Path(__file__).parent.resolve()
ROOT = BASE.parent
DATA = ROOT / "data"
CACHE_DIR = BASE / ".pdf_text_cache"

# Token limits
MAX_TOKENS_SAFE = 270_000   # точно под 272K (double rate праг)
MAX_TOKENS_HARD = 900_000   # под 922K (API input limit)

# Rate прагове
DOUBLE_RATE_THRESHOLD = 272_000
RATE_STANDARD_INPUT = 0.000002     # $2/M
RATE_STANDARD_OUTPUT = 0.000010    # $10/M
RATE_DOUBLE_INPUT = 0.000004       # $4/M
RATE_DOUBLE_OUTPUT = 0.000015      # $15/M
EST_OUTPUT_TOKENS = 15_000


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def extract_year(name):
    m = re.search(r'(\d{4})', name)
    return int(m.group(1)) if m else 0


def measure_tokens(texts):
    """tiktoken (точно) или heuristic (chars/2 за Cyrillic math)."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("o200k_base")
        return sum(len(enc.encode(t)) for t in texts)
    except ImportError:
        return sum(len(t) // 2 for t in texts)


def calc_cost(tokens, output_tokens=EST_OUTPUT_TOKENS):
    """Коректна цена с 272K threshold."""
    if tokens > DOUBLE_RATE_THRESHOLD:
        input_cost = tokens * RATE_DOUBLE_INPUT
        output_cost = output_tokens * RATE_DOUBLE_OUTPUT
        label = f"DOUBLE (>{DOUBLE_RATE_THRESHOLD // 1000}K)"
    else:
        input_cost = tokens * RATE_STANDARD_INPUT
        output_cost = output_tokens * RATE_STANDARD_OUTPUT
        label = f"standard (<{DOUBLE_RATE_THRESHOLD // 1000}K)"
    return input_cost + output_cost, label


# ═══════════════════════════════════════════════════════════════
# FILE SELECTION
# ═══════════════════════════════════════════════════════════════
def filter_target_files(skip_probs=True):
    """
    Връща всички релевантни файлове:
      - Областен 11 кл (всички години)
      - National 9-12 (всички години)
    Само тези, които имат cache (readable).

    skip_probs=True: пропуска -probs, защото sol съдържа stmt+sol
    """
    files = []
    skipped_probs = 0
    for f in CACHE_DIR.glob("*.txt"):
        stem = f.stem
        if skip_probs and "-probs" in stem:
            skipped_probs += 1
            continue
        is_11kl_regional = "Областен" in stem and "11 кл" in stem
        is_national = "Национален" in stem and "9-12 кл" in stem
        if is_11kl_regional or is_national:
            files.append(f)
    if skipped_probs:
        print(f"   Skipped -probs files: {skipped_probs}")
    return sorted(files, key=lambda f: (-extract_year(f.stem), f.name))


def select_with_pruning(files, max_tokens, texts):
    """
    Започва с всички. Ако над max_tokens, реже от най-старите години.
    Връща (selected, excluded, tokens, chars).
    """
    by_year = {}
    for f in files:
        year = extract_year(f.stem)
        by_year.setdefault(year, []).append(f)

    selected = list(files)
    excluded = []

    current_tokens = measure_tokens([texts[f] for f in selected])
    current_chars = sum(len(texts[f]) for f in selected)

    if current_tokens <= max_tokens:
        return selected, excluded, current_tokens, current_chars

    print(f"\n✂ Pruning: {current_tokens:,} > {max_tokens:,} (max)")
    for year in sorted(by_year.keys()):
        if current_tokens <= max_tokens:
            break
        dropped_tokens = measure_tokens([texts[f] for f in by_year[year]])
        dropped_chars = sum(len(texts[f]) for f in by_year[year])
        for f in by_year[year]:
            selected.remove(f)
            excluded.append(f)
        current_tokens -= dropped_tokens
        current_chars -= dropped_chars
        print(f"   - Year {year}: {len(by_year[year])} files, "
              f"{dropped_tokens:,} tok → now {current_tokens:,}")

    return selected, excluded, current_tokens, current_chars


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


def load_current_toolkit():
    text = (DATA / "tasks_data.js").read_text(encoding="utf-8")
    tasks = {}
    for m in re.finditer(
        r"num:\s*(\d+)[\s\S]{0,400}?toolkit:\s*\[([^\]]+)\]",
        text,
    ):
        tasks[int(m.group(1))] = re.findall(r"['\"]([^'\"]+)['\"]", m.group(2))
    return tasks


# ═══════════════════════════════════════════════════════════════
# PROMPT BUILDER
# ═══════════════════════════════════════════════════════════════
def build_prompt(files_data, steps, current_toolkit):
    steps_str = "\n".join(f"  {p['id']:<7} {p['title']}" for p in steps)
    toolkit_str = "\n".join(
        f"  Task {n}: {', '.join(ids)}"
        for n, ids in sorted(current_toolkit.items())
    )
    exams_str = ""
    for i, fd in enumerate(files_data, 1):
        exams_str += f"\n═══ EXAM {i}: {fd['name']} ═══\n{fd['text']}\n\n"

    return f"""Ти си Стефан Георгиев — учител по математика с 21 години стаж.

═══ ЗАДАЧА ═══
Анализирай {len(files_data)} реални български олимпиади за 11 клас:
областни кръгове (11 кл) и национални кръгове (9-12 кл, задачите за 11 са в тях).
За всяка от 4-те позиции (Task 1-4) определи кои STEPS точки се използват РЕАЛНО.

После:
1. Предложи разширен toolkit за всяка Task (5-12 точки)
2. Обоснови всяка добавена/премахната точка с конкретни задачи
3. Дизайнирай 25-седмичен LEVEL-driven план

═══ 160 STEPS ТОЧКИ ═══
{steps_str}

═══ ТЕКУЩ TOOLKIT ═══
{toolkit_str}

═══ РЕАЛНИ ОЛИМПИАДИ ({len(files_data)} файла) ═══
{exams_str}

═══ ПРИНЦИПИ ═══
1. MINIMAL SUFFICIENT toolkit — само точки, без които ученикът НЕ МОЖЕ
2. Цитирай източници (2024-11-1, 2003-11-2)
3. LEVEL-driven:
   - PREP (2 седмици): R.1-R.15
   - REGIONAL (12 седмици): 4 Tasks по новия toolkit
   - SIMULATIONS (3 седмици): mocks
   - NATIONAL (8 седмици): advanced (2.x, 4.x, 6.7-6.10, 7.x, 9.x)

═══ ФОРМАТ (САМО JSON) ═══
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
      "added": [{{"id": "5.2", "reason": "..."}}],
      "removed": [{{"id": "5.9", "reason": "..."}}]
    }},
    "task_2": {{...}},
    "task_3": {{...}},
    "task_4": {{...}}
  }},
  "plan_js": "const PLAN_PHASES = [\\n  {{num: 1, ...}}\\n];"
}}
"""


# ═══════════════════════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════════════════════
def call_ai(cfg, prompt):
    import requests
    print(f"\n🚀 {cfg['model']}  (reasoning: {cfg.get('reasoning_effort', 'default')})")
    print(f"   Prompt: {len(prompt):,} chars")

    r = requests.post(
        cfg["api_url"],
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": cfg["model"],
            "max_tokens": 20000,
            "temperature": 0.2,
            "reasoning_effort": cfg.get("reasoning_effort", "max"),
            "messages": [
                {"role": "system", "content":
                    "Ти си опитен учител по математика. Връщаш САМО валиден JSON."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=1800,
    )

    if not r.ok:
        print(f"✗ API {r.status_code}: {r.text[:500]}")
        return None

    data = r.json()
    usage = data.get("usage", {})
    print(f"✓ {usage.get('total_tokens', '?')} tok "
          f"(in={usage.get('prompt_tokens', '?')}, "
          f"out={usage.get('completion_tokens', '?')})")
    return (data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")).strip() or None


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
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Виж prompt-а без API call")
    ap.add_argument("--max-tokens", type=int, default=MAX_TOKENS_SAFE,
                    help=f"Token cap (default {MAX_TOKENS_SAFE})")
    ap.add_argument("--max-tokens-hard", type=int, default=MAX_TOKENS_HARD,
                    help=f"Hard cap за API limit (default {MAX_TOKENS_HARD})")
    ap.add_argument("--no-skip-probs", action="store_true",
                    help="Не skip-вай -probs (по-скъпо, но пълен stmt)")
    ap.add_argument("--output-tokens", type=int, default=EST_OUTPUT_TOKENS,
                    help=f"Estimate за output (default {EST_OUTPUT_TOKENS})")
    args = ap.parse_args()

    print("═" * 72)
    print("  ANALYZE ALL — 11 кл областни + National 9-12")
    print("═" * 72)
    print(f"  Token cap: {args.max_tokens:,}")
    print(f"  Skip probs: {'NO' if args.no_skip_probs else 'YES (sols only)'}")

    # Collect
    files = filter_target_files(skip_probs=not args.no_skip_probs)
    print(f"\n📂 Релевантни файлове: {len(files)}")

    if not files:
        print("✗ Няма файлове. Пусни scan_pdf_text.py първо.")
        return 1

    # Count by type
    is_11kl = sum(1 for f in files if "Областен" in f.stem and "11 кл" in f.stem)
    is_nat = len(files) - is_11kl
    print(f"   11 кл областни: {is_11kl}")
    print(f"   National 9-12:  {is_nat}")

    # Load all texts into memory once
    texts = {f: f.read_text(encoding="utf-8") for f in files}

    # Select with pruning
    selected, excluded, tokens, chars = select_with_pruning(
        files, args.max_tokens, texts
    )

    # Cost estimate (correct)
    cost, rate_label = calc_cost(tokens, args.output_tokens)

    print(f"\n{'═' * 72}")
    print(f"  SELECTION")
    print(f"{'═' * 72}")
    print(f"  Selected:  {len(selected)} files")
    print(f"  Excluded:  {len(excluded)} files")
    print(f"  Chars:     {chars:,}")
    print(f"  Tokens:    {tokens:,}")
    print(f"  Est cost:  ${cost:.2f}  ({rate_label})")

    if tokens > args.max_tokens_hard:
        print(f"\n❌ Still over hard limit {args.max_tokens_hard:,}. Abort.")
        return 1

    # Years breakdown
    sel_years = sorted(set(extract_year(f.stem) for f in selected), reverse=True)
    exc_years = sorted(set(extract_year(f.stem) for f in excluded), reverse=True)
    if sel_years:
        print(f"\n  Selected years: {sel_years[0]}–{sel_years[-1]} "
              f"({len(sel_years)} unique)")
    if exc_years:
        print(f"  Excluded years: {exc_years}")

    # Build prompt
    files_data = [{"name": f.stem, "text": texts[f]} for f in selected]
    steps = load_steps()
    current_toolkit = load_current_toolkit()
    print(f"\n✓ STEPS: {len(steps)}  |  Toolkit tasks: {len(current_toolkit)}")

    prompt = build_prompt(files_data, steps, current_toolkit)
    print(f"\n📝 Prompt: {len(prompt):,} chars (~{tokens:,} tok)")

    if args.dry_run:
        print("\n" + "=" * 72)
        print("  DRY RUN — first 3000 chars")
        print("=" * 72)
        print(prompt[:3000])
        print(f"\n[... {len(prompt) - 3000:,} chars hidden ...]")

        # Show selected files
        print("\n" + "=" * 72)
        print("  SELECTED FILES")
        print("=" * 72)
        for f in selected:
            yr = extract_year(f.stem)
            char_n = len(texts[f])
            kind = "regional" if "Областен" in f.stem else "national"
            print(f"  {yr}  {kind:<10}  {char_n:>6,}ch  {f.stem}")
        return 0

    # API call
    with open(BASE / "config.json", "r", encoding="utf-8") as f:
        cfg = dict(json.load(f)["escalation"])
    cfg["reasoning_effort"] = "max"

    response = call_ai(cfg, prompt)
    if not response:
        return 1

    parsed = parse_json(response)
    if not parsed:
        debug = BASE / f"analyze_all_debug_{date.today()}.txt"
        debug.write_text(response, encoding="utf-8")
        print(f"✗ JSON parse fail. Debug: {debug.name}")
        return 1

    # Save toolkit review
    review_file = DATA / f"toolkit_review_{date.today()}.json"
    review_file.write_text(
        json.dumps(parsed.get("toolkit_review", {}),
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✓ Toolkit review: {review_file.name}")

    # Show changes
    for task_key in sorted(parsed.get("toolkit_review", {}).keys()):
        r = parsed["toolkit_review"][task_key]
        added = r.get("added", [])
        removed = r.get("removed", [])
        print(f"\n  {task_key}: +{len(added)} / -{len(removed)}")
        for a in added:
            print(f"    + {a['id']}: {a['reason'][:70]}")
        for rm in removed:
            print(f"    - {rm['id']}: {rm['reason'][:70]}")

    # Save plan
    plan_js = parsed.get("plan_js", "")
    if plan_js:
        plan_file = DATA / "plan_phases.js"
        if plan_file.exists():
            backup = DATA / f"plan_phases.backup-{date.today()}.js"
            backup.write_text(plan_file.read_text(encoding="utf-8"),
                              encoding="utf-8")
            print(f"\n✓ Backup: {backup.name}")
        plan_file.write_text(plan_js + "\n", encoding="utf-8")
        print(f"✓ Plan: {plan_file}")
    else:
        print("\n⚠ No plan_js in response")

    return 0


if __name__ == "__main__":
    sys.exit(main())