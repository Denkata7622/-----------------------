#!/usr/bin/env python3
"""
master_migrate.py v2 — чист migration без consolidate.

Сценарий: регенерираш chunker data от нула, но пазиш скъпите неща
(статии, OCR cache, генерирани задачи, gap анализи, logs).

Прави:
  STEP 1: Migrate valuable data → generated/  (articles, OCR, logs, state)
  STEP 2: Archive old chunker data → backups/<ts>/
  STEP 3: Reset chunker state (extracted/merged/classified → fresh)
  STEP 4: Verify

Употреба:
    python master_migrate.py              # dry run
    python master_migrate.py --apply      # изпълнява
    python master_migrate.py --apply --wipe-articles
    python master_migrate.py --apply --wipe-ocr
    python master_migrate.py --verify-only
"""
import sys, io, shutil, json, argparse
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PIPE    = Path(__file__).parent.resolve()
ROOT    = PIPE.parent
GEN     = ROOT / "generated"
BACKUPS = ROOT / "backups"

MIN_FILE_SIZE = 100  # files < 100 bytes are stubs/empty


# ═══════════════════════════════════════════════════════════════
# STEP 1: MIGRATE valuable data
# ═══════════════════════════════════════════════════════════════
MIGRATE_MOVES = [
    # (source,                          target,              keep)
    ("output",       "articles"),        # 160 статии
    (".ocr_cache",   "cache/ocr"),       # 69 OCR pages (paid)
    ("logs",         "logs"),            # audit trail
]

MIGRATE_STATE_FILES = [
    "state.json",          # статии state — пазим
    "problem_state.json",  # 1_4 генерирано
    "gap_state.json",      # gap анализи
    # chunker_state.json — НЕ (reset)
]

MIGRATE_DIRS = [
    "articles", "anchors", "logs", "state",
    "cache/extracted", "cache/merged", "cache/classified", "cache/ocr",
]


def step_migrate(dry_run=True, wipe_articles=False, wipe_ocr=False):
    print("\n" + "═" * 72)
    print("  STEP 1/4: MIGRATE valuable data → generated/")
    print("═" * 72)

    to_migrate = []
    for src_name, dst_name in MIGRATE_MOVES:
        if wipe_articles and src_name == "output":
            print(f"  [SKIP]    {src_name:<15} (wipe-articles)")
            continue
        if wipe_ocr and src_name == ".ocr_cache":
            print(f"  [SKIP]    {src_name:<15} (wipe-ocr)")
            continue

        src = PIPE / src_name
        if not src.exists():
            print(f"  [missing] {src_name}")
            continue
        n = sum(1 for _ in src.iterdir())
        to_migrate.append((src_name, dst_name, src, n))
        print(f"  [KEEP]    {src_name:<15} → {dst_name:<15} ({n} items)")

    states = []
    for f in MIGRATE_STATE_FILES:
        p = PIPE / f
        if p.exists():
            states.append((f, p, p.stat().st_size))
            print(f"  [KEEP]    {f:<28} ({p.stat().st_size} B)")

    if dry_run:
        print(f"\n  DRY RUN — would move {len(to_migrate)} folders + {len(states)} state files")
        return

    print("\n  APPLYING...")

    for d in MIGRATE_DIRS:
        (GEN / d).mkdir(parents=True, exist_ok=True)
    print("  OK — created target dirs")

    moved = 0
    for src_name, dst_name, src, _ in to_migrate:
        dst = GEN / dst_name
        for item in src.iterdir():
            target = dst / item.name
            if target.exists():
                target = target.parent / f"{target.stem}_from_{src_name}{target.suffix}"
            try:
                shutil.move(str(item), str(target))
                moved += 1
            except Exception as e:
                print(f"  [FAIL] {item.name}: {e}")
        try:
            src.rmdir()
        except OSError:
            pass
    print(f"  OK — moved {moved} items")

    for f, src, _ in states:
        dst = GEN / "state" / f
        try:
            shutil.move(str(src), str(dst))
        except Exception as e:
            print(f"  [FAIL] {f}: {e}")
    print(f"  OK — moved {len(states)} state files")


# ═══════════════════════════════════════════════════════════════
# STEP 2: ARCHIVE old chunker data → backups/<ts>/
# ═══════════════════════════════════════════════════════════════
ARCHIVE_ITEMS = [
    # current (empty) chunker dirs
    (PIPE / "extracted",                       "chunker"),
    (PIPE / "merged",                          "chunker"),
    (PIPE / "classified",                      "chunker"),
    (PIPE / "real_problems",                   "chunker"),
    # old backup copies
    (PIPE / "extracted_20261020_1652",         "chunker-old"),
    (PIPE / "extracted_backup_20261020_1854",  "chunker-old"),
    (PIPE / "merged_20261020_1652",            "chunker-old"),
    (PIPE / "merged_backup_20261020_1854",     "chunker-old"),
    (PIPE / "classified_20261020_1652",        "chunker-old"),
    (PIPE / "classified_backup_20261020_1854", "chunker-old"),
    (PIPE / "real_problems_20261020_1652",     "chunker-old"),
    (PIPE / "real_problems_backup_20261020_1854","chunker-old"),
    # state backup files
    (PIPE / "chunker_state.json",                    "chunker-state"),
    (PIPE / "chunker_state_20261020_1652.json",      "chunker-state"),
    (PIPE / "chunker_state_backup_20261020_1854.json","chunker-state"),
    (PIPE / "state.json.broken-1792170226",          "chunker-state"),
    # old python backups
    (PIPE / "problem_generator.py.bak",              "code-old"),
    (PIPE / "prompts.bak.py",                        "code-old"),
    # root index.html backups
    (ROOT / "index.html.bak-1792422047",             "index-backups"),
    (ROOT / "index.html.bak-1792422424",             "index-backups"),
    (ROOT / "index.html.bak-1792422897",             "index-backups"),
    (ROOT / "Backup",                                "index-backups"),
]


def step_archive(dry_run=True):
    print("\n" + "═" * 72)
    print("  STEP 2/4: ARCHIVE old chunker + backups → backups/<ts>/")
    print("═" * 72)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archive_root = BACKUPS / ts

    existing = []
    total_size = 0
    for p, category in ARCHIVE_ITEMS:
        if not p.exists():
            continue
        if p.is_dir():
            size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            n = sum(1 for f in p.rglob("*") if f.is_file())
            print(f"  [dir/{category:<12}]  {p.name:<42} ({n} files, {size/1024:.0f} KB)")
        else:
            size = p.stat().st_size
            print(f"  [file/{category:<11}]  {p.name:<42} ({size/1024:.1f} KB)")
        total_size += size
        existing.append((p, category))

    if not existing:
        print("\n  Няма какво да се архивира.")
        return

    print(f"\n  Total: {len(existing)} items, {total_size/1024/1024:.1f} MB")

    if dry_run:
        print(f"\n  DRY RUN — would move to: backups/{ts}/")
        return

    # Safety: only archive if generated/articles exists with real content
    if not (GEN / "articles").exists():
        print("\n  ✗ ABORT: generated/articles/ не съществува.")
        print("    Пусни migration първо.")
        return
    articles_n = sum(1 for _ in (GEN / "articles").iterdir())
    if articles_n < 100:
        print(f"\n  ✗ ABORT: generated/articles/ има само {articles_n} items.")
        print("    Очаквам ≥100. Не архивирам нищо.")
        return

    archive_root.mkdir(parents=True, exist_ok=True)

    # Group by category
    by_cat = {}
    for p, category in existing:
        by_cat.setdefault(category, []).append(p)

    moved = 0
    for category, items in by_cat.items():
        cat_dir = archive_root / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        for p in items:
            target = cat_dir / p.name
            try:
                shutil.move(str(p), str(target))
                moved += 1
                print(f"  ✓ {category}/{p.name}")
            except Exception as e:
                print(f"  ✗ {p.name}: {e}")

    print(f"\n  OK — archived {moved}/{len(existing)} items")
    print(f"  Location: backups/{ts}/")
    print(f"  (НЕ са изтрити — можеш да ги върнеш ръчно)")

    return ts


# ═══════════════════════════════════════════════════════════════
# STEP 3: RESET chunker state
# ═══════════════════════════════════════════════════════════════
def step_reset(dry_run=True):
    print("\n" + "═" * 72)
    print("  STEP 3/4: RESET chunker state (fresh start)")
    print("═" * 72)

    # chunker_state.json is archived in step 2
    # Nothing else to reset — dirs will be recreated on next run
    print("  chunker_state.json → архивиран в step 2 (fresh state on next run)")
    print("  extracted/, merged/, classified/, real_problems/ → архивирани")
    print("  → следващият --extract ще започне от нула")

    if not dry_run:
        print("\n  ✓ Няма активни промени — state файлът вече е архивиран")


# ═══════════════════════════════════════════════════════════════
# STEP 4: VERIFY
# ═══════════════════════════════════════════════════════════════
def step_verify():
    print("\n" + "═" * 72)
    print("  STEP 4/4: VERIFY")
    print("═" * 72)

    if not GEN.exists():
        print("  ✗ generated/ НЕ съществува")
        return

    print("\n  generated/:")
    for sub in ["articles", "anchors", "cache/extracted", "cache/merged",
                "cache/classified", "cache/ocr", "logs", "state"]:
        p = GEN / sub
        if not p.exists():
            print(f"    · {sub:<20} (не съществува — OK, ще се създаде)")
            continue
        real  = sum(1 for f in p.rglob("*") if f.is_file() and f.stat().st_size >= MIN_FILE_SIZE)
        total = sum(1 for f in p.rglob("*") if f.is_file())
        if real == 0 and total == 0:
            print(f"    ✓ {sub:<20} празно (fresh)")
        else:
            print(f"    ✓ {sub:<20} {real} real + {total-real} stubs")

    state_dir = GEN / "state"
    if state_dir.exists():
        for f in ["state.json", "problem_state.json",
                  "gap_state.json", "chunker_state.json"]:
            p = state_dir / f
            if p.exists():
                print(f"    ✓ state/{f:<20} {p.stat().st_size} B")
            else:
                print(f"    · state/{f:<20} (missing — OK if reset)")

    print("\n  pipeline/ (code + still-in-use data):")
    keep_dirs = {"gap_output", "problems", "__pycache__", "logs"}
    for p in sorted(PIPE.iterdir()):
        if p.is_dir():
            n = sum(1 for f in p.rglob("*") if f.is_file())
            keep = "✓" if p.name in keep_dirs else "?"
            print(f"    {keep} {p.name}/ ({n} files)")
        else:
            size = p.stat().st_size
            if size > 1000:
                print(f"    · {p.name:<35} {size/1024:.1f} KB")

    if BACKUPS.exists():
        print(f"\n  backups/:")
        for ts_dir in sorted(BACKUPS.iterdir(), reverse=True)[:3]:
            n = sum(1 for f in ts_dir.rglob("*") if f.is_file())
            size = sum(f.stat().st_size for f in ts_dir.rglob("*") if f.is_file())
            print(f"    {ts_dir.name}/  ({n} files, {size/1024/1024:.1f} MB)")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser(
        description="Clean migration — keep expensive, archive old chunker data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примери:
    python master_migrate.py                       # dry run
    python master_migrate.py --apply               # изпълнява
    python master_migrate.py --apply --wipe-articles  # НЕ пази 160 статии
    python master_migrate.py --apply --wipe-ocr    # НЕ пази 69 OCR pages
    python master_migrate.py --verify-only         # само проверка
        """
    )
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--wipe-articles", action="store_true",
                    help="НЕ мигрирай output/ — ще се регенерира (~$5)")
    ap.add_argument("--wipe-ocr", action="store_true",
                    help="НЕ мигрирай .ocr_cache — ще се регенерира")
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()

    if args.verify_only:
        step_verify()
        return 0

    dry_run = not args.apply

    print("╔" + "═" * 70 + "╗")
    print("║" + "  MASTER MIGRATE v2 — clean state".center(70) + "║")
    if dry_run:
        print("║" + "  DRY RUN".center(70) + "║")
    else:
        print("║" + "  APPLYING".center(70) + "║")
    print("╚" + "═" * 70 + "╝")

    if args.wipe_articles:
        print("\n  ⚠ --wipe-articles: 160 статии НЯМА да се запазят")
    if args.wipe_ocr:
        print("  ⚠ --wipe-ocr: 69 OCR pages НЯМА да се запазят")

    try:
        step_migrate(dry_run=dry_run,
                     wipe_articles=args.wipe_articles,
                     wipe_ocr=args.wipe_ocr)

        if dry_run:
            step_archive(dry_run=True)
            step_reset(dry_run=True)
            print("\n" + "═" * 72)
            print("  DRY RUN ЗАВЪРШИ")
            print("  За реален запис: python master_migrate.py --apply")
            print("═" * 72)
        else:
            ts = step_archive(dry_run=False)
            step_reset(dry_run=False)
            step_verify()
            print("\n" + "═" * 72)
            print("  ГОТОВО")
            if ts:
                print(f"  Backup: backups/{ts}/")
            print("═" * 72)
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())