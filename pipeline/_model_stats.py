import json
from pathlib import Path
from collections import Counter

GEN = Path("../generated")

print("=" * 60)
print("ARTICLES — кой модел ги е генерирал")
print("=" * 60)
articles = GEN / "articles"
gen_counts = Counter()
for d in articles.iterdir():
    if not d.is_dir(): continue
    meta_file = d / "metadata.json"
    if not meta_file.exists(): continue
    try:
        m = json.loads(meta_file.read_text(encoding="utf-8"))
    except Exception:
        continue
    gen = m.get("generator_model", "?")
    gen_counts[gen] += 1

for model, count in gen_counts.most_common():
    print(f"  {model:35s} → {count} articles")

print()
print("=" * 60)
print("EXTRACTED — кой модел ги е извлякъл")
print("=" * 60)
ext = GEN / "cache" / "extracted"
ext_counts = Counter()
for d in ext.iterdir():
    if not d.is_dir(): continue
    f = d / "all_problems.json"
    if not f.exists(): continue
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    model = data.get("extraction_model", "(unknown — predi track)")
    ext_counts[model] += 1

for model, count in ext_counts.most_common():
    print(f"  {model:35s} → {count} PDFs")

print()
print("=" * 60)
print("CLASSIFIED — кой модел ги е класифицирал")
print("=" * 60)
cls = GEN / "cache" / "classified"
cls_counts = Counter()
for d in cls.iterdir():
    if not d.is_dir(): continue
    f = d / "all_problems.json"
    if not f.exists(): continue
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    model = data.get("classify_model", "(unknown — predi track)")
    cls_counts[model] += 1

for model, count in cls_counts.most_common():
    print(f"  {model:35s} → {count} olympiads")
