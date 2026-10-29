#!/usr/bin/env python3
"""
master_orchestrator.py v2 — 24/7 методичен worker.

Правилният дневен цикъл:
  1. Провери бюджет (4 state файла)
  2. Ако < 85%: пусни chain (extract → merge → classify → aggregate)
  3. Ако >= 85%: чакай 00:01 (нов ден)
  4. Ако всичко готово (0 pending): чакай нови PDF-ове

Употреба:
    python master_orchestrator.py --once     # 1 дневен цикъл, изход
    python master_orchestrator.py --daemon   # 24/7 фонов режим
    python master_orchestrator.py --status   # само проверка
"""
import sys, io, subprocess, json, time, argparse
from pathlib import Path
from datetime import date, datetime, timedelta

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PIPE = Path(__file__).parent.resolve()
PYTHON = sys.executable
GEN = PIPE.parent / "generated"
STATE = GEN / "state"

# Всички state файлове — за правилен budget tracking
STATE_FILES = [
    STATE / "chunker_state.json",
    STATE / "state.json",
    STATE / "problem_state.json",
    STATE / "gap_state.json",
]

DAILY_BUDGET = 3.00
STOP_AT = 2.55   # 85% — оставя $0.45 за изненади
RESUME_HOUR = 0  # 00:01 нов ден


# ═══════════════════════════════════════════════════════════════
# BUDGET TRACKING (чете от 4 state файла)
# ═══════════════════════════════════════════════════════════════
def today_spent() -> float:
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


def budget_ok() -> bool:
    return today_spent() < STOP_AT


# ═══════════════════════════════════════════════════════════════
# PENDING WORK — колко PDF-а остават
# ═══════════════════════════════════════════════════════════════
def count_pending_extract() -> int:
    """PDF-ове, които още не са extract-нати."""
    state_file = STATE / "chunker_state.json"
    if not state_file.exists():
        return 9999  # fresh start
    try:
        d = json.loads(state_file.read_text(encoding="utf-8"))
        extracted = d.get("extracted", {})
        done = sum(1 for v in extracted.values() if v.get("status") == "done")
        # Всички PDF-ове минус готовите
        # Груба оценка — 227 PDF-а според scan-а
        return max(0, 227 - done)
    except Exception:
        return 9999


def count_pending_merge() -> int:
    """Extracted папки без merged версия."""
    ex_dir = GEN / "cache" / "extracted"
    mg_dir = GEN / "cache" / "merged"
    if not ex_dir.exists():
        return 0
    extracted_bases = set()
    for d in ex_dir.iterdir():
        if not d.is_dir():
            continue
        name = d.name
        # Махаме -probs, -sol, (1) и т.н.
        import re
        base = re.sub(r'\s*[-_](probs?|sol)(\s*\(\d+\))?$', '', name, flags=re.I)
        base = re.sub(r'\s*\(\d+\)$', '', base)
        extracted_bases.add(base)
    merged_bases = set()
    if mg_dir.exists():
        for d in mg_dir.iterdir():
            if d.is_dir():
                merged_bases.add(d.name)
    return len(extracted_bases - merged_bases)


def count_pending_classify() -> int:
    """Merged olympiads без classified версия."""
    mg_dir = GEN / "cache" / "merged"
    cl_dir = GEN / "cache" / "classified"
    if not mg_dir.exists():
        return 0
    merged = {d.name for d in mg_dir.iterdir() if d.is_dir()}
    classified = {d.name for d in cl_dir.iterdir() if d.is_dir()} if cl_dir.exists() else set()
    return len(merged - classified)


def count_pending_aggregate() -> int:
    """Classified има, но aggregate не е пуснат скоро."""
    # Просто — ако има classified но anchors е празна, значи чака
    cl_dir = GEN / "cache" / "classified"
    an_dir = GEN / "anchors"
    if not cl_dir.exists():
        return 0
    has_classified = any(cl_dir.iterdir())
    has_anchors = an_dir.exists() and any(an_dir.glob("*.json"))
    if has_classified and not has_anchors:
        return 1
    return 0


# ═══════════════════════════════════════════════════════════════
# RUN PHASE
# ═══════════════════════════════════════════════════════════════
def run_phase(cmd: list, name: str, timeout: int = 7200) -> tuple:
    """Връща (exit_code, duration_sec, stopped_by_budget)."""
    print(f"\n{'=' * 70}")
    print(f"[ORCH] ▶ {name}  (budget: ${today_spent():.2f}/${DAILY_BUDGET:.2f})")
    print(f"{'=' * 70}")

    t0 = time.time()
    try:
        result = subprocess.run(
            [PYTHON] + cmd,
            cwd=PIPE,
            timeout=timeout,
        )
        dur = time.time() - t0
        # Проверка дали е спрял от BudgetExhausted (гледа в изхода? не можем)
        # Просто проверяваме бюджета след това
        stopped_by_budget = not budget_ok()
        status = "OK" if result.returncode == 0 else f"FAIL({result.returncode})"
        print(f"[ORCH] {'✓' if result.returncode == 0 else '✗'} {name} — "
              f"{status}, {dur:.0f}s, budget ${today_spent():.2f}")
        return result.returncode, dur, stopped_by_budget
    except subprocess.TimeoutExpired:
        print(f"[ORCH] ✗ {name} — timeout {timeout}s")
        return 124, timeout, False
    except Exception as e:
        print(f"[ORCH] ✗ {name} — exception: {e}")
        return 1, 0, False


# ═══════════════════════════════════════════════════════════════
# DAILY CYCLE
# ═══════════════════════════════════════════════════════════════
def run_daily_cycle():
    """Един пълен цикъл: extract → merge → classify → aggregate."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + f"  DAILY CYCLE  —  {datetime.now().strftime('%Y-%m-%d %H:%M')}".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"\n  Budget: ${today_spent():.2f} / ${DAILY_BUDGET:.2f}")
    print(f"  Pending: extract={count_pending_extract()} "
          f"merge={count_pending_merge()} "
          f"classify={count_pending_classify()} "
          f"aggregate={count_pending_aggregate()}")

    if not budget_ok():
        print(f"\n  ✗ Бюджетът е над ${STOP_AT:.2f} — skip днес")
        return False

    did_work = False

    # ─── 1. Extract ───
    if budget_ok() and count_pending_extract() > 0:
        rc, dur, stopped = run_phase(["pdf_chunker.py", "--extract"],
                                     "extract (всички PDF-ове)", timeout=10800)
        did_work = True
        if stopped or not budget_ok():
            print(f"\n  ⏸ Бюджетът свърши по време на extract")
            return True

    # ─── 2. Merge (безплатно) ───
    if count_pending_merge() > 0:
        run_phase(["pdf_chunker.py", "--merge"], "merge", timeout=600)
        did_work = True

    # ─── 3. Classify ───
    if budget_ok() and count_pending_classify() > 0:
        rc, dur, stopped = run_phase(["pdf_chunker.py", "--classify"],
                                     "classify", timeout=7200)
        did_work = True
        if stopped or not budget_ok():
            print(f"\n  ⏸ Бюджетът свърши по време на classify")
            return True

    # ─── 4. Aggregate (безплатно) ───
    if count_pending_aggregate() > 0 or count_pending_classify() == 0:
        run_phase(["pdf_chunker.py", "--aggregate"], "aggregate", timeout=600)
        did_work = True

    # ─── 5. Stats ───
    run_phase(["pdf_chunker.py", "--stats"], "stats", timeout=60)

    return did_work


# ═══════════════════════════════════════════════════════════════
# WAIT UNTIL TOMORROW
# ═══════════════════════════════════════════════════════════════
def wait_until_tomorrow():
    """Чака до 00:01 следващия ден."""
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(
        hour=RESUME_HOUR, minute=1, second=0, microsecond=0
    )
    wait_sec = (tomorrow - now).total_seconds()
    print(f"\n⏸ Бюджетът свърши. Чакам до {tomorrow.strftime('%Y-%m-%d %H:%M')}")
    print(f"  ({wait_sec/3600:.1f} часа)")
    time.sleep(wait_sec)


# ═══════════════════════════════════════════════════════════════
# DAEMON MODE
# ═══════════════════════════════════════════════════════════════
def run_daemon():
    print("╔" + "═" * 68 + "╗")
    print("║" + "  ORCHESTRATOR 24/7".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"\n  Daily budget: ${DAILY_BUDGET:.2f}")
    print(f"  Stop threshold: ${STOP_AT:.2f} (85%)")
    print(f"  Resume at: {RESUME_HOUR:02d}:01 daily")
    print(f"  State files: {len(STATE_FILES)}")
    print()

    cycle = 0
    while True:
        cycle += 1
        print(f"\n\n{'━' * 70}")
        print(f"  CYCLE #{cycle}")
        print(f"{'━' * 70}")

        try:
            did_work = run_daily_cycle()
        except KeyboardInterrupt:
            print("\n\n[ORCH] Спирам по потребителско желание")
            return
        except Exception as e:
            print(f"\n[ORCH] Грешка в цикъл: {e}")
            import traceback
            traceback.print_exc()
            print(f"  Чакам 5 мин преди retry...")
            time.sleep(300)
            continue

        # Решение какво следва
        if not budget_ok():
            wait_until_tomorrow()
            continue

        if not did_work:
            # Няма pending работа — чакаме нови PDF-ове
            pending_total = (count_pending_extract() +
                             count_pending_merge() +
                             count_pending_classify())
            if pending_total == 0:
                print(f"\n✓ Всичко готово. Няма pending работа.")
                print(f"  Чакам 1 час и проверявам пак...")
                time.sleep(3600)
                continue

        # Имаше работа, но не всичко свърши — пускай пак след 2 мин
        print(f"\n  Остават: extract={count_pending_extract()} "
              f"merge={count_pending_merge()} classify={count_pending_classify()}")
        print(f"  Следващ цикъл след 2 мин...")
        time.sleep(120)


# ═══════════════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════════════
def print_status():
    print("\n" + "═" * 60)
    print("  ORCHESTRATOR STATUS")
    print("═" * 60)
    print(f"\n  Date          : {date.today()}")
    print(f"  Budget spent  : ${today_spent():.4f} / ${DAILY_BUDGET:.2f}")
    print(f"  Budget OK     : {'✓' if budget_ok() else '✗ (would stop)'}")
    print(f"\n  Pending work:")
    print(f"    extract   : {count_pending_extract()} PDFs")
    print(f"    merge     : {count_pending_merge()} olympiads")
    print(f"    classify  : {count_pending_classify()} olympiads")
    print(f"    aggregate : {'needed' if count_pending_aggregate() else 'up-to-date'}")
    print(f"\n  State files:")
    for f in STATE_FILES:
        status = f"✓ {f.stat().st_size}B" if f.exists() else "✗ missing"
        print(f"    {f.name:<25} {status}")
    print("\n" + "═" * 60)


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true",
                    help="Един дневен цикъл и изход")
    ap.add_argument("--daemon", action="store_true",
                    help="24/7 фонов режим")
    ap.add_argument("--status", action="store_true",
                    help="Само статус")
    args = ap.parse_args()

    if args.status or (not args.once and not args.daemon):
        print_status()
        return 0

    if args.daemon:
        run_daemon()
        return 0

    if args.once:
        run_daily_cycle()
        print_status()
        return 0


if __name__ == "__main__":
    sys.exit(main())