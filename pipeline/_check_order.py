import json
from pathlib import Path

# 1. Какъв е редът в steps.js?
print("═══ Ред в steps.js (първите 20) ═══")
steps_file = Path("../data/steps.js")
content = steps_file.read_text(encoding="utf-8")
import re
ids = re.findall(r'id\s*:\s*"([^"]+)"', content)
for pid in ids[:20]:
    print(f"  {pid}")
print(f"  ... общо {len(ids)} точки")

# 2. Какъв е редът в anchors/ (filesystem)?
print("\n═══ Ред в anchors/ (filesystem) ═══")
anchor_files = list(Path("../generated/anchors").glob("*.json"))
for f in anchor_files[:20]:
    print(f"  {f.name}")
print(f"  ... общо {len(anchor_files)} файла")
