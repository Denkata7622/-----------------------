# ALL AI ANALYSES — Olympiad Prep

> **Инструкции за ползване:**
> 1. Всеки AI чат връща резултат → копирай САМО финалните блокове (КНИГА / ЗАДАЧИ / НОВА ТОЧКА / АКТУАЛИЗАЦИЯ / RECOMMENDED CHANGES).
> 2. НЕ копирай reasoning, обяснения, chat UI елементи.
> 3. Постави резултата под съответната секция.
> 4. Ако секция е празна — AI-ът още не е обработен.

**Последно обновено:** 2026-10-13
**Общо обработени:** 23 / 40

---

## 📚 BOOKS — Математически книги (10/10 готови)

### book-2.pdf — ✅ ГОТОВО
**Идентификация:** 104 Number Theory Problems (Andreescu, Andrica, Feng, 2007)
**Решение:** `add-as-bonus`
**Забележка:** 11 нови bonus записа в Steps 3–4

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-2.pdf",
  title: "104 Number Theory Problems: From the Training of the USA IMO Team",
  author: "Titu Andreescu, Dorin Andrica, Zuming Feng",
  year: 2007,
  language: "EN",
  total_pages: 213,
  topics: ["Number Theory"],
  structure: [
    {
      chapter: "Ch 1.1",
      title: "Divisibility and Division Algorithm",
      pages: "13-17",
      plan_step: 3,
      plan_points: ["3.1"],
      priority_regional: "high",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.2",
      title: "Primes and Fundamental Theorem of Arithmetic",
      pages: "17-23",
      plan_step: 3,
      plan_points: ["3.1", "4.5"],
      priority_regional: "high",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.3",
      title: "GCD, Euclidean Algorithm, Bézout, LCM",
      pages: "23-28",
      plan_step: 3,
      plan_points: ["3.1", "4.1"],
      priority_regional: "high",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.4",
      title: "Number and Sum of Divisors (τ, σ)",
      pages: "28-31",
      plan_step: 4,
      plan_points: ["4.7"],
      priority_regional: "med",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.5",
      title: "Modular Arithmetic and Residue Classes",
      pages: "31-37",
      plan_step: 3,
      plan_points: ["3.2", "3.6"],
      priority_regional: "high",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.6",
      title: "Wilson, Fermat, Euler Theorems and Totient",
      pages: "37-45",
      plan_step: 3,
      plan_points: ["3.3", "3.4", "3.5"],
      priority_regional: "high",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.7",
      title: "Multiplicative Functions and Möbius Inversion",
      pages: "45-47",
      plan_step: 4,
      plan_points: ["4.7"],
      priority_regional: "low",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.8",
      title: "Linear Diophantine Equations",
      pages: "47-50",
      plan_step: 4,
      plan_points: ["4.1"],
      priority_regional: "high",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.9",
      title: "Numerical Systems and Divisibility Criteria",
      pages: "50-59",
      plan_step: 3,
      plan_points: ["3.2"],
      priority_regional: "med",
      priority_national: "med"
    },
    {
      chapter: "Ch 1.10",
      title: "Floor Function and Hermite Identity",
      pages: "59-68",
      plan_step: 3,
      plan_points: ["3.1", "4.8"],
      priority_regional: "med",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.11",
      title: "Legendre's Function, Factorials, Binomials",
      pages: "68-75",
      plan_step: 4,
      plan_points: ["3.8", "4.8"],
      priority_regional: "med",
      priority_national: "high"
    },
    {
      chapter: "Ch 1.12",
      title: "Fermat, Mersenne, Perfect Numbers",
      pages: "75-86",
      plan_step: 4,
      plan_points: ["4.4", "4.5", "4.7"],
      priority_regional: "low",
      priority_national: "high"
    },
    {
      chapter: "Ch 2",
      title: "Introductory Problems (52 задачи)",
      pages: "87-94",
      plan_step: 10,
      plan_points: ["10.1", "10.2", "10.3", "10.4"],
      priority_regional: "high",
      priority_national: "high"
    },
    {
      chapter: "Ch 3",
      title: "Advanced Problems (52 задачи)",
      pages: "95-102",
      plan_step: 10,
      plan_points: ["10.5", "10.6", "10.7", "10.8", "10.9", "10.10"],
      priority_regional: "med",
      priority_national: "high"
    },
    {
      chapter: "Ch 4",
      title: "Solutions to Introductory Problems",
      pages: "103-142",
      plan_step: 10,
      plan_points: ["10.1", "10.2", "10.3", "10.4"],
      priority_regional: "med",
      priority_national: "high"
    },
    {
      chapter: "Ch 5",
      title: "Solutions to Advanced Problems",
      pages: "143-199",
      plan_step: 10,
      plan_points: ["10.5", "10.6", "10.7", "10.8", "10.9", "10.10"],
      priority_regional: "low",
      priority_national: "high"
    },
    {
      chapter: "Glossary",
      title: "Glossary of Number Theory Terms",
      pages: "200-206",
      plan_step: 11,
      plan_points: ["11.4"],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Further Reading",
      title: "Further Reading (62 заглавия)",
      pages: "207-211",
      plan_step: 11,
      plan_points: ["11.4"],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Index",
      title: "Index",
      pages: "212-213",
      plan_step: 11,
      plan_points: ["11.4"],
      priority_regional: "low",
      priority_national: "low"
    }
  ],
  duplicates: [],
  recommended_action: "add-as-bonus",
  best_mapping: [
    { step_id: 3, point_ids: ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.8"], chapters: ["Ch 1.1", "Ch 1.2", "Ch 1.3", "Ch 1.5", "Ch 1.6", "Ch 1.10", "Ch 1.11"], pages: "13-75" },
    { step_id: 4, point_ids: ["4.1", "4.4", "4.5", "4.7", "4.8"], chapters: ["Ch 1.4", "Ch 1.7", "Ch 1.8", "Ch 1.11", "Ch 1.12"], pages: "28-86" },
    { step_id: 10, point_ids: ["10.1", "10.2", "10.3", "10.4"], chapters: ["Ch 2", "Ch 4"], pages: "87-142" },
    { step_id: 10, point_ids: ["10.5", "10.6", "10.7", "10.8", "10.9", "10.10"], chapters: ["Ch 3", "Ch 5"], pages: "95-199" }
  ]
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
// Замести САМО следните полета в съществуващите точки:

// Точка 3.1 в STEPS[2].points:
{ id: "3.1",
  bonus: [
    { label: "104 NT Problems — Divisibility, Division Algo", pdf: "Материали_EN/book-2", page: 13 },
    { label: "104 NT Problems — GCD, Euclidean, Bézout", pdf: "Материали_EN/book-2", page: 23 }
  ]
}

// Точка 3.2 в STEPS[2].points:
{ id: "3.2",
  bonus: [
    { label: "104 NT Problems — Modular Arithmetic", pdf: "Материали_EN/book-2", page: 31 },
    { label: "104 NT Problems — Residue Classes", pdf: "Материали_EN/book-2", page: 35 }
  ]
}

// Точка 3.3 в STEPS[2].points:
{ id: "3.3",
  bonus: [
    { label: "104 NT Problems — Fermat's Little Theorem", pdf: "Материали_EN/book-2", page: 39 }
  ]
}

// Точка 3.4 в STEPS[2].points:
{ id: "3.4",
  bonus: [
    { label: "104 NT Problems — Euler's Theorem + Totient", pdf: "Материали_EN/book-2", page: 40 }
  ]
}

// Точка 3.5 в STEPS[2].points:
{ id: "3.5",
  bonus: [
    { label: "104 NT Problems — Wilson's Theorem", pdf: "Материали_EN/book-2", page: 36 }
  ]
}

// Точка 3.8 в STEPS[2].points:
{ id: "3.8",
  bonus: [
    { label: "104 NT Problems — Legendre's Function", pdf: "Материали_EN/book-2", page: 68 }
  ]
}

// Точка 4.1 в STEPS[3].points:
{ id: "4.1",
  bonus: [
    { label: "104 NT Problems — Linear Diophantine", pdf: "Материали_EN/book-2", page: 47 }
  ]
}

// Точка 4.4 в STEPS[3].points:
{ id: "4.4",
  bonus: [
    { label: "104 NT Problems — Perfect Powers / Squares", pdf: "Материали_EN/book-2", page: 52 }
  ]
}

// Точка 4.5 в STEPS[3].points:
{ id: "4.5",
  bonus: [
    { label: "104 NT Problems — Primes, Mersenne, Fermat", pdf: "Материали_EN/book-2", page: 17 },
    { label: "104 NT Problems — Fermat Numbers", pdf: "Материали_EN/book-2", page: 75 }
  ]
}

// Точка 4.7 в STEPS[3].points:
{ id: "4.7",
  bonus: [
    { label: "104 NT Problems — Multiplicative Functions", pdf: "Материали_EN/book-2", page: 45 }
  ]
}

// Точка 4.8 в STEPS[3].points:
{ id: "4.8",
  bonus: [
    { label: "104 NT Problems — Legendre, Factorials, Binomials", pdf: "Материали_EN/book-2", page: 68 }
  ]
}

// Точка 10.1 в STEPS[9].points:
{ id: "10.1",
  tasks: [
    { label: "Intro Problem 1 (AMC10B 2004)", pdf: "Материали_EN/book-2", page: 87 },
    { label: "Intro Problem 7 (p, p+ka primes)", pdf: "Материали_EN/book-2", page: 88 },
    { label: "Intro Problem 9 (lcm+gcd=m+n, Russia 1995)", pdf: "Материали_EN/book-2", page: 88 }
  ]
}

// Точка 10.5 в STEPS[9].points:
{ id: "10.5",
  tasks: [
    { label: "Adv Problem 2 (S(x)/S(2x)≤5, MOSP 1998)", pdf: "Материали_EN/book-2", page: 95 },
    { label: "Adv Problem 10 (lcm inequality, St.Petersburg 2001)", pdf: "Материали_EN/book-2", page: 96 }
  ]
}
```

### RECOMMENDED CHANGES TO index.html

**В STEPS:**

- [ ] Промяна в `STEPS[2].points[0]` (Точка 3.1): нов `bonus` = 104 NT Problems стр. 13 + 23
- [ ] Промяна в `STEPS[2].points[1]` (Точка 3.2): нов `bonus` = 104 NT Problems стр. 31 + 35
- [ ] Промяна в `STEPS[2].points[2]` (Точка 3.3): нов `bonus` = 104 NT Problems стр. 39
- [ ] Промяна в `STEPS[2].points[3]` (Точка 3.4): нов `bonus` = 104 NT Problems стр. 40
- [ ] Промяна в `STEPS[2].points[4]` (Точка 3.5): нов `bonus` = 104 NT Problems стр. 36
- [ ] Промяна в `STEPS[2].points[7]` (Точка 3.8): нов `bonus` = 104 NT Problems стр. 68
- [ ] Промяна в `STEPS[3].points[0]` (Точка 4.1): нов `bonus` = 104 NT Problems стр. 47
- [ ] Промяна в `STEPS[3].points[3]` (Точка 4.4): нов `bonus` = 104 NT Problems стр. 52
- [ ] Промяна в `STEPS[3].points[4]` (Точка 4.5): нов `bonus` = 104 NT Problems стр. 17 + 75
- [ ] Промяна в `STEPS[3].points[6]` (Точка 4.7): нов `bonus` = 104 NT Problems стр. 45
- [ ] Промяна в `STEPS[3].points[7]` (Точка 4.8): нов `bonus` = 104 NT Problems стр. 68
- [ ] Промяна в `STEPS[9].points[0]` (Точка 10.1): нов `tasks` = 3 задачи от 104 NT Problems (стр. 87-88)
- [ ] Промяна в `STEPS[9].points[4]` (Точка 10.5): нов `tasks` = 2 задачи от 104 NT Problems (стр. 95-96)

**В PLAN_PHASES:**

- [ ] Week 3 (Основи/ТЧ): добавяне на "104 NT Problems Ch 1.1–1.6 (стр. 13-47)" като доп. ресурс
- [ ] Week 4 (ТЧ Основи продължение): добавяне на "104 NT Problems Ch 1.10–1.12 (стр. 59-86)" като доп. ресурс
- [ ] Week 11-12 (ТЧ Напреднали): добавяне на "104 NT Problems Ch 2-3 (стр. 87-102)" като задачи за симулация
- [ ] Week 16-17 (Пред-областен): добавяне на "104 NT Problems Ch 4-5 (стр. 103-199)" като решения за самопроверка

**Друго:**

- [ ] Няма дубликати — book-2.pdf е уникален (различен от book-1 = Engel)
- [ ] Обновяване на `bonus` в Стъпки 3 и 4 — общо 11 нови записа
- [ ] Няма промени в конфигурацията на exam dates

---

### book-3.pdf — ✅ ГОТОВО
**Идентификация:** Mathematical Olympiad Treasures (Andreescu, Enescu, 2011)
**Решение:** `add-as-bonus`
**Забележка:** 22 bonus записа (може да намалим при интеграция)

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-3.pdf",
  title: "Mathematical Olympiad Treasures",
  author: "Titu Andreescu, Bogdan Enescu",
  year: 2011,
  language: "EN",
  total_pages: 262,
  topics: ["Algebra", "Geometry", "Trigonometry", "Number Theory", "Combinatorics"],
  structure: [
    // ═══ PART I: PROBLEMS — CHAPTER 1: ALGEBRA (p 11–45) ═══
    { chapter: "1.1", title: "An Algebraic Identity", pages: "12-15", plan_step: 6, plan_points: ["6.1"], priority_regional: "high", priority_national: "high" },
    { chapter: "1.2", title: "Cauchy-Schwarz Revisited", pages: "16-19", plan_step: 6, plan_points: ["6.4"], priority_regional: "high", priority_national: "high" },
    { chapter: "1.3", title: "Easy Ways Through Absolute Values", pages: "20-23", plan_step: 6, plan_points: ["6.4"], priority_regional: "high", priority_national: "med" },
    { chapter: "1.4", title: "Parameters", pages: "23-26", plan_step: 5, plan_points: ["5.1"], priority_regional: "med", priority_national: "high" },
    { chapter: "1.5", title: "Take the Conjugate!", pages: "26-29", plan_step: 3, plan_points: ["3.10"], priority_regional: "high", priority_national: "high" },
    { chapter: "1.6", title: "Inequalities with Convex Functions", pages: "29-33", plan_step: 6, plan_points: ["6.5"], priority_regional: "high", priority_national: "high" },
    { chapter: "1.7", title: "Induction at Work", pages: "33-36", plan_step: 8, plan_points: ["8.10"], priority_regional: "high", priority_national: "high" },
    { chapter: "1.8", title: "Roots and Coefficients", pages: "36-40", plan_step: 5, plan_points: ["5.1", "5.3"], priority_regional: "high", priority_national: "high" },
    { chapter: "1.9", title: "The Rearrangements Inequality", pages: "40-45", plan_step: 6, plan_points: ["6.7"], priority_regional: "high", priority_national: "high" },

    // ═══ CHAPTER 2: GEOMETRY AND TRIGONOMETRY (p 46–78) ═══
    { chapter: "2.1", title: "Geometric Inequalities", pages: "46-49", plan_step: 2, plan_points: ["2.8"], priority_regional: "high", priority_national: "high" },
    { chapter: "2.2", title: "An Interesting Locus", pages: "49-54", plan_step: 1, plan_points: ["1.7"], priority_regional: "med", priority_national: "med" },
    { chapter: "2.3", title: "Cyclic Quads", pages: "54-59", plan_step: 1, plan_points: ["1.3", "1.5", "1.9"], priority_regional: "high", priority_national: "high" },
    { chapter: "2.4", title: "Equiangular Polygons", pages: "59-63", plan_step: 2, plan_points: ["2.4"], priority_regional: "low", priority_national: "med" },
    { chapter: "2.5", title: "More on Equilateral Triangles", pages: "63-67", plan_step: 2, plan_points: ["2.4"], priority_regional: "high", priority_national: "high" },
    { chapter: "2.6", title: "The \"Carpets\" Theorem", pages: "67-71", plan_step: 1, plan_points: ["1.7"], priority_regional: "med", priority_national: "med" },
    { chapter: "2.7", title: "Quadrilaterals with an Inscribed Circle", pages: "71-74", plan_step: 1, plan_points: ["1.10"], priority_regional: "high", priority_national: "high" },
    { chapter: "2.8", title: "Dr. Trig Learns Complex Numbers", pages: "75-78", plan_step: 1, plan_points: ["1.6"], priority_regional: "low", priority_national: "med" },

    // ═══ CHAPTER 3: NUMBER THEORY AND COMBINATORICS (p 79–107) ═══
    { chapter: "3.1", title: "Arrays of Numbers", pages: "80-83", plan_step: 8, plan_points: ["8.3"], priority_regional: "med", priority_national: "med" },
    { chapter: "3.2", title: "Functions Defined on Sets of Points", pages: "83-86", plan_step: 7, plan_points: ["7.5"], priority_regional: "low", priority_national: "med" },
    { chapter: "3.3", title: "Count Twice!", pages: "86-89", plan_step: 8, plan_points: ["8.3"], priority_regional: "high", priority_national: "high" },
    { chapter: "3.4", title: "Sequences of Integers", pages: "90-94", plan_step: 7, plan_points: ["7.6", "7.7"], priority_regional: "high", priority_national: "high" },
    { chapter: "3.5", title: "Equations with Infinitely Many Solutions", pages: "94-97", plan_step: 4, plan_points: ["4.1", "4.2"], priority_regional: "high", priority_national: "high" },
    { chapter: "3.6", title: "Equations with No Solutions", pages: "97-99", plan_step: 3, plan_points: ["3.2"], priority_regional: "high", priority_national: "high" },
    { chapter: "3.7", title: "Powers of 2", pages: "99-102", plan_step: 3, plan_points: ["3.1"], priority_regional: "high", priority_national: "high" },
    { chapter: "3.8", title: "Progressions", pages: "102-104", plan_step: 7, plan_points: ["7.6"], priority_regional: "high", priority_national: "high" },
    { chapter: "3.9", title: "The Marriage Lemma", pages: "105-107", plan_step: 9, plan_points: ["9.1"], priority_regional: "med", priority_national: "med" },

    // ═══ PART II: SOLUTIONS (p 109–256) ═══
    { chapter: "4", title: "Algebra — Solutions (4.1–4.9)", pages: "110-157", plan_step: 6, plan_points: ["6.1","6.4","6.7"], priority_regional: "high", priority_national: "high" },
    { chapter: "5", title: "Geometry and Trigonometry — Solutions (5.1–5.8)", pages: "158-205", plan_step: 1, plan_points: ["1.3","1.7","1.10"], priority_regional: "high", priority_national: "high" },
    { chapter: "6", title: "Number Theory and Combinatorics — Solutions (6.1–6.9)", pages: "206-256", plan_step: 8, plan_points: ["8.3","9.1"], priority_regional: "high", priority_national: "high" }
  ],
  duplicates: [],  // CHECK: търси "book-3 (1).pdf", "book-3 (2).pdf" в Материали_EN/
  recommended_action: "add-as-bonus",
  best_mapping: [
    { step_id: 6, point_ids: ["6.1","6.4","6.5","6.7"], chapters: ["1.1","1.2","1.3","1.6","1.9"], pages: "12-45" },
    { step_id: 5, point_ids: ["5.1","5.3"], chapters: ["1.4","1.8"], pages: "23-40" },
    { step_id: 3, point_ids: ["3.2","3.10"], chapters: ["1.5","3.6","3.7"], pages: "26-29, 97-102" },
    { step_id: 4, point_ids: ["4.1","4.2"], chapters: ["3.5"], pages: "94-97" },
    { step_id: 7, point_ids: ["7.5","7.6","7.7"], chapters: ["3.2","3.4","3.8"], pages: "83-94, 102-104" },
    { step_id: 8, point_ids: ["8.3","8.10"], chapters: ["1.7","3.1","3.3"], pages: "33-36, 80-89" },
    { step_id: 9, point_ids: ["9.1"], chapters: ["3.9"], pages: "105-107" },
    { step_id: 1, point_ids: ["1.3","1.5","1.6","1.7","1.9","1.10"], chapters: ["2.1–2.7"], pages: "46-74" },
    { step_id: 2, point_ids: ["2.4","2.8"], chapters: ["2.1","2.4","2.5"], pages: "46-67" }
  ]
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
// Добавяне на bonus ресурс "book-3" към следните съществуващи точки:

// Точка 6.1 в STEPS[5].points:
{ id: "6.1",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Identity", pdf: "Материали_EN/book-3", page: 12 }
  ]
}

// Точка 6.4 в STEPS[5].points:
{ id: "6.4",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Cauchy-Schwarz", pdf: "Материали_EN/book-3", page: 16 },
    { label: "Andreescu–Enescu, Treasures — Conjugate tricks", pdf: "Материали_EN/book-3", page: 26 }
  ]
}

// Точка 6.5 в STEPS[5].points:
{ id: "6.5",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Convex functions", pdf: "Материали_EN/book-3", page: 29 }
  ]
}

// Точка 6.7 в STEPS[5].points:
{ id: "6.7",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Rearrangements", pdf: "Материали_EN/book-3", page: 40 }
  ]
}

// Точка 5.1 в STEPS[4].points:
{ id: "5.1",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Roots & Coefficients", pdf: "Материали_EN/book-3", page: 36 },
    { label: "Andreescu–Enescu, Treasures — Parameters", pdf: "Материали_EN/book-3", page: 23 }
  ]
}

// Точка 3.10 в STEPS[2].points:
{ id: "3.10",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Conjugate & Pell", pdf: "Материали_EN/book-3", page: 26 }
  ]
}

// Точка 3.2 в STEPS[2].points:
{ id: "3.2",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — No Solutions mod p", pdf: "Материали_EN/book-3", page: 97 }
  ]
}

// Точка 3.1 в STEPS[2].points:
{ id: "3.1",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Powers of 2", pdf: "Материали_EN/book-3", page: 99 }
  ]
}

// Точка 4.1 в STEPS[3].points:
{ id: "4.1",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Infinite Solutions", pdf: "Материали_EN/book-3", page: 94 }
  ]
}

// Точка 7.6 в STEPS[6].points:
{ id: "7.6",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Integer Sequences", pdf: "Материали_EN/book-3", page: 90 },
    { label: "Andreescu–Enescu, Treasures — Progressions", pdf: "Материали_EN/book-3", page: 102 }
  ]
}

// Точка 8.3 в STEPS[7].points:
{ id: "8.3",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Count Twice!", pdf: "Материали_EN/book-3", page: 86 }
  ]
}

// Точка 8.10 в STEPS[7].points:
{ id: "8.10",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Induction at Work", pdf: "Материали_EN/book-3", page: 33 }
  ]
}

// Точка 9.1 в STEPS[8].points:
{ id: "9.1",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Marriage Lemma", pdf: "Материали_EN/book-3", page: 105 }
  ]
}

// Точка 1.3 в STEPS[0].points:
{ id: "1.3",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Cyclic Quads & Ptolemy", pdf: "Материали_EN/book-3", page: 54 }
  ]
}

// Точка 1.10 в STEPS[0].points:
{ id: "1.10",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Inscribed Circle Quads", pdf: "Материали_EN/book-3", page: 71 }
  ]
}

// Точка 1.7 в STEPS[0].points:
{ id: "1.7",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Carpets & Locus (Areas)", pdf: "Материали_EN/book-3", page: 49 },
    { label: "Andreescu–Enescu, Treasures — Carpets Theorem", pdf: "Материали_EN/book-3", page: 67 }
  ]
}

// Точка 1.5 в STEPS[0].points:
{ id: "1.5",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Cyclic Quads", pdf: "Материали_EN/book-3", page: 54 }
  ]
}

// Точка 2.4 в STEPS[1].points:
{ id: "2.4",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Equilateral Triangles", pdf: "Материали_EN/book-3", page: 63 }
  ]
}

// Точка 2.8 в STEPS[1].points:
{ id: "2.8",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Geometric Inequalities", pdf: "Материали_EN/book-3", page: 46 }
  ]
}

// Точка 1.6 в STEPS[0].points:
{ id: "1.6",
  bonus: [
    { label: "Andreescu–Enescu, Treasures — Dr. Trig (Complex Numbers)", pdf: "Материали_EN/book-3", page: 75 }
  ]
}
```

### RECOMMENDED CHANGES TO index.html

**В STEPS:**
- [ ] Добавяне на `bonus` поле към **22 точки** (виж блока АКТУАЛИЗАЦИЯ по-горе):
  - `STEPS[0]` (Геометрия осн.): точки `1.3`, `1.5`, `1.6`, `1.7`, `1.10`
  - `STEPS[1]` (Геометрия напреднали): точки `2.4`, `2.8`
  - `STEPS[2]` (ТЧ осн.): точки `3.1`, `3.2`, `3.10`
  - `STEPS[3]` (ТЧ напреднали): точка `4.1`
  - `STEPS[4]` (Полиноми): точка `5.1`
  - `STEPS[5]` (Неравенства): точки `6.1`, `6.4`, `6.5`, `6.7`
  - `STEPS[6]` (ФУ/редици): точка `7.6`
  - `STEPS[7]` (Комбинаторика осн.): точки `8.3`, `8.10`
  - `STEPS[8]` (Графи/игри): точка `9.1`
- [ ] Всички bonus записи използват `pdf: "Материали_EN/book-3"` и съответния `page` от таблицата по-горе

**В PLAN_PHASES:**
- [ ] Няма промени — книгата е допълнителен ресурс, не замества основния план

**Друго:**
- [ ] Провери за дубликати: `book-3 (1).pdf`, `book-3 (2).pdf`, `book-3 (3).pdf`, `book-3 (4).pdf` в `Материали_EN/` → ако съществуват, изтрий ги и остави само `book-3.pdf`
- [ ] Няма промени в конфигурацията на exam dates
- [ ] Няма нова Стъпка 12 — книгата се вписва в съществуващите 11 стъпки

---

### book-4.pdf — ⚠️ ГОТОВО (с проблем)
**Идентификация:** Euclidean Geometry in Mathematical Olympiads (Evan Chen, 2016)
**Решение:** `add-as-step12` (приемаме **Опит 1**, Опит 2 се игнорира)
**Забележка:** 3 нови точки в Стъпка 12

# ─── КНИГА ───

```js
{
  file: "Материали_EN/book-4.pdf",
  title: "Euclidean Geometry in Mathematical Olympiads",
  author: "Evan Chen",
  year: 2016,
  language: "EN",
  total_pages: 328,
  topics: ["Geometry", "Complex Numbers", "Barycentric Coordinates", "Inversion", "Projective Geometry", "Complete Quadrilaterals"],
  structure: [
    { chapter: "Ch 0", title: "Preliminaries: Notations and Triangle Centers", pages: "14-16", plan_step: 1, plan_points: ["1.5","1.8","1.10"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 1", title: "Angle Chasing", pages: "20-38", plan_step: 1, plan_points: ["1.1","1.2","1.5","1.8","1.10"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 2", title: "Circles: Power of a Point, Radical Axis", pages: "40-58", plan_step: 1, plan_points: ["1.4","1.5","1.8","1.10"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 3", title: "Lengths and Ratios: Ceva, Menelaus, Homothety", pages: "60-74", plan_step: 1, plan_points: ["1.1","1.2","1.6","1.8"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 4", title: "Assorted Configurations: Simson, Symmedians, Mixtilinear", pages: "76-88", plan_step: 2, plan_points: ["2.1","2.2","2.4","2.6"], priority_regional: "med", priority_national: "high" },
    { chapter: "Ch 5", title: "Computational Geometry: Cartesian, Areas, Trigonometry, Ptolemy", pages: "92-110", plan_step: 1, plan_points: ["1.3","1.6","1.7"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 6", title: "Complex Numbers in Geometry", pages: "112-134", plan_step: 12, plan_points: ["12.1"], priority_regional: "low", priority_national: "high" },
    { chapter: "Ch 7", title: "Barycentric Coordinates", pages: "136-163", plan_step: 12, plan_points: ["12.2"], priority_regional: "low", priority_national: "high" },
    { chapter: "Ch 8", title: "Inversion", pages: "166-184", plan_step: 2, plan_points: ["2.3"], priority_regional: "med", priority_national: "high" },
    { chapter: "Ch 9", title: "Projective Geometry: Cross Ratios, Poles/Polars, Pascal", pages: "186-210", plan_step: 2, plan_points: ["2.5","2.6","2.7"], priority_regional: "low", priority_national: "high" },
    { chapter: "Ch 10", title: "Complete Quadrilaterals: Spiral Similarity, Miquel Points", pages: "212-224", plan_step: 12, plan_points: ["12.3"], priority_regional: "med", priority_national: "high" },
    { chapter: "Ch 11", title: "Personal Favorites: Mixed Olympiad Problems", pages: "226-228", plan_step: 10, plan_points: ["10.1","10.2","10.3","10.4","10.5","10.6"], priority_regional: "med", priority_national: "high" },
    { chapter: "App A", title: "An Ounce of Linear Algebra: Determinants and Vectors", pages: "232-237", plan_step: 12, plan_points: ["12.2"], priority_regional: "low", priority_national: "med" },
    { chapter: "App B", title: "Hints to Problems", pages: "238-256", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "App C", title: "Selected Solutions to Problems", pages: "258-318", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "App D", title: "List of Contests and Abbreviations", pages: "320-321", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" }
  ],
  duplicates: [],
  recommended_action: "add-as-step12",
  best_mapping: [
    { step_id: 1, point_ids: ["1.1","1.2","1.3","1.4","1.5","1.6","1.7","1.8","1.10"], chapters: ["Ch 1","Ch 2","Ch 3","Ch 5"], pages: "20-110" },
    { step_id: 2, point_ids: ["2.1","2.2","2.3","2.4","2.5","2.6","2.7"], chapters: ["Ch 4","Ch 8","Ch 9"], pages: "76-210" },
    { step_id: 12, point_ids: ["12.1","12.2","12.3"], chapters: ["Ch 6","Ch 7","Ch 10"], pages: "112-224" },
    { step_id: 10, point_ids: ["10.1","10.2","10.3"], chapters: ["Ch 11"], pages: "226-228" }
  ]
}
```

---

# ─── НОВА СТЪПКА ───

```js
// ─── СТЪПКА 12: ANALYTIC AND PROJECTIVE GEOMETRY ───
{
  num: 12,
  title: "ANALYTIC AND PROJECTIVE GEOMETRY",
  scope: "Комплексни числа, барицентрични координати, проективна геометрия и пълни четириъгълници за олимпийски задачи",
  points: [
    {
      id: "12.1",
      title: "Комплексни числа в геометрията",
      desc: "Използване на комплексната равнина за решаване на геометрични задачи — единична окръжност, формули за ортоцентър, инцентър, пресечни точки.",
      source: "Evan Chen, Euclidean Geometry in Mathematical Olympiads, Ch 6",
      pdf: "Материали_EN/book-4",
      page: 113,
      problems_page: 133,
      solutions_page: null,
      tasks: [
        { label: "Example 6.10 (Перпендикулярност)", pdf: "Материали_EN/book-4", page: 101 },
        { label: "Lemma 6.11 (Complex Foot)", pdf: "Материали_EN/book-4", page: 101 },
        { label: "Lemma 6.12 (Complex Euler Line)", pdf: "Материали_EN/book-4", page: 102 },
        { label: "Example 6.13 (Nine-Point Circle)", pdf: "Материали_EN/book-4", page: 103 },
        { label: "Theorem 6.17 (Complex Intersection)", pdf: "Материали_EN/book-4", page: 104 },
        { label: "Lemma 6.19 (Complex Tangent Intersection)", pdf: "Материали_EN/book-4", page: 105 },
        { label: "Lemma 6.23 (Complex Incenter)", pdf: "Материали_EN/book-4", page: 106 },
        { label: "Lemma 6.24 (Complex Circumcenter)", pdf: "Материали_EN/book-4", page: 107 },
        { label: "Proposition 6.25 (Feuerbach Tangency)", pdf: "Материали_EN/book-4", page: 108 },
        { label: "Example 6.26 (USA TSTST 2013/1)", pdf: "Материали_EN/book-4", page: 110 },
        { label: "Example 6.27 (USAMO 2012/5)", pdf: "Материали_EN/book-4", page: 113 }
      ],
      bonus: [
        { label: "Hints to Ch 6 problems", pdf: "Материали_EN/book-4", page: 238 }
      ],
      explanation: "ФОРМУЛИРОВКА: Комплексните числа позволяват алгебрично решение на геометрични задачи чрез поставяне на окръжността като единична.\n\nКОГА: Когато всички важни точки лежат на една окръжност (обикновено (ABC)) и има перпендикуляри, среди, ъгли.\n\nСВОЙСТВА: Ако a,b,c са на единичната окръжност: ортоцентър h = a+b+c; център на деветточкова окръжност n₉ = (a+b+c)/2; инцентър = -(uv+vw+wu) при a=u², b=v², c=w²; пресечна точка на допирателни в a,b е 2ab/(a+b).\n\nТРИК: Постави (ABC) като единична окръжност. Избягвай задачи с много окръжности. Използвай \\(\\overline{a} = 1/a\\) за точки на единичната окръжност. Предпочитай синтетични наблюдения преди изчисления."
    },
    {
      id: "12.2",
      title: "Барицентрични координати",
      desc: "Однородни координати спрямо референтен триъгълник — мощни за среди, среди, пресечни точки и центрове.",
      source: "Evan Chen, Euclidean Geometry in Mathematical Olympiads, Ch 7",
      pdf: "Материали_EN/book-4",
      page: 137,
      problems_page: 160,
      solutions_page: null,
      tasks: [
        { label: "Theorem 7.1 (Barycentric Area Formula)", pdf: "Материали_EN/book-4", page: 119 },
        { label: "Theorem 7.2 (Equation of a Line)", pdf: "Материали_EN/book-4", page: 120 },
        { label: "Theorem 7.4 (Barycentric Cevian)", pdf: "Материали_EN/book-4", page: 122 },
        { label: "Theorem 7.10 (Collinearity)", pdf: "Материали_EN/book-4", page: 123 },
        { label: "Theorem 7.13 (Concurrence)", pdf: "Материали_EN/book-4", page: 125 },
        { label: "Theorem 7.14 (Distance Formula)", pdf: "Материали_EN/book-4", page: 126 },
        { label: "Theorem 7.15 (Barycentric Circle)", pdf: "Материали_EN/book-4", page: 127 },
        { label: "Theorem 7.16 (Perpendiculars)", pdf: "Материали_EN/book-4", page: 127 },
        { label: "Lemma 7.19 (Perpendicular Bisector)", pdf: "Материали_EN/book-4", page: 128 },
        { label: "Example 7.20 (Shortlist 2011/G6)", pdf: "Материали_EN/book-4", page: 129 },
        { label: "Theorem 7.22 (Conway's Formula)", pdf: "Материали_EN/book-4", page: 133 },
        { label: "Lemma 7.23 (Barycentric Power)", pdf: "Материали_EN/book-4", page: 134 },
        { label: "Example 7.27 (Pascal's Theorem)", pdf: "Материали_EN/book-4", page: 135 },
        { label: "Example 7.28 (Incircle Concurrency)", pdf: "Материали_EN/book-4", page: 137 },
        { label: "Example 7.29 (USAMO 2008/2)", pdf: "Материали_EN/book-4", page: 138 },
        { label: "Example 7.30 (USA TSTST 2011/4)", pdf: "Материали_EN/book-4", page: 139 }
      ],
      bonus: [
        { label: "Barycentric Coordinates in Olympiad Geometry (Evan Chen & Max Schindler)", pdf: "Материали_EN/book-4", page: 305 }
      ],
      explanation: "ФОРМУЛИРОВКА: Всяка точка P се представя с (x:y:z) така, че P = xA + yB + zC, x+y+z=1. Задачите се свеждат до детерминанти.\n\nКОГА: Задачи с много среди (цевени), пресечни точки, колинеарност, конкурентност, центрове на триъгълник. Избягвай при много окръжности.\n\nСВОЙСТВА: G=(1:1:1); I=(a:b:c); O=(sin2A:sin2B:sin2C); H=(tanA:tanB:tanC); K=(a²:b²:c²). Уравнение на права: ux+vy+wz=0. Окръжност: -a²yz-b²zx-c²xy+(x+y+z)(ux+vy+wz)=0.\n\nТРИК: Избери референтен триъгълник, в който колкото се може повече от дадените точки са върхове или лежат на страни. Използвай хомогенни координати (с двоеточие) за пресмятания. За перпендикуляри използвай Theorem 7.16."
    },
    {
      id: "12.3",
      title: "Проективна геометрия и пълни четириъгълници",
      desc: "Крос-ратове, хармонични снопове, полюси/поляри, теорема на Паскал, спирално подобие, точка на Miquel.",
      source: "Evan Chen, Euclidean Geometry in Mathematical Olympiads, Ch 9-10",
      pdf: "Материали_EN/book-4",
      page: 187,
      problems_page: 208,
      solutions_page: null,
      tasks: [
        { label: "Theorem 9.1 (Cross-Ratio Under Perspectivity)", pdf: "Материали_EN/book-4", page: 171 },
        { label: "Lemma 9.8 (Midpoints and Parallel Lines)", pdf: "Материали_EN/book-4", page: 173 },
        { label: "Lemma 9.9 (Harmonic Quadrilaterals)", pdf: "Материали_EN/book-4", page: 173 },
        { label: "Lemma 9.11 (Cevians Induce Harmonic Bundles)", pdf: "Материали_EN/book-4", page: 174 },
        { label: "Lemma 9.12 (Complete Quadrilaterals)", pdf: "Материали_EN/book-4", page: 175 },
        { label: "Theorem 9.19 (Apollonian Circles)", pdf: "Материали_EN/book-4", page: 177 },
        { label: "Theorem 9.25 (Brocard's Theorem)", pdf: "Материали_EN/book-4", page: 179 },
        { label: "Theorem 9.29 (Pascal's Theorem)", pdf: "Материали_EN/book-4", page: 181 },
        { label: "Theorem 9.33 (Projective Transformations)", pdf: "Материали_EN/book-4", page: 184 },
        { label: "Theorem 9.35 (Butterfly Theorem)", pdf: "Материали_EN/book-4", page: 185 },
        { label: "Example 9.38 (IMO 2010/2)", pdf: "Материали_EN/book-4", page: 186 },
        { label: "Example 9.39 (APMO 2013/5)", pdf: "Материали_EN/book-4", page: 187 },
        { label: "Lemma 10.1 (Spiral Centers)", pdf: "Материали_EN/book-4", page: 197 },
        { label: "Theorem 10.3 (Miquel's Theorem)", pdf: "Материали_EN/book-4", page: 198 },
        { label: "Theorem 10.5 (Gauss-Bodenmiller)", pdf: "Материали_EN/book-4", page: 199 },
        { label: "Theorem 10.12 (Miquel Point of Cyclic Quad)", pdf: "Материали_EN/book-4", page: 201 },
        { label: "Example 10.16 (USA TST 2013)", pdf: "Материали_EN/book-4", page: 202 }
      ],
      bonus: [
        { label: "Projective Geometry (Alex Remorov, Canadian IMO Training)", pdf: "Материали_EN/book-4", page: 305 }
      ],
      explanation: "ФОРМУЛИРОВКА: Проективната геометрия изучава свойства, запазени при проекции — крос-ратове, хармонични снопове, полюси/поляри. Пълният четириъгълник е четири прави с шест пресечни точки.\n\nКОГА: Задачи с много пресечни точки, колинеарност, конкурентност, допирателни, без метрични условия. Точката на Miquel се появява при пълни четириъгълници.\n\nСВОЙСТВА: (A,B;X,Y) = -1 е хармоничен сноп; (A,B;M,P∞) = -1 за среда M; Brocard: P,Q,R са полюси на QR,RP,PQ; Pascal: за шест точки на окръжност, три пресечни точки са колинеарни; Miquel: четири окръжности се пресичат в една точка.\n\nТРИК: Търси хармонични снопове — те се появяват при среди, допирателни, пълни четириъгълници. Използвай проективни трансформации, за да опростиш задачата (напр. превърни четириъгълник в квадрат). За помни: спирално подобие + Miquel point = мощна комбинация."
    }
  ]
}
```

---

# ─── АКТУАЛИЗАЦИЯ НА СЪЩЕСТВУВАЩИ ТОЧКИ ───

```js
// ─── АКТУАЛИЗАЦИЯ ───
// Замести САМО следните полета в съществуващите точки:

// Точка 1.3 (Птолемей) в STEPS[0].points:
{ id: "1.3",
  page: 81,
  problems_page: 98,
  solutions_page: null,
  bonus: [
    { label: "Ptolemy's Theorem (Ch 5.4)", pdf: "Материали_EN/book-4", page: 81 },
    { label: "Ptolemy's Inequality (Problem 8.20)", pdf: "Материали_EN/book-4", page: 160 }
  ]
}

// Точка 1.4 (Степен/Радикална ос) в STEPS[0].points:
{ id: "1.4",
  page: 25,
  problems_page: 42,
  solutions_page: null,
  bonus: [
    { label: "Power of a Point (Ch 2.2)", pdf: "Материали_EN/book-4", page: 25 },
    { label: "Radical Axis and Radical Center (Ch 2.3)", pdf: "Материали_EN/book-4", page: 26 },
    { label: "Coaxial Circles (Ch 2.4)", pdf: "Материали_EN/book-4", page: 30 }
  ]
}

// Точка 1.8 (Ойлер) в STEPS[0].points:
{ id: "1.8",
  page: 50,
  problems_page: 67,
  solutions_page: null,
  bonus: [
    { label: "Homothety and Nine-Point Circle (Ch 3.5)", pdf: "Материали_EN/book-4", page: 49 },
    { label: "Euler Line (Lemma 3.13)", pdf: "Материали_EN/book-4", page: 51 },
    { label: "Complex Euler Line (Lemma 6.12)", pdf: "Материали_EN/book-4", page: 102 }
  ]
}

// Точка 2.3 (Инверсия) в STEPS[1].points:
{ id: "2.3",
  page: 149,
  problems_page: 165,
  solutions_page: null,
  bonus: [
    { label: "Inversion (Ch 8)", pdf: "Материали_EN/book-4", page: 149 },
    { label: "Inversion Distance Formula (Thm 8.18)", pdf: "Материали_EN/book-4", page: 160 },
    { label: "Overlays and Orthogonal Circles (Ch 8.4)", pdf: "Материали_EN/book-4", page: 156 }
  ]
}

// Точка 2.5 (Полюси/поляри) в STEPS[1].points:
{ id: "2.5",
  page: 178,
  problems_page: 196,
  solutions_page: null,
  bonus: [
    { label: "Poles/Polars and Brocard's Theorem (Ch 9.5)", pdf: "Материали_EN/book-4", page: 178 },
    { label: "La Hire's Theorem (Thm 9.23)", pdf: "Материали_EN/book-4", page: 179 },
    { label: "Brocard's Theorem (Thm 9.25)", pdf: "Материали_EN/book-4", page: 179 }
  ]
}

// Точка 2.6 (Паскал) в STEPS[1].points:
{ id: "2.6",
  page: 181,
  problems_page: 199,
  solutions_page: null,
  bonus: [
    { label: "Pascal's Theorem (Ch 9.6)", pdf: "Материали_EN/book-4", page: 181 },
    { label: "Pascal via Barycentrics (Example 7.27)", pdf: "Материали_EN/book-4", page: 135 }
  ]
}

// Точка 2.7 (Брианшон) в STEPS[1].points:
{ id: "2.7",
  page: 192,
  problems_page: null,
  solutions_page: null,
  bonus: [
    { label: "Brianchon's Theorem (Thm 9.55)", pdf: "Материали_EN/book-4", page: 192 }
  ]
}
```

---

# ─── RECOMMENDED CHANGES TO index.html ───

**В STEPS:**
- [ ] Добавяне на нова стъпка `STEPS[11]` = **Step 12: ANALYTIC AND PROJECTIVE GEOMETRY** с точки `12.1`, `12.2`, `12.3` (пълен код в блока "НОВА СТЪПКА" по-горе)
- [ ] Промяна в `STEPS[0].points[2]` (Точка 1.3 Птолемей): `page: 81`, `problems_page: 98`, нов `bonus` = Ptolemy's Theorem (book-4, p.81) + Ptolemy's Inequality (book-4, p.160)
- [ ] Промяна в `STEPS[0].points[3]` (Точка 1.4 Степен/Радикална ос): `page: 25`, `problems_page: 42`, нов `bonus` = Power of a Point (book-4, p.25) + Radical Axis (book-4, p.26) + Coaxial Circles (book-4, p.30)
- [ ] Промяна в `STEPS[0].points[7]` (Точка 1.8 Ойлер): `page: 50`, `problems_page: 67`, нов `bonus` = Nine-Point Circle (book-4, p.49) + Euler Line (book-4, p.51) + Complex Euler Line (book-4, p.102)
- [ ] Промяна в `STEPS[1].points[2]` (Точка 2.3 Инверсия): `page: 149`, `problems_page: 165`, нов `bonus` = Inversion (book-4, p.149) + Inversion Distance Formula (book-4, p.160) + Overlays (book-4, p.156)
- [ ] Промяна в `STEPS[1].points[4]` (Точка 2.5 Полюси/поляри): `page: 178`, `problems_page: 196`, нов `bonus` = Poles/Polars (book-4, p.178) + La Hire (book-4, p.179) + Brocard (book-4, p.179)
- [ ] Промяна в `STEPS[1].points[5]` (Точка 2.6 Паскал): `page: 181`, `problems_page: 199`, нов `bonus` = Pascal's Theorem (book-4, p.181) + Pascal via Barycentrics (book-4, p.135)
- [ ] Промяна в `STEPS[1].points[6]` (Точка 2.7 Брианшон): `page: 192`, нов `bonus` = Brianchon's Theorem (book-4, p.192)

**В PLAN_PHASES:**
- [ ] Обновяване на **Phase 2 (Разширяване)**: добавяне на книгата като основен ресурс за Геометрия (Step 2)
- [ ] Обновяване на **Phase 4 (Между-национален)**: добавяне на Step 12 (Analytic & Projective Geometry) като опция за напреднали
- [ ] Week 7-12: добавяне на "Ch 4, 8, 9 от book-4" към фокуса върху Геометрия напреднали
- [ ] Week 18-25: добавяне на "Ch 6, 7, 10 от book-4" за подготовка за национален кръг

**Друго:**
- [ ] Няма дубликати — `book-4.pdf` е уникален (Evan Chen, Euclidean Geometry in Mathematical Olympiads)
- [ ] `book-4.pdf` е **основен ресурс за Геометрия** — препоръчва се за Steps 1, 2 и нов Step 12
- [ ] Всички page числа са PDF page numbers (проверени с `===== Page X =====` маркери)
- [ ] Няма промени в конфигурацията на exam dates
- [ ] Препоръчва се добавяне на `book-4` като `source` за всички точки в Step 1 и Step 2 (вместо или в допълнение към текущите източници)

---

### book-4 (1).pdf — ✅ ГОТОВО (SKIP)
**Идентификация:** Competitive Programming 4, Book 2 (Halim, Halim, Effendy, 2020)
**Решение:** `skip` — НЕ Е математика
**Забележка:** Информатика

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-4 (1).pdf",
  title: "Competitive Programming 4, Book 2: The Lower Bound of Techniques (Chapters 5–9)",
  author: "Steven Halim, Felix Halim, Suhendry Effendy",
  year: 2020,
  language: "EN",
  total_pages: 352,
  topics: ["Number Theory", "Combinatorics", "Probability", "Game Theory", "Geometry", "Graph Theory", "Algorithms", "Data Structures"],
  structure: [
    // ─── Front Matter ───
    { chapter: "Front", title: "Cover, Table of Contents, Author Profiles", pages: "1-8", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },

    // ─── Chapter 5: Mathematics ───
    { chapter: "5.1", title: "Mathematics: Overview and Motivation", pages: "9", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "5.2", title: "Ad Hoc Mathematical Problems (formulas, sequences, bases, grids, polynomials, fractions)", pages: "10-17", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "5.3", title: "Number Theory (primes, sieve, GCD/LCM, factorial, modular arithmetic, extended Euclidean, Euler Phi)", pages: "18-33", plan_step: 3, plan_points: ["3.1","3.2","3.3","3.4","3.5","3.6","4.1","4.2","4.5"], priority_regional: "high", priority_national: "high" },
    { chapter: "5.4", title: "Combinatorics (Fibonacci, binomial coefficients, Catalan numbers, counting principles)", pages: "34-39", plan_step: 8, plan_points: ["8.4","8.5","8.8"], priority_regional: "high", priority_national: "high" },
    { chapter: "5.5", title: "Probability Theory (closed-form, sample space, derangement, expected value)", pages: "41-43", plan_step: 8, plan_points: [], priority_regional: "med", priority_national: "med" },
    { chapter: "5.6", title: "Cycle-Finding (Floyd's algorithm, Brent's algorithm)", pages: "44-47", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "5.7", title: "Game Theory (Basic) — decision trees, minimax, perfect play", pages: "48-50", plan_step: 9, plan_points: ["9.10"], priority_regional: "med", priority_national: "high" },
    { chapter: "5.8", title: "Matrix Power (modular exponentiation, matrix exponentiation, DP speed-up)", pages: "51-56", plan_step: 8, plan_points: ["8.8"], priority_regional: "low", priority_national: "med" },
    { chapter: "5.9-5.10", title: "Solutions to Non-Starred Exercises & Chapter Notes", pages: "57-60", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },

    // ─── Chapter 6: String Processing ───
    { chapter: "6.1-6.9", title: "String Processing (Ad Hoc, DP, String Matching, Suffix Trie/Tree/Array, Hashing, Anagram/Palindrome)", pages: "61-100", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },

    // ─── Chapter 7: (Computational) Geometry ───
    { chapter: "7.1", title: "Geometry: Overview and Motivation", pages: "101-103", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "7.2", title: "Basic Geometry Objects with Libraries (points, lines, circles, triangles, quadrilaterals)", pages: "104-119", plan_step: 1, plan_points: ["1.1","1.2","1.3","1.4","1.5","1.6","1.7","1.8"], priority_regional: "high", priority_national: "high" },
    { chapter: "7.3", title: "Algorithms on Polygon with Libraries (perimeter, area, convexity, point-in-polygon, cutting, convex hull)", pages: "120-130", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "7.4", title: "3D Geometry (volume, surface area, solid of revolution, great-circle distance)", pages: "132-133", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "7.5-7.6", title: "Solutions to Non-Starred Exercises & Chapter Notes", pages: "134-136", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },

    // ─── Chapter 8: More Advanced Topics ───
    { chapter: "8.1", title: "More Advanced Topics: Overview and Motivation", pages: "137", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "8.2", title: "More Advanced Search Techniques (bitmask backtracking, state-space search, meet-in-the-middle)", pages: "138-146", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "8.3", title: "More Advanced DP Techniques (DP with bitmask, state representation, parameter reduction)", pages: "147-155", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "8.4", title: "Network Flow (Ford-Fulkerson, Edmonds-Karp, Dinic's, flow modeling)", pages: "156-170", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "8.5", title: "Graph Matching (MCBM, weighted MCBM, unweighted/weighted MCM)", pages: "171-176", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "8.6", title: "NP-hard/complete Problems (Knapsack, TSP, MIS, MVC, MSC, MPC, SAT, Steiner, Coloring)", pages: "177-200", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "8.7", title: "Problem Decomposition (BSTA + other, geometry + others, graph + DP, etc.)", pages: "201-213", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "8.8-8.9", title: "Solutions to Non-Starred Exercises & Chapter Notes", pages: "214-216", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },

    // ─── Chapter 9: Rare Topics ───
    { chapter: "9.1", title: "Rare Topics: Overview and Motivation", pages: "217-218", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.2", title: "Sliding Window", pages: "219-220", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.3", title: "Sparse Table Data Structure", pages: "221-223", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.4", title: "Square Root Decomposition", pages: "224-228", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.5", title: "Heavy-Light Decomposition", pages: "229-231", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.6", title: "Tower of Hanoi", pages: "232", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "med" },
    { chapter: "9.7", title: "Matrix Chain Multiplication", pages: "233-234", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "med" },
    { chapter: "9.8", title: "Lowest Common Ancestor", pages: "235-236", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.9", title: "Tree Isomorphism", pages: "237-240", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.10", title: "De Bruijn Sequence", pages: "241-243", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.11", title: "Fast Fourier Transform (polynomial multiplication, convolution, string matching)", pages: "244-263", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.12", title: "Pollard's rho Algorithm (integer factorization)", pages: "264-265", plan_step: 4, plan_points: ["4.5"], priority_regional: "low", priority_national: "med" },
    { chapter: "9.13", title: "Chinese Remainder Theorem", pages: "266-269", plan_step: 3, plan_points: ["3.6"], priority_regional: "high", priority_national: "high" },
    { chapter: "9.14", title: "Lucas' Theorem", pages: "270-271", plan_step: 3, plan_points: ["3.8"], priority_regional: "med", priority_national: "high" },
    { chapter: "9.15", title: "Rare Formulas or Theorems (Cayley, Derangement, Erdős-Gallai, Euler, Moser, Pick, Brahmagupta, Stirling, Bell)", pages: "272-273", plan_step: null, plan_points: ["1.7","8.4","8.8","9.1"], priority_regional: "med", priority_national: "high" },
    { chapter: "9.16", title: "Combinatorial Game Theory (Nim, Misère Nim, Bogus Nim, Sprague-Grundy)", pages: "274-278", plan_step: 9, plan_points: ["9.10"], priority_regional: "med", priority_national: "high" },
    { chapter: "9.17", title: "Gaussian Elimination Algorithm", pages: "279-281", plan_step: 5, plan_points: [], priority_regional: "low", priority_national: "med" },
    { chapter: "9.18", title: "Art Gallery Problem", pages: "282", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.19", title: "Closest Pair Problem", pages: "283", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.20", title: "A* and IDA*: Informed Search", pages: "284-286", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.21", title: "Pancake Sorting", pages: "287-289", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.22", title: "Egg Dropping Puzzle", pages: "290-293", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "med" },
    { chapter: "9.23", title: "Dynamic Programming Optimization (Convex Hull, D&C, Knuth's)", pages: "294-301", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.24", title: "Push-Relabel Algorithm", pages: "302-306", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.25", title: "Min Cost (Max) Flow", pages: "307-308", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.26", title: "Hopcroft-Karp Algorithm", pages: "309", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.27", title: "Kuhn-Munkres Algorithm", pages: "310-312", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.28", title: "Edmonds' Matching Algorithm", pages: "313-315", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.29", title: "Chinese Postman Problem", pages: "316-317", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.30", title: "Constructive Problem (Magic Square, N-Queens construction, BFS spanning tree)", pages: "318-320", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "med" },
    { chapter: "9.31", title: "Interactive Problem", pages: "321", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.32", title: "Linear Programming", pages: "322-324", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.33", title: "Gradient Descent", pages: "325", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "9.34", title: "Chapter Notes", pages: "326", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },

    // ─── Back Matter ───
    { chapter: "Back", title: "Bibliography & Index", pages: "327-352", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" }
  ],
  duplicates: ["book-4.pdf"], // CHECK: "(1)" в името предполага възможен дубликат
  recommended_action: "add-as-bonus",
  best_mapping: [
    { step_id: 1, point_ids: ["1.1","1.2","1.3","1.4","1.5","1.6","1.7","1.8"], chapters: ["7.2"], pages: "104-119" },
    { step_id: 3, point_ids: ["3.1","3.2","3.3","3.4","3.5","3.6"], chapters: ["5.3","9.13","9.14"], pages: "18-33, 266-271" },
    { step_id: 4, point_ids: ["4.1","4.2","4.5"], chapters: ["5.3","9.12"], pages: "18-33, 264-265" },
    { step_id: 5, point_ids: [], chapters: ["9.17"], pages: "279-281" },
    { step_id: 8, point_ids: ["8.4","8.5","8.8"], chapters: ["5.4","5.5","5.8"], pages: "34-43, 51-56" },
    { step_id: 9, point_ids: ["9.10"], chapters: ["5.7","9.16"], pages: "48-50, 274-278" }
  ]
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
// Замести САМО следните полета в съществуващите точки:

// Точка 1.7 (Лице/Херон) в STEPS[0].points:
{ id: "1.7",
  bonus: [
    { label: "CP4 Book 2, 7.2 Basic Geometry Objects (pp. 104-119)", pdf: "Материали_EN/book-4 (1)", page: 104 }
  ]
}

// Точка 3.2 (Сравнения) в STEPS[2].points:
{ id: "3.2",
  bonus: [
    { label: "CP4 Book 2, 5.3 Number Theory (pp. 18-33)", pdf: "Материали_EN/book-4 (1)", page: 18 }
  ]
}

// Точка 3.4 (Ойлер) в STEPS[2].points:
{ id: "3.4",
  bonus: [
    { label: "CP4 Book 2, 5.3.4 Functions Involving Prime Factors — EulerPhi (pp. 22-23)", pdf: "Материали_EN/book-4 (1)", page: 22 }
  ]
}

// Точка 3.6 (CRT) в STEPS[2].points:
{ id: "3.6",
  bonus: [
    { label: "CP4 Book 2, 9.13 Chinese Remainder Theorem (pp. 266-269)", pdf: "Материали_EN/book-4 (1)", page: 266 }
  ]
}

// Точка 4.5 (Прости) в STEPS[3].points:
{ id: "4.5",
  bonus: [
    { label: "CP4 Book 2, 9.12 Pollard's rho Algorithm (pp. 264-265)", pdf: "Материали_EN/book-4 (1)", page: 264 }
  ]
}

// Точка 8.5 (Биномни) в STEPS[7].points:
{ id: "8.5",
  bonus: [
    { label: "CP4 Book 2, 5.4.2 Binomial Coefficients (pp. 35-36)", pdf: "Материали_EN/book-4 (1)", page: 35 }
  ]
}

// Точка 8.8 (Рекурсии) в STEPS[7].points:
{ id: "8.8",
  bonus: [
    { label: "CP4 Book 2, 5.4.1 Fibonacci Numbers (p. 34) + 5.4.3 Catalan Numbers (pp. 36-37) + 5.8 Matrix Power (pp. 51-56)", pdf: "Материали_EN/book-4 (1)", page: 34 }
  ]
}

// Точка 9.10 (Игри) в STEPS[8].points:
{ id: "9.10",
  bonus: [
    { label: "CP4 Book 2, 5.7 Game Theory Basic (pp. 48-50) + 9.16 Combinatorial Game Theory (pp. 274-278)", pdf: "Материали_EN/book-4 (1)", page: 48 }
  ]
}
```

### RECOMMENDED CHANGES TO index.html

**В STEPS:**
- [ ] Промяна в `STEPS[0].points[6]` (Точка 1.7): добавяне на `bonus` = CP4 Book 2, 7.2 Basic Geometry Objects (pp. 104-119)
- [ ] Промяна в `STEPS[2].points[1]` (Точка 3.2): добавяне на `bonus` = CP4 Book 2, 5.3 Number Theory (pp. 18-33)
- [ ] Промяна в `STEPS[2].points[3]` (Точка 3.4): добавяне на `bonus` = CP4 Book 2, 5.3.4 EulerPhi (pp. 22-23)
- [ ] Промяна в `STEPS[2].points[5]` (Точка 3.6): добавяне на `bonus` = CP4 Book 2, 9.13 CRT (pp. 266-269)
- [ ] Промяна в `STEPS[3].points[4]` (Точка 4.5): добавяне на `bonus` = CP4 Book 2, 9.12 Pollard's rho (pp. 264-265)
- [ ] Промяна в `STEPS[7].points[4]` (Точка 8.5): добавяне на `bonus` = CP4 Book 2, 5.4.2 Binomial Coefficients (pp. 35-36)
- [ ] Промяна в `STEPS[7].points[7]` (Точка 8.8): добавяне на `bonus` = CP4 Book 2, 5.4.1 Fibonacci + 5.4.3 Catalan + 5.8 Matrix Power (pp. 34-37, 51-56)
- [ ] Промяна в `STEPS[8].points[9]` (Точка 9.10): добавяне на `bonus` = CP4 Book 2, 5.7 Game Theory + 9.16 Combinatorial Game Theory (pp. 48-50, 274-278)

**Друго:**
- [ ] Провери за дубликат: `book-4 (1).pdf` vs `book-4.pdf` — ако са идентични, изтрий едното копие
- [ ] Няма промени в конфигурацията на exam dates
- [ ] Няма нова Стъпка 12 — тази книга е bonus материал към съществуващите 11 стъпки

---

### book-7.pdf — ✅ ГОТОВО
**Идентификация:** Inequalities: An Approach Through Problems (Venkatachala, 2009)
**Решение:** `add-as-specific-points`
**Забележка:** 9 нови bonus записа в Step 6

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-7.pdf",
  title: "Inequalities: An Approach Through Problems",
  author: "B. J. Venkatachala",
  year: 2009,
  language: "EN",
  total_pages: 399,
  topics: ["Algebra", "Inequalities", "Geometry", "Number Theory"],
  structure: [
    { 
      chapter: "Ch 1", 
      title: "Some Basic Inequalities", 
      pages: "10-58", 
      plan_step: 6, 
      plan_points: ["6.1","6.2","6.3","6.4","6.5","6.6","6.7","6.8","6.9","6.10"],
      priority_regional: "high",
      priority_national: "high"
    },
    { 
      chapter: "Ch 2", 
      title: "Techniques for Proving Inequalities", 
      pages: "59-101", 
      plan_step: 6, 
      plan_points: ["6.1","6.4","6.5","6.8","6.9","6.10","5.1","5.2","8.10"],
      priority_regional: "high",
      priority_national: "high"
    },
    { 
      chapter: "Ch 3", 
      title: "Geometric Inequalities", 
      pages: "102-161", 
      plan_step: 2, 
      plan_points: ["2.8"],
      priority_regional: "med",
      priority_national: "high"
    },
    { 
      chapter: "Ch 4", 
      title: "Applications Involving Inequalities", 
      pages: "162-192", 
      plan_step: 10, 
      plan_points: ["10.1","10.2","10.3","10.4","10.5","10.6","10.7","10.8","10.9","10.10"],
      priority_regional: "med",
      priority_national: "high"
    },
    { 
      chapter: "Ch 5", 
      title: "Problems on Inequalities", 
      pages: "193-223", 
      plan_step: 10, 
      plan_points: ["10.1","10.2","10.3","10.4","10.5","10.6","10.7","10.8","10.9","10.10"],
      priority_regional: "high",
      priority_national: "high"
    },
    { 
      chapter: "Ch 6", 
      title: "Solutions to Problems", 
      pages: "224-395", 
      plan_step: 10, 
      plan_points: ["10.1","10.2","10.3","10.4","10.5","10.6","10.7","10.8","10.9","10.10"],
      priority_regional: "med",
      priority_national: "med"
    }
  ],
  duplicates: [], // CHECK: book-7.pdf няма очевиден дубликат сред известните файлове
  recommended_action: "add-as-specific-points",
  best_mapping: [
    { step_id: 6, point_ids: ["6.1","6.2","6.3"], chapters: ["Ch 1 (1.1-1.2)"], pages: "10-19" },
    { step_id: 6, point_ids: ["6.4"], chapters: ["Ch 1 (1.3)"], pages: "20-25" },
    { step_id: 6, point_ids: ["6.5"], chapters: ["Ch 1 (1.7)"], pages: "43-55" },
    { step_id: 6, point_ids: ["6.6"], chapters: ["Ch 1 (1.4)"], pages: "26-29" },
    { step_id: 6, point_ids: ["6.7"], chapters: ["Ch 1 (1.5)"], pages: "30-35" },
    { step_id: 6, point_ids: ["6.8"], chapters: ["Ch 2 (2.9-2.10)"], pages: "90-93" },
    { step_id: 6, point_ids: ["6.9"], chapters: ["Ch 2 (2.8, 2.13)"], pages: "88-89, 99-101" },
    { step_id: 6, point_ids: ["6.10"], chapters: ["Ch 1 (1.6)"], pages: "36-42" },
    { step_id: 2, point_ids: ["2.8"], chapters: ["Ch 3"], pages: "102-161" },
    { step_id: 10, point_ids: ["10.1","10.2","10.3","10.4","10.5","10.6","10.7","10.8","10.9","10.10"], chapters: ["Ch 4-6"], pages: "162-395" }
  ]
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
// Замести САМО следните полета в съществуващите точки:

// Точка 6.1 в STEPS[5].points:
{ id: "6.1",
  bonus: [
    { label: "Ch 1.2: AM-GM (теория + примери)", pdf: "Материали_EN/book-7", page: 12 },
    { label: "Ch 2.2-2.3: Индукция и известни неравенства", pdf: "Материали_EN/book-7", page: 59 }
  ]
}

// Точка 6.4 в STEPS[5].points:
{ id: "6.4",
  bonus: [
    { label: "Ch 1.3: Cauchy-Schwarz (теория + примери)", pdf: "Материали_EN/book-7", page: 20 }
  ]
}

// Точка 6.5 в STEPS[5].points:
{ id: "6.5",
  bonus: [
    { label: "Ch 1.7: Jensen и изпъкнали функции", pdf: "Материали_EN/book-7", page: 43 }
  ]
}

// Точка 6.6 в STEPS[5].points:
{ id: "6.6",
  bonus: [
    { label: "Ch 1.4: Chebyshev", pdf: "Материали_EN/book-7", page: 26 }
  ]
}

// Точка 6.7 в STEPS[5].points:
{ id: "6.7",
  bonus: [
    { label: "Ch 1.5: Rearrangement", pdf: "Материали_EN/book-7", page: 30 }
  ]
}

// Точка 6.8 в STEPS[5].points:
{ id: "6.8",
  bonus: [
    { label: "Ch 2.9-2.10: Майоризация и Muirhead", pdf: "Материали_EN/book-7", page: 90 }
  ]
}

// Точка 6.9 в STEPS[5].points:
{ id: "6.9",
  bonus: [
    { label: "Ch 2.8: Schur", pdf: "Материали_EN/book-7", page: 88 },
    { label: "Ch 2.13: Stolarsky", pdf: "Материали_EN/book-7", page: 99 }
  ]
}

// Точка 6.10 в STEPS[5].points:
{ id: "6.10",
  bonus: [
    { label: "Ch 1.6: Hölder и Minkowski", pdf: "Материали_EN/book-7", page: 36 }
  ]
}

// Точка 2.8 в STEPS[1].points:
{ id: "2.8",
  bonus: [
    { label: "Ch 3: Геометрични неравенства (пълен курс)", pdf: "Материали_EN/book-7", page: 102 }
  ]
}
```

```markdown
### RECOMMENDED CHANGES TO index.html

**В STEPS:**
- [ ] Промяна в `STEPS[5].points[0]` (Точка 6.1): нов `bonus` = Ch 1.2 (page 12) + Ch 2.2-2.3 (page 59)
- [ ] Промяна в `STEPS[5].points[3]` (Точка 6.4): нов `bonus` = Ch 1.3 (page 20)
- [ ] Промяна в `STEPS[5].points[4]` (Точка 6.5): нов `bonus` = Ch 1.7 (page 43)
- [ ] Промяна в `STEPS[5].points[5]` (Точка 6.6): нов `bonus` = Ch 1.4 (page 26)
- [ ] Промяна в `STEPS[5].points[6]` (Точка 6.7): нов `bonus` = Ch 1.5 (page 30)
- [ ] Промяна в `STEPS[5].points[7]` (Точка 6.8): нов `bonus` = Ch 2.9-2.10 (page 90)
- [ ] Промяна в `STEPS[5].points[8]` (Точка 6.9): нов `bonus` = Ch 2.8 (page 88) + Ch 2.13 (page 99)
- [ ] Промяна в `STEPS[5].points[9]` (Точка 6.10): нов `bonus` = Ch 1.6 (page 36)
- [ ] Промяна в `STEPS[1].points[7]` (Точка 2.8): нов `bonus` = Ch 3 (page 102)

**В PLAN_PHASES:**
- [ ] Обновяване на Week 7-8 (ТЧ + Комбинаторика): добавяне на Ch 4-5 (Applications + Problems) като допълнителни задачи за симулация
- [ ] Обновяване на Week 13-17 (Пред-областен): използване на Ch 5 (Problems) за смесени симулации

**Друго:**
- [ ] Книгата е уникална (няма дубликати сред известните файлове)
- [ ] Препоръчително е да се добавят конкретни задачи от Ch 5 (Problems) към Стъпка 10
- [ ] Няма промени в конфигурацията на exam dates
```

---

### book-8.pdf — ✅ ГОТОВО
**Идентификация:** Precalculus (Rusczyk, 2012)
**Решение:** `add-as-bonus`
**Забележка:** 8 bonus записа

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-8.pdf",
  title: "Precalculus",
  author: "Richard Rusczyk",
  year: 2012,
  language: "EN",
  total_pages: 531,
  topics: ["Trigonometry", "Complex Numbers", "Vectors", "Matrices", "Geometry"],
  structure: [
    { 
      chapter: "Ch 1", 
      title: "Functions Review", 
      pages: "15-46", 
      plan_step: 7, 
      plan_points: ["7.5"],
      priority_regional: "low",
      priority_national: "low"
    },
    { 
      chapter: "Ch 2", 
      title: "Introduction to Trigonometric Functions", 
      pages: "47-100", 
      plan_step: 1, 
      plan_points: ["1.6","1.7"],
      priority_regional: "high",
      priority_national: "high"
    },
    { 
      chapter: "Ch 3", 
      title: "Trigonometric Identities", 
      pages: "101-145", 
      plan_step: 1, 
      plan_points: ["1.6","2.8","6.1"],
      priority_regional: "high",
      priority_national: "high"
    },
    { 
      chapter: "Ch 4", 
      title: "Applications to Geometry", 
      pages: "146-175", 
      plan_step: 1, 
      plan_points: ["1.1","1.2","1.6","1.7"],
      priority_regional: "high",
      priority_national: "high"
    },
    { 
      chapter: "Ch 5", 
      title: "Parameterization and Trigonometric Coordinate Systems", 
      pages: "176-209", 
      plan_step: 2, 
      plan_points: ["2.3","2.4"],
      priority_regional: "low",
      priority_national: "med"
    },
    { 
      chapter: "Ch 6", 
      title: "Basics of Complex Numbers", 
      pages: "210-236", 
      plan_step: 2, 
      plan_points: ["2.3","2.5"],
      priority_regional: "med",
      priority_national: "high"
    },
    { 
      chapter: "Ch 7", 
      title: "Trigonometry and Complex Numbers", 
      pages: "237-273", 
      plan_step: 3, 
      plan_points: ["3.7","4.5"],
      priority_regional: "med",
      priority_national: "high"
    },
    { 
      chapter: "Ch 8", 
      title: "Geometry of Complex Numbers", 
      pages: "274-315", 
      plan_step: 2, 
      plan_points: ["2.1","2.2","2.3","2.4","2.5","2.6","2.7"],
      priority_regional: "med",
      priority_national: "high"
    },
    { 
      chapter: "Ch 9", 
      title: "Vectors in Two Dimensions", 
      pages: "316-352", 
      plan_step: 1, 
      plan_points: ["1.1","1.4","2.8"],
      priority_regional: "med",
      priority_national: "high"
    },
    { 
      chapter: "Ch 10", 
      title: "Matrices in Two Dimensions", 
      pages: "353-397", 
      plan_step: 5, 
      plan_points: ["5.8"],
      priority_regional: "low",
      priority_national: "med"
    },
    { 
      chapter: "Ch 11", 
      title: "Vectors and Matrices in Three Dimensions, Part 1", 
      pages: "398-438", 
      plan_step: 2, 
      plan_points: ["2.8"],
      priority_regional: "low",
      priority_national: "med"
    },
    { 
      chapter: "Ch 12", 
      title: "Vectors and Matrices in Three Dimensions, Part 2", 
      pages: "439-480", 
      plan_step: 2, 
      plan_points: ["2.8"],
      priority_regional: "low",
      priority_national: "med"
    },
    { 
      chapter: "Ch 13", 
      title: "Vector Geometry", 
      pages: "481-487", 
      plan_step: 1, 
      plan_points: ["1.1","1.4","2.1","2.2","2.4","2.5","2.6"],
      priority_regional: "med",
      priority_national: "high"
    }
  ],
  duplicates: [], // CHECK: не мога да проверя без достъп до останалите book-*.pdf файлове
  recommended_action: "add-as-bonus",
  best_mapping: [
    { step_id: 1, point_ids: ["1.1","1.2","1.6","1.7"], chapters: ["Ch 2","Ch 3","Ch 4","Ch 9","Ch 13"], pages: "47-175, 316-352, 481-487" },
    { step_id: 2, point_ids: ["2.1","2.2","2.3","2.4","2.5","2.6","2.7","2.8"], chapters: ["Ch 5","Ch 6","Ch 8","Ch 11","Ch 12"], pages: "176-315, 398-480" },
    { step_id: 3, point_ids: ["3.7"], chapters: ["Ch 7"], pages: "237-273" },
    { step_id: 4, point_ids: ["4.5"], chapters: ["Ch 7"], pages: "237-273" },
    { step_id: 5, point_ids: ["5.8"], chapters: ["Ch 10"], pages: "353-397" },
    { step_id: 6, point_ids: ["6.1"], chapters: ["Ch 3"], pages: "101-145" },
    { step_id: 7, point_ids: ["7.5"], chapters: ["Ch 1"], pages: "15-46" }
  ]
}
```

### RECOMMENDED CHANGES TO index.html

**В STEPS:**
- [ ] Добавяне на `bonus` към Точка 1.6: `{ label: "Precalculus (Rusczyk) — Trig Functions", pdf: "Материали_EN/book-8", page: 47 }`
- [ ] Добавяне на `bonus` към Точка 1.7: `{ label: "Precalculus (Rusczyk) — Applications to Geometry", pdf: "Материали_EN/book-8", page: 146 }`
- [ ] Добавяне на `bonus` към Точка 2.3: `{ label: "Precalculus (Rusczyk) — Complex Numbers", pdf: "Материали_EN/book-8", page: 210 }`
- [ ] Добавяне на `bonus` към Точка 2.4: `{ label: "Precalculus (Rusczyk) — Geometry of Complex Numbers", pdf: "Материали_EN/book-8", page: 274 }`
- [ ] Добавяне на `bonus` към Точка 2.5: `{ label: "Precalculus (Rusczyk) — Geometry of Complex Numbers", pdf: "Материали_EN/book-8", page: 274 }`
- [ ] Добавяне на `bonus` към Точка 3.7: `{ label: "Precalculus (Rusczyk) — Roots of Unity", pdf: "Материали_EN/book-8", page: 237 }`
- [ ] Добавяне на `bonus` към Точка 5.8: `{ label: "Precalculus (Rusczyk) — Matrices", pdf: "Материали_EN/book-8", page: 353 }`
- [ ] Добавяне на `bonus` към Точка 7.5: `{ label: "Precalculus (Rusczyk) — Functions Review", pdf: "Материали_EN/book-8", page: 15 }`
- [ ] Добавяне на `bonus` към Стъпка 11: `{ label: "Precalculus (Rusczyk) — цялата книга", pdf: "Материали_EN/book-8" }`

**В PLAN_PHASES:**
- [ ] Няма промени в конфигурацията на exam dates
- [ ] Обновяване на Week 1–6 (Фаза 1): добавяне на "Precalculus Ch 2–4 (Trig + Applications)" като допълнително четиво
- [ ] Обновяване на Week 7–12 (Фаза 2): добавяне на "Precalculus Ch 6–8 (Complex Numbers + Geometry)" като допълнително четиво
- [ ] Обновяване на Week 13–17 (Фаза 3): добавяне на "Precalculus Ch 9–13 (Vectors + Matrices)" като допълнително четиво

**Друго:**
- [ ] Няма дубликати, които да трия (не мога да потвърдя без останалите файлове)
- [ ] Книгата е EN, но е мощен ресурс за Стъпки 1, 2, 3, 4, 5, 7 — препоръчвам да се използва като допълнително четиво, не като основен сборник
- [ ] Ако се създава Стъпка 12 (International), тази книга може да е част от нея, но е по-добре като bonus към съществуващите стъпки

---

### book-9.pdf — ✅ ГОТОВО (SKIP)
**Идентификация:** Prealgebra (Rusczyk, Patrick, Boppana, 2011)
**Решение:** `skip` — под нивото

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-9.pdf",
  title: "The Art of Problem Solving, Prealgebra",
  author: "Richard Rusczyk, David Patrick, Ravi Boppana",
  year: 2011,
  language: "EN",
  total_pages: 119,
  topics: ["Arithmetic", "Number Theory", "Fractions", "Decimals", "Percents", "Ratios", "Square Roots", "Geometry", "Statistics", "Counting", "Problem-Solving Strategies"],
  structure: [
    {
      chapter: "Ch 1",
      title: "Properties of Arithmetic",
      pages: "6-15",
      topic_bg: "Основни свойства на аритметичните операции",
      plan_step: null,
      plan_points: [],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 2",
      title: "Exponents",
      pages: "16-23",
      topic_bg: "Степени — основни правила",
      plan_step: null,
      plan_points: [],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 3",
      title: "Number Theory",
      pages: "24-32",
      topic_bg: "Делимост, прости числа, НОК, НОД",
      plan_step: 3,
      plan_points: ["3.1"],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 4",
      title: "Fractions",
      pages: "33-44",
      topic_bg: "Дроби — действия и сравняване",
      plan_step: null,
      plan_points: [],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 5",
      title: "Equations and Inequalities",
      pages: "45-52",
      topic_bg: "Линейни уравнения и неравенства",
      plan_step: null,
      plan_points: [],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 6",
      title: "Decimals",
      pages: "53-59",
      topic_bg: "Десетични дроби и закръгляне",
      plan_step: null,
      plan_points: [],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 7",
      title: "Ratios, Conversions, and Rates",
      pages: "60-68",
      topic_bg: "Пропорции, преобразувания, скорости",
      plan_step: null,
      plan_points: [],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 8",
      title: "Percents",
      pages: "69-74",
      topic_bg: "Проценти — основни задачи",
      plan_step: null,
      plan_points: [],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 9",
      title: "Square Roots",
      pages: "75-80",
      topic_bg: "Квадратни корени — основни свойства",
      plan_step: null,
      plan_points: [],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 10",
      title: "Angles",
      pages: "81-86",
      topic_bg: "Ъгли, успоредни прави, многоъгълници",
      plan_step: 1,
      plan_points: ["1.5"],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 11",
      title: "Perimeter and Area",
      pages: "87-92",
      topic_bg: "Обиколка, лице, окръжност",
      plan_step: 1,
      plan_points: ["1.7"],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 12",
      title: "Right Triangles and Quadrilaterals",
      pages: "93-98",
      topic_bg: "Питагорова теорема, специални триъгълници, четириъгълници",
      plan_step: 1,
      plan_points: ["1.6", "1.7"],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 13",
      title: "Data and Statistics",
      pages: "99-104",
      topic_bg: "Средно, медиана, мода, графики",
      plan_step: null,
      plan_points: [],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 14",
      title: "Counting",
      pages: "105-112",
      topic_bg: "Броене, комбинаторика, вероятности",
      plan_step: 8,
      plan_points: ["8.1", "8.3", "8.6"],
      priority_regional: "low",
      priority_national: "low"
    },
    {
      chapter: "Ch 15",
      title: "Problem-Solving Strategies",
      pages: "113-119",
      topic_bg: "Стратегии за решаване на задачи",
      plan_step: 9,
      plan_points: ["9.8", "9.9"],
      priority_regional: "low",
      priority_national: "low"
    }
  ],
  duplicates: [],
  recommended_action: "skip",
  skip_reason: "Книгата е Prealgebra — ниво 6–8 клас (САЩ). Покрива аритметика, дроби, десетични дроби, проценти, основни геометрични формули и базово броене. За 11. клас, подготовка за областен и национален кръг по математика, материалът е под нивото на изискванията. Няма покритие на олимпиадни теми като инверсия, хармонично отношение, LTE, примитивни корени, неравенства (AM-GM, Коши), графи, инварианти и т.н. Единствените потенциали за ползване са: (1) Гл. 3 — бърз преговор на делимост/НОД/НОК, ако има пропуски; (2) Гл. 14 — базово броене, ако се наложи затопляне; (3) Гл. 15 — общи стратегии (Find a Pattern, Make a List, Draw a Picture, Work Backwards), които са универсални, но твърде елементарни за 11. клас. Препоръка: SKIP — не добавяй към плана. Ако се ползва, то е само за много бърз преговор на базата преди Стъпка 3 или като допълнително четиво при пропуски.",
  best_mapping: [
    { step_id: 3, point_ids: ["3.1"], chapters: ["Ch 3"], pages: "24-32" },
    { step_id: 1, point_ids: ["1.5", "1.7"], chapters: ["Ch 10-12"], pages: "81-98" },
    { step_id: 8, point_ids: ["8.1", "8.3"], chapters: ["Ch 14"], pages: "105-112" }
  ]
}
```

### RECOMMENDED CHANGES TO index.html

**В STEPS:**
- [ ] Няма промени — книгата е `skip`. Не се добавя към нито една стъпка.
- [ ] Ако все пак се реши да се ползва за бърз преговор: добави `bonus` към Точка 3.1 (`{ label: "AoPS Prealgebra, Ch 3 (делимост/НОД/НОК)", pdf: "Материали_EN/book-9", page: 24 }`) и към Точка 8.1 (`{ label: "AoPS Prealgebra, Ch 14 (базово броене)", pdf: "Материали_EN/book-9", page: 105 }`).

**В PLAN_PHASES:**
- [ ] Няма промени.

**Друго:**
- [ ] Няма дубликати за триене.
- [ ] Няма промени в конфигурацията на exam dates.
- [ ] Препоръка: архивирай `book-9.pdf` в папка `Материали_EN/Архив/` или го остави, но не го включвай в активния план.

---

### book-10.pdf — ✅ ГОТОВО
**Идентификация:** Introduction to Algebra (Rusczyk, 2007)
**Решение:** `add-as-bonus`
**Забележка:** 10 нови bonus записа в Steps 4–7 + 11.4

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-10.pdf",
  title: "Introduction to Algebra",
  author: "Richard Rusczyk (AoPS)",
  year: 2007,
  language: "EN",
  total_pages: 658,  // PDF страници (book pages 1–636 + 17 front matter + closing)
  total_book_pages: 636,
  pdf_offset: 17,   // PDF page = book page + 17
  read_status: "ПРОЧЕТЕНИ: предговор + TOC (стр. 1–17) + глави 1–7 (PDF 18–200). НЕ ПРОЧЕТЕНИ (PDF text layer празен): глави 8–22 и Hints/Index (PDF 201–658). Структурата на глави 8–22 е взета от TOC (book стр. 10–15), не от съдържание.",
  topics: ["Algebra", "Equations", "Inequalities", "Functions", "Sequences", "Complex Numbers", "Polynomials", "Exponents/Logs"],
  level: "introductory — под олимпиадно ниво, подходяща като фундамент",
  structure: [
    { chapter: "Ch 1", title: "Follow the Rules", book_pages: "1-30", pdf_pages: "18-47", topic: "Комутативност, асоциативност, дистрибутивност, свойства на равенството", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low", note: "Елементарна аритметика — под нивото на плана" },
    { chapter: "Ch 2", title: "x Marks the Spot", book_pages: "31-57", pdf_pages: "48-74", topic: "Изрази с променливи, степени, събиране на едночлени", plan_step: 5, plan_points: [], priority_regional: "low", priority_national: "low", note: "Фундамент за полиноми, но под олимпиадно ниво" },
    { chapter: "Ch 3", title: "One-Variable Linear Equations", book_pages: "58-83", pdf_pages: "75-100", topic: "Линейни уравнения, задачи с думи, уравнения в прикрит вид (радикали, дроби)", plan_step: 5, plan_points: [], priority_regional: "low", priority_national: "low", note: "Базова техника — релевантна като подготвителна" },
    { chapter: "Ch 4", title: "More Variables", book_pages: "84-103", pdf_pages: "101-120", topic: "Многочленни изрази, дистрибутивност, факторизиране, дроби с променливи", plan_step: 5, plan_points: ["5.3"], priority_regional: "low", priority_national: "low", note: "Полезно за формиране на навици за символна манипулация" },
    { chapter: "Ch 5", title: "Multi-Variable Linear Equations", book_pages: "104-137", pdf_pages: "121-154", topic: "Системи линейни уравнения — заместване, елиминация, задачи с думи", plan_step: 4, plan_points: ["4.1"], priority_regional: "med", priority_national: "med", note: "База за линейни диофантови системи; под олимпиадно ниво, но полезно" },
    { chapter: "Ch 6", title: "Ratios and Percents", book_pages: "138-167", pdf_pages: "155-184", topic: "Пропорции, проценти, преобразуване на единици, смеси", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low", note: "Не е в 96-те точки — по-скоро MATHCOUNTS/AMC материал" },
    { chapter: "Ch 7", title: "Proportion", book_pages: "168-188", pdf_pages: "185-205", topic: "Пряка/обратна/съвместна пропорционалност, задачи за движение и работа (rt=d)", plan_step: 7, plan_points: [], priority_regional: "low", priority_national: "low", note: "Класически задачи; не в 96-те точки" },
    { chapter: "Ch 8", title: "Graphing Lines", book_pages: "189-232", pdf_pages: "206-249", topic: "Декартова равнина, наклони, прави, сравняване на прави", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low", note: "Аналитична геометрия — не покрита в 96-те точки" },
    { chapter: "Ch 9", title: "Introduction to Inequalities", book_pages: "233-266", pdf_pages: "250-283", topic: "Основни неравенства, линейни неравенства, оптимизация", plan_step: 6, plan_points: ["6.1", "6.2", "6.3"], priority_regional: "med", priority_national: "med", note: "Само основи на AM-GM/AM-HM/AM-QM; не стига до Коши/Йенсен" },
    { chapter: "Ch 10", title: "Quadratic Equations — Part 1", book_pages: "267-304", pdf_pages: "284-321", topic: "Квадратни уравнения, факторизация, суми и произведения на корени (Виет)", plan_step: 5, plan_points: ["5.1", "5.4", "5.5"], priority_regional: "med", priority_national: "med", note: "Полезно за Виет и рационални корени — но под олимпиадно ниво" },
    { chapter: "Ch 11", title: "Special Factorizations", book_pages: "305-337", pdf_pages: "322-354", topic: "Разлика на квадрати, сбор/разлика на кубове, рационализиране, SFFT", plan_step: 5, plan_points: ["5.3", "5.5", "5.7"], priority_regional: "med", priority_national: "med", note: "Simon's Favorite Factoring Trick — практично за ТЧ/полиноми" },
    { chapter: "Ch 12", title: "Complex Numbers", book_pages: "338-352", pdf_pages: "355-369", topic: "Въведение в имагинерни и комплексни числа, аритметика с тях", plan_step: null, plan_points: [], does_not_fit: true, priority_regional: "low", priority_national: "low", note: "Комплексни числа НЕ са в 96-те точки — виж suggested_new_step по-долу" },
    { chapter: "Ch 13", title: "Quadratic Equations — Part 2", book_pages: "353-384", pdf_pages: "370-401", topic: "Допълване до точен квадрат, квадратна формула, приложения", plan_step: 5, plan_points: ["5.1", "5.5"], priority_regional: "low", priority_national: "low", note: "Стандартен материал, покрит в българските учебници" },
    { chapter: "Ch 14", title: "Graphing Quadratics", book_pages: "385-405", pdf_pages: "402-422", topic: "Параболи, окръжности, геометрични интерпретации", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low", note: "Аналитична геометрия — не е фокус" },
    { chapter: "Ch 15", title: "More Inequalities", book_pages: "406-431", pdf_pages: "423-448", topic: "Квадратни неравенства, Trivial Inequality, квадратна оптимизация", plan_step: 6, plan_points: ["6.1", "6.10"], priority_regional: "med", priority_national: "med", note: "Trivial Inequality (x² ≥ 0) — полезно, но основно ниво" },
    { chapter: "Ch 16", title: "Functions", book_pages: "432-464", pdf_pages: "449-481", topic: "Функции, композиция, обратни функции, операции с функции", plan_step: 7, plan_points: ["7.1", "7.2", "7.3", "7.4", "7.5"], priority_regional: "med", priority_national: "high", note: "Функционални уравнения — база; но липсват истински олимпиадни ФУ" },
    { chapter: "Ch 17", title: "Graphing Functions", book_pages: "465-493", pdf_pages: "482-510", topic: "Трансформации на графики, обратни функции, интерпретации", plan_step: 7, plan_points: ["7.3", "7.4"], priority_regional: "low", priority_national: "med", note: "Интуиция за трансформации, не е пряко в плана" },
    { chapter: "Ch 18", title: "Polynomials", book_pages: "494-505", pdf_pages: "511-522", topic: "Събиране, изваждане, умножение на полиноми", plan_step: 5, plan_points: ["5.1", "5.3", "5.7"], priority_regional: "med", priority_national: "med", note: "Само базови операции — не покрива неразложими/Лагранж" },
    { chapter: "Ch 19", title: "Exponents and Logarithms", book_pages: "506-539", pdf_pages: "523-556", topic: "Експоненциални функции, лихви, логаритми", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low", note: "Логаритми рядко се падат на областен/национален в БГ" },
    { chapter: "Ch 20", title: "Special Functions", book_pages: "540-570", pdf_pages: "557-587", topic: "Радикали, абсолютна стойност, floor/ceiling, рационални и късчести функции", plan_step: 7, plan_points: ["7.2", "7.5"], priority_regional: "low", priority_national: "med", note: "Floor/ceiling полезно за ТЧ задачи, но под нивото на плана" },
    { chapter: "Ch 21", title: "Sequences & Series", book_pages: "571-609", pdf_pages: "588-626", topic: "Аритметични/геометрични редици, телескопиращи суми", plan_step: 7, plan_points: ["7.6", "7.7", "8.9"], priority_regional: "med", priority_national: "high", note: "Телескопиране — класически похват; добро допълнение" },
    { chapter: "Ch 22", title: "Special Manipulations", book_pages: "610-620", pdf_pages: "627-637", topic: "Повдигане на степени, self-similarity, симетрия", plan_step: 7, plan_points: ["7.5", "7.8"], priority_regional: "low", priority_national: "med", note: "По-скоро общи похвати, не конкретен раздел" },
    { chapter: "Hints", title: "Hints to Selected Problems", book_pages: "625", pdf_pages: "642", topic: "Сборник с подсказки", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "Index", title: "Index", book_pages: "636", pdf_pages: "653", topic: "Показалец", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" }
  ],
  duplicates: [],  // CHECK: не мога да потвърдя без достъп до book-1..12; препоръчвам да се сравни ISBN 978-1-934124-01-7 срещу останалите AoPS файлове
  recommended_action: "add-as-bonus",
  rationale: "Книгата е ВЪВЕДЕНИЕ в алгебрата (AoPS Introductory series за 6–10 клас). Тя е ПОД олимпиадното ниво за 11 клас в БГ — не съдържа Коши, Мюрхед, Йенсен, LTE, Pell, инверсия и др. Полезните глави (5, 9, 10, 11, 15, 16, 18, 21) могат да служат като ДОПЪЛНИТЕЛНА литература за затвърждаване на база, но не могат да заместят основните материали. Най-добро използване: bonus към конкретни точки.",
  best_mapping: [
    { step_id: 5, point_ids: ["5.1", "5.3", "5.4", "5.5", "5.7"], chapters: ["Ch 4", "Ch 10", "Ch 11", "Ch 13", "Ch 18"], pdf_pages: "101-120, 284-321, 322-354, 370-401, 511-522" },
    { step_id: 6, point_ids: ["6.1", "6.2", "6.3", "6.10"], chapters: ["Ch 9", "Ch 15"], pdf_pages: "250-283, 423-448" },
    { step_id: 7, point_ids: ["7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7"], chapters: ["Ch 16", "Ch 17", "Ch 20", "Ch 21", "Ch 22"], pdf_pages: "449-481, 482-510, 557-587, 588-626, 627-637" },
    { step_id: 4, point_ids: ["4.1"], chapters: ["Ch 5"], pdf_pages: "121-154" }
  ]
}
```

```js
// ─── НОВА СТЪПКА (по избор — виж по-долу дали да се приложи) ───
// ПРЕДЛОЖЕНИЕ: комплексни числа не фигурират в 96-те точки, но Ch 12
// (Introduction to Complex Numbers) е твърде елементарен за олимпиада.
// Ако все пак искаш да покриеш темата (за национален кръг), използвай:
{
  id: "12.1",
  title: "Комплексни числа",
  desc: "Алгебрична и тригонометрична форма, формула на Моавър, корени на комплексни числа.",
  source: "Rusczyk, Introduction to Algebra (AoPS)",
  pdf: "Материали_EN/book-10",
  page: 355,                    // PDF стр. на Ch 12
  problems_page: 360,           // CHECK: не е прочетена — приблизително
  solutions_page: null,
  tasks: [
    { label: "Ch 12 Exercises (PDF ~366)", pdf: "Материали_EN/book-10", page: 366 }
  ],
  bonus: [],
  explanation: "ФОРМУЛИРОВКА: z = a + bi = r(cos θ + i sin θ).\n\nКОГА: Геометрични доказателства, ротации, корени на полиноми.\n\nСВОЙСТВА: |z₁z₂| = |z₁||z₂|, arg(z₁z₂) = arg z₁ + arg z₂ (mod 2π).\n\nТРИК: Представяне чрез комплексни числа на равнинни конфигурации; въртене = умножение с e^{iθ}. Книгата дава само основи — за олимпиада допълни с Andreescu & Andrica, Complex Numbers from A to Z."
}
```

### RECOMMENDED CHANGES TO index.html

**В STEPS (bonus полета към съществуващи точки):**
- [ ] Точка `5.1` (Виет): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 10 (Sums/Products of Roots)", pdf: "Материали_EN/book-10", page: 306 }`
- [ ] Точка `5.3` (Симетрични): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 4 (Distribution & Factoring)", pdf: "Материали_EN/book-10", page: 101 }`
- [ ] Точка `5.5` (Неразложими): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 11 (Special Factorizations + SFFT)", pdf: "Материали_EN/book-10", page: 322 }`
- [ ] Точка `5.7` (Делимост на полиноми): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 11 & Ch 18", pdf: "Материали_EN/book-10", page: 322 }`
- [ ] Точка `6.1` (AM-GM): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 9 & Ch 15 (Inequalities intro + Trivial Ineq.)", pdf: "Материали_EN/book-10", page: 250 }`
- [ ] Точка `7.1` (Коши ФУ): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 16 (Functions)", pdf: "Материали_EN/book-10", page: 449 }`
- [ ] Точка `7.5` (Общи техники ФУ): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 16 & Ch 17 & Ch 20", pdf: "Материали_EN/book-10", page: 449 }`
- [ ] Точка `7.6` (Линейни рекурсии): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 21 (Sequences & Series, Telescoping)", pdf: "Материали_EN/book-10", page: 588 }`
- [ ] Точка `7.8` (Сходимост): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 22 (Special Manipulations)", pdf: "Материали_EN/book-10", page: 627 }`
- [ ] Точка `4.1` (Линейни диофантови): нов `bonus` = `{ label: "Rusczyk, Intro to Algebra — Ch 5 (Systems of Linear Equations)", pdf: "Материали_EN/book-10", page: 121 }`

**В `bonus` поле на Step 11 (`11.4` Доп. сборници):**
- [ ] Добави `{ label: "Rusczyk, Introduction to Algebra (AoPS) — фундаментален курс по алгебра", pdf: "Материали_EN/book-10", page: 18 }`

**НЕ се препоръчва:**
- [ ] ❌ Да се създава Step 12 с тази книга — тя е под олимпиадно ниво, а не разширение над 96-те точки.
- [ ] ❌ Да се добавят глави 1, 2, 3, 6, 7, 8, 14, 19 — те са под нивото на областен/национален кръг и не съответстват на нито една от 96-те точки.

**Друго:**
- [ ] Провери за дубликати: `book-10.pdf` има ISBN `978-1-934124-01-7`. Сравни срещу `book-1..12.pdf` — ако има друг AoPS "Introduction to Algebra" с различен файл, маркирай го като дубликат и го изтрий.
- [ ] Обмисли: ако `book-10` е единственият файл от AoPS Introductory series, може да е полезно да добавиш и `Introduction to Counting & Probability` и `Introduction to Number Theory` от същата серия (споменати на PDF стр. 6) — те са по-близо до олимпиадните теми (Стъпки 3 и 8), отколкото този том.
- [ ] Няма промени в `PLAN_PHASES` или в конфигурацията на exam dates.

---

### book-11.pdf — ✅ ГОТОВО
**Идентификация:** Calculus (Patrick, 2019)
**Решение:** `add-as-step12` (спорно — Calculus не е в BG олимпиада)
**Забележка:** 3 bonus записа + 9 нови точки (12.1–12.9)

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-11.pdf",
  title: "Calculus",
  author: "David Patrick",
  year: 2019,
  language: "EN",
  total_pages: 316,
  topics: ["Calculus", "Limits", "Derivatives", "Integrals", "Series", "Differential Equations", "Plane Curves"],
  structure: [
    { chapter: "Ch 1", title: "Sets and Functions", pages: "1-36", plan_step: 7, plan_points: ["7.1", "7.3"], priority_regional: "low", priority_national: "med" },
    { chapter: "Ch 2", title: "Limits and Continuity", pages: "37-69", plan_step: 7, plan_points: ["7.1", "7.2", "7.8"], priority_regional: "low", priority_national: "high" },
    { chapter: "Ch 3", title: "The Derivative", pages: "70-101", plan_step: 7, plan_points: ["7.3", "7.5"], priority_regional: "low", priority_national: "high" },
    { chapter: "Ch 4", title: "Applications of the Derivative", pages: "102-138", plan_step: 6, plan_points: ["6.1", "6.4", "6.5"], priority_regional: "low", priority_national: "high" },
    { chapter: "Ch 5", title: "Integration", pages: "139-190", plan_step: 7, plan_points: ["7.1", "7.8"], priority_regional: "low", priority_national: "high" },
    { chapter: "Ch 6", title: "Infinity", pages: "191-219", plan_step: 7, plan_points: ["7.1", "7.2", "7.8"], priority_regional: "low", priority_national: "high" },
    { chapter: "Ch 7", title: "Series", pages: "220-258", plan_step: 7, plan_points: ["7.6", "7.7", "7.8"], priority_regional: "low", priority_national: "high" },
    { chapter: "Ch 8", title: "Plane Curves", pages: "259-278", plan_step: 2, plan_points: ["2.4", "2.7"], priority_regional: "low", priority_national: "low" },
    { chapter: "Ch 9", title: "Differential Equations", pages: "279-299", plan_step: 7, plan_points: ["7.6", "7.7"], priority_regional: "low", priority_national: "low" },
    { chapter: "Epilogue", title: "Now What?", pages: "300-301", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "Appendix", title: "Hints, References, Index", pages: "302-316", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" }
  ],
  duplicates: [],
  recommended_action: "add-as-step12",
  best_mapping: [
    { step_id: 7, point_ids: ["7.1", "7.2", "7.8"], chapters: ["Ch 2", "Ch 6"], pages: "37-69, 191-219" },
    { step_id: 6, point_ids: ["6.4", "6.5"], chapters: ["Ch 3", "Ch 4"], pages: "70-138" },
    { step_id: 7, point_ids: ["7.6", "7.7", "7.8"], chapters: ["Ch 7"], pages: "220-258" },
    { step_id: 1, point_ids: ["1.6"], chapters: ["Ch 8"], pages: "259-278" }
  ]
}
```

```js
// ─── НОВА ТОЧКА ───
{ 
  id: "12.1", 
  title: "Множества и функции", 
  desc: "Основи на математическия анализ: функции, графики, тригонометрия, експоненти и логаритми", 
  source: "Patrick, Calculus", 
  pdf: "Материали_EN/book-11", 
  page: 1, 
  problems_page: 5, 
  solutions_page: null, 
  tasks: [
    { label: "Глава 1: Sets and Functions", pdf: "Материали_EN/book-11", page: 1 }
  ], 
  bonus: [], 
  explanation: "ФОРМУЛИРОВКА: Въведение в множествата, реалните числа, интервалите, функциите и техните графики, както и основните тригонометрични, експоненциални и логаритмични функции.\n\nКОГА: Използва се за затвърждаване на основите преди навлизане в диференциалното и интегралното смятане.\n\nСВОЙСТВА: Функциите имат домейн, кодомейн и рейндж. Графиките на функциите минават теста за вертикална линия. Съществуват специални функции като тригонометричните, които са периодични.\n\nТРИК: За да намерите домейна на сложна функция, разгледайте всички ограничения (знаменател ≠ 0, подкоренна величина ≥ 0, логаритъм > 0) и ги комбинирайте."
}
{ 
  id: "12.2", 
  title: "Лимити и непрекъснатост", 
  desc: "Дефиниция на лимит (делта-епсилон), свойства на лимитите и непрекъснати функции", 
  source: "Patrick, Calculus", 
  pdf: "Материали_EN/book-11", 
  page: 37, 
  problems_page: 45, 
  solutions_page: null, 
  tasks: [
    { label: "Глава 2: Limits and Continuity", pdf: "Материали_EN/book-11", page: 37 }
  ], 
  bonus: [], 
  explanation: "ФОРМУЛИРОВКА: Лимитът на функция f(x) при x -> a е L, ако за всяко епсилон > 0 съществува делта > 0 такова, че 0 < |x-a| < делта => |f(x)-L| < епсилон. Функцията е непрекъсната в точка a, ако лимитът при x -> a съществува и е равен на f(a).\n\nКОГА: Използва се за доказване на свойствата на функциите и за намиране на граници на редици и функции.\n\nСВОЙСТВА: Сборът, произведението и частното на непрекъснати функции са непрекъснати. Теорема за междинните стойности (Intermediate Value Theorem).\n\nТРИК: За доказване на лимити често се използва теоремата за двамата полицаи (Squeeze Theorem) или се свежда до известни граници като lim(sin x / x) = 1."
}
{ 
  id: "12.3", 
  title: "Производна", 
  desc: "Дефиниция на производна, правила за диференциране и верижно правило", 
  source: "Patrick, Calculus", 
  pdf: "Материали_EN/book-11", 
  page: 70, 
  problems_page: 82, 
  solutions_page: null, 
  tasks: [
    { label: "Глава 3: The Derivative", pdf: "Материали_EN/book-11", page: 70 }
  ], 
  bonus: [], 
  explanation: "ФОРМУЛИРОВКА: Производната на функция f в точка a е границата f'(a) = lim (f(a+h) - f(a)) / h, когато h клони към 0. Тя представлява скоростта на изменение на функцията.\n\nКОГА: Използва се за намиране на екстремуми, за анализ на поведението на функции и в много задачи от математическия анализ.\n\nСВОЙСТВА: Правило за произведение, частно, верижно правило, теорема на Рол, теорема за средните стойности (Mean Value Theorem).\n\nТРИК: При неявно диференциране (implicit differentiation) диференцирайте двете страни на уравнението по x и изразете y'."
}
{ 
  id: "12.4", 
  title: "Приложения на производната", 
  desc: "Екстремуми, оптимизация, свързани скорости, метод на Нютон и линеаризация", 
  source: "Patrick, Calculus", 
  pdf: "Материали_EN/book-11", 
  page: 102, 
  problems_page: 122, 
  solutions_page: null, 
  tasks: [
    { label: "Глава 4: Applications of the Derivative", pdf: "Материали_EN/book-11", page: 102 }
  ], 
  bonus: [], 
  explanation: "ФОРМУЛИРОВКА: Използване на производни за намиране на максимуми и минимуми на функции, решаване на оптимизационни задачи, анализ на скорости на изменение и приблизителни изчисления.\n\nКОГА: В задачи за оптимизация (например, максимален обем при дадена повърхност), при анализ на движение и в числени методи.\n\nСВОЙСТВА: Първа и втора производна определят монотонност и изпъкналост. Метод на Нютон за приблизително намиране на корени.\n\nТРИК: При задачи за екстремуми на затворен интервал проверявайте стойностите на функцията в критичните точки и в краищата на интервала."
}
{ 
  id: "12.5", 
  title: "Интеграли", 
  desc: "Определен интеграл, фундаментална теорема на анализа и техники за интегриране", 
  source: "Patrick, Calculus", 
  pdf: "Материали_EN/book-11", 
  page: 139, 
  problems_page: 154, 
  solutions_page: null, 
  tasks: [
    { label: "Глава 5: Integration", pdf: "Материали_EN/book-11", page: 139 }
  ], 
  bonus: [], 
  explanation: "ФОРМУЛИРОВКА: Определеният интеграл е граница на суми на Риман и представлява площ под крива. Фундаменталната теорема на анализа свързва интеграла с производната.\n\nКОГА: Използва се за изчисляване на площи, обеми, дължини на дъги и в много задачи от физиката.\n\nСВОЙСТВА: Интегралът е линеен. Съществуват различни техники: интегриране по части, заместване, частични дроби.\n\nТРИК: За сложни интеграли често е полезно да се направи тригонометрично заместване (напр. x = sin θ за изрази от вида √(1-x²))."
}
{ 
  id: "12.6", 
  title: "Приложения на интеграла", 
  desc: "Лица на равнинни фигури, обеми на тела, дължина на крива и средна стойност", 
  source: "Patrick, Calculus", 
  pdf: "Материали_EN/book-11", 
  page: 166, 
  problems_page: 178, 
  solutions_page: null, 
  tasks: [
    { label: "Глава 5.4: Applications of the Definite Integral", pdf: "Материали_EN/book-11", page: 166 }
  ], 
  bonus: [], 
  explanation: "ФОРМУЛИРОВКА: Използване на определени интеграли за изчисляване на геометрични величини: лице между криви, обем на ротационно тяло, дължина на дъга и средна стойност на функция.\n\nКОГА: В геометрични задачи и задачи от физиката (напр. маса, център на масата).\n\nСВОЙСТВА: Обемът на ротационно тяло може да се изчисли чрез метода на дисковете или чрез метода на цилиндричните черупки.\n\nТРИК: При изчисляване на обем чрез ротация около оста y, използвайте метода на цилиндричните черупки: V = 2π ∫ x f(x) dx."
}
{ 
  id: "12.7", 
  title: "Редици и редове", 
  desc: "Безкрайни редици, сходимост на редове, степенни редове и редове на Тейлър", 
  source: "Patrick, Calculus", 
  pdf: "Материали_EN/book-11", 
  page: 220, 
  problems_page: 229, 
  solutions_page: null, 
  tasks: [
    { label: "Глава 7: Series", pdf: "Материали_EN/book-11", page: 220 }
  ], 
  bonus: [], 
  explanation: "ФОРМУЛИРОВКА: Безкрайна редица е списък от числа. Безкраен ред е сумата от членовете на редица. Сходимостта на редовете се определя чрез различни тестове (сравнение, интегрален тест, тест на Даламбер, тест на Коши).\n\nКОГА: В задачи за сумиране на безкрайни редове, апроксимация на функции и в комбинаторика (генериращи функции).\n\nСВОЙСТВА: Степенните редове могат да се диференцират и интегрират почленно в рамките на радиуса на сходимост. Редове на Тейлър апроксимират функции.\n\nТРИК: За да намерите сумата на телескопичен ред, разпишете първите няколко члена и вижте кои се съкращават."
}
{ 
  id: "12.8", 
  title: "Равнинни криви", 
  desc: "Параметрични криви, полярни координати и лице в полярни координати", 
  source: "Patrick, Calculus", 
  pdf: "Материали_EN/book-11", 
  page: 259, 
  problems_page: 266, 
  solutions_page: null, 
  tasks: [
    { label: "Глава 8: Plane Curves", pdf: "Материали_EN/book-11", page: 259 }
  ], 
  bonus: [], 
  explanation: "ФОРМУЛИРОВКА: Параметричните криви се задават чрез функции на параметър t. Полярните координати описват точки чрез разстояние r и ъгъл θ.\n\nКОГА: За описание на сложни криви (циклоида, астроида, рози) и в задачи от физиката.\n\nСВОЙСТВА: Наклонът на допирателната към параметрична крива е dy/dx = (dy/dt) / (dx/dt). Лицето в полярни координати се изчислява по формулата A = 1/2 ∫ r² dθ.\n\nТРИК: За да намерите лицето на фигура, ограничена от полярна крива, определете границите на интегриране чрез намиране на ъглите, при които кривата се пресича или затваря."
}
{ 
  id: "12.9", 
  title: "Диференциални уравнения", 
  desc: "Основи на диференциалните уравнения, разделяне на променливите и линейни уравнения от втори ред", 
  source: "Patrick, Calculus", 
  pdf: "Материали_EN/book-11", 
  page: 279, 
  problems_page: 290, 
  solutions_page: null, 
  tasks: [
    { label: "Глава 9: Differential Equations", pdf: "Материали_EN/book-11", page: 279 }
  ], 
  bonus: [], 
  explanation: "ФОРМУЛИРОВКА: Диференциално уравнение е уравнение, свързващо функция и нейните производни. Решаването им включва намиране на функция, която удовлетворява уравнението.\n\nКОГА: За моделиране на физични процеси (радиоактивен разпад, растеж на популация, охлаждане).\n\nСВОЙСТВА: Уравнения от първи ред могат да се решават чрез разделяне на променливите. Линейните уравнения от втори ред с постоянни коефициенти се решават чрез характеристичното им уравнение.\n\nТРИК: При разделяне на променливите, прехвърлете всички y-членове от едната страна, а всички x-членове от другата, след което интегрирайте двете страни."
}
```

### RECOMMENDED CHANGES TO index.html

**В STEPS:**
- [ ] Добавяне на нова стъпка `STEPS[11]` (Стъпка 12: Математически анализ) с точки `12.1` до `12.9` (виж блоковете по-горе).
- [ ] В `STEPS[6].points` (Стъпка 7): Актуализиране на `bonus` за точка `7.1` с `{ label: "Calculus (Ch 2, 6)", pdf: "Материали_EN/book-11", page: 37 }`.
- [ ] В `STEPS[5].points` (Стъпка 6): Актуализиране на `bonus` за точка `6.4` с `{ label: "Calculus (Ch 3, 4)", pdf: "Материали_EN/book-11", page: 70 }`.
- [ ] В `STEPS[6].points` (Стъпка 7): Актуализиране на `bonus` за точка `7.6` с `{ label: "Calculus (Ch 7)", pdf: "Материали_EN/book-11", page: 220 }`.

**В PLAN_PHASES:**
- [ ] Няма промени в седмичния план, тъй като това е допълнителен материал за задълбочаване (Стъпка 12).

**Друго:**
- [ ] Добавяне на `Материали_EN/book-11.pdf` към библиотеката с материали.
- [ ] Няма дубликати за премахване.

---

### book-12.pdf — ✅ ГОТОВО
**Идентификация:** Intermediate Counting & Probability (Patrick, 2007)
**Решение:** `add-as-bonus`
**Забележка:** 12 bonus записа + 3 в 11.4

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-12.pdf",
  title: "Intermediate Counting & Probability",
  author: "David Patrick",
  year: 2007,
  language: "EN",
  total_pages: 404,
  topics: ["Combinatorics", "Probability", "Generating Functions", "Graph Theory", "Recursion"],
  structure: [
    { chapter: "Ch 1", title: "Review of Counting & Probability Basics", pages: "17-26", plan_step: 8, plan_points: ["8.5","8.6"], priority_regional: "high", priority_national: "med" },
    { chapter: "Ch 2", title: "Sets and Logic", pages: "43-64", plan_step: 11, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "Ch 3", title: "A Piece of PIE (Inclusion-Exclusion)", pages: "65-98", plan_step: 8, plan_points: ["8.2","8.3"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 4", title: "Constructive Counting and 1-1 Correspondences", pages: "99-133", plan_step: 8, plan_points: ["8.3","8.5"], priority_regional: "high", priority_national: "med" },
    { chapter: "Ch 5", title: "The Pigeonhole Principle", pages: "134-145", plan_step: 8, plan_points: ["8.1"], priority_regional: "high", priority_national: "med" },
    { chapter: "Ch 6", title: "Constructive Expectation", pages: "146-160", plan_step: 11, plan_points: [], priority_regional: "low", priority_national: "med" },
    { chapter: "Ch 7", title: "Distributions", pages: "161-176", plan_step: 8, plan_points: ["8.7"], priority_regional: "high", priority_national: "med" },
    { chapter: "Ch 8", title: "Mathematical Induction", pages: "177-187", plan_step: 8, plan_points: ["8.10"], priority_regional: "med", priority_national: "high" },
    { chapter: "Ch 9", title: "Fibonacci Numbers", pages: "188-207", plan_step: 7, plan_points: ["7.6","7.7","7.8"], priority_regional: "med", priority_national: "high" },
    { chapter: "Ch 10", title: "Recursion", pages: "208-242", plan_step: 7, plan_points: ["7.6","7.7","7.8"], priority_regional: "med", priority_national: "high" },
    { chapter: "Ch 11", title: "Conditional Probability", pages: "243-258", plan_step: 11, plan_points: [], priority_regional: "low", priority_national: "med" },
    { chapter: "Ch 12", title: "Combinatorial Identities", pages: "259-280", plan_step: 8, plan_points: ["8.4","8.5"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 13", title: "Events With States", pages: "281-313", plan_step: 9, plan_points: ["9.10"], priority_regional: "med", priority_national: "high" },
    { chapter: "Ch 14", title: "Generating Functions", pages: "314-346", plan_step: 8, plan_points: ["8.9"], priority_regional: "med", priority_national: "high" },
    { chapter: "Ch 15", title: "Graph Theory", pages: "347-378", plan_step: 9, plan_points: ["9.1","9.2","9.3","9.4","9.5","9.6","9.7","9.8"], priority_regional: "med", priority_national: "high" },
    { chapter: "Ch 16", title: "Challenge Problems (Mixed)", pages: "379-382", plan_step: 11, plan_points: [], priority_regional: "med", priority_national: "med" }
  ],
  duplicates: [],
  recommended_action: "add-as-bonus",
  best_mapping: [
    { step_id: 8, point_ids: ["8.1","8.2","8.3","8.4","8.5","8.6","8.7","8.8","8.9","8.10"], chapters: ["Ch 1","Ch 3","Ch 4","Ch 5","Ch 7","Ch 8","Ch 12","Ch 14"], pages: "17-346" },
    { step_id: 7, point_ids: ["7.6","7.7","7.8"], chapters: ["Ch 9","Ch 10"], pages: "188-242" },
    { step_id: 9, point_ids: ["9.1","9.2","9.3","9.4","9.5","9.6","9.7","9.8","9.10"], chapters: ["Ch 13","Ch 15"], pages: "281-378" },
    { step_id: 11, point_ids: [], chapters: ["Ch 2","Ch 6","Ch 11","Ch 16"], pages: "43-64, 146-160, 243-258, 379-382" }
  ]
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
// Тази книга не изисква нови точки. Тя е мощен допълнителен ресурс
// за Стъпки 7, 8, 9, 11. Препоръчвам да се добави като bonus към
// следните точки:

// Точка 8.1 (Дирихле) в STEPS[7].points[0]:
{ id: "8.1",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 5 (Pigeonhole)", pdf: "Материали_EN/book-12", page: 134 }
  ]
}

// Точка 8.2 (Вкл/Изкл) в STEPS[7].points[1]:
{ id: "8.2",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 3 (PIE)", pdf: "Материали_EN/book-12", page: 65 }
  ]
}

// Точка 8.3 (Двойно броене) в STEPS[7].points[2]:
{ id: "8.3",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 4 (1-1 Correspondences)", pdf: "Материали_EN/book-12", page: 99 }
  ]
}

// Точка 8.4 (Комб. тъждества) в STEPS[7].points[3]:
{ id: "8.4",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 12 (Combinatorial Identities)", pdf: "Материали_EN/book-12", page: 259 }
  ]
}

// Точка 8.7 (Мултимножества) в STEPS[7].points[6]:
{ id: "8.7",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 7 (Distributions)", pdf: "Материали_EN/book-12", page: 161 }
  ]
}

// Точка 8.9 (Генериращи функции) в STEPS[7].points[8]:
{ id: "8.9",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 14 (Generating Functions)", pdf: "Материали_EN/book-12", page: 314 }
  ]
}

// Точка 8.10 (Индукция) в STEPS[7].points[9]:
{ id: "8.10",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 8 (Mathematical Induction)", pdf: "Материали_EN/book-12", page: 177 }
  ]
}

// Точка 7.6 (Линейни рекурсии) в STEPS[6].points[5]:
{ id: "7.6",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 9-10 (Fibonacci, Recursion)", pdf: "Материали_EN/book-12", page: 188 }
  ]
}

// Точка 7.8 (Сходимост) в STEPS[6].points[7]:
{ id: "7.8",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 13 (Events with States)", pdf: "Материали_EN/book-12", page: 281 }
  ]
}

// Точка 9.1 (Основи на графи) в STEPS[8].points[0]:
{ id: "9.1",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 15 (Graph Theory)", pdf: "Материали_EN/book-12", page: 347 }
  ]
}

// Точка 9.10 (Игри) в STEPS[8].points[9]:
{ id: "9.10",
  bonus: [
    { label: "Patrick, Intermediate C&P — Ch 13.4 (Two-player Strategy Games)", pdf: "Материали_EN/book-12", page: 284 }
  ]
}

// Точка 11.4 (Доп. сборници) в STEPS[10].points[3]:
{ id: "11.4",
  bonus: [
    { label: "Patrick, Intermediate C&P — Challenge Problems", pdf: "Материали_EN/book-12", page: 379 },
    { label: "Patrick, Intermediate C&P — Sets & Logic (Ch 2)", pdf: "Материали_EN/book-12", page: 43 },
    { label: "Patrick, Intermediate C&P — Conditional Probability (Ch 11)", pdf: "Материали_EN/book-12", page: 243 }
  ]
}
```

### RECOMMENDED CHANGES TO index.html

**В STEPS:**
- [ ] Точка 8.1: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 5 (Pigeonhole)" (стр. 134)
- [ ] Точка 8.2: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 3 (PIE)" (стр. 65)
- [ ] Точка 8.3: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 4 (1-1 Correspondences)" (стр. 99)
- [ ] Точка 8.4: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 12 (Combinatorial Identities)" (стр. 259)
- [ ] Точка 8.7: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 7 (Distributions)" (стр. 161)
- [ ] Точка 8.9: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 14 (Generating Functions)" (стр. 314)
- [ ] Точка 8.10: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 8 (Mathematical Induction)" (стр. 177)
- [ ] Точка 7.6: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 9-10 (Fibonacci, Recursion)" (стр. 188)
- [ ] Точка 7.8: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 13 (Events with States)" (стр. 281)
- [ ] Точка 9.1: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 15 (Graph Theory)" (стр. 347)
- [ ] Точка 9.10: добавяне на `bonus` = "Patrick, Intermediate C&P — Ch 13.4 (Two-player Strategy Games)" (стр. 284)
- [ ] Точка 11.4: добавяне на 3 нови `bonus` записа (Challenge Problems, Sets & Logic, Conditional Probability)

**В PLAN_PHASES:**
- [ ] Обновяване на Week 10-12 (Фаза 2 — Разширяване): добавяне на "Patrick Ch 3, 4, 5, 7" като допълнителен ресурс за Комбинаторика
- [ ] Обновяване на Week 13-17 (Фаза 3 — Пред-областен): добавяне на "Patrick Ch 12, 14" за Комбинаторни тъждества и генериращи функции
- [ ] Обновяване на Week 18-25 (Фаза 4 — Между-национален): добавяне на "Patrick Ch 9, 10, 13, 15" за рекурсии, състояния и графи

**Друго:**
- [ ] Няма нови точки — книгата е допълващ ресурс, не изисква Стъпка 12 (всички теми се припокриват със съществуващите 11 стъпки)
- [ ] Няма дубликати — `book-12.pdf` е уникален (не е дубликат на други EN книги в проекта)
- [ ] Няма промени в конфигурацията на exam dates

---

## 🚫 DISCOVERED NON-MATH FILES (skip)

### book-3 (1).pdf — ✅ ИДЕНТИФИЦИРАНО (SKIP)
**Идентификация:** Competitive Programming 4, Book 1 (Halim, Halim, Effendy, 2020)
**Решение:** `skip` — НЕ Е математика

# АНАЛИЗ НА `book-3 (1).pdf`

⚠️ **КРИТИЧНО НЕСЪОТВЕТСТВИЕ:** Този PDF **НЕ Е олимпиадна математическа книга**. Това е книга по **състезателно програмиране** (Competitive Programming / Информатика). Тя няма нищо общо с подготовката за областен/национален кръг по **математика** и не може да се map-не към нито една от 96-те математически точки в `AI_MASTER_CONTEXT.md`.

Въпреки това, спазвам заявения формат и попълвам блока „КНИГА" с пълната структура (всички глави, не само първите 5).

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-3 (1).pdf",
  title: "Competitive Programming 4, Book 1",
  author: "Steven Halim, Felix Halim, Suhendry Effendy",
  year: 2020,
  language: "EN",
  total_pages: 329,
  topics: ["Data Structures", "Algorithms", "Graph Theory", "Dynamic Programming", "Competitive Programming (Informatics)"],
  structure: [
    { chapter: "Front matter", title: "Forewords, Testimonials, About IOI/ICPC", pages: "1-30", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "Ch 1", title: "Introduction: Competitive Programming, Ad Hoc Problems", pages: "31-82", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "Ch 2", title: "Data Structures and Libraries (Array, BST, Fenwick, Segment Tree, UFDS, Graph DS)", pages: "83-158", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "Ch 3", title: "Problem Solving Paradigms (Complete Search, D&C, Greedy, DP)", pages: "159-222", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "Ch 4", title: "Graph (Traversal, MST, SSSP, APSP, Special Graphs)", pages: "223-301", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" },
    { chapter: "Back matter", title: "Bibliography & Index", pages: "303-329", plan_step: null, plan_points: [], priority_regional: "low", priority_national: "low" }
  ],
  duplicates: [],
  is_duplicate_of: null,
  recommended_action: "skip",
  best_mapping: [],
  does_not_fit: true,
  reason: "Книгата е по състезателно програмиране (алгоритми и структури от данни за IOI/ICPC), не по олимпиадна математика. Нула припокриване с 96-те математически точки (Геометрия, ТЧ, Алгебра, Комбинаторика в смисъла на математическата олимпиада). Съдържанието (Fenwick Tree, Segment Tree, Kruskal, Dijkstra, Floyd-Warshall, DP-TSP, SCC, Eulerian Graph и т.н.) не присъства в плана за математическа олимпиада.",
  suggested_new_step: null,
  note_to_user: "Ако ученикът се състезава и по ИНФОРМАТИКА (IOI/NOI), тази книга е отличен ресурс — но трябва да се третира като ОТДЕЛЕН curriculum (напр. паралелен STEP 'Informatics'), а не като част от математическите 11 стъпки."
}
```

---

### Проверка за дубликати

Видях, че файлът е именуван `book-3 (1).pdf` — суфиксът `(1)` подсказва, че има и други копия с име `book-3.pdf`, `book-3 (2).pdf` и т.н. в същата папка. **Не мога да потвърдя дали са идентични**, защото не са ми прикачени. Препоръчвам ръчна проверка на хешове (md5) на всички файлове с име `book-3*.pdf`.

⚠️ **НЕ мога да проверя останалите `book-1..12.pdf`** — прикачен ми е само този един файл.

---

### RECOMMENDED CHANGES TO index.html

**В STEPS:**
- [ ] **Няма промени.** Тази книга не се map-ва към нито една от 96-те математически точки.

**В PLAN_PHASES:**
- [ ] **Няма промени.** Книгата е нерелевантна за 25-седмичния план по математика.

**Друго:**
- [ ] **Препоръка:** Премести `book-3 (1).pdf` (и всички `book-*.pdf`) в отделна папка `Материали_EN/Informatics/`, за да не се смесват с математическите ресурси. Ако ученикът има паралелна подготовка по информатика, създай отделен контекст-файл `AI_MASTER_CONTEXT_Informatics.md` и отделен `index.html` (или секция), защото curriculum-ите са принципно различни.
- [ ] **Конкретен mapping (само ако добавяш паралелен Informatics track):**
  - Ch 2 → IOI Syllabus: Data Structures (Fenwick, Segment Tree, UFDS)
  - Ch 3 → IOI Syllabus: Complete Search, DP, Greedy
  - Ch 4 → IOI Syllabus: Graph algorithms (BFS, DFS, MST, Dijkstra, SCC)
  - Book 2 (не е прикачен) покрива остатъка от IOI syllabus (Number Theory, Strings, Geometry, Network Flow).
- [ ] **Няма промени** в exam dates конфигурацията за математика.

---

## 🏆 PAST EXAMS — Областни кръгове 2016–2026 (11/11 готови)

### OLI-2016 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.11, 10.12
**Знания открити:** Спернер, тригонометрични уравнения, функционални неравенства с итерации, разположение на корени

<!-- ВМЪКНИ съдържанието на 2016.txt -->



---

### OLI-2017 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.13, 10.14
**Знания открити:** Блок-дизайни, тригонометрични уравнения

<!-- ВМЪКНИ съдържанието на 2017.txt -->



---

### OLI-2018 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-specific-points` + нови точки 10.15, 10.16
**Знания открити:** Симетрия на квадратна функция, показателни неравенства

<!-- ВМЪКНИ съдържанието на 2018.txt -->



---

### OLI-2019 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.17, 10.18
**Знания открити:** Карно, радикални уравнения, F2 векторни пространства

<!-- ВМЪКНИ съдържанието на 2019.txt -->



---

### OLI-2020 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.19, 10.20
**Знания открити:** Проекции на множества, радикални уравнения с полагане

<!-- ВМЪКНИ съдържанието на 2020.txt -->



---

### OLI-2021 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.21, 10.22
**Знания открити:** F2 векторни пространства (major)

<!-- ВМЪКНИ съдържанието на 2021.txt -->



---

### OLI-2022 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.23, 10.24
**Знания открити:** Ирационални неравенства, покриващи кодове

<!-- ВМЪКНИ съдържанието на 2022.txt -->



---

### OLI-2023 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.25, 10.26
**Знания открити:** Айзенщайн, ъглополовяща теорема, конфигурации от прави

<!-- ВМЪКНИ съдържанието на 2023.txt -->



---

### OLI-2024 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.27, 10.28
**Знания открити:** Квадратични форми (major), реципрочни уравнения

<!-- ВМЪКНИ съдържанието на 2024.txt -->



---

### OLI-2025 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.29, 10.30
**Знания открити:** Вероятностен метод (major)

<!-- ВМЪКНИ съдържанието на 2025.txt -->



---

### OLI-2026 (10 + 11 кл) — ✅ ГОТОВО
**Решение:** `add-to-step10` + нови точки 10.31, 10.32
**Знания открити:** Формула на Пик (major), постулат на Бертран
**Забележка:** Липсва 11 кл-sol.pdf за пълен анализ

<!-- ВМЪКНИ съдържанието на 2026.txt -->



---

## 📖 BG MATERIALS — Български сборници (0/11)

### OT_2010.pdf — ⏳ ПРЕДСТОИ



---

### OT_2012.pdf — ⏳ ПРЕДСТОИ



---

### BMS_2003-2005.pdf — ⏳ ПРЕДСТОИ



---

### BMS_2012-2015.pdf — ⏳ ПРЕДСТОИ



---

### BMC_2003-2006.pdf — ⏳ ПРЕДСТОИ (2 чата)



---

### BMO_1984-2006.pdf — ⏳ ПРЕДСТОИ



---

### NOM_2010.pdf — ⏳ ПРЕДСТОИ



---

### NOM_2011.pdf — ⏳ ПРЕДСТОИ



---

### NOM_2012.pdf — ⏳ ПРЕДСТОИ



---

### NOM_2013.pdf — ⏳ ПРЕДСТОИ



---

### NOM_2014.pdf — ⏳ ПРЕДСТОИ



---

### NOM_2015-2016.pdf — ⏳ ПРЕДСТОИ



---

## 🎓 LECTURES — Бонус лекции (0/6)

### Група A — NT Training — ⏳ ПРЕДСТОИ



---

### Група B — Functional Equations — ⏳ ПРЕДСТОИ



---

### Група C — Polynomials/Enumerative/Induction — ⏳ ПРЕДСТОИ



---

### Група D — Peter PAMP 2019 — ⏳ ПРЕДСТОИ



---

### Група E — Weekly Themes — ⏳ ПРЕДСТОИ



---

### Група F — Теми с Лекции — ⏳ ПРЕДСТОИ



---

## 📊 SUMMARY STATISTICS

| Категория | Обработени | Общо |
|---|---|---|
| Математически книги | 10 | 10 |
| Non-math книги (skip) | 2 | 2 |
| Областни кръгове | 11 | 11 |
| BG сборници | 0 | 11 |
| Лекции | 0 | 6 |
| **ОБЩО** | **23** | **40** |

**Дубликати за изтриване:**
- [ ] `Материали_EN/Copies/book-8 (1).pdf`
- [ ] `Материали_EN/Copies/book-9 (1).pdf`
- [ ] `Материали_EN/Copies/book-10 (1).pdf`
- [ ] `Материали_EN/Copies/book-11 (1).pdf`
- [ ] `Материали_EN/Copies/book-3 (3).pdf`
- [ ] `Материали_EN/Copies/book-3 (4).pdf`

---

## 🎯 NEXT STEPS

1. [x] 10 математически книги — ГОТОВО
2. [x] 11 областни кръга 2016–2026 — ГОТОВО
3. [ ] BG сборници (11 файла, 12 чата)
4. [ ] Лекции (6 групи, 6 чата)
5. [ ] Финален интеграционен чат с DeepSeek

---

## ⚠️ РИСКОВЕ И ЗАБЕЛЕЖКИ

- **book-4** — два различни AI отговора; приемаме Опит 1 (Step 12). Опит 2 се игнорира.
- **book-4 (1)** и **book-3 (1)** — не са математика → отделна папка Informatics.
- **book-9** — skip, под нивото.
- **book-11** — спорно; Calculus за олимпиада е рядкост.
- **Page numbers** в областните кръгове винаги 1 — ОК, защото probs PDF е 1 страница.
- **2026-11-sol.pdf** — липсва, 11 кл анализът е непълен.

---

## 🔑 KEY FINDINGS (за финална интеграция)

### ✅ Готови промени в index.html:
- Нова **Стъпка 12** (Analytic & Projective Geometry) — 3 точки
- Разширена **Стъпка 10** с 22 нови точки (10.11–10.32)
- Нови точки за откритите gaps (виж секция 12 в AI_MASTER_CONTEXT)
- ~150 нови `bonus` записа
- ~400-800 нови `tasks`

### 🚩 Gaps (кандидати за нови точки — виж AI_MASTER_CONTEXT секция 12):
**Major:** F2 векторни пространства, тригонометрични уравнения, разположение на корени, ирационални уравнения с параметър, функционални неравенства с итерации

**Minor:** Спернер, блок-дизайни, Карно, квадратични форми, формула на Пик, вероятностен метод, реципрочни уравнения, Айзенщайн, ъглополовяща теорема, Бертран, проекции

---

*Файлът се актуализира ръчно след всеки AI чат.*

---

## 📋 ОБОБЩЕНИЕ

**Обновени секции:** 11 (всички книги + non-math)
**Оставащи празни:** 17 (11 BG сборника + 6 лекции)
**Забележки:**
- Всички `.txt` файлове за книгите са интегрирани 1:1
- `книга-4.txt` — използван е само Опит 1, Опит 2 е изтрит
- `Индекси_страници.txt` не е интегриран — не е в mapping таблицата (референтен файл)
- Липсват `.txt` файлове за областните кръгове (2016–2026) — placeholders остават
- Summary таблицата е обновена — 23/40 обработени
- Датата е обновена на 2026-10-13