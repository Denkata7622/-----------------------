#!/usr/bin/env python3
"""
verify_only.py — Верифицира съществуваща статия БЕЗ да я генерира наново.
Струва ~$0.08 (само Sol verifier call).

Употреба:
    python verify_only.py 1.1
    python verify_only.py 1.1 --version 2
"""
import sys
import json
import re
from pathlib import Path
from datetime import datetime

from pipeline import (
    BASE_DIR, CONFIG, State, Queue, AIClient,
    format_prompt, ARTICLE_VERIFICATION_PROMPT, ARTICLE_REVIEWER,
)


def _parse_json(text: str):
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```\s*$', '', text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find('{'), text.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return None
    candidate = text[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        fixed = re.sub(r',\s*([}\]])', r'\1', candidate)
        try:
            return json.loads(fixed)
        except Exception:
            return None


def verify_only(point_id: str, use_version: int = None):
    safe_id = point_id.replace(".", "_")
    article_dir = BASE_DIR.parent / "generated" / "articles" / safe_id

    if not article_dir.exists():
        print(f"✗ Няма директория: {article_dir}")
        return 1

    if use_version:
        article_path = article_dir / f"deep-v{use_version}.md"
    else:
        article_path = article_dir / "deep.md"

    if not article_path.exists():
        print(f"✗ Няма {article_path.name}")
        return 1

    content = article_path.read_text(encoding="utf-8")
    if "\n---\n" in content:
        article = content.split("\n---\n", 1)[1].strip()
    else:
        article = content

    word_count = len(article.split())
    print(f"📄 {article_path.name}: {word_count} думи")

    queue = Queue()
    item = queue.get(point_id)
    if item is None:
        print(f"⚠ {point_id} не е в queue — ползвам defaults")
        class _F: pass
        item = _F()
        item.id = point_id
        item.title = "?"
        item.desc = ""

    if not CONFIG.get("enable_verification") or not CONFIG["verifier"].get("api_key"):
        print("✗ Verification disabled или липсва api_key")
        return 1

    verifier = AIClient(CONFIG["verifier"], name="ver")

    user = format_prompt(
        ARTICLE_VERIFICATION_PROMPT,
        title=item.title,
        point_id=item.id,
        desc=item.desc or "(няма описание)",
        article_markdown=article,
    )

    print(f"🔍 Верификация с {CONFIG['verifier']['model']}...")
    text, tokens, cost = verifier.call(
        ARTICLE_REVIEWER, user, item.id, force_json=True
    )

    if text is None:
        print("✗ Verifier не върна отговор")
        return 1

    parsed = _parse_json(text)
    if parsed is None:
        print("✗ JSON parse failed")
        print(f"RAW (first 800): {text[:800]!r}")
        return 1

    score = parsed.get("score", "?")
    verdict = parsed.get("verdict", "?")

    print()
    print("═" * 60)
    print(f"  SCORE: {score}/10 — {verdict}")
    print(f"  Cost:  ${cost:.4f}")
    print(f"  Tokens: {tokens}")
    print("═" * 60)

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    vf = parsed

    def _lst(key):
        return "\n".join(f"- {x}" for x in vf.get(key, [])) or "-"

    issues_md = "\n".join(
        f"- [{i.get('severity','?')}] **{i.get('section','')}**: {i.get('description','')}"
        for i in vf.get("issues", [])
    ) or "-"
    math_md = "\n".join(
        f"- `{m.get('formula','')}` — {m.get('problem','')} → {m.get('fix','')}"
        for m in vf.get("math_errors", [])
    ) or "-"

    md = f"""# Verification re-check — {item.title}

**ID:** `{item.id}`
**Дата:** {ts}
**Verifier:** {CONFIG['verifier']['model']}
**Article:** {article_path.name} ({word_count} думи)

## Verdict: {vf.get('verdict', '?')} — Score: {vf.get('score', '?')}/10

**Reasoning:** {vf.get('verdict_reasoning', '—')}

## Strengths
{_lst('strengths')}

## Issues
{issues_md}

## Math errors
{math_md}

## Missing topics
{_lst('missing_topics')}

## Suggestions
{_lst('suggestions')}
"""
    (article_dir / "verify-recheck.md").write_text(md, encoding="utf-8")
    (article_dir / "verify-recheck.json").write_text(
        json.dumps({**vf, "_cost": cost, "_tokens": tokens,
                    "_model": CONFIG['verifier']['model']},
                   ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"✓ Записано: verify-recheck.md, verify-recheck.json")
    print()
    if vf.get("issues"):
        print("Issues:")
        for iss in vf["issues"]:
            print(f"  [{iss.get('severity','?')}] {iss.get('section','')}: "
                  f"{iss.get('description','')[:160]}")
    if vf.get("math_errors"):
        print()
        print("Math errors:")
        for m in vf["math_errors"]:
            print(f"  {m.get('formula','')}: {m.get('problem','')[:120]}")

    state = State()
    state.add_cost(cost, tokens)
    print(f"\n💰 Похарчено: ${cost:.4f} | Остава днес: ${state.budget_remaining():.2f}")

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Употреба: python verify_only.py <point_id> [--version N]")
        sys.exit(1)
    point_id = sys.argv[1]
    version = None
    if "--version" in sys.argv:
        idx = sys.argv.index("--version")
        if idx + 1 < len(sys.argv):
            version = int(sys.argv[idx + 1])
    sys.exit(verify_only(point_id, version))