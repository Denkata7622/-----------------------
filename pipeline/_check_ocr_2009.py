import json
p = '..\\generated\\cache\\ocr\\OLI-2-Областен кръг-2009-10 кл-sol__v2.json'
d = json.load(open(p, encoding='utf-8'))
for pg in d:
    print(f'=== page {pg["page"]} ({len(pg["text"])} chars) ===')
    print(pg['text'][:600])
    print()
