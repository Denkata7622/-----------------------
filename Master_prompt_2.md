# MASTER PROMPT — Olympiad Prep Terminal (пълна екосистема)

## 1. PROJECT IDENTITY

**Име:** Olympiad Prep Terminal
**Цел:** уеб платформа за подготовка по математика за областен и национален кръг. Ученик 11 клас, СМГ.
**Целеви резултат:** 18-22 точки областен, 20+ национален.
**Изпити:** областен 2027-02-08, национален 2027-04-03 до 2027-04-06.
**Учебен план:** 25 седмици, 5 нива, старт 2026-10-23.
**Автор:** Denislav Tsenov, self-taught, работи по проекта от ~2 седмици, Windows + PowerShell.

**Два продукта в един repo:**
1. **Study Terminal** (`index.html`, `style.css`, `ai_assistant.js`, `data/*.js`) — SPA с 14 стъпки / 164 точки, KaTeX, Pomodoro, Exam Sim, AI Tutor с памёт.
2. **Content Pipeline** (`pipeline/*.py`) — PDF → OCR → extract → merge → classify → aggregate → generate articles → generate problems → dual verify. Работи 24/7 през `master_orchestrator.py`.

**Директория (Windows):** `C:\Users\denis\Downloads\Материали Олимпиада МАТ\`
- Frontend: root
- Pipeline: `pipeline\`
- Generated data: `generated\`
- Backups: `backups\`

**Стартиране:**
- Frontend: `python ai_proxy.py` → `http://localhost:8000/index.html`
- Pipeline: `.\py.bat pipeline.py` (24/7) или `--once --point X.Y` (една точка)

---

## 2. FRONTEND (Study Terminal)

### 2.1 Структура на данните (`data/*.js`)

**`data/steps.js`** — 14 стъпки, 164 точки:
```
00 ПРЕГОВОР (15):              R.1–R.15
01 ГЕОМЕТРИЯ ОСНОВНИ (11):     1.1–1.11
02 ГЕОМЕТРИЯ НАПРЕДНАЛИ (12):  2.1–2.12
03 ТЧ ОСНОВИ (12):             3.1–3.12
04 ТЧ НАПРЕДНАЛИ (10):         4.1–4.10
05 АЛГЕБРА ПОЛИНОМИ (12):      5.1–5.12
06 АЛГЕБРА НЕРАВЕНСТВА (10):   6.1–6.10
07 ФУ И РЕДИЦИ (9):            7.1–7.9
08 КОМБИНАТОРИКА ОСНОВИ (15):  8.1–8.15
09 ГРАФИ И ИГРИ (11):          9.1–9.11
10 СМЕСЕНИ НАЦИОНАЛНИ (32):    10.1–10.32
11 БОНУС (8):                  11.1–11.8
12 АНАЛИТИЧНА И ПРОЕКТИВНА (3): 12.1–12.3
13 АДИТИВНА (4):               13.1–13.4
```

Всяка точка има:
- `id` (уникален, каноничен)
- `title` (заглавие)
- `desc` (кратко описание)
- `source` (OT_2012, BMS_2012-2015, ОИ 2026 и т.н.)
- `page` (страница в PDF)
- `explanation` (пълно обяснение / статия)
- `deepExplanation` (опционално, разширена версия за Deep Dive)
- `tasks[]` (практически задачи — за задачите по-долу)
- `bonus[]` (опционално, допълнителни ресурси — video, pdf)

**`data/plan_phases.js`** — 25-седмичен план (5 фази):
- PREP: 2 седмици (R.1-R.15)
- Region: 12 седмици (1.x, 3.x, 5.x, 6.x, 8.x, 7.5-7.6)
- National: 8 седмици (2.x, 4.x, 6.7-6.10, 7.1-7.9, 9.x, 8.9-8.14)
- IMO: 2 седмици (11.x, 12.x, 13.x)
- Simulations: 4 седмици (10.x)

**`data/tasks_data.js`** — 4 типа задачи (Parametric, Equations, Divisibility, Geometry). Всяка има: `num`, `name`, `color`, `points_on_exam`, `meta_technique`, `why`, `toolkit[]` (point IDs), `source_problems[]`.

**`data/config.js`** — AI config:
```js
window.AI_CONFIG = {
  models: [...5 модела...],
  api_url: "/api/chat",           // relative, same-origin
  api_key: "",
  model: "openai/gpt-6.1-sol",
  memory_model: "openai/gpt-6.1-sol"
};
```

### 2.2 LEVELS (roadmap)

5 нива (различни от STEPS):
- Level 0: ПРЕГОВОР (~2 седмици)
- Level 1: ОБЛАСТЕН (~12 седмици)
- Level 2: НАЦИОНАЛЕН (~8 седмици)
- Level 3: IMO/СПЕЦИАЛИЗАЦИЯ (~2 седмици)
- Level 4: СИМУЛАЦИИ (~4 седмици)

### 2.3 Режими (ModeSwitcher)

- **ABS** (absolute): показва STEPS 1:1
- **ROADMAP**: показва LEVELS с групи по теми
- **PREVIEW**: показва само Level 0 групи (Алгебра, Геометрия, ТЧ, Комбинаторика)

### 2.4 AI Tutor (`ai_assistant.js` v4)

**Persona:** Стефан Георгиев (учител, 21 години СМГ).

**Модули:**
- `AIMemory` — памет за ученика (profile, weaknesses, strengths, preferences, context)
- `AIChats` — множество чатове (pinned, archived)
- `AISettings` — модел + memory frequency (smart/close/every_n/off)
- `AIAssistant` — orchestrator

**Memory extraction:**
- Тригър при: close, context change, newchat, visibilitychange, every_n_send
- Праща последните 20 съобщения + existing memory към `memory_model`
- Връща `{facts: [{category, point_id?, note}]}`
- Few-shot правила: "Извличай САМО факти, които СА ЯВНО споменати"
- Дедупликира чрез Jaccard similarity (>0.5)

**Context injection (`getContext`):**
1. **Site overview** — 14 стъпки + 5 нива (заглавия, не съдържание)
2. **Progress** — X/164, дни до областен, текущ изглед, най-слаби 3 стъпки
3. **Current point** (ако е отворена) — title, desc, prereqs, tasks progress, deepExplanation (до 2500 chars)

**Критично:** `STEPS`, `LEVELS`, `CONFIG`, `Store`, `Stats`, `Tabs`, `PREREQS` са декларирани като `const` на top-level. `window.STEPS` е `undefined`. Затова `getContext` използва `typeof STEPS !== 'undefined'`.

**Verify Math бутон (`verifyMath()`):**
- Инжектира **пълната статия** (не truncate-ната) в system prompt
- Използва `MATH_VERIFICATION_PROMPT` с checklist (числа, substitution, цитати, edge cases)
- max_tokens: 4000, temperature: 0.1, timeout: 120s
- Връща таблица с грешки + оценка

**renderMarkdown поддържа:**
- Math protection (extract `$$...$$` и `$...$` преди markdown)
- Tables (`| ... |` + separator)
- Headers (`#` до `######`)
- Ordered/unordered lists
- Blockquotes (`>`)
- Bold/italic
- Code blocks + inline code
- Horizontal rules
- KaTeX rendering след като markdown-ът е готов

### 2.5 CSS стилове (скорошни)

- `.ai-md-table` — таблици с accent headers, zebra hover
- `.ai-suggestion-card.suggestion-special` — жълт акцент за verify бутона
- Headers, lists, blockquotes — стилизирани

---

## 3. PIPELINE — ОБЩА АРХИТЕКТУРА

```
PDF files (Задачи_Минали_Години/, Материали_БГ/, Материали_EN/)
  ↓
pdf_chunker.py — OCR + extract + merge + classify + aggregate
  ↓
generated/anchors/<point>.json — групирани по point_id
  ↓
pipeline.py — article generation + verification
  ↓
output/<point>/ — deep.md, text.md, metadata.json, verify.md
```

**State файлове (4):**
- `chunker_state.json` — extract/merge/classify/aggregate
- `state.json` — articles + budget
- `problem_state.json` — problems
- `gap_state.json` — gap analysis

**Оркестраторът** (`master_orchestrator.py`) сумира `budget.spent_usd` от всички четири.

**Бюджет:** $3/ден общо, стоп на $2.55 (85%), резерв $0.45.

---

## 4. PIPELINE — EXTRACTION (pdf_chunker.py)

### 4.1 Входни файлове

**Директории:**
- `../Задачи_Минали_Години/Областен/` — областни кръгове (OLI-2-...-XXXX-XX кл-probs.pdf и -sol.pdf)
- `../Задачи_Минали_Години/Национален/` — национални (OLI-3-...)
- `../Материали_БГ/` — български книги (OT_2010, OT_2012, BMO_1984-2006, BMS_2012-2015, BMC_2003-2006, NOM_2013, NOM_2014, NOM_2015-2016)
- `../Материали_EN/` — английски книги (book-2 до book-12, CP4, EGMO)

**Именуване (важно за parse):**
- `OLI-2-Областен кръг-2024-11 кл-probs` → base=OLI-2-Областен кръг-2024-11 кл, kind=probs
- `OLI-2-Областен кръг-2024-11 кл-sol` → base=..., kind=sol
- `OLI-2-Областен кръг-2024-11 кл-sol (1)` → variant="(1)"
- `BMO_1984-2006` → standalone, no suffix
- `OT_2012` → standalone

### 4.2 OCR (generated/cache/ocr/)

**Pipeline:**
1. Опитва директно text extraction с `pymupdf` (fitz)
2. Ако текста е < `min_text_chars_for_skip` (50 chars) на страница → OCR
3. OCR модел: `mistral-ocr-latest` през Hack Club proxy
4. Цена: $0.001/page

**Кеш структура:** `generated/cache/ocr/<safe_pdf_name>/page_001.txt`, `page_002.txt`, ...

**Забележка:** OCR cache е празен за повечето PDF-и, защото повечето имат native text. Файловете в кеша са само за сканирани PDF-и.

### 4.3 Extraction (AI)

**Модел:** `openai/gpt-oss-120b` (classify), но extraction ползва config [`generator`] по подразбиране.

**Chunking:**
- `chunk_size_pages: 8`
- `chunk_overlap_pages: 1`
- Всяка страница → text → chunk от 8 страници с 1 припокриване

**За всяка chunk:**
- Prompt: "Извлечи всички задачи от този текст. Върни JSON с problems[]"
- Всеки problem има: `num`, `grade`, `grade_range`, `year`, `round`, `statement`, `solution`, `answer`, `page`
- Валидация (`_validate_problem`):
  - statement >= 20 chars
  - solution не е None и >= 20 chars
  - Иначе се пропуска

**Изход:** `generated/cache/extracted/<safe_pdf_name>/all_problems.json`
```json
{
  "pdf": "OLI-2-Областен кръг-2024-11 кл",
  "extraction_model": "openai/gpt-oss-120b",
  "extracted_at": "...",
  "problems": [...]
}
```

### 4.4 Merge (probs + sols)

**Задача:** Свържи `-probs.pdf` (условия) с `-sol.pdf` (решения).

**Ключ:** `(grade, num)` — НЕ само `num`, защото различни класове могат да имат еднакви номера.

**Функция:** `_merge_pair(probs, sols)`
- Ако sols е празен → връща probs verbatim
- Ако probs е празен → връща sols verbatim
- Ако и двете имат — за всяка probs задача, търси sol с същия (grade, num)
- Ако няма match → запазва probs (без решение) или sol (без условие)
- Филтрира statement < 20 chars
- Dedupe: при duplicate (grade, num), предпочита този с solution

**Изход:** `generated/cache/merged/<safe_pdf_name>/all_problems.json`

### 4.5 Classification (paired)

**Задача:** За всяка задача да определи `point_id` (R.1, 1.4, 5.7 и т.н.).

**Модел:** `openai/gpt-oss-120b` (classify), цена $0.0005/call.

**Paired approach:**
- Взима списък с всички STEPS точки (164) с title + desc
- За всяка задача: prompt с "Коя точка от STEPS най-добре описва тази задача?"
- Моделът връща `matched[]` (stmt_num → sol_num → point_id), `orphan_sols_with_statement[]`, `orphan_sols_without_statement[]`, `unmatched_probs[]`

**Grade detection** (`_grade_from_filename_or_text`):
- Приоритет: `text_evidence` > `filename.grade` > `filename.grade_range` > unknown
- Text evidence: "Задача 9.6." → grade=9
- Filename "11 кл" → grade=11
- Filename "9-12 кл" → grade_range=[9,12]

**Изход:** `generated/cache/classified/<safe_pdf_name>/all_problems.json`
```json
{
  "pdf": "...",
  "classify_model": "openai/gpt-oss-120b",
  "classified_at": "...",
  "paired": true,
  "matched": N,
  "orphan_kept": M,
  "no_sol": 0,
  "dropped_unclassifiable": 0,
  "problems": [
    {
      "num": 2,
      "grade": 11,
      "point_id": "1.4",
      "statement": "...",
      "solution": "...",
      "difficulty": "medium",
      "techniques": ["power_of_point", "tangent"],
      "confidence": "exact"
    }
  ]
}
```

### 4.6 Aggregation

**Задача:** Групира всички класифицирани задачи по `point_id` в anchor файлове.

**Функция:** `run_aggregate()`
- Чете `generated/cache/classified/*/all_problems.json`
- За всяка задача с `point_id != None` → добавя към `by_point[point_id]`
- Ако `point_id is None` → `_unclassified`

**Dedupe:** по `(year, num, statement[:100])` — в рамките на един source. Не между различни PDF-и (съзнателно — една задача може да се появи в различни източници).

**Sorting:** по difficulty (easy → medium → hard), после по source.

**Изход:** `generated/anchors/<point_id_with_underscore>.json`
```json
{
  "point_id": "1.4",
  "total": 10,
  "by_difficulty": {"easy": 3, "medium": 5, "hard": 2},
  "problems": [
    {
      "source": "OT_2010, Приложения окръжност (Н. Белухов)",
      "num": 2,
      "grade": 11,
      "year": 2010,
      "statement": "...",
      "solution": "...",
      "answer": null,
      "difficulty": "medium",
      "techniques": ["power_of_point"],
      "confidence": "exact"
    }
  ]
}
```

**Текущо състояние на anchors (проверено):**
- 86 точки имат anchor файл
- **39 точки имат < 3 problems** (R.10, R.5, R.6, 1.11, 2.1, 2.2, 2.8 и т.н.) — те ще имат слаби статии
- 21 точки имат 0 anchor файл (включително **R.9** — но R.9 мина със score 7 без тях)
- Най-много: 1.5 (21), 1.10 (25), 8.1 (25), 5.11 (20), 5.1 (20)
- `.unclassified`: 56 задачи (главно от BMC_2003-2006, English books)

### 4.7 Известни проблеми с extraction/classification

1. **R.10 има само 1 anchor problem** (от ОИ 2025-11). Това не е bug — просто R.10 като тема се среща рядко.
2. **R.9 има 0 anchor problems** — но успява да напише добра статия generic.
3. **BMC_2003-2006 → 682 problems, всички без point_id** (classify failed). Те са в `.unclassified` anchor.
4. **Classify работи добре** — 3 от 4 задачи в ОИ 2025-11 са класифицирани правилно (5.1, 6.7, 5.5); само 1 е R.10.
5. **Extraction е пълен** — 4 problems от PDF = 4 в all_problems.json.

**Ключов извод:** Extraction НЕ губи данни. Classification е коректен. Проблемът е, че някои теми (R.10, R.5, R.6) имат малко задачи в източниците — това е data limitation, не bug.

---

## 5. PIPELINE — ARTICLE GENERATION (pipeline.py v7)

### 5.1 Config

```json
{
  "generator": {
    "model": "openai/gpt-6.1-sol",  // или z-ai/glm-5.3-flash
    "max_tokens": 32000,
    "temperature": 0.3,
    "reasoning_effort": null
  },
  "verifier": {
    "model": "deepseek/deepseek-v3.2",  // или z-ai/glm-5.3-flash
    "max_tokens": 12000,
    "temperature": 0.1
  },
  "daily_budget_usd": 3.0,
  "budget_stop_pct": 0.80,
  "min_verification_score": 7,
  "max_verification_retries": 2,
  "target_word_count_min": 2800,
  "target_word_count_max": 3400,
  "improve_threshold_pct": 0.3,
  "article_structure": {
    "expand_ranges": "3.1-3.6, 4.1-4.3",
    "min_words_per_section": 300,
    "total_sections": 9
  },
  "max_real_problems": 4,
  "real_problem_truncation": {"statement_chars": 600, "solution_chars": 1500}
}
```

### 5.2 Queue & pending

**Queue файл:** `queue.jsonl` — един JSON на ред.
```json
{"id": "1.4", "title": "Степен на точка", "desc": "...", "source": "OT_2010", "pdf": "Материали_БГ/OT_2010", "page": 31}
```

**Pending filter:**
- `status in ("pending", "error")`
- `not state.is_done(id)`
- `attempts < max_retries (3)`

**Sorting:** R.1 → R.15 → 1.1 → 1.15 → 2.1 → ... → 13.4

### 5.3 Prompt loading за всяка точка

`format_prompt(ARTICLE_PROMPT, ...)` подава:

| Параметър | Откъде | Пример |
|---|---|---|
| `title` | item.title | "Степен на точка" |
| `point_id` | item.id | "1.4" |
| `desc` | item.desc | "Инструмент за окръжности" |
| `prereqs` | `_load_prereqs()` — от PREREQS в index.html | "1.2, 1.5" |
| `source_problems` | `_load_source_problems()` — от item.explanation | (до 1500 chars) |
| `real_problems` | `_load_real_problems()` — от anchors/1_4.json | (до 4 примера) |
| `next_topic` | `_load_next_topic()` — следващата точка в списъка | "1.5" |

**`_load_real_problems`:**
- Чете `../generated/anchors/<point>.json`
- Валидира всяка задача с `_validate_problem` (импорт от pdf_chunker)
- Взима първите `max_real_problems` (4)
- Форматира: "Условие: [600 chars], Реално решение (ИЗПОЛЗВАЙ ГО КАТО КОПИЕ): [1500 chars]"
- Ако няма — "(няма заредени реални задачи — генерирай по темата, но маркирай ясно примерите като '**Пример (типичен, не от минала олимпиада):**')"

### 5.4 Generation

`AIClient.call(ARTICLE_WRITER, gen_user, item.id, force_json=True)`
- model: `CONFIG["generator"]["model"]`
- max_tokens: 32000 (за GLM), 64000 препоръчано за Sol
- temperature: 0.3
- timeout: 300s (трябва fix за Sol на 600s)
- force_json: True → `response_format: {type: "json_object"}`

**Очакван JSON отговор:**
```json
{
  "title": "Степен на точка",
  "article_markdown": "# Статия...\n\n## 1. Защо е важно...",
  "word_count": 3000,
  "learning_objectives": ["...", "..."],
  "common_mistakes": ["...", "..."],
  "self_quiz": [{"level": "basic", "q": "...", "a": "..."}]
}
```

**Парсване:** `_parse_json(text)` с fallback-и (markdown fences, trailing comma, prose around).

**Word count validation:**
- `min_acceptable = 2500` (config `min_word_count`)
- Ако actual_wc < 2500 → warning
- Ако > max_target + 500 → warning

### 5.5 Article structure (9 секции)

`ARTICLE_PROMPT` инструктира модела да напише 9 секции:

1. **Защо е важно** — 2-3 реални задачи с конкретни ID-та
2. **Какво ще научиш** — 3-5 измерими цели
3. **Теория** — 3.1 интуиция (пример преди формула) → 3.2 формално определение → 3.3 теореми с доказателства → 3.4 връзка с училищна математика → 3.5 множество гледни точки → 3.6 edge cases
4. **Примери с решения** — 4.1 easy (3) + CHECK → 4.2 medium (3-4) + CHECK → 4.3 hard (2-3) + CHECK. Всеки пример: "Как мисля:", "Решение:", "Забележи:".
5. **Как да разпознаеш** — 8-10 сигнала + 2-3 counterexamples
6. **Чести грешки** — 5-7, формат "как изглежда → защо е грешно → как да избегнеш"
7. **Критерии за готовност** — Easy/Medium/Hard
8. **Самооценка (Quiz)** — 5 въпроса × 5 нива (basic, edge_case, discrimination, counterexample, transfer)
9. **Върни се след 3 дни** — recap

### 5.6 Verification

`_verify(item, article_markdown)`:
- `format_prompt(ARTICLE_VERIFICATION_PROMPT, title=..., point_id=..., desc=..., article_markdown=...)`
- Model: `CONFIG["verifier"]["model"]`
- Force JSON

**Очакван JSON:**
```json
{
  "verdict": "approve|revise|reject",
  "score": 7,
  "verdict_reasoning": "Защо точно тази оценка",
  "strengths": ["...", "..."],
  "issues": [{"severity": "critical|major|minor", "section": "3.5", "description": "..."}],
  "math_errors": [{"formula": "...", "problem": "...", "fix": "..."}],
  "missing_topics": ["..."],
  "suggestions": ["..."],
  "structure_check": {"section_1_why_important": true, ...},
  "examples_check": {"real_olympiad": true, "easy_count": 3, "medium_count": 3, "hard_count": 2}
}
```

**Score interpretation:**
- `score >= 7` → approve, break retry loop
- `score < 7` → retry
- 1 грешна формула → max 3
- Нереални примери → max 5
- Само козметични → min 9

### 5.7 Retry loop

**Логика:**
```python
improve_threshold = int(min_acceptable * improve_threshold_pct)  # 2500 * 0.3 = 750
use_improve = actual_wc >= improve_threshold
```

- Ако статията е >= 750 думи → **IMPROVE** (разширяване, запазва)
- Ако е < 750 → **REGEN** (от нулата, но вижда предишната)

**IMPROVE prompt:**
- Включва предишната статия
- Feedback от verifier
- `sections_min = ceil(min_target / total_sections) = ceil(2800/9) = 312`
- Handle negative word_deficit (ако статията е > max_target)

**REGEN prompt:**
- Включва предишната статия като КОНТЕКСТ (не за копиране)
- "НЕ копирай предишната — тя е твърде кратка"
- Self-check преди връщане ("Преброй думите. Ако < 2800 — продължи")
- sections_min = 312

**Max retries:** 2 (config `max_verification_retries`)

### 5.8 Output

`output/<point_id_with_underscore>/`:
- **`text.md`** — резюме (първите 2 секции от article_markdown, чрез `_extract_summary_section`)
- **`deep.md`** — пълна статия с header (ID, дата, версия, думи, generator, verifier)
- **`metadata.json`** — title, point_id, version, word_count, learning_objectives, common_mistakes, self_quiz, generator_model, verifier_model
- **`verify.md`** — човешки четимо: verdict, score, reasoning, strengths, issues, math_errors, missing_topics, suggestions
- **`verify-v<N>.json`** — машинен с `_model` field

---

## 6. PIPELINE — PROBLEM GENERATION (problem_generator.py)

**Двуфазов:**
1. Generation: 9 problems (3 easy, 3 medium, 3 hard) по point
2. Solutions: за всяка задача, solution + answer + 3 hints

**Dual verification:**
- Verifier 1: `deepseek/deepseek-v3.2`
- Verifier 2: `openai/gpt-oss-120b`
- Ако двамата се разминават → arbiter: `openai/gpt-6.1-sol-pro`

**Output:** `pipeline/problems/<point_id>/`
- `problems.json` — id "1.4-M4", difficulty, problem, status
- `solutions.json` — solution, answer, hints[3], verified
- `verification.json` — per-num: score, can_ship, issues
- `meta.json` — models used, cost_usd, retries

**Критерии за can_ship:**
- Solvable, solution_correct, topic_match ∈ {exact, partial}
- 3 hints без да разкриват решението
- can_ship: true от dual verify (или arbiter)

---

## 7. STATE MANAGEMENT

### 7.1 state.json (articles)

```json
{
  "processed": {
    "R.1": {"status": "done", "cost": 0.0026, "tokens": 28000, "ts": 1234567890},
    "R.2": {"status": "error", "cost": 0.0, "tokens": 0, "ts": 1234567891}
  },
  "budget": {"date": "2026-10-27", "spent_usd": 0.5, "calls": 15},
  "started_at": 1234567890,
  "total_calls": 15,
  "total_cost_usd": 0.5
}
```

**Thread safety:** RLock + atomic save (tmp + replace) с retry при PermissionError.

**Reset:** `--reset-point X.Y` трие само тази точка. `--reset` трие целия файл.

### 7.2 chunker_state.json

Същата структура, но за extraction/classification етапите. Полета: `extracted`, `merged`, `classified`, `budget`.

### 7.3 Budget check

- `budget_remaining()` = `daily_budget_usd - spent_usd`
- `budget_exceeded()` = `spent_usd >= daily_budget_usd * budget_stop_pct`
- `check_budget_reset()` — ако `date != today` → reset

### 7.4 Backup стратегия

**Преди всяка destructive операция:**
```powershell
$ts = Get-Date -Format "yyyy-MM-dd_HHmmss"
New-Item -ItemType Directory -Force -Path "..\backups\$ts" | Out-Null
Copy-Item "state.json" "..\backups\$ts\state.json" -Force
Copy-Item "output" "..\backups\$ts\output" -Recurse -Force
```

**НИКОГА не трий state.json** — използвай `--reset-point`.

**НИКОГА не трий output/** — премести в `backups/`.

---

## 8. ИЗВЕСТНИ ПРОБЛЕМИ

### 8.1 Моделни ограничения

- **GLM-5.3-Flash не може доказателствена математика.** ProofBench 21%. Работи за процедурни (R.12-R.15 score 10), проваля се за доказателствени (R.1, R.10 score 4).
- **Self-verification problem.** GLM верифицира GLM → пропуска собствени грешки.
- **GLM-5.3-Flash не измисля добри примери.** R.1 има 4 реални грешки в примери.
- **Sol е 20× по-скъп.** $0.12/статия vs $0.001-0.003 за GLM.
- **Sol е бавен.** 2-4 мин/статия.

### 8.2 Конкретни грешки в R.1

- `(a+b)³ - (a-b)³ = 4ab(a²+b²)` → трябва `6a²b + 2b³`
- `(5-2)³ + (5+2)³ = 133` → трябва 370 (a=3, b=7)
- Измислени цитати "областен кръг 2018 Пловдив" (7+4)²-(7-4)²
- Edge case overclaim: "при a=b формулата се чупи" (чупи се само делението)

### 8.3 Конкретни грешки в R.10

- `MC = MD = 6` за секуща от външна точка (невъзможно)
- Централен ъгъл над AC = 90° при AM=2, MB=8, CM=4 (невъзможно)
- Грешно обяснение на ключова стъпка в Пример 7

### 8.4 Verifier failures

- **Empty response.** R.11 получи `RAW: ''` — verifier не върна нищо. Статията мина без верификация (score —, no-verify).
- **Timeout.** 300s е малко за Sol.
- **JSON parse fail.** Понякога моделът връща partial JSON.

### 8.5 Retry проблеми

- **Retry може да замени добра статия с лоша.** Ако първата е 3000 думи score 4, а retry е 500 думи score 2 — губим 3000-думната.
- **REGEN не работи за много къси статии.** R.10 с 253 думи → REGEN → 342 думи → score 2.
- **IMPROVE не работи при отрицателен word_deficit.** R.11 с 4581 думи → IMPROVE → 5118 думи (стана по-дълга).

### 8.6 SymPy verification

- **314 issues, 310 false positives.** SymPy не разбира дефиниции (`AD=CD`), верижни равенства, целочислено деление, regex-скача през редове.
- **Не е production-ready.** Само `KNOWN_WRONG` patterns са полезни (100% точни, но ниско покритие).

### 8.7 Data limitations

- **39 точки с < 3 anchor problems.** Това са теми, които рядко се срещат в източниците.
- **21 точки с 0 anchor problems.** Включително R.9, но тя успя да напише добра статия generic.
- **BMC_2003-2006 → 682 problems unclassified.** Classify моделът не успя да ги класифицира (вероятно защото са на английски).

---

## 9. ТЕКУЩО СЪСТОЯНИЕ (2026-10-27)

### 9.1 Готови статии

| Тема | Модел | Score | Проблеми |
|---|---|---|---|
| R.1 | GLM | 4 (revise) | 4 реални грешки |
| R.9 | GLM | 7 (approve) | 0 грешки |
| R.10 | GLM | 4 (revise) | 3 реални грешки |
| R.11 | GLM | — (no-verify) | 5118 думи, verifier empty |
| R.12 | GLM | 10 (approve) | процедурна |
| R.13 | GLM | 10 (approve) | процедурна |
| R.14 | GLM | 8 (revise) | процедурна |
| R.15 | GLM | 10 (approve) | процедурна |

### 9.2 Готови тестове

- `pytest` — 168 passed, 3 skipped (pure)
- Live тестове с `--run-live` — минават

### 9.3 Budget today

- Daily: $0.00 (нов ден)
- Всичко похарчено: ~$0.508 (от предишния ден)

### 9.4 Избран модел

- Generator: `z-ai/glm-5.3-flash` (предишен), ще се сменя на `openai/gpt-6.1-sol` за R.1-R.15
- Verifier: `z-ai/glm-5.3-flash` (трябва да се смени на `deepseek/deepseek-v3.2` или Sol)

### 9.5 Приложени fix-ове (в pipeline.py)

- ✅ REGEN prompt с контекст + ceil math + self-check
- ✅ IMPROVE prompt с ceil math + negative deficit handling
- ✅ load_config deep merge за всички dict ключове
- ✅ AIClient always sends reasoning_effort
- ✅ 400 handler маха response_format и reasoning_effort
- ✅ improve_threshold_pct fallback 0.3
- ✅ article_header_pattern от config
- ✅ --check-config CLI
- ✅ Retry запазва по-добрата статия (нов fix)
- ✅ Verifier retry при empty response (нов fix)
- ✅ _extract_usage fallback при липсващ cost (нов fix)
- ⏳ request_timeout_sec: 600 (трябва да се приложи)

### 9.6 Неприложени fix-ове

- `request_timeout_sec: 600` (вместо hardcoded 300)
- `cost_per_call_usd: 0.12` (вместо 0.015)
- `max_tokens: 64000` за Sol
- `KNOWN_ERRORS` в prompt (research казва: по-добре да НЕ се слага — anchoring)

---

## 10. ПЛАН ЗА ДНЕС (2026-10-27)

### 10.1 Приоритети

1. **Fix timeout + cost** в pipeline.py (преди да пуснеш Sol)
2. **Backup** на state.json и output/
3. **Тест с R.1** ($0.12) — провери quality и tracking
4. **Ако добре** → пусни R.2-R.5 ($0.48) или hybrid ($0.26)
5. **Задачите** — прескачаш за преговор

### 10.2 Cost planning

| Сценарий | Цена | Качество |
|---|---|---|
| 5 статии Sol | $0.60 | 9-10/10 |
| 5 статии hybrid | $0.26 | R.1, R.5: 9-10; R.2-R.4: 8-10 |
| 15 статии R.1-R.15 със Sol | $1.80 | 9-10/10 |
| 164 статии Sol | $19.68 | 9-10/10 |
| 164 hybrid | $10-12 | смесено |

### 10.3 Какво да НЕ правиш

- Не пипай prompts (работи за R.12-R.15)
- Не три state.json (използвай --reset-point)
- Не слагай KNOWN_ERRORS в prompt (anchoring)
- Не пускай SymPy verification (98% false positives)
- Не regen всички статии наведнъж (загубиш работещите)

---

## 11. QUICK REFERENCE

### 11.1 Commands

```powershell
# Stats
.\py.bat pipeline.py --stats

# Config
.\py.bat pipeline.py --check-config

# Generate one point
.\py.bat pipeline.py --once --no-scan --point R.1

# Generate batch
.\py.bat pipeline.py

# Tests
.\pytest.bat tests/ -v
.\pytest.bat tests/test_pipeline.py -v --run-live

# Frontend
python ai_proxy.py
```

### 11.2 Key files

| Път | Какво |
|---|---|
| `pipeline/config.json` | API keys, models, budgets |
| `pipeline/personas.py` | MASTER_PERSONA, ARTICLE_WRITER, ARTICLE_REVIEWER |
| `pipeline/prompts.py` | ARTICLE_PROMPT, ARTICLE_VERIFICATION_PROMPT |
| `pipeline/pipeline.py` | Article generation |
| `pipeline/pdf_chunker.py` | Extraction/classify/aggregate |
| `pipeline/problem_generator.py` | Problems |
| `pipeline/master_orchestrator.py` | 24/7 worker |
| `generated/anchors/*.json` | Point → real problems |
| `output/*/deep.md` | Generated articles |
| `state.json` | Processing state + budget |
| `data/steps.js` | 164 points |
| `data/plan_phases.js` | 25-week plan |
| `data/tasks_data.js` | 4 task types |
| `data/config.js` | Frontend AI config |
| `ai_assistant.js` | AI Tutor v4 |
| `ai_proxy.py` | CORS proxy |

### 11.3 Model recommendations

| Задача | Модел | Защо |
|---|---|---|
| Доказателствени статии | `gpt-6.1-sol` | 99% ProofBench |
| Процедурни статии | `glm-5.3-flash` | Достатъчно, 40× по-евтин |
| Verification (final) | `gpt-6.1-sol` | Хваща чужди грешки |
| Verification (quick) | `glm-5.3-flash` | За batch тест |
| Classification | `gpt-oss-120b` | Достатъчно |
| Arbiter | `gpt-6.1-sol-pro` | За dual verify разминаване |

---

## 12. АНТИ-ПАТЪРНИ

1. ❌ `file://` за frontend — само `http://localhost:8000`
2. ❌ `str.format()` върху промпт с LaTeX (използвай `format_prompt`)
3. ❌ Retry при HTTP 402 (BudgetExhausted → спира всичко)
4. ❌ Ръчно писане в `generated/`
5. ❌ Нов CSS файл или framework
6. ❌ `print()` в pipeline код — само `log.*`
7. ❌ Hardcode-нати модели — винаги от config
8. ❌ `--force` без backup
9. ❌ Генериране на 160 статии „да видим" — първо 1-2, после batch
10. ❌ React/Vue/Tailwind
11. ❌ `min_verification_score` под 7
12. ❌ Един verifier вместо dual (за нови задачи)
13. ❌ Игнориране на `[неразчетено]` в OCR
14. ❌ Дублиране на `MASTER_PERSONA` в нов prompt
15. ❌ `Remove-Item state.json` — използвай `--reset-point`
16. ❌ `KNOWN_ERRORS` в prompt (anchoring bias)
17. ❌ SymPy verify без ръчна проверка (98% false positives)
