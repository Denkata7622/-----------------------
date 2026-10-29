import json
p = '..\\generated\\state\\chunker_state.json'
s = json.load(open(p, encoding='utf-8'))
s['budget']['spent_usd'] = 1.48
json.dump(s, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"Reset: ${s['budget']['spent_usd']:.2f} / $3.00")
