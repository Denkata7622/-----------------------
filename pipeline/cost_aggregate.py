#!/usr/bin/env python3
"""cost_aggregate.py — обединява provider_costs.json + ledger.jsonl."""
import argparse, json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.resolve()
DEFAULT_HISTORICAL = BASE / "provider_costs.json"
DEFAULT_LEDGER     = BASE.parent / "generated" / "costs" / "ledger.jsonl"
DEFAULT_OUT        = BASE.parent / "generated" / "costs" / "combined.json"


def read_ledger(path, since=None):
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            if since and (e.get("ts") or "")[:10] < since:
                continue
            out.append(e)
    return out


def read_json_entries(path):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data.get("entries", [])
    except Exception:
        return []


def _empty_bucket():
    return {
        "calls": 0, "tokens": 0, "cost": 0.0, "errors": 0,
        "reasoning_tokens": 0, "cached_tokens": 0,
        "cost_prompt": 0.0, "cost_completion": 0.0,
    }


def aggregate(entries):
    by_model = defaultdict(_empty_bucket)
    by_day   = defaultdict(_empty_bucket)
    by_role  = defaultdict(_empty_bucket)
    totals   = _empty_bucket()

    for e in entries:
        model  = e.get("model") or "unknown"
        day    = (e.get("ts") or "")[:10]
        role   = e.get("role") or e.get("module") or "unknown"
        cost   = float(e.get("cost") or 0.0)
        tokens = int(e.get("tokens") or (e.get("in_tokens", 0) + e.get("out_tokens", 0)))
        reason = int(e.get("reasoning_tokens") or 0)
        cached = int(e.get("cached_tokens") or 0)
        c_prom = float(e.get("cost_prompt") or 0.0)
        c_comp = float(e.get("cost_completion") or 0.0)
        is_err = (e.get("status") == "error")

        for bucket in (by_model[model], by_day[day], by_role[role], totals):
            bucket["calls"]              += 1
            bucket["tokens"]             += tokens
            bucket["cost"]               += cost
            bucket["reasoning_tokens"]   += reason
            bucket["cached_tokens"]      += cached
            bucket["cost_prompt"]        += c_prom
            bucket["cost_completion"]    += c_comp
            if is_err:
                bucket["errors"] += 1

    # rounded floats (за да не излизат 0.000000000000001 в JSON)
    def _round(d):
        for b in d.values():
            for k in ("cost", "cost_prompt", "cost_completion"):
                b[k] = round(b[k], 6)
    _round(by_model); _round(by_day); _round(by_role)
    for k in ("cost", "cost_prompt", "cost_completion"):
        totals[k] = round(totals[k], 6)

    return {
        "by_model": {k: v for k, v in sorted(by_model.items(), key=lambda x: -x[1]["cost"])},
        "by_day":   dict(sorted(by_day.items())),
        "by_role":  {k: v for k, v in sorted(by_role.items(), key=lambda x: -x[1]["cost"])},
        "totals":   totals,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--historical", default=str(DEFAULT_HISTORICAL))
    ap.add_argument("--ledger",     default=str(DEFAULT_LEDGER))
    ap.add_argument("--out",        default=str(DEFAULT_OUT))
    ap.add_argument("--since",      default=None)
    args = ap.parse_args()

    hist = read_json_entries(Path(args.historical))
    live = read_ledger(Path(args.ledger), since=args.since)
    combined = hist + live
    agg = aggregate(combined)

    out = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "sources": {"historical": len(hist), "live": len(live), "combined": len(combined)},
        **agg,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    t = out["totals"]
    print(f"→ {out_path}")
    print(f"  Historical:  {len(hist)} entries")
    print(f"  Live:        {len(live)} entries")
    print(f"  Total:       ${t['cost']:.4f} ({t['calls']} calls)")
    print(f"  Reasoning:   {t['reasoning_tokens']:,} tokens")
    print(f"  Cached:      {t['cached_tokens']:,} tokens")
    print(f"  Cost split:  ${t['cost_prompt']:.4f} prompt  +  ${t['cost_completion']:.4f} completion")
    print(f"  Models:      {len(out['by_model'])}")
    print(f"  Days:        {len(out['by_day'])}")
    print(f"  Roles:       {len(out['by_role'])}")


if __name__ == "__main__":
    main()