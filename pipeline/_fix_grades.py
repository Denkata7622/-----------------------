import json, re
from pathlib import Path

fixed = 0
for d in Path('..', 'generated', 'cache', 'extracted').iterdir():
    if not d.is_dir(): continue
    f = d / 'all_problems.json'
    if not f.exists(): continue
    data = json.load(open(f, encoding='utf-8'))
    pdf = data.get('pdf', '')
    
    # Extract grade from filename (e.g., "2011-10 кл" -> 10, "2011-9-12 кл" -> range)
    m = re.search(r'-(\d{1,2})-(\d{1,2})\s*кл', pdf)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        for p in data.get('problems', []):
            p['grade'] = None
            p['grade_range'] = [lo, hi]
        changed = True
    else:
        m = re.search(r'-(\d{1,2})\s*кл', pdf)
        if not m: continue
        grade = int(m.group(1))
        changed = False
        for p in data.get('problems', []):
            if p.get('grade') != grade:
                p['grade'] = grade
                p['grade_range'] = None
                changed = True
    if changed:
        json.dump(data, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        fixed += 1

print(f'Fixed grades in {fixed} files')
