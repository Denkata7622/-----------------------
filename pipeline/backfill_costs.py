#!/usr/bin/env python3
"""
backfill_costs.py — robust reconstruction of costs.jsonl
"""
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.resolve()
STATE = BASE / "state.json"
COSTS = BASE / "costs.jsonl"
LOGS_DIR = BASE / "logs"
ARTICLES_DIR = BASE.parent / "generated" / "articles"

MAX_GAP_SEC = 3600  # If gen→ver gap > 1h, timestamps are unreliable


def log(msg):
    print(msg, flush=True)


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════
# LOG PARSER
# ═══════════════════════════════════════════════════════════════
_LOG_LINE = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\[(\w+)\]\s+(.*)$')
_ITEM_ID = re.compile(r'\[(\d+\.\d+|R\.\d+)\]')  # only match IDs inside brackets


def parse_logs(logs_dir):
    items = {}
    if not logs_dir.exists():
        return items

    for log_file in sorted(logs_dir.glob("pipeline_*.log")):
        try:
            content = log_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for line in content.splitlines():
            m = _LOG_LINE.match(line)
            if not m:
                continue
            ts_str, level, msg = m.groups()
            try:
                ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").timestamp()
            except Exception:
                continue

            im = _ITEM_ID.search(msg)
            if not im:
                continue
            item_id = im.group(1)

            entry = items.setdefault(item_id, {
                "start_ts": None, "end_ts": None, "attempts": [],
            })

            if "▶" in msg and "опит" in msg:
                if entry["start_ts"] is None:
                    entry["start_ts"] = ts

            if re.search(r'💾 Temp: attempt-01-initial\.md \(\d+w, score \?\)', msg):
                entry["attempts"].append({"gen_done_ts": ts, "ver_done_ts": None, "score": None})

            m1 = re.search(r'💾 Temp: attempt-01-initial\.md \(\d+w, score (\d+)\)', msg)
            if m1 and entry["attempts"] and entry["attempts"][-1]["ver_done_ts"] is None:
                entry["attempts"][-1]["ver_done_ts"] = ts
                entry["attempts"][-1]["score"] = int(m1.group(1))

            if re.search(r'💾 Temp: attempt-\d+-retry-\d+\.md \(\d+w, score \?\)', msg):
                entry["attempts"].append({"gen_done_ts": ts, "ver_done_ts": None, "score": None})

            m2 = re.search(r'💾 Temp: attempt-\d+-retry-\d+\.md \(\d+w, score (\d+)\)', msg)
            if m2 and entry["attempts"] and entry["attempts"][-1]["ver_done_ts"] is None:
                entry["attempts"][-1]["ver_done_ts"] = ts
                entry["attempts"][-1]["score"] = int(m2.group(1))

            if msg.startswith("✓"):
                entry["end_ts"] = ts

    return items


# ═══════════════════════════════════════════════════════════════
# VERIFICATION READER
# ═══════════════════════════════════════════════════════════════
def read_ver_attempts(article_dir, fallback_model):
    attempts = []
    if not article_dir.exists():
        return attempts

    temp_dir = article_dir / "temp"
    if temp_dir.exists():
        for f in sorted(temp_dir.glob("attempt-*-verify.json")):
            data = _read_json(f)
            if not isinstance(data, dict):
                continue
            tokens = data.get("_tokens", 0) or 0
            model = data.get("_model") or data.get("model") or fallback_model
            if tokens > 0:
                attempts.append({
                    "tokens": tokens,
                    "model": model,
                    "score": data.get("score"),
                    "verdict": data.get("verdict"),
                    "source": f.name,
                })

    if not attempts:
        verify_files = sorted(article_dir.glob("verify-v*.json"))
        if verify_files:
            data = _read_json(verify_files[-1])
            if isinstance(data, dict):
                tokens = data.get("_tokens", 0) or 0
                model = data.get("_model") or data.get("model") or fallback_model
                if tokens > 0:
                    attempts.append({
                        "tokens": tokens,
                        "model": model,
                        "score": data.get("score"),
                        "verdict": data.get("verdict"),
                        "source": verify_files[-1].name,
                    })

    return attempts


# ═══════════════════════════════════════════════════════════════
# GLOBAL RATIO
# ═══════════════════════════════════════════════════════════════
def compute_global_ver_ratio(all_items):
    ratios = []
    for item in all_items:
        pid = item["pid"]
        total_tokens = item["data"].get("tokens", 0) or 0
        if total_tokens <= 0:
            continue
        article_dir = ARTICLES_DIR / pid.replace(".", "_")
        ver = read_ver_attempts(article_dir, "unknown")
        if not ver:
            continue
        sum_tokens = sum(a["tokens"] for a in ver)
        if 0 < sum_tokens < total_tokens:
            ratios.append(sum_tokens / total_tokens)
    return round(sum(ratios) / len(ratios), 3) if ratios else 0.4


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def _ts_iso(ts):
    return datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def _sane_timestamps(gen_ts, ver_ts, item_ts):
    """
    Ensure gen_ts < ver_ts and both are reasonable.
    Fallback to item_ts if data is missing or corrupted.
    """
    # If either is missing, fallback to item_ts
    if not gen_ts or not ver_ts:
        if item_ts:
            return (item_ts - 60, item_ts)
        return (gen_ts or ver_ts or 0, gen_ts or ver_ts or 0)

    # If reversed or gap is absurd, fallback
    if ver_ts <= gen_ts or (ver_ts - gen_ts) > MAX_GAP_SEC:
        # Use item_ts pair if available
        if item_ts:
            return (item_ts - 60, item_ts)
        # Otherwise force gap of 60s
        return (gen_ts, gen_ts + 60)

    return (gen_ts, ver_ts)


# ═══════════════════════════════════════════════════════════════
# ENTRY BUILDER
# ═══════════════════════════════════════════════════════════════
def build_entries(pid, data, log_info, global_ratio):
    total_cost = data.get("cost", 0) or 0
    total_tokens = data.get("tokens", 0) or 0
    gen_model = data.get("generator_model") or "unknown"
    ver_model = data.get("verifier_model") or "unknown"
    item_ts = data.get("ts") or 0

    if total_cost <= 0:
        return []

    article_dir = ARTICLES_DIR / pid.replace(".", "_")
    ver_attempts = read_ver_attempts(article_dir, ver_model)
    n_ver = len(ver_attempts)
    ver_tokens_known = sum(a["tokens"] for a in ver_attempts)

    log_attempts = log_info.get("attempts") or []
    n_log = len(log_attempts)
    item_start = log_info.get("start_ts")
    item_end = log_info.get("end_ts")

    # Determine ver_ratio
    if n_ver > 0 and total_tokens > 0:
        if n_log >= n_ver and n_ver > 0:
            est_ver_tokens = ver_tokens_known * max(n_log, n_ver) / n_ver
        else:
            est_ver_tokens = ver_tokens_known
        if 0 < est_ver_tokens < total_tokens:
            ver_ratio = est_ver_tokens / total_tokens
            method = "exact_tokens"
        else:
            ver_ratio = global_ratio
            method = "global_ratio"
    else:
        ver_ratio = global_ratio
        method = "global_ratio"

    ver_cost_total = total_cost * ver_ratio
    gen_cost_total = total_cost - ver_cost_total

    entries = []

    # Multi-attempt split (only when we have full verification data)
    if n_ver > 0 and n_log == n_ver and ver_tokens_known > 0:
        for i in range(n_ver):
            va = ver_attempts[i]
            la = log_attempts[i] if i < n_log else {}

            att_ver_tokens = va["tokens"]
            att_ver_cost = ver_cost_total * (att_ver_tokens / ver_tokens_known)
            att_gen_cost = gen_cost_total / n_ver
            att_gen_tokens = int((total_tokens - ver_tokens_known) / n_ver)

            gen_ts = la.get("gen_done_ts")
            ver_ts = la.get("ver_done_ts")
            gen_ts, ver_ts = _sane_timestamps(
                gen_ts, ver_ts, item_ts if i == n_ver - 1 else None
            )

            gen_role = "gen" if i == 0 else f"gen_retry_{i}"
            ver_role = "ver" if i == 0 else f"ver_retry_{i}"

            if att_gen_cost > 0:
                entries.append({
                    "ts": _ts_iso(gen_ts),
                    "item": pid,
                    "role": gen_role,
                    "model": gen_model,
                    "tokens": att_gen_tokens,
                    "cost": round(att_gen_cost, 6),
                    "_method": method,
                })
            if att_ver_cost > 0:
                entries.append({
                    "ts": _ts_iso(ver_ts),
                    "item": pid,
                    "role": ver_role,
                    "model": va["model"],
                    "tokens": att_ver_tokens,
                    "cost": round(att_ver_cost, 6),
                    "_method": method,
                })
        return entries

    # Single pair
    gen_ts = None
    ver_ts = None
    if log_attempts:
        gen_ts = log_attempts[0].get("gen_done_ts")
        # For ver, use the LAST attempt's ver_done_ts (end of all processing)
        for la in reversed(log_attempts):
            if la.get("ver_done_ts"):
                ver_ts = la["ver_done_ts"]
                break

    if not gen_ts:
        gen_ts = item_start
    if not ver_ts:
        ver_ts = item_end

    gen_ts, ver_ts = _sane_timestamps(gen_ts, ver_ts, item_ts)

    # Token split
    if n_ver > 0 and total_tokens > 0:
        est_ver_tokens = ver_tokens_known
        if n_log > n_ver:
            est_ver_tokens = int(ver_tokens_known * n_log / n_ver)
        est_ver_tokens = min(est_ver_tokens, int(total_tokens * 0.9))
        ver_tokens = est_ver_tokens
        gen_tokens = total_tokens - ver_tokens
    else:
        ver_tokens = int(total_tokens * ver_ratio)
        gen_tokens = total_tokens - ver_tokens

    if gen_cost_total > 0:
        entries.append({
            "ts": _ts_iso(gen_ts),
            "item": pid,
            "role": "gen",
            "model": gen_model,
            "tokens": gen_tokens,
            "cost": round(gen_cost_total, 6),
            "_method": method,
        })
    if ver_cost_total > 0:
        entries.append({
            "ts": _ts_iso(ver_ts),
            "item": pid,
            "role": "ver",
            "model": ver_model,
            "tokens": ver_tokens,
            "cost": round(ver_cost_total, 6),
            "_method": method,
        })

    return entries


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--no-method", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not STATE.exists():
        log(f"✗ state.json не съществува: {STATE}")
        return 1

    state = _read_json(STATE)
    if not state:
        log("✗ Не мога да прочета state.json")
        return 1

    procs = state.get("processed", {})
    if not isinstance(procs, dict):
        log("✗ processed не е dict")
        return 1

    log(f"📖 state.json: {len(procs)} items")

    log_data = parse_logs(LOGS_DIR)
    log(f"📖 logs/: {len(log_data)} items с log данни")

    all_items = []
    skipped = 0
    for pid, data in procs.items():
        if not isinstance(data, dict):
            skipped += 1
            continue
        if data.get("status") != "done":
            skipped += 1
            continue
        all_items.append({"pid": pid, "data": data})

    log(f"   → {len(all_items)} done items ({skipped} skipped)")

    if not all_items:
        log("✗ Няма done items")
        return 1

    global_ratio = compute_global_ver_ratio(all_items)
    log(f"📊 Global ver/total ratio: {global_ratio:.3f} ({global_ratio*100:.1f}%)")

    log(f"\n🔧 Строя entries…")
    all_entries = []
    method_counts = {}
    per_attempt_count = 0
    single_pair_count = 0
    unknown_models = 0

    for item in all_items:
        pid = item["pid"]
        data = item["data"]
        log_info = log_data.get(pid, {})
        entries = build_entries(pid, data, log_info, global_ratio)
        if not entries:
            continue

        if any(e.get("model") == "unknown" for e in entries):
            unknown_models += 1

        has_retry = any("_retry_" in e["role"] for e in entries)
        if has_retry:
            per_attempt_count += 1
        else:
            single_pair_count += 1

        for e in entries:
            m = e.get("_method", "unknown")
            method_counts[m] = method_counts.get(m, 0) + 1
        all_entries.extend(entries)

        if args.verbose:
            log(f"  {pid}: {len(entries)} entries")
            for e in entries:
                log(f"    {e['ts'][11:19]} {e['role']:<14} ${e['cost']:.6f}  {e['tokens']:>7}tok  {e.get('_method','')}")

    if args.no_method:
        for e in all_entries:
            e.pop("_method", None)

    all_entries.sort(key=lambda e: e["ts"])
    total = sum(e["cost"] for e in all_entries)

    # Correct comparison field:
    state_total = state.get("total_cost_usd", 0)
    state_budget_today = state.get("budget", {}).get("spent_usd", 0)

    log(f"\n📊 Резултат:")
    log(f"   Entries: {len(all_entries)}")
    log(f"   Items per-attempt: {per_attempt_count}  |  single-pair: {single_pair_count}")
    log(f"   Unknown models: {unknown_models}")
    log(f"   Method breakdown: {method_counts}")
    log(f"   Sum cost:       ${total:.4f}")
    log(f"   state.total:    ${state_total:.4f}")
    log(f"   state.budget:   ${state_budget_today:.4f} (днес)")
    if state_total > 0:
        diff_pct = (total - state_total) / state_total * 100
        log(f"   Diff vs total:  ${total - state_total:+.4f}  ({diff_pct:+.1f}%)")

    if args.dry_run:
        log(f"\n⚠ DRY RUN — нищо не е записано")
        for e in all_entries[:15]:
            log(f"   {e}")
        if len(all_entries) > 15:
            log(f"   … и още {len(all_entries) - 15}")
        return 0

    if args.append:
        existing = set()
        if COSTS.exists():
            for line in COSTS.read_text(encoding="utf-8").splitlines():
                try:
                    e = json.loads(line)
                    existing.add((e.get("item"), e.get("role"), e.get("ts")))
                except Exception:
                    pass
        new_entries = [e for e in all_entries
                       if (e.get("item"), e.get("role"), e.get("ts")) not in existing]
        log(f"\n📝 Append: {len(new_entries)} нови, {len(all_entries) - len(new_entries)} дубликата")
        with open(COSTS, "a", encoding="utf-8") as f:
            for e in new_entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        log(f"✓ Дописани {len(new_entries)} entries")
    else:
        if COSTS.exists():
            backup = COSTS.with_suffix(f".jsonl.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            COSTS.rename(backup)
            log(f"\n💾 Backup → {backup.name}")
        with open(COSTS, "w", encoding="utf-8") as f:
            for e in all_entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        log(f"✓ Записани {len(all_entries)} entries → {COSTS}")

    return 0


if __name__ == "__main__":
    sys.exit(main())