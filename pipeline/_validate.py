import json
from pathlib import Path

issues = []
for d in Path('..', 'generated', 'cache', 'extracted').iterdir():
    if not d.is_dir(): continue
    f = d / 'all_problems.json'
    if not f.exists(): continue
    data = json.load(open(f, encoding='utf-8'))
    pdf = data.get('pdf', '?')
    for p in data.get('problems', []):
        if p.get('num') is None:
            issues.append(f'{pdf}: num=null at page {p.get("page")}')
        if not p.get('statement') and not p.get('solution'):
            issues.append(f'{pdf}: empty at num={p.get("num")}')

print(f'Total issues: {len(issues)}')
for i in issues[:20]: print(f'  {i}')
