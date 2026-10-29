import re, shutil
from pathlib import Path

p = Path('pdf_chunker.py')
shutil.copy2(p, p.with_suffix('.py.bak'))
src = p.read_text(encoding='utf-8')
original_len = len(src)

# ─── Fix 1: Reindent run_classify_paired body ───
# Find the def line
DEF_LINE = '    def run_classify_paired(self, limit=None, filter_fn=None):'
def_pos = src.find(DEF_LINE)
if def_pos == -1:
    print("❌ Cannot find run_classify_paired def")
    exit(1)

# Find next line after the def
body_start = src.find('\n', def_pos) + 1

# The body ends where the next method starts (print_stats or CLI section)
# Look for the marker `# STATS` comment or `def print_stats` at class level
END_MARKER = '    # ═══════════════════════════════════════════════════════════\n    # STATS'
end_pos = src.find(END_MARKER, body_start)
if end_pos == -1:
    # Fallback: look for 'def print_stats(self):'
    end_pos = src.find('    def print_stats(self):', body_start)
    if end_pos == -1:
        print("❌ Cannot find end of run_classify_paired")
        exit(1)

body = src[body_start:end_pos]

# Check if body is already indented (first non-empty line starts with 8 spaces)
first_line = next((l for l in body.split('\n') if l.strip()), '')
already_indented = first_line.startswith('        ')
print(f"Body first line: {first_line[:60]!r}")
print(f"Already indented (8 spaces): {already_indented}")

if not already_indented:
    # Reindent: +4 spaces to every non-empty line
    new_body = '\n'.join(
        ('    ' + line if line.strip() else line)
        for line in body.split('\n')
    )
    src = src[:body_start] + new_body + src[end_pos:]
    print(f"✓ Reindented body: {len(body)} → {len(new_body)} chars")
else:
    print("ℹ Body already indented, skipping")

# ─── Fix 2: Add CLI flag + dispatch ───
# Add argparse argument
ARG_ANCHOR = 'ap.add_argument("--classify", action="store_true", help="Класифицирай")'
if '--classify-paired' not in src:
    if ARG_ANCHOR in src:
        src = src.replace(
            ARG_ANCHOR,
            ARG_ANCHOR + '\n    ap.add_argument("--classify-paired", action="store_true",\n'
                        '                    help="Paired classify: probs+sol в 1 AI call (11 кл областен first)")',
            1,
        )
        print("✓ Added argparse flag --classify-paired")
    else:
        print("⚠ Cannot find argparse anchor for --classify")

# Add dispatch logic
DISPATCH_ANCHOR = '''    if args.classify or args.all:
        chunker.run_classify(limit=args.limit)'''
if 'run_classify_paired(limit=args.limit)' not in src:
    if DISPATCH_ANCHOR in src:
        src = src.replace(
            DISPATCH_ANCHOR,
            '''    if args.classify_paired:
        chunker.run_classify_paired(limit=args.limit, pdf_pattern=args.pdf)
    elif args.classify or args.all:
        chunker.run_classify(limit=args.limit)''',
            1,
        )
        print("✓ Added dispatch logic for --classify-paired")
    else:
        print("⚠ Cannot find dispatch anchor")

p.write_text(src, encoding='utf-8')
print(f"\n✓ File: {original_len} → {len(src)} chars")
print(f"✓ Backup: {p.with_suffix('.py.bak').name}")
