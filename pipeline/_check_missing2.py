import re
from pathlib import Path
all_pids = re.findall(r'id\s*:\s*"([^"]+)"', Path("../data/steps.js").read_text(encoding="utf-8"))
existing = {d.name.replace("_", ".") for d in Path("../generated/articles").iterdir() if d.is_dir()}
missing = [p for p in all_pids if p not in existing]
print(f"Missing {len(missing)}: {missing}")
for pid in missing:
    p = Path(f"../generated/articles/{pid.replace('.', '_')}/deep.md")
    print(f"  {pid}: folder={p.parent.exists()}, deep.md={p.exists()}")
