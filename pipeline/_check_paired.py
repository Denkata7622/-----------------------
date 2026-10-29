import json
from pathlib import Path

c = Path('../generated/cache/classified')
if not c.exists():
    print(f'Missing: {c}')
    exit(1)

dirs = [d for d in c.iterdir() if d.is_dir()]
if not dirs:
    print('No classified folders yet')
    exit(0)

for d in sorted(dirs):
    f = d / 'all_problems.json'
    if not f.exists():
        continue
    data = json.load(open(f, encoding='utf-8'))
    probs = data['problems']
    if not probs:
        continue

    matched = sum(1 for p in probs if p.get('_paired'))
    orphans = sum(1 for p in probs if p.get('_orphan'))
    no_sol = sum(1 for p in probs if p.get('_no_solution'))
    standalone = sum(1 for p in probs if p.get('_standalone'))

    print()
    print(f'=== {d.name} ({len(probs)} entries) ===')
    print(f'  matched={matched}, orphans={orphans}, no_sol={no_sol}, standalone={standalone}')
    print()

    for p in probs:
        tags = []
        if p.get('_paired'): tags.append('MATCH')
        if p.get('_orphan'):
            t = 'ORPHAN'
            if p.get('_grade_uncertain'): t += '?gr'
            tags.append(t)
        if p.get('_no_solution'): tags.append('NO_SOL')
        if p.get('_standalone'): tags.append('STANDALONE')

        pid = p.get('point_id') or '?'
        diff = p.get('difficulty') or '?'
        num = p.get('num', '?')
        grade = p.get('grade', '?')
        stmt_preview = (p.get('statement') or '')[:50].replace(chr(10), ' ')

        tag_str = ','.join(tags) if tags else '?'
        print(f'  #{num} (g={grade}) [{tag_str:15s}] → {pid:6s} ({diff:6s}) | {stmt_preview}')
