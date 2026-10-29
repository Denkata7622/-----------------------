#!/usr/bin/env python3
"""scan_status.py — показва текущия статус на pipeline stages."""
import sys, io, json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

GEN = Path(__file__).parent.parent / "generated"

SEP_THIN = "-" * 70
SEP_THICK = "=" * 70


def scan_stage(name, subdir, file_name="all_problems.json"):
    d = GEN / subdir
    if not d.exists():
        print(f"\n{name.upper()}: (не съществува)")
        return 0, 0

    total_problems = 0
    total_stmt = 0
    total_sol = 0
    files = 0

    print(f"\n{name.upper()}:")
    for sub in sorted(d.iterdir()):
        if not sub.is_dir():
            continue
        f = sub / file_name
        if not f.exists():
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            probs = data.get("problems", [])
            n = len(probs)
            with_stmt = sum(1 for p in probs if (p.get("statement") or "").strip())
            with_sol = sum(1 for p in probs if (p.get("solution") or "").strip())
            total_problems += n
            total_stmt += with_stmt
            total_sol += with_sol
            files += 1
            print(f"  {sub.name:<60} {n:>4} prob  ({with_stmt} stmt, {with_sol} sol)")
        except Exception as e:
            print(f"  {sub.name:<60} ERROR: {e}")

    print(SEP_THIN)
    print(f"  {files} files, {total_problems} problems total")
    print(f"  ({total_stmt} with stmt, {total_sol} with sol)")
    return files, total_problems


def scan_anchors():
    d = GEN / "anchors"
    if not d.exists():
        print(f"\nANCHORS: (не съществува)")
        return 0, 0

    files = sorted(d.glob("*.json"))
    real = [f for f in files if not f.name.startswith("_")]
    total = 0
    print(f"\nANCHORS:")
    for f in real:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            n = data.get("total", 0)
            pid = data.get("point_id", f.stem)
            d_diff = data.get("by_difficulty", {})
            easy = d_diff.get("easy", 0)
            med = d_diff.get("medium", 0)
            hard = d_diff.get("hard", 0)
            total += n
            print(f"  {pid:<10} {n:>3} prob  (e={easy}, m={med}, h={hard})")
        except Exception:
            pass

    uncl = d / "_unclassified.json"
    if uncl.exists():
        try:
            data = json.loads(uncl.read_text(encoding="utf-8"))
            print(f"  {'unclassified':<10} {data.get('total', 0):>3} prob")
        except Exception:
            pass

    print(SEP_THIN)
    print(f"  {len(real)} point-files, {total} real problems")
    return len(real), total


def scan_state():
    state_file = GEN / "state" / "chunker_state.json"
    if not state_file.exists():
        print(f"\nCHUNKER STATE: (не съществува)")
        return

    data = json.loads(state_file.read_text(encoding="utf-8"))
    extracted = data.get("extracted", {})

    done = []
    partial = []
    for name, info in extracted.items():
        status = info.get("status", "?")
        n = info.get("problems", 0)
        if status == "done":
            done.append((name, n))
        elif status == "partial":
            failed = info.get("failed_chunks", "?")
            total = info.get("total_chunks", "?")
            partial.append((name, failed, total))

    print(f"\nCHUNKER STATE:")
    print(f"  done:    {len(done)}")
    print(f"  partial: {len(partial)}")
    for name, n in sorted(done):
        print(f"    [done]    {name:<55} {n:>4} prob")
    for name, f, t in sorted(partial):
        print(f"    [partial] {name:<55} {f}/{t} chunks")


def main():
    print(SEP_THICK)
    print("  PIPELINE STATUS")
    print(SEP_THICK)

    ex_files, ex_probs = scan_stage("extracted", "cache/extracted")
    mg_files, mg_probs = scan_stage("merged", "cache/merged")
    cl_files, cl_probs = scan_stage("classified", "cache/classified")
    an_files, an_probs = scan_anchors()
    scan_state()

    print(f"\n{SEP_THICK}")
    print("  SUMMARY")
    print(SEP_THICK)
    print(f"  extracted:    {ex_files:>3} files, {ex_probs:>4} problems")
    print(f"  merged:       {mg_files:>3} files, {mg_probs:>4} problems")
    print(f"  classified:   {cl_files:>3} files, {cl_probs:>4} problems")
    print(f"  anchors:      {an_files:>3} files, {an_probs:>4} problems")
    print(SEP_THICK)


if __name__ == "__main__":
    main()