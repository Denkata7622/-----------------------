import json
p = 'generated/cache/ocr/OLI-2-Областен кръг-1995-10 кл-sol__v2.json'
d = json.load(open(p, encoding='utf-8'))
print('pages:', len(d))
print()
for pg in d:
    txt = pg['text']
    print(f'=== стр.{pg["page"]} ({len(txt)} chars) ===')
    print(txt[:800])
    print()
