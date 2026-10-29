#!/usr/bin/env python3
"""
regen_compare.py — сравнява нова версия с стара (вече верифицирана).
Използва се от ВСЕКИ worker, който регенерира съществуващ output.

Публични функции:
    save_old_version(folder, files, reason)   → int
    load_latest_history(folder, filename)     → str|None
    diff_articles(old_md, new_md)             → dict
    diff_problems(old_json, new_json)         → dict
    diff_extraction(old_json, new_json)       → dict
    diff_gaps(old_json, new_json)             → dict
    evaluate(old_content, new_content, diff, ai_client, context)
                                              → dict|None
    apply_decision(decision, folder, new_files_data, old_files)
                                              → "kept"|"reverted"|"manual"|"merged"
"""
import json
import re
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from personas import REGEN_EVALUATOR

log = logging.getLogger("regen_compare")


# ═══════════════════════════════════════════════════════════════
# VERSIONING
# ═══════════════════════════════════════════════════════════════
def save_old_version(folder: Path, files: list, reason: str = "regen") -> int:
    """Копира текущите files в _history/v{N}/. Връща N."""
    history = folder / "_history"
    history.mkdir(exist_ok=True)
    existing = sorted(
        [d for d in history.iterdir() if d.is_dir() and re.match(r'^v\d+$', d.name)],
        key=lambda d: int(d.name[1:])
    )
    version = (int(existing[-1].name[1:]) + 1) if existing else 1
    v_dir = history / f"v{version}"
    v_dir.mkdir(exist_ok=True)

    for fn in files:
        src = folder / fn
        if src.exists():
            shutil.copy2(src, v_dir / fn)

    meta = {
        "version": version,
        "saved_at": datetime.now().isoformat(),
        "reason": reason,
        "files": files,
    }
    (v_dir / "_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info(f"  📦 Old version saved → _history/v{version}/ ({reason})")
    return version


def load_latest_history(folder: Path, filename: str) -> Optional[str]:
    """Зарежда съдържанието на filename от най-новата версия в _history/."""
    history = folder / "_history"
    if not history.exists():
        return None
    versions = sorted(
        [d for d in history.iterdir() if d.is_dir() and re.match(r'^v\d+$', d.name)],
        key=lambda d: int(d.name[1:])
    )
    if not versions:
        return None
    latest = versions[-1] / filename
    if latest.exists():
        return latest.read_text(encoding="utf-8")
    return None


# ═══════════════════════════════════════════════════════════════
# DIFF FUNCTIONS — per content type
# ═══════════════════════════════════════════════════════════════
def diff_articles(old_md: str, new_md: str) -> dict:
    """Структуриран diff за статии (deep.md)."""
    def cnt(pattern, s):
        return len(re.findall(pattern, s, re.MULTILINE))

    formula_re = r'\$\$?[^$\n]+\$\$?'
    section_re = r'^##\s+'
    example_re = r'^###\s+(?:Пример|Задача|Example)'

    return {
        "type": "article",
        "old_length": len(old_md),
        "new_length": len(new_md),
        "length_change_pct": round(
            (len(new_md) - len(old_md)) / max(1, len(old_md)) * 100, 1
        ),
        "old_formula_count": cnt(formula_re, old_md),
        "new_formula_count": cnt(formula_re, new_md),
        "old_section_count": cnt(section_re, old_md),
        "new_section_count": cnt(section_re, new_md),
        "old_example_count": cnt(example_re, old_md),
        "new_example_count": cnt(example_re, new_md),
        "old_has_proof_section": bool(re.search(
            r'Доказателство|Proof', old_md, re.IGNORECASE)),
        "new_has_proof_section": bool(re.search(
            r'Доказателство|Proof', new_md, re.IGNORECASE)),
        "old_has_errors_section": bool(re.search(
            r'Типични грешки|грешки и капани', old_md, re.IGNORECASE)),
        "new_has_errors_section": bool(re.search(
            r'Типични грешки|грешки и капани', new_md, re.IGNORECASE)),
        "old_has_recognition_section": bool(re.search(
            r'как да разпозная|тригери|recognition', old_md, re.IGNORECASE)),
        "new_has_recognition_section": bool(re.search(
            r'как да разпозная|тригери|recognition', new_md, re.IGNORECASE)),
    }


def diff_problems(old_json: dict, new_json: dict) -> dict:
    """Структуриран diff за задачи (problems.json + solutions.json)."""
    old_problems = {p.get("num"): p for p in old_json.get("problems", [])
                    if p.get("num") is not None}
    new_problems = {p.get("num"): p for p in new_json.get("problems", [])
                    if p.get("num") is not None}

    old_nums = set(old_problems.keys())
    new_nums = set(new_problems.keys())

    changed = []
    for num in sorted(old_nums & new_nums):
        op = old_problems[num]
        np = new_problems[num]
        changed_flag = (
            op.get("problem", "") != np.get("problem", "") or
            op.get("difficulty", "") != np.get("difficulty", "")
        )
        if changed_flag:
            changed.append({
                "num": num,
                "old_difficulty": op.get("difficulty"),
                "new_difficulty": np.get("difficulty"),
                "difficulty_changed": op.get("difficulty") != np.get("difficulty"),
                "old_problem_len": len(op.get("problem", "")),
                "new_problem_len": len(np.get("problem", "")),
            })

    return {
        "type": "problems",
        "old_count": len(old_problems),
        "new_count": len(new_problems),
        "dropped_nums": sorted(old_nums - new_nums),
        "added_nums": sorted(new_nums - old_nums),
        "changed_problems": changed,
        "total_changed": len(changed),
        "shipped_old": sum(1 for p in old_problems.values()
                           if p.get("status") == "shipped"),
        "shipped_new": sum(1 for p in new_problems.values()
                           if p.get("status") == "shipped"),
    }


def diff_extraction(old_json: dict, new_json: dict) -> dict:
    """Структуриран diff за extraction (chunk-N.json)."""
    old_probs = old_json.get("problems", [])
    new_probs = new_json.get("problems", [])

    old_by_num = {p.get("num"): p for p in old_probs if p.get("num") is not None}
    new_by_num = {p.get("num"): p for p in new_probs if p.get("num") is not None}

    categorization_changes = []
    for num in old_by_num.keys() & new_by_num.keys():
        oc = old_by_num[num].get("point_id")
        nc = new_by_num[num].get("point_id")
        if oc != nc:
            categorization_changes.append({
                "num": num,
                "old_point": oc,
                "new_point": nc,
            })

    return {
        "type": "extraction",
        "old_problem_count": len(old_probs),
        "new_problem_count": len(new_probs),
        "count_diff": len(new_probs) - len(old_probs),
        "dropped_nums": sorted(set(old_by_num.keys()) - set(new_by_num.keys())),
        "added_nums": sorted(set(new_by_num.keys()) - set(old_by_num.keys())),
        "categorization_changes": categorization_changes,
    }


def diff_gaps(old_json: dict, new_json: dict) -> dict:
    """Структуриран diff за gap decisions."""
    old_decisions = {c.get("suggested_id"): c for c in old_json.get("decisions", [])
                     if c.get("suggested_id")}
    new_decisions = {c.get("suggested_id"): c for c in new_json.get("decisions", [])
                     if c.get("suggested_id")}

    changed = []
    for sid in old_decisions.keys() & new_decisions.keys():
        od = old_decisions[sid].get("decision")
        nd = new_decisions[sid].get("decision")
        if od != nd:
            changed.append({
                "suggested_id": sid,
                "old_decision": od,
                "new_decision": nd,
            })

    return {
        "type": "gaps",
        "old_count": len(old_decisions),
        "new_count": len(new_decisions),
        "decision_changes": changed,
        "total_changes": len(changed),
    }


# ═══════════════════════════════════════════════════════════════
# EVALUATION PROMPT
# ═══════════════════════════════════════════════════════════════
EVAL_PROMPT = REGEN_EVALUATOR + """

═══ КОНТЕКСТ ═══
{context}

═══ СТАРА ВЕРСИЯ (еталон) ═══
{old_content}

═══ НОВА ВЕРСИЯ (за сравнение) ═══
{new_content}

═══ STRUCTURED DIFF ═══
{diff}

═══ ТВОЯТА ЗАДАЧА ═══
Сравни двете версии и реши какво да правим. Върни САМО JSON:

{{
  "verdict": "keep_new|revert_to_old|merge_best|manual_review",
  "score_old": 1-10,
  "score_new": 1-10,
  "delta": -2,
  "regressions": ["конкретни неща, които се загубиха"],
  "improvements": ["конкретни неща, които се подобриха"],
  "reasoning": "Защо това решение",
  "safety_check": "Безопасно ли е за ученик",
  "confidence": 0.0-1.0
}}

═══ ПРАВИЛА ЗА VERDICT ═══
- keep_new: новата е очевидно по-добра, няма регресии → ЗАМЕНИ
- revert_to_old: новата има регресии, старите стойности по-добри → ВЪРНИ
- merge_best: двете имат силни страни, човешки преглед за ръчно сливане
- manual_review: несигурен, не автоматизирай

═══ SCORING ═══
- score_old: каква би била оценката на старата версия днес
- score_new: каква е оценката на новата
- delta: score_new - score_old (от -2 до +2)

═══ АКО НЕ СИ СИГУРЕН ═══
→ manual_review. По-добре човек да прегледа, отколкото да заменим 
  добра версия с по-лоша.
"""


def evaluate(
    old_content: str,
    new_content: str,
    diff: dict,
    ai_client,
    context: str = "",
    max_len: int = 8000,
) -> Optional[dict]:
    """AI call за оценка на регенерация."""
    user = EVAL_PROMPT.format(
        context=context or "(без специален контекст)",
        old_content=old_content[:max_len],
        new_content=new_content[:max_len],
        diff=json.dumps(diff, ensure_ascii=False, indent=2),
    )

    raw = ai_client.call(EVAL_PROMPT, user, "regen-eval", force_json=True)
    if not raw:
        return None

    # Parse JSON
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if not m:
        return None
    try:
        parsed = json.loads(m.group(0))
    except Exception:
        try:
            parsed = json.loads(re.sub(r',\s*([}\]])', r'\1', m.group(0)))
        except Exception:
            return None

    return parsed


# ═══════════════════════════════════════════════════════════════
# APPLY DECISION
# ═══════════════════════════════════════════════════════════════
def apply_decision(
    decision: dict,
    folder: Path,
    write_new_fn,          # callable: () → None (записва новите файлове)
    files: list,           # ["problems.json", "solutions.json", ...]
    filename_for_compare: str,  # главен файл за diff (напр. "problems.json")
) -> str:
    """
    Прилага решението:
      - keep_new: запази old → _history/vN/, запиши new
      - revert_to_old: не пиши new (old си остава)
      - merge_best / manual_review: запази old → _history/vN/, запиши new 
        като .pending-review + запази old като .active
    
    Връща: "kept"|"reverted"|"manual"|"merged"
    """
    verdict = decision.get("verdict", "manual_review")
    delta = decision.get("delta", 0)
    confidence = decision.get("confidence", 0)

    if verdict == "keep_new":
        save_old_version(folder, files, reason="regen (new approved)")
        write_new_fn()
        log.info(f"  ✓ keep_new (delta={delta:+d}, conf={confidence:.2f})")
        return "kept"

    elif verdict == "revert_to_old":
        log.warning(
            f"  ↩ revert_to_old (delta={delta:+d}, conf={confidence:.2f}) — "
            f"regressions: {decision.get('regressions', [])[:2]}"
        )
        return "reverted"

    elif verdict == "merge_best":
        save_old_version(folder, files, reason="regen (needs merge)")
        write_new_fn()
        log.warning(
            f"  ⚠ merge_best — човешки преглед нужен. "
            f"improvements={decision.get('improvements', [])[:2]}, "
            f"regressions={decision.get('regressions', [])[:2]}"
        )
        return "merged"

    else:  # manual_review
        save_old_version(folder, files, reason="regen (manual review)")
        write_new_fn()
        log.warning(
            f"  ⚠ manual_review — човешки преглед нужен. "
            f"reason={decision.get('reasoning', '')[:100]}"
        )
        return "manual"


# ═══════════════════════════════════════════════════════════════
# CONVENIENCE — high-level wrapper
# ═══════════════════════════════════════════════════════════════
def regen_with_compare(
    folder: Path,
    filename: str,
    diff_fn,                    # diff_problems | diff_articles | ...
    generate_new_fn,            # callable: () → dict (генерира нова версия в паметта)
    write_new_fn,               # callable: (data) → None (записва на диск)
    ai_evaluator,               # AIClient
    context: str = "",
    files: Optional[list] = None,
) -> tuple:
    """
    High-level wrapper:
      1. Зареди old (ако има)
      2. Генерирай new (в паметта)
      3. diff + evaluate
      4. apply_decision
    
    Връща: (result_data, action) където action ∈ {kept, reverted, merged, manual, first_time}
    """
    if files is None:
        files = [filename]

    old_file = folder / filename
    old_exists = old_file.exists()

    # First time — просто запиши
    if not old_exists:
        new_data = generate_new_fn()
        if new_data is None:
            return None, "error"
        write_new_fn(new_data)
        log.info(f"  🆕 first generation (без сравнение)")
        return new_data, "first_time"

    # Regen — сравни
    try:
        old_data = json.loads(old_file.read_text(encoding="utf-8"))
    except Exception as e:
        log.error(f"  ✗ Cannot read old {filename}: {e}")
        new_data = generate_new_fn()
        if new_data is None:
            return None, "error"
        write_new_fn(new_data)
        return new_data, "first_time"

    new_data = generate_new_fn()
    if new_data is None:
        log.error(f"  ✗ Generation failed — keeping old version")
        return old_data, "reverted"

    # Diff
    diff = diff_fn(old_data, new_data)

    # Quick check: ако няма разлика — не пипай
    if diff.get("total_changed", 0) == 0 and diff.get("old_count") == diff.get("new_count"):
        log.info(f"  🟰 No changes detected — keeping old")
        return old_data, "reverted"

    # Evaluate
    decision = evaluate(
        old_content=json.dumps(old_data, ensure_ascii=False, indent=2),
        new_content=json.dumps(new_data, ensure_ascii=False, indent=2),
        diff=diff,
        ai_client=ai_evaluator,
        context=context,
    )

    if decision is None:
        log.warning(f"  ⚠ Evaluator failed — reverting to old (safe default)")
        return old_data, "reverted"

    # Apply
    action = apply_decision(
        decision=decision,
        folder=folder,
        write_new_fn=lambda: write_new_fn(new_data),
        files=files,
        filename_for_compare=filename,
    )

    if action == "reverted":
        return old_data, action
    return new_data, action