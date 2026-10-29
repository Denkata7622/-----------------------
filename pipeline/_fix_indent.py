import shutil
from pathlib import Path

p = Path('pdf_chunker.py')
shutil.copy2(p, p.with_suffix('.py.bak'))
src = p.read_text(encoding='utf-8')

START = 'def _format_problems_list(self, problems, prefix):'
END = 'def run_classify_paired(self, limit=None, filter_fn=None):'

start_pos = src.find(START)
if start_pos == -1:
    print(f"❌ START not found: {START!r}")
    exit(1)

end_pos = src.find(END, start_pos)
if end_pos == -1:
    print(f"❌ END not found: {END!r}")
    exit(1)

end_of_def = src.find('\n', end_pos) + 1
broken = src[start_pos:end_of_def]

# Reindent: +4 spaces to every non-empty line
reindented = '\n'.join(
    ('    ' + line if line.strip() else line)
    for line in broken.split('\n')
)

body = '''        """Classify probs+sol together in one AI call per olympiad."""
        grouped = self._group_extracted_by_base()
        bases = [b for b in grouped.keys() if grouped[b].get('probs') or grouped[b].get('sols')]
        if filter_fn:
            bases = [b for b in bases if filter_fn(b)]
        bases.sort(key=self._priority_key_paired)
        if limit:
            bases = bases[:limit]

        log.info(f"Classify-paired: {len(bases)} olympiads")

        for i, base in enumerate(bases, 1):
            if self.state.budget_exceeded():
                log.warning(f"Budget exhausted at {i}/{len(bases)}")
                break

            group = grouped[base]
            probs = group.get('probs', [])
            sols = group.get('sols', [])
            log.info(f"[{i}/{len(bases)}] {base}: {len(probs)}p, {len(sols)}s")

            if group.get('standalone') and not sols:
                entries = [{**p, 'point_id': None, 'point_confidence': 'pending',
                            'difficulty': None, 'techniques': [], '_standalone': True}
                           for p in probs]
            elif not probs or not sols:
                only = probs or sols
                entries = []
                for p in only:
                    cls = self.classify_problem(p)
                    entries.append({**p, **cls} if cls else {**p, 'point_id': None, 'point_confidence': 'failed'})
                    if self.state.budget_exceeded():
                        break
            else:
                result = self._classify_paired(base, probs, sols)
                if not result:
                    log.error(f"  paired classify failed")
                    continue
                entries = self._build_paired_entries(base, probs, sols, result)

            out_dir = CLASSIFIED_DIR / safe_name(base)
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / 'all_problems.json').write_text(
                json.dumps({'pdf': base, 'problems': entries}, ensure_ascii=False, indent=2),
                encoding='utf-8')

            matched = sum(1 for e in entries if e.get('_paired'))
            orphans = sum(1 for e in entries if e.get('_orphan'))
            log.info(f"  ✓ total={len(entries)} (matched={matched}, orphans={orphans})")
'''

# Check if body already exists
after_def = src[end_of_def:end_of_def + 500]
if 'grouped = self._group_extracted_by_base' in after_def:
    new_block = reindented
    print("ℹ Body exists — only reindenting")
else:
    new_block = reindented + body
    print("ℹ Body missing — adding it")

new_src = src[:start_pos] + new_block + src[end_of_def:]
p.write_text(new_src, encoding='utf-8')
print(f"✓ Fixed: {len(src)} → {len(new_src)} chars")
print(f"✓ Backup: {p.with_suffix('.py.bak')}")
