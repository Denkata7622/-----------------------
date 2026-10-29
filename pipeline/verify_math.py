#!/usr/bin/env python3
"""
verify_math.py — Deterministic math verification for generated articles.

Usage:
    python verify_math.py output/R_1/deep.md
    python verify_math.py output/              # all deep.md files
    python verify_math.py output/ --strict     # only files with issues

Requires:
    pip install sympy antlr4-python3-runtime
"""
import re
import sys
import random
import argparse
from pathlib import Path

try:
    import sympy as sp
    from sympy.parsing.latex import parse_latex
except ImportError:
    print("pip install sympy antlr4-python3-runtime")
    sys.exit(1)


# Article math delimiters — pipeline articles use \(...\) and \[...\]
# but we also support $...$ for legacy content.
DISPLAY_PATTERNS = [
    re.compile(r'\$\$(.+?)\$\$', re.DOTALL),
    re.compile(r'\\\[(.+?)\\\]', re.DOTALL),
]
INLINE_PATTERNS = [
    re.compile(r'\$([^$\n]{2,}?)\$'),
    re.compile(r'\\\((.+?)\\\)', re.DOTALL),
]

# Known-bad formulas from GLM 5.3 patterns (extendable)
KNOWN_WRONG = [
    {
        'pattern': r'\(a\s*\+\s*b\)\^3\s*[-−]\s*\(a\s*[-−]\s*b\)\^3\s*=?\s*4ab',
        'correct': '(a+b)³ − (a−b)³ = 6a²b + 2b³',
        'desc': 'Cubic difference formula (GLM confuses with 4ab)',
    },
    {
        'pattern': r'\(a\s*\+\s*b\)\^3\s*\+\s*\(a\s*[-−]\s*b\)\^3\s*=?\s*4ab',
        'correct': '(a+b)³ + (a−b)³ = 2a³ + 6ab² = 2a(a²+3b²)',
        'desc': 'Cubic sum formula (GLM confuses with 4ab)',
    },
    {
        'pattern': r'\(a\s*[-−]\s*b\)\^2\s*=\s*a\^2\s*[-−]\s*b\^2',
        'correct': '(a−b)² = a² − 2ab + b²',
        'desc': 'Missing middle term in squared binomial',
    },
]


def extract_math(text):
    """Extract all math blocks from all delimiter variants."""
    blocks = []
    # Track which ranges are already consumed to avoid overlap
    consumed = []
    for pat in DISPLAY_PATTERNS:
        for m in pat.finditer(text):
            if any(s <= m.start() < e for s, e in consumed):
                continue
            blocks.append(('display', m.group(1).strip(), m.start()))
            consumed.append((m.start(), m.end()))
    # For inline, work on stripped text (display replaced by spaces)
    stripped = text
    for pat in DISPLAY_PATTERNS:
        stripped = pat.sub(lambda m: ' ' * len(m.group(0)), stripped)
    for pat in INLINE_PATTERNS:
        for m in pat.finditer(stripped):
            if any(s <= m.start() < e for s, e in consumed):
                continue
            blocks.append(('inline', m.group(1).strip(), m.start()))
    return blocks


def _try_parse(latex_str):
    """Try multiple strategies to parse LaTeX to SymPy. Returns None on failure."""
    if not latex_str:
        return None
    # Strategy 1: direct parse_latex
    try:
        return parse_latex(latex_str)
    except Exception:
        pass
    # Strategy 2: strip display markers, retry
    cleaned = latex_str.strip().strip('$').strip()
    try:
        return parse_latex(cleaned)
    except Exception:
        pass
    # Strategy 3: manual simple numeric check (only for pure arithmetic)
    try:
        return sp.sympify(cleaned)
    except Exception:
        return None


def is_identity(expr):
    """
    Check if 'LHS = RHS' is algebraically true.
    Returns: True / False / None (can't determine).
    """
    if '=' not in expr:
        return None
    if any(x in expr for x in ['==', '<=', '>=', '!=', '<', '>']):
        return None
    parts = expr.split('=')
    if len(parts) != 2:
        return None
    lhs, rhs = parts[0].strip(), parts[1].strip()
    if not lhs or not rhs:
        return None

    L = _try_parse(lhs)
    R = _try_parse(rhs)
    if L is None or R is None:
        return None

    # Try symbolic simplification
    try:
        diff = sp.simplify(L - R)
        if diff == 0:
            return True
        if diff.is_number:
            return abs(float(diff)) < 1e-9
    except Exception:
        pass

    # Numeric substitution — 5 random points
    free = set()
    for obj in (L, R):
        try:
            free |= obj.free_symbols
        except Exception:
            pass

    if not free:
        try:
            return abs(float(sp.N(L - R))) < 1e-6
        except Exception:
            return None

    for _ in range(5):
        subs = {
            s: sp.Rational(random.randint(2, 19), random.randint(1, 7))
            for s in free
        }
        try:
            v = float(sp.N((L - R).subs(subs)))
            if abs(v) > 1e-6:
                return False
        except Exception:
            continue

    return None


def check_numeric_arithmetic(text):
    """
    Find simple numeric arithmetic claims like '27 + 125 = 152' and verify.
    Catches GLM errors where substitution is wrong but formula structure is correct.
    """
    issues = []
    # Match: <number> <op> <number> = <number>
    # Examples: '27 + 125 = 152', '4\cdot9=36', '2^5=32'
    pattern = re.compile(
        r'(\d+(?:\.\d+)?)\s*'
        r'([+\-−\*×·/÷])\s*'
        r'(\d+(?:\.\d+)?)\s*'
        r'=\s*'
        r'(-?\d+(?:\.\d+)?)'
    )
    for m in pattern.finditer(text):
        a_str, op, b_str, result_str = m.groups()
        try:
            a = float(a_str)
            b = float(b_str)
            result = float(result_str)
        except ValueError:
            continue
        if op in ('+',):
            expected = a + b
        elif op in ('-', '−'):
            expected = a - b
        elif op in ('*', '×', '·'):
            expected = a * b
        elif op in ('/', '÷'):
            if b == 0:
                continue
            expected = a / b
        else:
            continue
        if abs(expected - result) > 1e-6:
            line_no = text[:m.start()].count('\n') + 1
            issues.append({
                'type': 'NUMERIC_FAIL',
                'line': line_no,
                'expr': m.group(0),
                'expected': expected,
            })
    return issues


def check_known_patterns(text):
    issues = []
    for kb in KNOWN_WRONG:
        if re.search(kb['pattern'], text):
            issues.append({
                'type': 'KNOWN_BAD_FORMULA',
                'desc': kb['desc'],
                'correct': kb['correct'],
            })
    return issues


def check_article(path, verbose=False):
    text = path.read_text(encoding='utf-8')
    issues = []
    blocks = extract_math(text)

    for kind, expr, pos in blocks:
        r = is_identity(expr)
        if r is False:
            line_no = text[:pos].count('\n') + 1
            issues.append({
                'type': 'IDENTITY_FAIL',
                'line': line_no,
                'expr': expr[:140].replace('\n', ' '),
            })

    issues += check_known_patterns(text)
    issues += check_numeric_arithmetic(text)
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='File or directory')
    parser.add_argument('--strict', action='store_true', help='Only files with issues')
    args = parser.parse_args()

    p = Path(args.target)
    files = [p] if p.is_file() else sorted(p.rglob('deep.md'))

    total = 0
    flagged_files = 0

    for f in files:
        issues = check_article(f)
        if not issues and args.strict:
            continue
        if issues:
            flagged_files += 1
        print(f"\n{'=' * 60}")
        print(f"  {f}")
        print('=' * 60)
        if not issues:
            print("  ✅ No issues detected by SymPy")
        for iss in issues:
            total += 1
            if iss['type'] == 'IDENTITY_FAIL':
                print(f"  ❌ Line {iss['line']}: {iss['expr']}")
                print(f"     → LHS ≠ RHS (verified with random substitution)")
            elif iss['type'] == 'NUMERIC_FAIL':
                print(f"  ❌ Line {iss['line']}: {iss['expr']}")
                print(f"     → Correct result: {iss['expected']}")
            else:
                print(f"  ❌ {iss['desc']}")
                print(f"     → Correct: {iss['correct']}")

    print(f"\n{'=' * 60}")
    print(f"  TOTAL: {total} issue(s) across {len(files)} file(s) "
          f"({flagged_files} file(s) flagged)")
    print('=' * 60)

    sys.exit(1 if total > 0 else 0)


if __name__ == '__main__':
    main()