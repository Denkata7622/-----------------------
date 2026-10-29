#!/usr/bin/env python3
"""
extract_data.py — изнася STEPS, PLAN_PHASES, TASKS_DATA от index.html
в отделни файлове в data/.

Употреба:
    cd pipeline
    python extract_data.py --dry-run    # проверка БЕЗ запис
    python extract_data.py              # реален запис

Rollback:
    cp ../index.html.bak-* ../index.html
"""
import shutil, time, argparse, re
from pathlib import Path


CONSTS = ['STEPS', 'PLAN_PHASES', 'TASKS_DATA']


def find_declaration(html: str, name: str):
    """
    Намира 'const NAME = ' в началото на ред (не в коментар/string).
    Returns (start, end, open_char, close_char) или None.
    """
    # ^ (MULTILINE) гарантира че не е в коментар '// const NAME = '
    pattern = re.compile(rf'^const\s+{re.escape(name)}\s*=\s*', re.MULTILINE)
    match = pattern.search(html)
    if not match:
        return None
    
    start = match.start()
    first_bracket_pos = match.end()
    
    # Открий [ или { веднага след '='
    if first_bracket_pos >= len(html):
        return None
    open_char = html[first_bracket_pos]
    if open_char == '[':
        close_char = ']'
    elif open_char == '{':
        close_char = '}'
    else:
        return None
    
    # Bracket matching с tracking на strings
    depth = 0
    in_str = False
    quote = None
    escape = False
    
    for i in range(first_bracket_pos, len(html)):
        c = html[i]
        if escape:
            escape = False
            continue
        if in_str:
            if c == '\\':
                escape = True
            elif c == quote:
                in_str = False
            continue
        if c in ('"', "'", '`'):
            in_str = True
            quote = c
            continue
        if c == open_char:
            depth += 1
        elif c == close_char:
            depth -= 1
            if depth == 0:
                # Включи ';' ако има
                end = i + 1
                while end < len(html) and html[end] in ' \t\r':
                    end += 1
                if end < len(html) and html[end] == '\n':
                    end += 1
                elif end < len(html) and html[end] == ';':
                    end += 1
                return (start, end, open_char, close_char)
    
    return None  # не е намерен затварящ bracket


def verify_balanced(content: str, open_char: str, close_char: str) -> bool:
    """Проверява че bracket-ите в извлечения content са балансирани."""
    depth = 0
    in_str = False
    quote = None
    escape = False
    for c in content:
        if escape:
            escape = False
            continue
        if in_str:
            if c == '\\':
                escape = True
            elif c == quote:
                in_str = False
            continue
        if c in ('"', "'", '`'):
            in_str = True
            quote = c
            continue
        if c == open_char:
            depth += 1
        elif c == close_char:
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--html', default='../index.html')
    ap.add_argument('--dry-run', action='store_true',
                    help='Покажи какво ще се промени, БЕЗ да записва')
    args = ap.parse_args()
    
    html_path = Path(args.html).resolve()
    if not html_path.exists():
        print(f'✗ Липсва: {html_path}')
        return 1
    
    html = html_path.read_text(encoding='utf-8')
    original_size = len(html.encode('utf-8'))
    original_lines = html.count('\n') + 1
    
    print(f'Файл: {html_path}')
    print(f'  {original_lines:,} реда, {original_size:,} B')
    print()
    
    # ═══ СТЪПКА 1: Извлечи всичко в паметта (БЕЗ запис) ═══
    print('═══ Извличане ═══')
    extracted = []  # [(name, content, start, end, open, close), ...]
    new_html = html
    
    for name in CONSTS:
        result = find_declaration(new_html, name)
        if result is None:
            print(f'  ⚠ {name:15s}  не е намерен (или не е балансиран)')
            continue
        
        start, end, open_char, close_char = result
        content = new_html[start:end]
        
        # Verify balance
        if not verify_balanced(content, open_char, close_char):
            print(f'  ✗ {name:15s}  НЕ Е БАЛАНСИРАН — пропускам')
            continue
        
        # Replace with comment
        comment = f'// [{name} is in data/{name.lower()}.js]\n'
        new_html = new_html[:start] + comment + new_html[end:]
        
        lines = content.count('\n') + 1
        size = len(content.encode('utf-8'))
        print(f'  ✓ {name:15s}  {lines:>6,} реда, {size:>9,} B')
        extracted.append((name, content, open_char, close_char))
    
    if not extracted:
        print()
        print('✗ Нищо не е извлечено. Файлът НЕ е променен.')
        return 1
    
    # ═══ СТЪПКА 2: Провери insertion point ═══
    print()
    print('═══ Проверка на insertion point ═══')
    
    if '</head>' in new_html:
        insertion_marker = '</head>'
        insertion_type = '</head>'
    elif '<body' in new_html:
        # Намери края на <body...>
        body_start = new_html.find('<body')
        body_end = new_html.find('>', body_start)
        if body_end == -1:
            print('✗ Не мога да намеря края на <body> тага. Aborting.')
            return 1
        insertion_marker = new_html[body_start:body_end + 1]
        insertion_type = '<body>'
    else:
        print('✗ Не мога да намеря нито </head> нито <body>. Aborting.')
        return 1
    
    print(f'  ✓ Намерен: {insertion_type}')
    
    # Провери дали вече има data/ script tags
    existing = [name for name, _, _, _ in extracted
                if f'<script src="data/{name.lower()}.js"' in html]
    
    if existing:
        print(f'  ⚠ Вече заредени: {existing} — ще ги пропусна')
        extracted = [e for e in extracted if e[0] not in existing]
    
    if not extracted:
        print()
        print('✓ Всичко вече е изнесено. Няма промени.')
        return 0
    
    # ═══ СТЪПКА 3: Dry run? ═══
    if args.dry_run:
        print()
        print('═══ DRY RUN — НИЩО НЕ Е ЗАПИСАНО ═══')
        print(f'  Ще създам: data/' + ', data/'.join(f'{n.lower()}.js' for n, _, _, _ in extracted))
        print(f'  Ще вмъкна {len(extracted)} <script> тага преди {insertion_type}')
        return 0
    
    # ═══ СТЪПКА 4: Backup ═══
    backup_name = f'{html_path.name}.bak-{int(time.time())}'
    backup = html_path.parent / backup_name
    shutil.copy2(html_path, backup)
    print()
    print(f'✓ Backup: {backup_name}')
    
    # ═══ СТЪПКА 5: Запиши data файлове ═══
    data_dir = html_path.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    for name, content, _, _ in extracted:
        path = data_dir / f'{name.lower()}.js'
        path.write_text(content, encoding='utf-8')
        print(f'✓ data/{name.lower()}.js')
    
    # ═══ СТЪПКА 6: Вмъкни script тагове ═══
    script_tags = ''.join(
        f'<script src="data/{name.lower()}.js"></script>\n'
        for name, _, _, _ in extracted
    )
    
    if insertion_marker == '</head>':
        new_html = new_html.replace('</head>', f'{script_tags}</head>', 1)
    else:  # <body ...>
        new_html = new_html.replace(insertion_marker, f'{insertion_marker}\n{script_tags}', 1)
    
    # ═══ СТЪПКА 7: Запиши HTML ═══
    html_path.write_text(new_html, encoding='utf-8')
    
    # ═══ СТЪПКА 8: Verify ═══
    final = html_path.read_text(encoding='utf-8')
    issues = []
    
    for name, _, _, _ in extracted:
        if re.search(rf'^const\s+{re.escape(name)}\s*=', final, re.MULTILINE):
            issues.append(f'{name} все още в index.html')
        if not (data_dir / f'{name.lower()}.js').exists():
            issues.append(f'data/{name.lower()}.js липсва')
        if f'data/{name.lower()}.js' not in final:
            issues.append(f'<script src> за {name} липсва')
    
    new_size = len(new_html.encode('utf-8'))
    new_lines = new_html.count('\n') + 1
    
    print()
    print('═' * 65)
    print(f'  index.html:  {original_lines:>6,} реда → {new_lines:>6,} реда')
    print(f'  Size:        {original_size:>9,} B → {new_size:>9,} B')
    print(f'  Спестени:    {original_size - new_size:,} B ({(1-new_size/original_size)*100:.1f}%)')
    print('═' * 65)
    
    if issues:
        print()
        print('✗ ПРОБЛЕМИ:')
        for i in issues:
            print(f'  - {i}')
        print()
        print(f'ROLLBACK: cp {backup_name} index.html')
        return 1
    
    print()
    print('✓ Готово. Провери сайта:')
    print('  1. Отвори index.html в браузър')
    print('  2. Ctrl+Shift+R (hard reload, за да не ползва cache)')
    print('  3. Кликни на 1.4 — трябва да отвори Modal с теория')
    print('  4. Tab PLAN — 5 фази')
    print('  5. Tab TASKS — 4 карти')
    print('  6. F12 → Console → 0 errors')
    print()
    print('АКО НЕЩО СЕ СЧУПИ:')
    print(f'  cp {backup_name} index.html')
    print()
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())