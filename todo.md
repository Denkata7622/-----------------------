# 📋 TODO — Olympiad Prep

_Last updated: 2026-10-26_
_Източник: консолидация на всички идеи от разговора_

---

## 🔴 P0 — Блокери (преди всякакъв тест)

### Pipeline bugs (открити в code review)

- [ ] **1.4** Fix `state.save()` race condition — retry при `PermissionError` ✅ приложено в v6
- [ ] **1.5** Fix scan грешка (`const STEPS` в `index.html` vs `steps.js`)
- [ ] **1.6** `--point` филтър в daemon mode (не само с `--once`)
- [ ] **1.7** 402 `BudgetExhausted` спира целия run ✅ приложено в v6
- [ ] **1.8** Aggregate валидация на `point_id` срещу `steps_info` (хваща `4.13`, whitespace)
- [ ] **1.9** Aggregate трие стари anchor файлове преди rerun (идемпотентност)

### V6 code review findings

- [ ] Fix type hint на `_verify` → `tuple[Optional[dict], float]`
- [ ] `_verify` да връща `(None, 0.0)` вместо `None` при `verifier is None`
- [ ] `attempts` counter да се пази в `state.json` (за истински max 3 опита общо)
- [ ] Log файлът да се ротира при преминаване през полунощ
- [ ] Reject статии (score < 3) да не се записват като "done"

### Bug table (приоритетно)

| # | Проблем | Severity | Време |
|---|---|---|---|
| 1 | Migration не е приложен | 🔴 блокер | 5 мин |
| 2 | WinError 5 в 4 файла | 🔴 блокер | 20 мин |
| 3 | 402 не спира | 🔴 блокер | 15 мин |
| 4 | Budget подценен 17× | 🔴 блокер | 5 мин |
| 5 | Orchestrator вижда 2/4 state | 🔴 блокер | 2 мин |
| 6 | `_load_next_topic` счупен | 🟡 nuisance | 5 мин |
| 7 | `extract_css` дублира link | 🟡 cosmetic | 2 мин |
| 8 | classify модел скъп | 🟡 budget | 2 мин |

---

## 🔧 1. Pipeline bug fixes

| # | Идея | Статус |
|---|---|---|
| 1.1 | Idempotent `--classify-paired` с `--force` | ✅ |
| 1.2 | R-first sort на pending | ✅ |
| 1.3 | Deadlock fix (`Lock` → `RLock`) | ✅ v6 |
| 1.4 | Race condition в `state.save()` | ✅ v6 |
| 1.5 | Real cost от `usage.cost` (не hardcoded) | ✅ v6 |
| 1.6 | `BudgetExhausted` спира целия run | ✅ v6 |
| 1.7 | Verifier cost не се губи при JSON fail | ✅ v6 |
| 1.8 | Budget reset race в `add_cost` | ✅ v6 |
| 1.9 | Mode recalc при retry | ✅ v6 |
| 1.10 | Windows UTF-8 encoding | ✅ v6 |
| 1.11 | `_parse_json` с markdown fences + fallback | ✅ v6 |
| 1.12 | Scan грешка (`const STEPS`) | ⏳ чака |
| 1.13 | `--point` в daemon mode | ⏳ чака |
| 1.14 | Aggregate валидация на `point_id` срещу `steps_info` | ⏳ чака |
| 1.15 | Aggregate трие стари anchor файлове преди rerun | ⏳ чака |
| 1.16 | `attempts` counter да се пази между run-ове | 💡 идея |

---

## 💾 2. Data preservation

| # | Идея | Статус |
|---|---|---|
| 2.1 | Split ambiguous files (`-probs` / `-sol` отделно) | ✅ |
| 2.2 | Запази всички sub-conditions/variants (не collapse по num) | ✅ |
| 2.3 | Dedupe ключ с `pdf` в него | ✅ |
| 2.4 | Orphan handling (keep, не skip) | ✅ |
| 2.5 | Backup `extracted/` преди merge | ⏳ чака |
| 2.6 | Backup `articles/` преди регенерация | ✅ |
| 2.7 | Backup `anchors/` преди rerun | ✅ |

---

## 🎯 3. Classification improvements

| # | Идея | Статус |
|---|---|---|
| 3.1 | Paired classification (probs+sol в 1 call) | ✅ |
| 3.2 | Priority sort (11 кл областен first) | ✅ |
| 3.3 | Fix 4 класификационни грешки (2004/1, 2001/2, 2013/2, 2022/2) | ✅ |
| 3.4 | Prompt fix — класифицирай по решение, не по условие | 💡 идея |
| 3.5 | Избягване на 10.x капана | ✅ |

---

## ✅ 4. Verification / QA

| # | Идея | Статус |
|---|---|---|
| 4.1 | Daily verifier като detector (пише `reclassify.json`) | ✅ |
| 4.2 | Двустепенна верификация (120b бърз scan → Sol detailed) | 💡 идея |
| 4.3 | Очакван брой задачи в verifier (4 областен, 6 национален) | 💡 идея |
| 4.4 | probs + sol в 1 промпт за verifier | 💡 идея |
| 4.5 | Diff вместо регенерация (patches: replace/remove/add) | 💡 идея |
| 4.6 | Boolean flag "needs_change" за пестене на пари | 💡 идея |
| 4.7 | >50% patches → re-extract от нулата | 💡 идея |
| 4.8 | Pre-check скрипт (0 API) преди verifier | 💡 идея |
| 4.9 | Verifier чете PDF + OCR cache + all_problems.json | 💡 идея |
| 4.10 | Тествай verifier на 5-10 known PDF-а преди всички 190 | 💡 идея |
| 4.11 | Използвай verifier result за IMPROVE на следващия retry | ✅ v6 |

---

## 📄 5. OCR подобрения

| # | Идея | Статус |
|---|---|---|
| 5.1 | Скрипт за `[неразчетено]` detection (0 API) | 💡 идея |
| 5.2 | Re-OCR на страница при `[неразчетено]` | 💡 идея |
| 5.3 | Pre-check дали OCR cache има текста преди re-OCR | 💡 идея |
| 5.4 | Разделяне `ocr_missed` vs `extraction_missed` | 💡 идея |
| 5.5 | Re-OCR само за `ocr_missed` случаи (спестява 70%) | 💡 идея |
| 5.6 | Gemini 3.8 Flash като OCR replacement | 💡 идея |
| 5.7 | Self-host GLM-OCR Bulgarian (fine-tuned на кирилица) | 💡 идея |

> **Бележка:** `[неразчетено]` е ~95% OCR проблем, ~5% extraction. Re-OCR е правилният fix.

---

## 🤖 6. Model strategy

| # | Идея | Статус |
|---|---|---|
| 6.1 | Cheap extractor (120b) + verifier (Sol) | ✅ тествано |
| 6.2 | Тествай 120b за няколко статии преди всички | ✅ |
| 6.3 | Смени и generator, и verifier на евтини | ✅ v6 |
| 6.4 | GLM-5.3-Flash за verifier | ✅ |
| 6.5 | Gemini 3.8 Flash за generator (ако 120b се провали) | 💡 идея |
| 6.6 | GPT-6.1 Sol като fallback за generator | 💡 идея |

---

## 📝 7. Regeneration strategy (статии)

| # | Идея | Статус |
|---|---|---|
| 7.1 | Приоритетна регенерация R → 1.x → 2.x | ✅ |
| 7.2 | Контролиран тест с 4 статии | ✅ |
| 7.3 | Сравнение стара vs нова R.1 | ✅ |
| 7.4 | Clean regenerate (изтрий state, articles за приоритетните) | ✅ |
| 7.5 | R точките като теория (0 anchors е ОК) | ✅ |
| 7.6 | IMPROVE vs REGENERATE при retry | ✅ v6 |

---

## 💰 8. Cost optimization

| # | Идея | Статус |
|---|---|---|
| 8.1 | Pre-check (0 API) преди verifier | 💡 идея |
| 8.2 | Само suspicious PDF-и отиват при Sol | 💡 идея |
| 8.3 | Re-OCR само за `ocr_missed` | 💡 идея |
| 8.4 | Diff вместо full JSON | 💡 идея |
| 8.5 | Real cost от API (не hardcoded) | ✅ v6 |
| 8.6 | Един модел (120b) за generator + verifier | ✅ тествано |

---

## 📊 9. Analysis / diagnostics

| # | Идея | Статус |
|---|---|---|
| 9.1 | Проверка на EuroEval за български | ✅ |
| 9.2 | Проверка на форуми за real-world мнения | ✅ |
| 9.3 | Сравнение Sol/Luna/120b за олимпиадна математика | ✅ |
| 9.4 | Ръчна оценка на anchors | ✅ |
| 9.5 | Проверка на config / activity log | ✅ |

---

## 🌐 10. UI/UX задачи (index.html)

- [ ] Добави опции за смяна на дължината на помодоро таймер
- [ ] Оправи всички scrollbars
- [ ] Оправи font size settings
- [ ] Daily задача (от плана)
- [ ] Добави ИИ в problem log
- [ ] По-добра подредба на теми (2 начина — абсолютни теми и roadmap-like теми)
- [ ] Оправи quiz
- [ ] Автоматично категоризиране на E/M/H
- [ ] По-добър симулатор + първоначален избор м/у областен и национален + по-добър UI
- [ ] Оправи Grid enable/disable проблем
- [ ] Оправи връщането назад (разлика м/у типове действия)
- [ ] ОПРАВИ DEEPDIVE бутон
- [ ] Не затваряй settings dropdown, докато сменяш теми
- [ ] Добави Copied копче при копиране в deepdive
- [ ] Добави преговорни теми

---

## 🚀 11. Phases (P0–P6)

### 🔴 P0 — Данни (днес/утре, 1-2 часа)

- [ ] Изнеси `STEPS` от `index.html` → `data/steps.js` (`window.STEPS = [...]`)
  - 25,000 реда → отделен файл, кешира се от браузъра
  - `index.html` пада на ~5000 реда
- [ ] Изнеси `PLAN_PHASES`, `TASKS_DATA` → `data/plan.js`
- [ ] Изнеси `GENERATED_TASKS`, `REAL_PROBLEMS` → `data/generated.js` (генерира се от `integrate.py`)
- [ ] `index.html` остава с `<script src="data/steps.js"></script>` и т.н.

> **Защо първо:** Без него не можем да добавим chat (още 500+ реда в `index.html`).

### 🟡 P1 — Интеграция (тази седмица, 4-6 часа)

- [ ] `related_topics` в `SOLUTIONS_PROMPT` — 3 реда промяна
- [ ] `integrate.py` разширение:
  - Чете `problems/{id}/problems.json` + `solutions.json` → `GENERATED_TASKS`
  - Чете `real_problems/*.json` → `REAL_PROBLEMS`
  - Пише `data/generated.js`
- [ ] Modal UI за `generated_tasks`:
  - Условия + difficulty badge
  - Hints (3 бутона)
  - "Покажи решение" бутон
  - `related_topics` chips → клик отваря урок
- [ ] Sidebar collapse — бутон + `Ctrl+B` + `localStorage`

### 🟢 P2 — AI асистент (тази седмица, 2-3 часа)

- [ ] `proxy.py` — Flask proxy (40 реда)
- [ ] `.env.example` — `AI_API_KEY=sk-hc-v1-...`
- [ ] Chat widget в Modal — JS + CSS (~200 реда)
- [ ] Context-aware — point + problem + solution в system prompt
- [ ] History persist в `localStorage` (да не се губи при reload)
- [ ] Тест — питаш "не разбирам стъпка 2" → contextual отговор

### 🔵 P3 — Site polish (следваща седмица)

- [ ] PLAN view redesign — timeline + "Today" marker + progress per phase
- [ ] `.gitignore` — PDF-и, `data/`, API keys
- [ ] `LICENSE` — GPLv3 (изискване на НОИТ)

### ⚪ P4 — Съдържание (следваща седмица)

- [ ] Пусни `pipeline.py --limit 20` (20 статии)
- [ ] Пусни `problem_generator.py --limit 5` (5 точки за тест)
- [ ] Ако 5/5 са ≥10/12 shipped → пусни всички 160

### ⚫ P5 — Автоматизация (след това)

- [ ] Vision fallback за 49 сканирани PDF-а (+150 anchors)
- [ ] Merge fix (104 загубени задачи)
- [ ] `gap_worker.py` rewrite (plan-aware)
- [ ] `master_orchestrator.py` + `daily_verifier.py` (автоматизация)

### 🏆 P6 — Конкурс (по-късно)

- [ ] `README.md`, `ARCHITECTURE.md`
- [ ] GitHub repo + Vercel deploy
- [ ] Документация по шаблона на МОН
- [ ] Demo video / screenshots

---

## 📁 12. Нови файлове

| Файл | Редове | Отговорност |
|---|---|---|
| `data/priorities.js` | 60 | 2 нива × 4 tasks × toolkit |
| `pipeline/plan.py` | 220 | Парсва 4 data файла; 8 API функции; cache |
| `pipeline/point_status.py` | 150 | Чете/пише `generated/status/<point>.json` |
| `tests/test_plan.py` | 180 | 25 unit теста (без API) |
| `tests/test_point_status.py` | 100 | 10 unit теста |

---

## 🔨 13. Модификации (патчове, не rewrite)

| Файл | Редове промяна | Какво |
|---|---|---|
| `pipeline.py` | +80 | `--task`, `--level`, `--priority auto` |
| `daily_verifier.py` | +120 | `audit_task_completion()`, чете `plan.py`, пише `point_status` |
| `master_orchestrator.py` | +40 | Преди extract: чете `plan.get_current_focus()`; след aggregate: `pipeline --priority auto` |
| `pdf_chunker.py` | +15 | `load_steps_info()` → `plan.get_all_points()` |
| `problem_generator.py` | +20 | Същото + `--priority auto` |
| `index.html` | +3 | `<script src="data/priorities.js"></script>` |

---

## 📊 Обобщение

| Категория | Общо | ✅ | ⏳ | 💡 |
|---|---|---|---|---|
| 1. Pipeline fixes | 16 | 12 | 2 | 2 |
| 2. Data preservation | 7 | 5 | 1 | 1 |
| 3. Classification | 5 | 4 | 0 | 1 |
| 4. Verification/QA | 11 | 2 | 0 | 9 |
| 5. OCR | 7 | 0 | 0 | 7 |
| 6. Model strategy | 6 | 4 | 0 | 2 |
| 7. Regeneration | 6 | 6 | 0 | 0 |
| 8. Cost optimization | 6 | 2 | 0 | 4 |
| 9. Analysis | 5 | 5 | 0 | 0 |
| 10. UI/UX | 15 | 0 | 0 | 15 |
| 11. P0–P6 Phases | 26 | 0 | 0 | 26 |
| **Общо** | **110** | **40** | **3** | **67** |

---

## 🎯 Следващи стъпки (в ред)

1. **Тествай v6** с 4 R статии (~$0.01)
2. **Прочети `verify.md` за R.8** (score 2 при 3295 думи) — защо verifier-ът отхвърля?
3. **Ако 120b се провали → Gemini 3.8 Flash** за generator (~$0.03/статия)
4. **P0 Data refactor** — изнеси STEPS/PLAN/GENERATED от `index.html`
5. **Verifier идеите (#4)** — очакван брой + diff + boolean flag
6. **OCR re-processing** — само за `[неразчетено]` случаи

Phase 2 — Премахване на integrate.py (утре/вдругиден)
Цел: index.html да е Jinja2 шаблон, който Flask сервира динамично.

Какво се променя:

index.html → templates/index.html.j2

serve.py има route / който рендерира шаблона с данните от articles/

integrate.py се изтрива

При всяка нова статия → нищо не правиш, просто отваряш сайта

Цена: ~2-3 часа работа (заради 164 теми и текущия дизайн на index.html).

Кажи ми кога си готов и ще го направим стъпка по стъпка.

Phase 3 — Interactive Controls (след седмица)
От dashboard-а:

Start/Stop pipeline бутони

Retry конкретна тема (без CLI)

Re-extract anchors от PDF

Live logs stream (WebSocket)

Cost breakdown по ден/модел/тема

Това е "професионален dashboard" — но изисква още работа.