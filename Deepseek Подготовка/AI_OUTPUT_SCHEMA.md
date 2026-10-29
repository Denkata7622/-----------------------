# OUTPUT SCHEMA — какъв формат искам
# Version: 3.0

---

## ⚠️ ОБЩИ ПРАВИЛА

1. **Никакви обяснения извън посочените блокове.**
2. **Точен JS синтаксис** — кавички, запетаи, скоби.
3. **Ако нещо липсва** — `null` + `// CHECK`.
4. **Всички текстове на български** (освен части от EN книги).
5. **Всеки отговор завършва с RECOMMENDED CHANGES.**
6. **Извличай `knowledge_requirements` за всяка задача** — задължително!

---

## БЛОК 1: КНИГА

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-1.pdf",
  title: "Problem-Solving Strategies",
  author: "Arthur Engel",
  year: 1997,
  language: "EN",
  total_pages: 403,
  topics: ["Algebra", "Number Theory", "Geometry", "Combinatorics"],
  structure: [
    { 
      chapter: "Ch 1", 
      title: "Invariants", 
      pages: "1-45", 
      plan_step: 9, 
      plan_points: ["9.8"],
      priority_regional: "low",
      priority_national: "high"
    }
    // ... всички глави
  ],
  duplicates: ["book-3 (1).pdf"],  // само ако е същата книга
  is_duplicate_of: null,
  recommended_action: "add-as-step12" | "add-as-bonus" | "add-as-specific-points" | "skip",
  best_mapping: [
    { step_id: 3, point_ids: ["3.3","3.4"], chapters: ["Ch 4"], pages: "113-145" },
    { step_id: 6, point_ids: ["6.1","6.4"], chapters: ["Ch 7-8"], pages: "180-260" }
  ]
}
```

---

## БЛОК 2: ЗАДАЧИ (минали олимпиади) — РАЗШИРЕН

**Винаги връщай отделен блок за 10. и 11. клас.**

```js
// ─── ЗАДАЧИ: {ГОДИНА}-{КЛАС} ───
{
  source_pdf_probs: "Задачи_Минали_Години/OLI-2-Областен кръг-2023-11 кл-probs.pdf",
  source_pdf_sols:  "Задачи_Минали_Години/OLI-2-Областен кръг-2023-11 кл-sol.pdf",
  year: 2023,
  grade: 11,
  exam_type: "областен",
  problems: [
    {
      num: 1,
      // ─── БАЗА ───
      topic: "ТЧ",
      subtopic: "Сравнения по модул",
      difficulty: 3,                  // 1-5
      probs_page: 1,
      sol_page: 3,
      summary: "Да се докаже, че 2^n + 1 не се дели на 7 за никое n.",
      
      // ─── MAP КЪМ ПЛАНА ───
      plan_step: 3,
      plan_point: "3.2",
      related_points: ["3.3", "3.4"],
      prerequisites: ["3.1", "3.2"],
      add_as_task_to: ["3.2", "3.3"],
      
      // ─── ⭐ KNOWLEDGE REQUIREMENTS ───
      required_knowledge: [
        { point_id: "3.2", technique: "Сравнения mod 7", 
          why_needed: "Ядро на доказателството" },
        { point_id: "3.3", technique: "Малка теорема на Ферма", 
          why_needed: "За цикличности на степените" },
        { point_id: null, technique: "Теорема на Дирихле за прости", 
          why_needed: "Не е нужно, но помага за обобщение" }
      ],
      techniques_not_in_plan: [],  // само реално липсващи
      gap_severity: "none",        // none | minor | major
      
      // ─── ПРАКТИЧЕСКО ───
      estimated_time_minutes: 30,
      common_pitfalls: "Учениците забравят да проверят всички случаи mod 7.",
      recommended_for_simulation: true,
      prerequisite_review: "Преговори 3.2 и 3.3 преди да опиташ."
    }
    // ... всички задачи
  ],
  difficulty_distribution: { easy: 1, medium: 3, hard: 2 },
  recommended_action: "add-to-step10" | "add-to-specific-points" | "use-for-simulation",
  recommended_for_simulation: [1, 4, 6]
}
```

### ⭐ Quality checklist (провери преди да върнеш)

- [ ] Всички задачи от PDF-а са включени
- [ ] 10. и 11. клас са отделни блокове
- [ ] `difficulty` е 1–5
- [ ] `topic` е от: `Геометрия | ТЧ | Алгебра | Комбинаторика`
- [ ] `probs_page`/`sol_page` са реални PDF страници
- [ ] `prerequisites` е само ID-та от списъка с 100+ точки
- [ ] `required_knowledge` е попълнен за **всяка** задача
- [ ] `techniques_not_in_plan` не е празен, ако има такива
- [ ] `gap_severity` е none | minor | major
- [ ] `recommended_for_simulation` съдържа точно 3 номера (11 кл.)

---

## БЛОК 2.5: KNOWLEDGE PROFILE ЗА ГОДИНАТА ⭐

**Нов задължителен блок след всяка година.**

```js
// ─── KNOWLEDGE PROFILE: {ГОДИНА} ───
{
  year: 2023,
  total_problems_analyzed: 12,   // 10 кл + 11 кл
  most_used_points: [
    { point_id: "1.1", count: 3, examples: [1, 4, 6] },
    { point_id: "3.2", count: 2, examples: [2, 5] },
    { point_id: "6.4", count: 1, examples: [7] }
  ],
  techniques_used: [
    "Менелай", "Чева", "Сравнения mod p", 
    "Коши-Буняковски", "Дирихле"
  ],
  gaps_identified: [
    { 
      technique: "Полярно преобразувание", 
      appeared_in: ["11 кл зад 3"], 
      recommendation: "Добави нова точка 2.9 'Полярно преобразувание'" 
    }
  ],
  study_priority: [
    "1.1 — Менелай (3 задачи)",
    "3.2 — Сравнения (2 задачи)",
    "1.4 — Радикална ос (2 задачи)"
  ],
  summary: "Тази година доминираха геометрия (3 задачи) и ТЧ (2). Липсваща техника: полярно преобразувание."
}
```

### Quality checklist за profile:
- [ ] `most_used_points` включва само реални точки
- [ ] `gaps_identified` не е празен, ако има такива
- [ ] `study_priority` подреден по важност (count descending)
- [ ] `summary` в 1–2 изречения

---

## БЛОК 3: НОВА ТОЧКА (готова за copy-paste)

```js
{ 
  id: "12.1", 
  title: "Заглавие на български",
  desc: "1 изречение описание",
  source: "Evan Chen, Euclidean Geometry in Mathematical Olympiads, Ch 6",
  pdf: "Материали_EN/book-4",
  page: 113,
  problems_page: 133,
  solutions_page: null,
  tasks: [
    { 
      label: "Example 6.26 (USA TSTST 2013/1)", 
      pdf: "Материали_EN/book-4", 
      page: 110,
      difficulty: 5,
      requires_also: ["12.1"],
      prerequisite_review: "Преговори 12.1 преди да опиташ"
    }
  ],
  bonus: [
    { label: "Hints to Ch 6 problems", pdf: "Материали_EN/book-4", page: 238 }
  ],
  explanation: "ФОРМУЛИРОВКА: ...\n\nКОГА: ...\n\nСВОЙСТВА: ...\n\nТРИК: ..."
}
```

### Валидация
- `id` е нов
- `pdf` без `.pdf`
- `explanation` използва `\n\n` (не реални нови редове)
- Всички кавички са единични

---

## БЛОК 4: АКТУАЛИЗАЦИЯ НА СЪЩЕСТВУВАЩА ТОЧКА

```js
// ─── АКТУАЛИЗАЦИЯ ───

// Точка 1.3 в STEPS[0].points:
{ id: "1.3",
  page: 81,                         // ако се променя
  problems_page: 98,
  tasks: [                          // нови задачи от минали олимпиади
    { 
      label: "ОИ 2023/11 кл, Зад 1 (Птолемей)", 
      pdf: "Задачи_Минали_Години/OLI-2-Областен кръг-2023-11 кл-probs",
      page: 1,
      difficulty: 3,
      requires_also: ["1.6"],
      prerequisite_review: "Преговори 1.5 и 1.6"
    }
  ],
  bonus: [
    { label: "Ptolemy's Theorem (book-4 Ch 5.4)", pdf: "Материали_EN/book-4", page: 81 }
  ]
}
```

### Валидация
- НЕ включвай полета, които не се променят
- НЕ дублирай `title`, `desc`, `source`
- Ако само `tasks` → не пиши `page`

---

## БЛОК 5: RECOMMENDED CHANGES (задължителен)

```markdown
### RECOMMENDED CHANGES TO index.html

**В STEPS:**
- [ ] Промяна в `STEPS[0].points[2]` (Точка 1.3): нов `bonus`
- [ ] Добавяне на нови `tasks` в точки 1.1, 1.4, 3.2
- [ ] Създаване на нова точка `12.1` в нов масив `STEPS[11]`

**В PLAN_PHASES:**
- [ ] Обновяване на Week 16: "Симулация ОИ 2023"

**Друго:**
- [ ] Трия `book-3 (3).pdf`, `book-3 (4).pdf` — дубликати
- [ ] Идентифицирани gaps: полярно преобразувание (major)
```

---

## СПЕЦИАЛНИ СЛУЧАИ

### Случай A: Сборник без отделни решения
```js
{ solutions_page: null,  // CHECK: вградени в текста
  problems_page: page }
```

### Случай B: Материал без 11. клас
```js
{ grade: 10,
  problems: [/* ... */],
  note_for_11th_grade: "Всички задачи са подходящи за 11. клас" }
```

### Случай C: Дубликат
```js
{ file: "Материали_EN/book-3 (3).pdf",
  is_duplicate_of: "book-3 (2).pdf",
  recommended_action: "delete" }
```

### Случай D: Материал, който не се вписва в 12 стъпки
```js
{ 
  file: "...",
  does_not_fit: true,
  reason: "Темата е 'Complex analysis' — няма такава стъпка",
  suggested_new_step: {
    num: 13,
    title: "COMPLEX ANALYSIS",
    scope: "..."
  }
}
```

### Случай E: Техника, липсваща в плана ⭐
```js
{ 
  technique: "Полярно преобразувание",
  appeared_in: ["11 кл зад 3", "10 кл зад 5"],
  frequency: 2,
  gap_severity: "major",
  suggested_mapping: {
    step_id: 2,
    new_point: "2.9",
    title: "Полярно преобразувание",
    scope: "Преобразуване, което изпраща прави в окръжности през центъра"
  }
}
```

---

## ФИНАЛНА САМОПРОВЕРКА

Преди да върнеш:

- [ ] Всички ID-та съществуват в 100+ точки
- [ ] Няма markdown обяснения около JS
- [ ] RECOMMENDED CHANGES е в края
- [ ] Всички страници са PDF (не печатни)
- [ ] `null` за липсващи полета
- [ ] JS синтаксис валиден
- [ ] Няма добавени нови полета извън схемата
- [ ] `knowledge_requirements` е попълнен за всяка задача ⭐
- [ ] `KNOWLEDGE PROFILE` е попълнен за всяка година ⭐
- [ ] `techniques_not_in_plan` не е празно при нужда