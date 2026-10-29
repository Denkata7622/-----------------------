import json
d = json.load(open('..\\generated\\cache\\extracted\\OLI-2-Областен кръг-2004-11 кл-probs\\all_problems.json', encoding='utf-8'))
print(f'Total: {len(d["problems"])}')
for p in d['problems']:
    stmt = (p.get('statement') or '')[:60]
    sol = (p.get('solution') or '')[:20] or '(null)'
    print(f'  #{p["num"]}: stmt={stmt!r}... sol={sol!r}')
