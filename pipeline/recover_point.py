#!/usr/bin/env python3
"""recover_point.py — възстановява точка от temp файлове след crash."""
import json
import sys
import re
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.resolve()
ARTICLES = BASE.parent / "generated" / "articles"


def recover(point_id: str) -> bool:
    safe_id = point_id.replace(".", "_")
    article_dir = ARTICLES / safe_id
    temp_dir = article_dir / "temp"

    if not temp_dir.exists():
        print(f"✗ Няма temp за {point_id}")
        return False

    temps = sorted(temp_dir.glob("*.md"))
    if not temps:
        print(f"✗ Празна temp директория за {point_id}")
        return False

    # Find best temp by score (parse header)
    best = None
    best_score = -1
    for t in temps:
        content = t.read_text(encoding="utf-8")
        m = re.search(r'\*\*Score:\*\*\s*(\d+)/10', content)
        score = int(m.group(1)) if m else 0
        if score > best_score:
            best_score = score
            best = (t, content, score)

    t, content, score = best
    print(f"✓ Най-добър: {t.name} (score {score})")

    # Strip temp header (everything up to first \n---\n\n)
    parts = content.split("\n---\n\n", 1)
    article = parts[1].strip() if len(parts) > 1 else content

    word_count = len(article.split())
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    meta_file = article_dir / "metadata.json"
    meta = {}
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    title = meta.get("title", "Теорема на Менелай")
    v = meta.get("version", 1) + 1

    # deep.md + deep-vN.md
    deep = f"""# {title} — Пълна статия

**ID:** `{point_id}`
**Генерирано:** {ts}
**Версия:** v{v}
**Думи:** {word_count}
**Generator:** anthropic/claude-sonnet-5.5
**Verifier:** openai/gpt-6.1-sol

---

{article}
"""
    (article_dir / "deep.md").write_text(deep, encoding="utf-8")
    (article_dir / f"deep-v{v}.md").write_text(deep, encoding="utf-8")

    # text.md — first 2 sections
    matches = list(re.finditer(r'(?m)^##\s+(\d+\.\s*[^\n]+)', article))
    if matches:
        out = []
        for i, m in enumerate(matches[:2]):
            start = m.start()
            end = matches[i+1].start() if i+1 < len(matches) else len(article)
            out.append(article[start:end].strip())
        sections_text = "\n\n".join(out)
    else:
        sections_text = article[:500]

    text_md = f"""# {title}

**ID:** `{point_id}`
**Генерирано:** {ts}
**Версия:** v{v}
**Думи:** {word_count}

---

{sections_text}
"""
    (article_dir / "text.md").write_text(text_md, encoding="utf-8")
    (article_dir / f"text-v{v}.md").write_text(text_md, encoding="utf-8")

    # metadata.json
    meta.update({
        "title": title,
        "point_id": point_id,
        "generated_at": ts,
        "version": v,
        "word_count": word_count,
    })
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # verify.md — минимален, защото детайлите са загубени при crash
    verdict = "approve" if score >= 7 else "revise" if score >= 4 else "reject"
    # Провери дали имаме запазен verify JSON в temp
    temp_verify_path = temp_dir / f"{t.stem}-verify.json"
    if temp_verify_path.exists():
        try:
            vf_full = json.loads(temp_verify_path.read_text(encoding="utf-8"))
            # Имаме пълния verification — запиши истински verify.md
            strengths = "\n".join(f"- {s}" for s in vf_full.get("strengths", [])) or "-"
            issues = "\n".join(
                f"- [{i.get('severity','?')}] **{i.get('section','')}**: {i.get('description','')}"
                for i in vf_full.get("issues", [])
            ) or "-"
            math_err = "\n".join(
                f"- `{m.get('formula','')}` — {m.get('problem','')} → {m.get('fix','')}"
                for m in vf_full.get("math_errors", [])
            ) or "-"
            missing = "\n".join(f"- {m}" for m in vf_full.get("missing_topics", [])) or "-"
            suggestions = "\n".join(f"- {s}" for s in vf_full.get("suggestions", [])) or "-"

            verify_md = f"""# Verification report (recovered) — {title}

**ID:** `{point_id}`
**Дата:** {ts}
**Score:** {vf_full.get('score', '?')}/10
**Verdict:** {vf_full.get('verdict', '?')}
**Reasoning:** {vf_full.get('verdict_reasoning', '—')}

Възстановено от temp файл: `{t.name}` + `{temp_verify_path.name}`.

## Strengths
{strengths}

## Issues
{issues}

## Math errors
{math_err}

## Missing topics
{missing}

## Suggestions
{suggestions}
"""
            (article_dir / "verify.md").write_text(verify_md, encoding="utf-8")
            # И запази като verify-vN.json
            (article_dir / f"verify-v{v}.json").write_text(
                json.dumps(vf_full, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"  ✓ Възстановен пълен verify.md от {temp_verify_path.name}")
        except Exception as e:
            print(f"  ⚠ Грешка при четене на {temp_verify_path.name}: {e}")
            # Fallback на stub
            _write_stub_verify(article_dir, title, point_id, ts, score, verdict, t)
    else:
        _write_stub_verify(article_dir, title, point_id, ts, score, verdict, t)


def _write_stub_verify(article_dir, title, point_id, ts, score, verdict, t):
    verify_md = f"""# Verification report — {title}

**ID:** `{point_id}`
**Дата:** {ts}
**Score:** {score}/10
**Verdict:** {verdict}

⚠️ Пълните детайли от верификацията липсват (verify JSON не е намерен в temp).
Възстановено от temp файл: `{t.name}`.
Ако искаш пълен verify.md, пусни: python verify_only.py {point_id}
"""
    (article_dir / "verify.md").write_text(verify_md, encoding="utf-8")

    # state.json
    state_file = BASE / "state.json"
    state = json.loads(state_file.read_text(encoding="utf-8"))
    state.setdefault("processed", {})[point_id] = {
        "status": "done",
        "cost": 0,
        "tokens": 0,
        "ts": datetime.now().timestamp(),
        "score": score,
        "verdict": verdict,
        "word_count": word_count,
        "note": f"Manually recovered from {t.name}",
    }
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✓ {point_id} възстановен: {word_count}w, score {score}, verdict {verdict}")
    print(f"  → deep-v{v}.md, text-v{v}.md, metadata.json, verify.md, state.json")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Употреба: python recover_point.py <point_id>  (напр. 1.1)")
        sys.exit(1)
    ok = recover(sys.argv[1])
    sys.exit(0 if ok else 1)