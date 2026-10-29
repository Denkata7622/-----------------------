import re, json, sys
from pathlib import Path

js = Path("../data/steps.js").read_text(encoding="utf-8")

# Намери масива STEPS
marker = "const STEPS = ["
start = js.find(marker)
if start == -1:
    print("STEPS масивът не е намерен", file=sys.stderr)
    sys.exit(1)
start += len("const STEPS = ")

# Намери края на масива (балансирани скоби)
depth = 0; in_str = False; quote = None; escape = False; end = len(js)
for i in range(start, len(js)):
    c = js[i]
    if escape: escape = False; continue
    if in_str:
        if c == '\\': escape = True
        elif c == quote: in_str = False
        continue
    if c in ('"', "'", '`'): in_str = True; quote = c; continue
    if c == '[': depth += 1
    elif c == ']':
        depth -= 1
        if depth == 0: end = i; break

steps_str = js[start:end+1]

# Извлечи id / title / desc
points = []
for m in re.finditer(
    r'\{\s*id\s*:\s*"([^"]+)"[^{}]*?title\s*:\s*"((?:\\.|[^"\\])*)"[^{}]*?desc\s*:\s*"((?:\\.|[^"\\])*)"',
    steps_str, re.DOTALL,
):
    pid = m.group(1)
    title = m.group(2).replace('\\"', '"').replace("\\'", "'")
    desc = m.group(3).replace('\\"', '"').replace("\\'", "'").replace("\n", " ")
    if len(desc) > 80: desc = desc[:80] + "..."
    points.append({"id": pid, "title": title, "desc": desc})

# Запиши като текст и JSON
with open("_steps_summary.txt", "w", encoding="utf-8") as f:
    for p in points:
        f.write(f'{p["id"]:<6} | {p["title"]:<55} | {p["desc"]}\n')

with open("_steps_summary.json", "w", encoding="utf-8") as f:
    json.dump(points, f, ensure_ascii=False, indent=2)

print(f"✓ {len(points)} точки → _steps_summary.txt + _steps_summary.json")

# Групирай по главна точка
from collections import Counter
main = Counter(p["id"].split(".")[0] for p in points)
print("\nРазпределение по главни точки:")
for k in sorted(main, key=lambda x: int(x) if x.isdigit() else 999):
    print(f"  {k}.x → {main[k]} подточки")
