#!/usr/bin/env python3
"""
extract_css.py v2 — изнася <style> блокове от index.html в style.css.

Промени в v2:
- Намира ИСТИНСКИЯ </head> (между <head> и <body>), не първия срещнат
- Не извлича <style> блокове, които са в <script> или <!-- --> (защита от JS стрингове)
- Verify: <link> е преди </head>, </head> е преди <body>
- Warns при 2+ </head> тага

Употреба:
    cd pipeline
    python extract_css.py --dry-run    # проверка БЕЗ запис
    python extract_css.py              # реален запис

Rollback:
    cp ../index.html.bak-* ../index.html
"""
import shutil, time, argparse, re
from pathlib import Path


def find_style_blocks(html):
    """Намира всички <style>...</style> блокове."""
    blocks = []
    pos = 0
    while True:
        start_match = re.search(r'<style[^>]*>', html[pos:], re.IGNORECASE)
        if not start_match:
            break
        start = pos + start_match.start()
        content_start = pos + start_match.end()
        
        end_match = re.search(r'</style\s*>', html[content_start:], re.IGNORECASE)
        if not end_match:
            break
        content_end = content_start + end_match.start()
        end = content_start + end_match.end()
        
        blocks.append((start, end, content_start, content_end))
        pos = end
    
    return blocks


def find_script_ranges(html):
    """Returns [(start, end), ...] за всички <script>...</script>."""
    ranges = []
    pos = 0
    while True:
        start_match = re.search(r'<script[^>]*>', html[pos:], re.IGNORECASE)
        if not start_match:
            break
        start = pos + start_match.start()
        content_start = pos + start_match.end()
        
        end_match = re.search(r'</script\s*>', html[content_start:], re.IGNORECASE)
        if not end_match:
            break
        end = content_start + end_match.end()
        
        ranges.append((start, end))
        pos = end
    
    return ranges


def find_comment_ranges(html):
    """Returns [(start, end), ...] за всички <!-- ... -->."""
    ranges = []
    pos = 0
    while True:
        start_match = re.search(r'<!--', html[pos:])
        if not start_match:
            break
        start = pos + start_match.start()
        content_start = pos + start_match.end()
        
        end_match = re.search(r'-->', html[content_start:])
        if not end_match:
            break
        end = content_start + end_match.end()
        
        ranges.append((start, end))
        pos = end
    
    return ranges


def is_inside(pos, ranges):
    """Проверява дали pos е в някой от дадените диапазони."""
    for s, e in ranges:
        if s <= pos < e:
            return True
    return False


def verify_balanced(content):
    """Проверява че { и } са балансирани в CSS (без да брои в strings/comments)."""
    depth = 0
    in_comment = False
    in_str = False
    quote = None
    escape = False
    
    i = 0
    while i < len(content):
        c = content[i]
        
        if not in_str and i + 1 < len(content) and c == '/' and content[i + 1] == '*':
            in_comment = True
            i += 2
            continue
        if in_comment:
            if i + 1 < len(content) and c == '*' and content[i + 1] == '/':
                in_comment = False
                i += 2
                continue
            i += 1
            continue
        
        if escape:
            escape = False
            i += 1
            continue
        if in_str:
            if c == '\\':
                escape = True
            elif c == quote:
                in_str = False
            i += 1
            continue
        if c in ('"', "'"):
            in_str = True
            quote = c
            i += 1
            continue
        
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth < 0:
                return False
        
        i += 1
    
    return depth == 0 and not in_comment


def find_head_close(html):
    """
    Намира ИСТИНСКИЯ </head> — този, който е между <head> и <body>.
    Не хваща </head> в JS стрингове.
    
    Returns (position, error) — точно едно от двете е None.
    """
    head_match = re.search(r'<head[^>]*>', html, re.IGNORECASE)
    if not head_match:
        return None, "Няма <head> таг в HTML"
    
    body_match = re.search(r'<body[^>]*>', html[head_match.end():], re.IGNORECASE)
    if not body_match:
        return None, "Няма <body> таг след <head>"
    
    body_start = head_match.end() + body_match.start()
    
    close_match = re.search(
        r'</head\s*>',
        html[head_match.end():body_start],
        re.IGNORECASE
    )
    if not close_match:
        return None, "Няма </head> между <head> и <body>"
    
    absolute_pos = head_match.end() + close_match.start()
    return absolute_pos, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--html', default='../index.html')
    ap.add_argument('--dry-run', action='store_true')
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
    
    # ═══ Диагностика: колко </head> има? ═══
    all_head_closes = len(re.findall(r'</head\s*>', html, re.IGNORECASE))
    if all_head_closes != 1:
        print(f'  ⚠ Внимание: намерени {all_head_closes} </head> тага в целия файл')
        print(f'     (нормално е 1 — другите са вероятно в JS стрингове)')
        print()
    
    # ═══ Намери style блокове ═══
    print('═══ Извличане на <style> блокове ═══')
    blocks = find_style_blocks(html)
    
    if not blocks:
        print('  ⚠ Не са намерени <style> блокове. Нищо за извличане.')
        return 0
    
    print(f'  Намерени {len(blocks)} <style> блок(а)')
    
    # ═══ Провери че никой не е в <script> или <!-- --> ═══
    script_ranges = find_script_ranges(html)
    comment_ranges = find_comment_ranges(html)
    
    safe_blocks = []
    for i, (start, end, cs, ce) in enumerate(blocks, 1):
        if is_inside(start, script_ranges):
            print(f'  ⚠ Блок {i}: ВЪТРЕ в <script> — пропускам (не бива да изваждаме от JS)')
            continue
        if is_inside(start, comment_ranges):
            print(f'  ⚠ Блок {i}: ВЪТРЕ в <!-- --> — пропускам')
            continue
        safe_blocks.append((start, end, cs, ce))
    
    if not safe_blocks:
        print()
        print('✗ Няма безопасни <style> блокове за извличане.')
        return 1
    
    blocks = safe_blocks
    print(f'  Извличам {len(blocks)} безопасни блок(а)')
    print()
    
    # ═══ Провери balance на всеки ═══
    all_ok = True
    for i, (start, end, cs, ce) in enumerate(blocks, 1):
        content = html[cs:ce]
        size = len(content.encode('utf-8'))
        if verify_balanced(content):
            print(f'  ✓ Блок {i}: {size:>8,} B — балансиран')
        else:
            print(f'  ✗ Блок {i}: {size:>8,} B — НЕ Е БАЛАНСИРАН')
            all_ok = False
    
    if not all_ok:
        print()
        print('✗ Поне един блок не е балансиран. Aborting.')
        return 1
    
    # ═══ Обедини CSS ═══
    all_css_parts = []
    for i, (start, end, cs, ce) in enumerate(blocks, 1):
        all_css_parts.append(f'/* === Style block {i} (extracted from index.html) === */\n')
        all_css_parts.append(html[cs:ce].strip())
        all_css_parts.append('\n\n')
    all_css = ''.join(all_css_parts)
    all_css_size = len(all_css.encode('utf-8'))
    
    print()
    print(f'  Обединен CSS: {all_css_size:,} B')
    
    # ═══ Изгради new_html: премахни <style> блокове (отзад напред) ═══
    new_html = html
    for start, end, cs, ce in reversed(blocks):
        new_html = new_html[:start] + new_html[end:]
    
    # ═══ Намери ИСТИНСКИЯ </head> в новия HTML ═══
    head_close_pos, err = find_head_close(new_html)
    if err:
        print()
        print(f'✗ {err}')
        return 1
    
    # ═══ Вмъкни <link> ═══
    link_tag = '<link rel="stylesheet" href="style.css">\n'
    new_html = new_html[:head_close_pos] + link_tag + new_html[head_close_pos:]
    
    print(f'  <link> вмъкнат на позиция {head_close_pos:,}')
    
    # ═══ Dry run? ═══
    if args.dry_run:
        print()
        print('═══ DRY RUN — НИЩО НЕ Е ЗАПИСАНО ═══')
        print(f'  Ще създам: style.css ({all_css_size:,} B)')
        print(f'  Ще вмъкна <link> преди </head>')
        print(f'  Ще премахна {len(blocks)} <style> блок(а) от index.html')
        return 0
    
    # ═══ Backup ═══
    backup_name = f'{html_path.name}.bak-{int(time.time())}'
    backup = html_path.parent / backup_name
    shutil.copy2(html_path, backup)
    print()
    print(f'✓ Backup: {backup_name}')
    
    # ═══ Запиши style.css ═══
    css_path = html_path.parent / 'style.css'
    css_path.write_text(all_css, encoding='utf-8')
    print(f'✓ style.css ({all_css_size:,} B)')
    
    # ═══ Запиши index.html ═══
    html_path.write_text(new_html, encoding='utf-8')
    
    # ═══ Verify ═══
    final = html_path.read_text(encoding='utf-8')
    issues = []
    
    # 1. <link> съществува
    link_pos = final.find('href="style.css"')
    if link_pos == -1:
        issues.append('Липсва <link rel="stylesheet" href="style.css">')
    
    # 2. <link> е преди истинския </head>
    final_head_close, final_err = find_head_close(final)
    if final_err:
        issues.append(f'Верификация: {final_err}')
    elif link_pos != -1 and link_pos > final_head_close:
        issues.append('<link> е СЛЕД </head> (грешно място)')
    
    # 3. Няма изтекли <style> блокове
    remaining_styles = find_style_blocks(final)
    script_ranges_final = find_script_ranges(final)
    comment_ranges_final = find_comment_ranges(final)
    leaked = [
        i for i, (s, e, cs, ce) in enumerate(remaining_styles, 1)
        if not is_inside(s, script_ranges_final) and not is_inside(s, comment_ranges_final)
    ]
    if leaked:
        issues.append(f'{len(leaked)} <style> блок(а) не са извлечени (извън scripts/comments)')
    
    # 4. style.css съществува и е непразен
    if not css_path.exists():
        issues.append('style.css не съществува')
    elif css_path.stat().st_size == 0:
        issues.append('style.css е празен')
    
    new_size = len(new_html.encode('utf-8'))
    new_lines = new_html.count('\n') + 1
    
    print()
    print('═' * 65)
    print(f'  index.html:  {original_lines:>6,} реда → {new_lines:>6,} реда')
    print(f'  Size:        {original_size:>9,} B → {new_size:>9,} B')
    print(f'  Спестени:    {original_size - new_size:,} B ({(1-new_size/original_size)*100:.1f}%)')
    print(f'  style.css:   {all_css_size:>9,} B')
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
    print('  2. Ctrl+Shift+R (hard reload)')
    print('  3. Стиловете трябва да са същите като преди')
    print('  4. F12 → Network → style.css трябва да е 200 OK')
    print('  5. F12 → Console → 0 errors')
    print()
    print('АКО СТИЛОВЕТЕ СА СЧУПЕНИ:')
    print(f'  cp {backup_name} index.html')
    print()
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())