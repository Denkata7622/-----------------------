#!/usr/bin/env python3
"""
fix_multiline_explanations.py
=============================

Fixes `explanation:"..."` fields in HTML files that contain REAL newlines
(which cause `SyntaxError: Invalid or unexpected token` in JS parsers)
by converting them to template literals: `explanation:`...``

The script is idempotent — running it multiple times on the same file is safe.

Usage
-----
    python fix_multiline_explanations.py index.html
    python fix_multiline_explanations.py --dry-run index.html
    python fix_multiline_explanations.py --no-backup index.html

Exit codes
----------
    0  success
    1  some errors remain (manual fix needed)
    2  file error
"""

import sys
import re
import shutil
from pathlib import Path


# ─── Match: explanation:<ws>"<content>" ──────────────────────────
# Content: sequence of (escape sequence | non-quote non-backslash char).
# `[^"\\]` INCLUDES newlines, so multi-line strings are matched correctly.
# The pattern stops at the first UNESCAPED `"`.
EXPLANATION_RE = re.compile(
    r'(explanation\s*:\s*)"((?:\\.|[^"\\])*)"',
    re.DOTALL,
)

# ─── Extract inline JS blocks from HTML ─────────────────────────
SCRIPT_RE = re.compile(
    r'<script\b[^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)


# ═════════════════════════════════════════════════════════════════
#  Helpers
# ═════════════════════════════════════════════════════════════════

def read_file(path: Path) -> str:
    """Read text preserving original line endings."""
    with open(path, 'r', encoding='utf-8', newline='') as f:
        return f.read()


def write_file(path: Path, content: str) -> None:
    """Write text preserving line endings (no translation)."""
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(content)


def extract_js(html: str) -> str:
    """Concatenate all inline <script>...</script> blocks."""
    return '\n'.join(m.group(1) for m in SCRIPT_RE.finditer(html))


def escape_for_template(content: str) -> str:
    """
    Escape ONLY the chars that would break a template literal:
        `   ->  \\`
        ${  ->  \\${
    All other escape sequences (\\", \\\\, \\n, \\t, \\uXXXX, ...) pass through unchanged.
    """
    out = []
    i, n = 0, len(content)
    while i < n:
        c = content[i]
        if c == '\\' and i + 1 < n:
            # preserve existing escape pair (e.g. \" or \\n) as-is
            out.append(c)
            out.append(content[i + 1])
            i += 2
        elif c == '`':
            out.append('\\`')
            i += 1
        elif c == '$' and i + 1 < n and content[i + 1] == '{':
            out.append('\\$')
            i += 1
        else:
            out.append(c)
            i += 1
    return ''.join(out)


# ═════════════════════════════════════════════════════════════════
#  Lexical scanner: find unterminated multi-line `"..."` strings
# ═════════════════════════════════════════════════════════════════

def find_multiline_string_errors(js: str) -> list[tuple[int, str]]:
    """
    Lexical scan. Correctly counts EVERY `"..."` string that contains
    a raw newline, even if multiple occur in the same code block.
    """
    errors = []
    i, n = 0, len(js)
    state = 'code'
    line = 1
    sline = 1
    snippet = ''
    skip_until_closing_quote = False   # ← нов флаг

    while i < n:
        c = js[i]
        nxt = js[i + 1] if i + 1 < n else ''

        # Когато сме в "broken" режим — търсим затварящата ", игнорирайки всичко друго
        if skip_until_closing_quote:
            if c == '\\':
                i += 2
                if i > 0 and js[i-1] == '\n': line += 1
                continue
            if c == '"':
                skip_until_closing_quote = False
            if c == '\n': line += 1
            i += 1
            continue

        if state == 'code':
            if c == '/' and nxt == '/':
                state = 'lc'; i += 2; continue
            if c == '/' and nxt == '*':
                state = 'bc'; i += 2; continue
            if c == '"':
                state = 'dq'; sline = line
                snippet = js[i + 1:i + 61].split('\n', 1)[0]
                i += 1; continue
            if c == "'":
                state = 'sq'; i += 1; continue
            if c == '`':
                state = 'tpl'; i += 1; continue

        elif state == 'lc':
            if c == '\n': state = 'code'

        elif state == 'bc':
            if c == '*' and nxt == '/':
                state = 'code'; i += 2; continue

        elif state == 'dq':
            if c == '\\':
                i += 2; continue
            if c == '\n':
                errors.append((sline, snippet))
                # НЕ ресетваме на code — влизаме в "skip" режим,
                # който търси истинската затваряща "
                skip_until_closing_quote = True
                state = 'code'
            elif c == '"':
                state = 'code'

        elif state == 'sq':
            if c == '\\':
                i += 2; continue
            if c == '\n': state = 'code'
            elif c == "'": state = 'code'

        elif state == 'tpl':
            if c == '\\':
                i += 2; continue
            if c == '`':
                state = 'code'

        if c == '\n': line += 1
        i += 1

    return errors

# ═════════════════════════════════════════════════════════════════
#  Fixer
# ═════════════════════════════════════════════════════════════════

def fix_html(src: str, dry_run: bool) -> tuple[str, list[tuple[int, str]], int]:
    """
    Returns (new_src, list_of_fixed_fields, count_of_skipped_single_line_fields).
    fixed_fields: list of (line_number, first_line_snippet)
    """
    fixed: list[tuple[int, str]] = []
    skipped = 0

    def repl(m: re.Match) -> str:
        nonlocal skipped
        prefix = m.group(1)      # e.g.  'explanation:'  or  'explanation : '
        content = m.group(2)     # raw content (may contain real newlines)

        if '\n' not in content and '\r' not in content:
            skipped += 1
            return m.group(0)    # leave single-line strings untouched

        line = src.count('\n', 0, m.start()) + 1
        first = content.split('\n', 1)[0][:60]
        fixed.append((line, first))
        return f'{prefix}`{escape_for_template(content)}`'

    new_src = EXPLANATION_RE.sub(repl, src)
    return new_src, fixed, skipped


# ═════════════════════════════════════════════════════════════════
#  CLI
# ═════════════════════════════════════════════════════════════════

def process_file(fname: str, backup: bool, dry_run: bool) -> tuple[int, bool]:
    """
    Returns (fields_fixed, ok) — ok=False means errors remain.
    """
    path = Path(fname)
    if not path.exists():
        print(f'❌ {fname}: file not found')
        return 0, False

    print(f'\n📄 {fname}')
    src = read_file(path)

    # ── PRE-CHECK ──────────────────────────────────────────────
    js = extract_js(src)
    before = find_multiline_string_errors(js)
    if not before:
        print('   ✓ No multi-line string errors — nothing to fix.')
        return 0, True

    print(f'   🔍 Found {len(before)} broken field(s):')
    for ln, snip in before[:10]:
        print(f'      • line {ln}: {snip!r}...')
    if len(before) > 10:
        print(f'      … and {len(before) - 10} more')

    # ── FIX ────────────────────────────────────────────────────
    new_src, fixed, skipped = fix_html(src, dry_run=dry_run)

    if dry_run:
        print(f'\n   🔍 DRY RUN — would convert {len(fixed)} field(s).')
        print(f'   ·  Skipped {skipped} single-line string(s).')
        return len(fixed), True

    if new_src == src:
        print('   ⚠️  No changes made (should not happen).')
        return 0, True

    if backup:
        bak = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, bak)
        print(f'\n   📦 Backup: {bak.name}')

    write_file(path, new_src)

    print(f'\n   ✎ Converted {len(fixed)} field(s) to template literals:')
    for ln, snip in fixed:
        print(f'      • line {ln}: {snip!r}…')
    print(f'   ·  Skipped {skipped} single-line string(s).')

    # ── POST-CHECK ─────────────────────────────────────────────
    src2 = read_file(path)
    after = find_multiline_string_errors(extract_js(src2))
    if after:
        print(f'   ⚠️  Still {len(after)} broken field(s) remain — manual check needed.')
        for ln, snip in after[:5]:
            print(f'      • line {ln}: {snip!r}…')
        return len(fixed), False

    print(f'   ✅ Fix verified — no unterminated strings remain.')
    return len(fixed), True


def main() -> int:
    args = sys.argv[1:]
    dry_run   = '--dry-run'   in args
    no_backup = '--no-backup' in args
    files = [a for a in args if not a.startswith('--')]

    if not files:
        print(__doc__)
        return 1

    total_fixed = 0
    all_ok = True

    for fname in files:
        try:
            fixed, ok = process_file(fname, backup=not no_backup, dry_run=dry_run)
            total_fixed += fixed
            all_ok = all_ok and ok
        except Exception as e:
            print(f'   ❌ Error processing {fname}: {e}')
            all_ok = False

    print('\n' + '─' * 62)
    if total_fixed:
        print(f'📊 Total: {total_fixed} field(s) fixed')
    else:
        print('📊 Nothing to fix.')
    if not dry_run and total_fixed and not no_backup:
        print('💾 Backups saved with .bak extension')
    print('─' * 62)

    if not all_ok:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())