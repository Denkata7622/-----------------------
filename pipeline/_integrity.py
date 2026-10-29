import json
from pathlib import Path

print("=" * 60)
print("  INTEGRITY CHECK")
print("=" * 60)

# 1. config.json валиден ли е
try:
    cfg = json.load(open('config.json', encoding='utf-8'))
    print(f"\n✓ config.json: valid JSON, {len(cfg)} keys")
    for k in ['generator', 'verifier', 'verifier_2', 'arbiter', 'escalation', 'chunker', 'ocr']:
        if k in cfg and 'model' in cfg[k]:
            print(f"    {k:12s}: {cfg[k]['model']}")
    if 'chunker' in cfg and 'classify_model' in cfg['chunker']:
        print(f"    chunker.classify_model: {cfg['chunker']['classify_model']}")
except Exception as e:
    print(f"\n✗ config.json: BROKEN — {e}")

# 2. state файл валиден ли е
try:
    st = json.load(open('../generated/state/chunker_state.json', encoding='utf-8'))
    print(f"\n✓ chunker_state.json: valid")
    print(f"    extracted entries: {len(st.get('extracted', {}))}")
    done = sum(1 for v in st.get('extracted', {}).values() if v.get('status') == 'done')
    partial = sum(1 for v in st.get('extracted', {}).values() if v.get('status') == 'partial')
    print(f"    done: {done}, partial: {partial}")
    print(f"    budget: ${st['budget']['spent_usd']:.2f} ({st['budget']['date']})")
except Exception as e:
    print(f"\n✗ chunker_state.json: BROKEN — {e}")

# 3. Всички extracted файлове валидни ли са
ext = Path('../generated/cache/extracted')
broken_files = []
total_files = 0
total_probs = 0
for d in ext.iterdir():
    if not d.is_dir(): continue
    f = d / 'all_problems.json'
    if not f.exists(): continue
    total_files += 1
    try:
        data = json.load(open(f, encoding='utf-8'))
        total_probs += len(data.get('problems', []))
    except Exception as e:
        broken_files.append(f"{d.name}: {e}")

if broken_files:
    print(f"\n✗ BROKEN JSON files: {len(broken_files)}")
    for b in broken_files[:10]:
        print(f"    {b}")
else:
    print(f"\n✓ extracted/: {total_files} files, {total_probs} problems, all valid JSON")

# 4. State vs disk consistency
state = json.load(open('../generated/state/chunker_state.json', encoding='utf-8'))
state_keys = set(state.get('extracted', {}).keys())
disk_keys = set(d.name for d in ext.iterdir() if d.is_dir())
orphan_state = state_keys - disk_keys
orphan_disk = disk_keys - state_keys
print(f"\n{'✓' if not orphan_state else '⚠'} State entries without disk files: {len(orphan_state)}")
if orphan_state:
    for k in list(orphan_state)[:5]: print(f"    {k}")
print(f"{'✓' if not orphan_disk else '⚠'} Disk files without state entries: {len(orphan_disk)}")
if orphan_disk:
    for k in list(orphan_disk)[:5]: print(f"    {k}")

# 5. Backup folder съществува ли
backup = Path('../generated/cache/extracted_sol_backup')
if backup.exists():
    n = len(list(backup.iterdir()))
    print(f"\n✓ Sol backup: {n} folders intact")
else:
    print(f"\n⚠ Sol backup folder missing")

# 6. Остатъчни gpt-oss артефакти
print(f"\n{'=' * 60}")
print("  CONFIG SANITY")
print("=" * 60)
gen_model = cfg.get('generator', {}).get('model', '?')
if 'gpt-oss' in gen_model:
    print(f"⚠ generator.model = {gen_model}")
    print(f"  → Следващ --extract ще ползва gpt-oss (провален за extract)")
    print(f"  → Смени на openai/gpt-6.1-sol ако ще правиш extract")
else:
    print(f"✓ generator.model = {gen_model} (OK за extract)")
