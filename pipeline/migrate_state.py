import json
import re
from pathlib import Path

BASE = Path(__file__).parent.resolve()
STATE_FILE = BASE / "state.json"
ARTICLES_DIR = BASE.parent / "generated" / "articles"

if not STATE_FILE.exists():
    print("Няма state.json")
    raise SystemExit(1)

data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
processed = data.get("processed", {})

updated = 0
skipped = 0

for folder in sorted(ARTICLES_DIR.iterdir()):
    if not folder.is_dir():
        continue

    meta_file = folder / "metadata.json"
    verify_file = folder / "verify.md"

    if not meta_file.exists():
        skipped += 1
        continue

    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ✗ {folder.name}: {e}")
        skipped += 1
        continue

    pid = meta.get("point_id")
    if not pid or pid not in processed:
        skipped += 1
        continue

    entry = processed[pid]

    # Only enrich if missing score
    if entry.get("score") is not None:
        continue

    # Extract score from verify.md (fallback to verify-vN.json)
    score = None
    verdict = None
    math_err_count = 0
    issues_count = 0

    if verify_file.exists():
        vtext = verify_file.read_text(encoding="utf-8")
        m = re.search(r"Score:\s*(\d+)", vtext)
        if m:
            score = int(m.group(1))
        m = re.search(r"Verdict:\s*(\w+)", vtext)
        if m:
            verdict = m.group(1)
        # Count math errors (lines starting with "- `")
        math_err_count = len(re.findall(r"^- `", vtext, re.MULTILINE))
        # Count issues (lines starting with "- [")
        issues_count = len(re.findall(r"^- \[", vtext, re.MULTILINE))

    entry["score"] = score
    entry["verdict"] = verdict
    entry["word_count"] = meta.get("word_count")
    entry["generator_model"] = meta.get("generator_model")
    entry["verifier_model"] = meta.get("verifier_model")
    entry["math_errors"] = math_err_count
    entry["issues"] = issues_count
    # Attempts not available in metadata; leave as-is

    updated += 1
    print(f"  ✓ {pid}: score={score}, verdict={verdict}, wc={meta.get('word_count')}")

STATE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print()
print(f"Обновени: {updated}, пропуснати: {skipped}")
