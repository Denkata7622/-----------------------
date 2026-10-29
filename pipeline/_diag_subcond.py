import json

for pdf in ['OLI-2-Областен кръг-2009-10 кл-probs', 'OLI-2-Областен кръг-2009-10 кл-sol',
            'OLI-2-Областен кръг-2011-10 кл-probs', 'OLI-2-Областен кръг-2011-10 кл-sol']:
    path = f'..\\generated\\cache\\extracted\\{pdf}\\all_problems.json'
    try:
        d = json.load(open(path, encoding='utf-8'))
    except FileNotFoundError:
        print(f'{pdf}: NOT EXTRACTED YET\n')
        continue
    print(f'=== {pdf} ({len(d["problems"])} problems) ===')
    for p in d['problems']:
        num = p.get('num')
        grade = p.get('grade')
        stmt = (p.get('statement') or '')[:60].replace('\n', ' ')
        sol = (p.get('solution') or '')[:40].replace('\n', ' ')
        print(f'  num={num} grade={grade} | stmt: {stmt!r}')
        if sol: print(f'                       | sol:  {sol!r}')
    print()
