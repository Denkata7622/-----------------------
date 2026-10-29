#!/usr/bin/env python3
"""Регенерира project_scan.txt във формат: '<size> KB  |  <path>'."""
import os
from pathlib import Path

OUTPUT = 'project_scan.txt'
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.idea', '.vscode', '.ocr_cache'}
SKIP_PREFIXES = ('.',)  # всички скрити папки/файлове

def fmt_size(n_bytes: int) -> str:
    kb = n_bytes / 1024.0
    if n_bytes % 1024 == 0:
        return str(n_bytes // 1024)
    return f"{kb:.1f}"

def main():
    # 1. Truncate output first — така при повторно пускане
    #    output файлът се вижда с размер 0 (както в примера)
    Path(OUTPUT).write_text('', encoding='utf-8')

    rows = []
    for dirpath, dirnames, filenames in os.walk('.'):
        # Премахни skip-натите директории in-place (os.walk ги пропуска)
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)

        for fname in filenames:
            fpath = Path(dirpath) / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                continue

            rel = str(fpath)
            # Махни './' или '.\' от началото
            if rel.startswith('./'):
                rel = rel[2:]
            elif rel.startswith('.\\'):
                rel = rel[2:]

            rows.append((size, f"{fmt_size(size)} KB  |  {rel}"))

    # Сортирай: първо по размер, после по път (за детерминистичност при равни)
    rows.sort(key=lambda x: (x[0], x[1].lower()))

    Path(OUTPUT).write_text(
        '\n'.join(line for _, line in rows) + '\n',
        encoding='utf-8',
    )

    total_size = sum(s for s, _ in rows) / 1024
    print(f"✓ {OUTPUT}: {len(rows)} файла, {total_size:.1f} KB общо")

if __name__ == '__main__':
    main()