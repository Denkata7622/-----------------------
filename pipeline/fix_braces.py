#!/usr/bin/env python3
"""fix_braces.py — поправя JSON braces в GENERATION_PROMPT и VERIFICATION_PROMPT."""
import re
from pathlib import Path

p = Path("problem_generator.py")
src = p.read_text(encoding="utf-8")

# Backup
Path("problem_generator.py.bak").write_text(src, encoding="utf-8")
print("💾 Backup: problem_generator.py.bak")

# ── Fix GENERATION_PROMPT ──
# Намери секцията "═══ ФОРМАТ (САМО JSON) ═══\n{" до следващия "═══ ПРАВИЛА"
pattern_gen = re.compile(
    r'(═══ ФОРМАТ \(САМО JSON\) ═══\n)(\{)(.*?)(\n\}\n\n═══ ПРАВИЛА)',
    re.DOTALL
)
def fix_gen_json(m):
    header, open_brace, body, footer = m.groups()
    # Escape всички { и } в тялото
    body_fixed = body.replace('{', '{{').replace('}', '}}')
    return header + '{{' + body_fixed + '\n}}\n\n═══ ПРАВИЛА'

src_new, n1 = pattern_gen.subn(fix_gen_json, src)
if n1:
    src = src_new
    print(f"✓ Fixed GENERATION_PROMPT ({n1} match)")
else:
    print("✗ Не намерих GENERATION_PROMPT JSON блок")

# ── Fix VERIFICATION_PROMPT ──
pattern_ver = re.compile(
    r'(═══ ФОРМАТ \(САМО JSON\) ═══\n)(\{)(.*?)(\n\}\n\nПРАВИЛА:)',
    re.DOTALL
)
src_new, n2 = pattern_ver.subn(fix_gen_json, src)
# Note: fix_gen_json has hardcoded "═══ ПРАВИЛА" footer — need different one for verifier
# Do manual replace instead:

# Simpler: do targeted string replacement
old_gen_block = '''═══ ФОРМАТ (САМО JSON) ═══
{
  "problems": [
    {
      "num": 1,'''
new_gen_block = '''═══ ФОРМАТ (САМО JSON) ═══
{{
  "problems": [
    {{
      "num": 1,'''

if old_gen_block in src:
    src = src.replace(old_gen_block, new_gen_block)
    print("✓ GENERATION_PROMPT JSON open braces")
else:
    print("✗ GENERATION_PROMPT JSON start not found")

old_gen_close = '''      "tests_misconception": "Кое недоразумение тества"
    },
    ... 8 още
  ]
}'''
new_gen_close = '''      "tests_misconception": "Кое недоразумение тества"
    }},
    ... 8 още
  ]
}}'''

if old_gen_close in src:
    src = src.replace(old_gen_close, new_gen_close)
    print("✓ GENERATION_PROMPT JSON close braces")
else:
    print("✗ GENERATION_PROMPT JSON end not found")

# ── VERIFICATION_PROMPT ──
old_ver_block = '''═══ ФОРМАТ (САМО JSON) ═══
{
  "results": {
    "1": {
      "score": 1-10,'''
new_ver_block = '''═══ ФОРМАТ (САМО JSON) ═══
{{
  "results": {{
    "1": {{
      "score": 1-10,'''

if old_ver_block in src:
    src = src.replace(old_ver_block, new_ver_block)
    print("✓ VERIFICATION_PROMPT JSON open braces")
else:
    print("✗ VERIFICATION_PROMPT JSON start not found")

old_ver_close = '''    "2": {...},
    ... 9 още
  },
  "summary": {
    "avg_score": 8.2,
    "shipped": 8,
    "rejected": 1,
    "recommendation": "ship|regenerate_failed|review"
  }
}'''
new_ver_close = '''    "2": {{...}},
    ... 9 още
  }},
  "summary": {{
    "avg_score": 8.2,
    "shipped": 8,
    "rejected": 1,
    "recommendation": "ship|regenerate_failed|review"
  }}
}}'''

if old_ver_close in src:
    src = src.replace(old_ver_close, new_ver_close)
    print("✓ VERIFICATION_PROMPT JSON close braces")
else:
    print("✗ VERIFICATION_PROMPT JSON end not found")

# Запис
p.write_text(src, encoding="utf-8")
print("\n✅ Записан problem_generator.py")
print("Ако нещо липсва — виж .bak файла")