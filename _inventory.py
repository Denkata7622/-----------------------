import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

BASE = Path("..")
GEN = BASE / "generated"

print("═" * 70)
print("  КАКВО ИМА В GENERATED/")
print("═" * 70)

# ── Articles ──
articles = GEN / "articles"
if articles.exists():
    dirs = [d for d in articles.iterdir() if d.is_dir()]
    with_deep = sum(1 for d in dirs if (d / "deep.md").exists())
    print(f"\n📄 ARTICLES: {len(dirs)} folders, {with_deep} with deep.md")
    
    # Fresh vs old
    now = datetime.now().timestamp()
    fresh_24h = sum(1 for d in dirs if (d / "deep.md").exists() and now - (d / "deep.md").stat().st_mtime < 86400)
    print(f"   Generated last 24h: {fresh_24h}")
    
    # By section
    sections = Counter()
    for d in dirs:
        pid = d.name.replace("_", ".")
        if pid.startswith("R."):
            sections["R"] += 1
        else:
            sections[pid.split(".")[0]] += 1
    print(f"   By section: {dict(sections)}")

# ── Anchors ──
anchors = GEN / "anchors"
if anchors.exists():
    files = list(anchors.glob("*.json"))
    total_problems = 0
    for f in files:
        if f.name == "_unclassified.json": continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            total_problems += data.get("total", 0)
        except: pass
    print(f"\n🎯 ANCHORS: {len(files)} files, {total_problems} problems total")

# ── Classified ──
classified = GEN / "cache" / "classified"
if classified.exists():
    dirs = [d for d in classified.iterdir() if d.is_dir()]
    print(f"\n📊 CLASSIFIED: {len(dirs)} olympiads")

# ── Extracted ──
extracted = GEN / "cache" / "extracted"
if extracted.exists():
    dirs = [d for d in extracted.iterdir() if d.is_dir()]
    total_probs = 0
    for d in dirs:
        f = d / "all_problems.json"
        if f.exists():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                total_probs += len(data.get("problems", []))
            except: pass
    print(f"\n📚 EXTRACTED: {len(dirs)} PDFs, {total_probs} problems")

# ── State budget ──
state_files = [
    BASE / "pipeline" / "state.json",
    BASE / "state" / "chunker_state.json",
]
print(f"\n💰 BUDGET:")
for sf in state_files:
    if sf.exists():
        try:
            data = json.loads(sf.read_text(encoding="utf-8"))
            budget = data.get("budget", {})
            print(f"   {sf.name}: {budget.get('date', '?')} — ${budget.get('spent_usd', 0):.4f}")

print("\n" + "═" * 70)
