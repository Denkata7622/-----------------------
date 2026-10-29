# ALL AI ANALYSES — Olympiad Prep

> **Инструкции за ползване:**
> 1. Всеки AI чат връща резултат → копирай САМО финалните блокове (КНИГА / ЗАДАЧИ / НОВА ТОЧКА / АКТУАЛИЗАЦИЯ / RECOMMENDED CHANGES).
> 2. НЕ копирай reasoning, обяснения, chat UI елементи.
> 3. Постави резултата под съответната секция.
> 4. Ако секция е празна — AI-ът още не е обработен.

**Последно обновено:** 2026-10-12
**Общо обработени:** 40 / 40 ✅

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
  year: 2007, language: "EN", total_pages: 213, topics: ["Number Theory"],
  structure: [
    { chapter: "Ch 1.1", title: "Divisibility and Division Algorithm", pages: "13-17", plan_step: 3, plan_points: ["3.1"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 1.2", title: "Primes and FTA", pages: "17-23", plan_step: 3, plan_points: ["3.1", "4.5"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 1.3", title: "GCD, Euclidean, Bézout, LCM", pages: "23-28", plan_step: 3, plan_points: ["3.1", "4.1"], priority_regional: "high", priority_national: "high" },
    { chapter: "Ch 1.4", title: "Number and Sum of Divisors", pages: "28-31", plan_step: 4, plan_points: ["4.7"] },
    { chapter: "Ch 1.5", title: "Modular Arithmetic", pages: "31-37", plan_step: 3, plan_points: ["3.2", "3.6"] },
    { chapter: "Ch 1.6", title: "Wilson, Fermat, Euler", pages: "37-45", plan_step: 3, plan_points: ["3.3", "3.4", "3.5"] },
    { chapter: "Ch 1.7", title: "Multiplicative Functions", pages: "45-47", plan_step: 4, plan_points: ["4.7"] },
    { chapter: "Ch 1.8", title: "Linear Diophantine", pages: "47-50", plan_step: 4, plan_points: ["4.1"] },
    { chapter: "Ch 1.10", title: "Floor Function", pages: "59-68", plan_step: 3, plan_points: ["3.1", "4.8"] },
    { chapter: "Ch 1.11", title: "Legendre's Function", pages: "68-75", plan_step: 4, plan_points: ["3.8", "4.8"] },
    { chapter: "Ch 1.12", title: "Fermat, Mersenne, Perfect Numbers", pages: "75-86", plan_step: 4, plan_points: ["4.4", "4.5", "4.7"] },
    { chapter: "Ch 2", title: "Introductory Problems (52)", pages: "87-94", plan_step: 10 },
    { chapter: "Ch 3", title: "Advanced Problems (52)", pages: "95-102", plan_step: 10 },
    { chapter: "Ch 4-5", title: "Solutions", pages: "103-199", plan_step: 10 }
  ],
  duplicates: [],
  recommended_action: "add-as-bonus",
  best_mapping: [
    { step_id: 3, point_ids: ["3.1","3.2","3.3","3.4","3.5","3.6","3.8"], chapters: ["Ch 1.1","1.2","1.3","1.5","1.6","1.10","1.11"] },
    { step_id: 4, point_ids: ["4.1","4.4","4.5","4.7","4.8"], chapters: ["Ch 1.4","1.7","1.8","1.11","1.12"] },
    { step_id: 10, point_ids: ["10.1","10.2","10.3","10.4","10.5"], chapters: ["Ch 2-5"] }
  ]
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
{ id: "3.1", bonus: [{ label: "104 NT Problems — Divisibility, Division Algo", pdf: "Материали_EN/book-2", page: 13 }, { label: "104 NT Problems — GCD, Euclidean, Bézout", pdf: "Материали_EN/book-2", page: 23 }] }
{ id: "3.2", bonus: [{ label: "104 NT Problems — Modular Arithmetic", pdf: "Материали_EN/book-2", page: 31 }, { label: "Residue Classes", pdf: "Материали_EN/book-2", page: 35 }] }
{ id: "3.3", bonus: [{ label: "104 NT Problems — Fermat's Little Theorem", pdf: "Материали_EN/book-2", page: 39 }] }
{ id: "3.4", bonus: [{ label: "104 NT Problems — Euler's Theorem + Totient", pdf: "Материали_EN/book-2", page: 40 }] }
{ id: "3.5", bonus: [{ label: "104 NT Problems — Wilson's Theorem", pdf: "Материали_EN/book-2", page: 36 }] }
{ id: "3.8", bonus: [{ label: "104 NT Problems — Legendre's Function", pdf: "Материали_EN/book-2", page: 68 }] }
{ id: "4.1", bonus: [{ label: "104 NT Problems — Linear Diophantine", pdf: "Материали_EN/book-2", page: 47 }] }
{ id: "4.4", bonus: [{ label: "104 NT Problems — Perfect Powers / Squares", pdf: "Материали_EN/book-2", page: 52 }] }
{ id: "4.5", bonus: [{ label: "104 NT Problems — Primes, Mersenne, Fermat", pdf: "Материали_EN/book-2", page: 17 }, { label: "Fermat Numbers", pdf: "Материали_EN/book-2", page: 75 }] }
{ id: "4.7", bonus: [{ label: "104 NT Problems — Multiplicative Functions", pdf: "Материали_EN/book-2", page: 45 }] }
{ id: "4.8", bonus: [{ label: "104 NT Problems — Legendre, Factorials, Binomials", pdf: "Материали_EN/book-2", page: 68 }] }
{ id: "10.1", tasks: [{ label: "Intro Problem 1 (AMC10B 2004)", pdf: "Материали_EN/book-2", page: 87 }, { label: "Intro Problem 7 (p, p+ka primes)", pdf: "Материали_EN/book-2", page: 88 }, { label: "Intro Problem 9 (lcm+gcd=m+n)", pdf: "Материали_EN/book-2", page: 88 }] }
{ id: "10.5", tasks: [{ label: "Adv Problem 2 (S(x)/S(2x)≤5)", pdf: "Материали_EN/book-2", page: 95 }, { label: "Adv Problem 10 (lcm inequality)", pdf: "Материали_EN/book-2", page: 96 }] }
```

---

### book-3.pdf — ✅ ГОТОВО
**Идентификация:** Mathematical Olympiad Treasures (Andreescu, Enescu, 2011)
**Решение:** `add-as-bonus`
**Забележка:** 22 bonus записа

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-3.pdf",
  title: "Mathematical Olympiad Treasures",
  author: "Titu Andreescu, Bogdan Enescu",
  year: 2011, language: "EN", total_pages: 262,
  topics: ["Algebra", "Geometry", "Trigonometry", "Number Theory", "Combinatorics"],
  structure: [
    // Chapter 1: ALGEBRA
    { chapter: "1.1", title: "An Algebraic Identity", pages: "12-15", plan_step: 6, plan_points: ["6.1"] },
    { chapter: "1.2", title: "Cauchy-Schwarz Revisited", pages: "16-19", plan_step: 6, plan_points: ["6.4"] },
    { chapter: "1.3", title: "Easy Ways Through Absolute Values", pages: "20-23", plan_step: 6 },
    { chapter: "1.4", title: "Parameters", pages: "23-26", plan_step: 5 },
    { chapter: "1.5", title: "Take the Conjugate!", pages: "26-29", plan_step: 3, plan_points: ["3.10"] },
    { chapter: "1.6", title: "Inequalities with Convex Functions", pages: "29-33", plan_step: 6, plan_points: ["6.5"] },
    { chapter: "1.7", title: "Induction at Work", pages: "33-36", plan_step: 8, plan_points: ["8.10"] },
    { chapter: "1.8", title: "Roots and Coefficients", pages: "36-40", plan_step: 5, plan_points: ["5.1","5.3"] },
    { chapter: "1.9", title: "The Rearrangements Inequality", pages: "40-45", plan_step: 6, plan_points: ["6.7"] },
    // Chapter 2: GEOMETRY & TRIG
    { chapter: "2.1", title: "Geometric Inequalities", pages: "46-49", plan_step: 2, plan_points: ["2.8"] },
    { chapter: "2.2", title: "An Interesting Locus", pages: "49-54", plan_step: 1, plan_points: ["1.7"] },
    { chapter: "2.3", title: "Cyclic Quads", pages: "54-59", plan_step: 1, plan_points: ["1.3","1.5","1.9"] },
    { chapter: "2.5", title: "More on Equilateral Triangles", pages: "63-67", plan_step: 2, plan_points: ["2.4"] },
    { chapter: "2.6", title: "The Carpets Theorem", pages: "67-71", plan_step: 1, plan_points: ["1.7"] },
    { chapter: "2.7", title: "Quads with Inscribed Circle", pages: "71-74", plan_step: 1, plan_points: ["1.10"] },
    { chapter: "2.8", title: "Dr. Trig Learns Complex Numbers", pages: "75-78", plan_step: 1, plan_points: ["1.6"] },
    // Chapter 3: NT & COMBINATORICS
    { chapter: "3.1", title: "Arrays of Numbers", pages: "80-83", plan_step: 8, plan_points: ["8.3"] },
    { chapter: "3.3", title: "Count Twice!", pages: "86-89", plan_step: 8, plan_points: ["8.3"] },
    { chapter: "3.4", title: "Sequences of Integers", pages: "90-94", plan_step: 7, plan_points: ["7.6","7.7"] },
    { chapter: "3.5", title: "Equations with Infinitely Many Solutions", pages: "94-97", plan_step: 4, plan_points: ["4.1","4.2"] },
    { chapter: "3.6", title: "Equations with No Solutions", pages: "97-99", plan_step: 3, plan_points: ["3.2"] },
    { chapter: "3.7", title: "Powers of 2", pages: "99-102", plan_step: 3, plan_points: ["3.1"] },
    { chapter: "3.8", title: "Progressions", pages: "102-104", plan_step: 7, plan_points: ["7.6"] },
    { chapter: "3.9", title: "The Marriage Lemma", pages: "105-107", plan_step: 9, plan_points: ["9.1"] }
  ],
  duplicates: [],
  recommended_action: "add-as-bonus"
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
{ id: "6.1", bonus: [{ label: "Andreescu–Enescu — Identity", pdf: "Материали_EN/book-3", page: 12 }] }
{ id: "6.4", bonus: [{ label: "Cauchy-Schwarz", pdf: "Материали_EN/book-3", page: 16 }, { label: "Conjugate tricks", pdf: "Материали_EN/book-3", page: 26 }] }
{ id: "6.5", bonus: [{ label: "Convex functions", pdf: "Материали_EN/book-3", page: 29 }] }
{ id: "6.7", bonus: [{ label: "Rearrangements", pdf: "Материали_EN/book-3", page: 40 }] }
{ id: "5.1", bonus: [{ label: "Roots & Coefficients", pdf: "Материали_EN/book-3", page: 36 }, { label: "Parameters", pdf: "Материали_EN/book-3", page: 23 }] }
{ id: "3.10", bonus: [{ label: "Conjugate & Pell", pdf: "Материали_EN/book-3", page: 26 }] }
{ id: "3.2", bonus: [{ label: "No Solutions mod p", pdf: "Материали_EN/book-3", page: 97 }] }
{ id: "3.1", bonus: [{ label: "Powers of 2", pdf: "Материали_EN/book-3", page: 99 }] }
{ id: "4.1", bonus: [{ label: "Infinite Solutions", pdf: "Материали_EN/book-3", page: 94 }] }
{ id: "7.6", bonus: [{ label: "Integer Sequences", pdf: "Материали_EN/book-3", page: 90 }, { label: "Progressions", pdf: "Материали_EN/book-3", page: 102 }] }
{ id: "8.3", bonus: [{ label: "Count Twice!", pdf: "Материали_EN/book-3", page: 86 }] }
{ id: "8.10", bonus: [{ label: "Induction at Work", pdf: "Материали_EN/book-3", page: 33 }] }
{ id: "9.1", bonus: [{ label: "Marriage Lemma", pdf: "Материали_EN/book-3", page: 105 }] }
{ id: "1.3", bonus: [{ label: "Cyclic Quads & Ptolemy", pdf: "Материали_EN/book-3", page: 54 }] }
{ id: "1.10", bonus: [{ label: "Inscribed Circle Quads", pdf: "Материали_EN/book-3", page: 71 }] }
{ id: "1.7", bonus: [{ label: "Carpets & Locus", pdf: "Материали_EN/book-3", page: 49 }, { label: "Carpets Theorem", pdf: "Материали_EN/book-3", page: 67 }] }
{ id: "1.5", bonus: [{ label: "Cyclic Quads", pdf: "Материали_EN/book-3", page: 54 }] }
{ id: "2.4", bonus: [{ label: "Equilateral Triangles", pdf: "Материали_EN/book-3", page: 63 }] }
{ id: "2.8", bonus: [{ label: "Geometric Inequalities", pdf: "Материали_EN/book-3", page: 46 }] }
{ id: "1.6", bonus: [{ label: "Dr. Trig (Complex Numbers)", pdf: "Материали_EN/book-3", page: 75 }] }
```

---

### book-4.pdf — ⚠️ ГОТОВО (Опит 1 — Step 12)
**Идентификация:** Euclidean Geometry in Mathematical Olympiads (Evan Chen, 2016)
**Решение:** `add-as-step12`
**Забележка:** 3 нови точки в Стъпка 12

```js
// ─── НОВА СТЪПКА 12: ANALYTIC AND PROJECTIVE GEOMETRY ───
{
  num: 12, title: "ANALYTIC AND PROJECTIVE GEOMETRY",
  scope: "Комплексни числа, барицентрични координати, проективна геометрия и пълни четириъгълници",
  points: [
    {
      id: "12.1", title: "Комплексни числа в геометрията",
      source: "Evan Chen, EGMO, Ch 6", pdf: "Материали_EN/book-4", page: 113, problems_page: 133,
      tasks: [
        { label: "Example 6.10 (Перпендикулярност)", pdf: "Материали_EN/book-4", page: 101 },
        { label: "Lemma 6.11 (Complex Foot)", pdf: "Материали_EN/book-4", page: 101 },
        { label: "Lemma 6.12 (Complex Euler Line)", pdf: "Материали_EN/book-4", page: 102 },
        { label: "Example 6.13 (Nine-Point Circle)", pdf: "Материали_EN/book-4", page: 103 },
        { label: "Theorem 6.17 (Complex Intersection)", pdf: "Материали_EN/book-4", page: 104 },
        { label: "Lemma 6.19 (Complex Tangent)", pdf: "Материали_EN/book-4", page: 105 },
        { label: "Lemma 6.23 (Complex Incenter)", pdf: "Материали_EN/book-4", page: 106 },
        { label: "Lemma 6.24 (Complex Circumcenter)", pdf: "Материали_EN/book-4", page: 107 },
        { label: "Example 6.26 (USA TSTST 2013/1)", pdf: "Материали_EN/book-4", page: 110 },
        { label: "Example 6.27 (USAMO 2012/5)", pdf: "Материали_EN/book-4", page: 113 }
      ],
      bonus: [{ label: "Hints to Ch 6 problems", pdf: "Материали_EN/book-4", page: 238 }]
    },
    {
      id: "12.2", title: "Барицентрични координати",
      source: "Evan Chen, EGMO, Ch 7", pdf: "Материали_EN/book-4", page: 137, problems_page: 160,
      tasks: [
        { label: "Theorem 7.1 (Barycentric Area Formula)", pdf: "Материали_EN/book-4", page: 119 },
        { label: "Theorem 7.2 (Equation of a Line)", pdf: "Материали_EN/book-4", page: 120 },
        { label: "Theorem 7.4 (Barycentric Cevian)", pdf: "Материали_EN/book-4", page: 122 },
        { label: "Theorem 7.10 (Collinearity)", pdf: "Материали_EN/book-4", page: 123 },
        { label: "Theorem 7.13 (Concurrence)", pdf: "Материали_EN/book-4", page: 125 },
        { label: "Theorem 7.14 (Distance Formula)", pdf: "Материали_EN/book-4", page: 126 },
        { label: "Theorem 7.15 (Barycentric Circle)", pdf: "Материали_EN/book-4", page: 127 },
        { label: "Theorem 7.16 (Perpendiculars)", pdf: "Материали_EN/book-4", page: 127 },
        { label: "Example 7.20 (Shortlist 2011/G6)", pdf: "Материали_EN/book-4", page: 129 },
        { label: "Theorem 7.22 (Conway's Formula)", pdf: "Материали_EN/book-4", page: 133 },
        { label: "Example 7.29 (USAMO 2008/2)", pdf: "Материали_EN/book-4", page: 138 },
        { label: "Example 7.30 (USA TSTST 2011/4)", pdf: "Материали_EN/book-4", page: 139 }
      ],
      bonus: [{ label: "Barycentric Coordinates (Chen & Schindler)", pdf: "Материали_EN/book-4", page: 305 }]
    },
    {
      id: "12.3", title: "Проективна геометрия и пълни четириъгълници",
      source: "Evan Chen, EGMO, Ch 9-10", pdf: "Материали_EN/book-4", page: 187, problems_page: 208,
      tasks: [
        { label: "Theorem 9.1 (Cross-Ratio)", pdf: "Материали_EN/book-4", page: 171 },
        { label: "Lemma 9.12 (Complete Quadrilaterals)", pdf: "Материали_EN/book-4", page: 175 },
        { label: "Theorem 9.25 (Brocard's Theorem)", pdf: "Материали_EN/book-4", page: 179 },
        { label: "Theorem 9.29 (Pascal's Theorem)", pdf: "Материали_EN/book-4", page: 181 },
        { label: "Theorem 9.35 (Butterfly Theorem)", pdf: "Материали_EN/book-4", page: 185 },
        { label: "Example 9.38 (IMO 2010/2)", pdf: "Материали_EN/book-4", page: 186 },
        { label: "Theorem 10.3 (Miquel's Theorem)", pdf: "Материали_EN/book-4", page: 198 },
        { label: "Theorem 10.5 (Gauss-Bodenmiller)", pdf: "Материали_EN/book-4", page: 199 },
        { label: "Example 10.16 (USA TST 2013)", pdf: "Материали_EN/book-4", page: 202 }
      ],
      bonus: [{ label: "Projective Geometry (Remorov)", pdf: "Материали_EN/book-4", page: 305 }]
    }
  ]
}
```

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
  author: "B. J. Venkatachala", year: 2009, language: "EN", total_pages: 399,
  topics: ["Algebra", "Inequalities", "Geometry", "Number Theory"],
  structure: [
    { chapter: "Ch 1", title: "Some Basic Inequalities", pages: "10-58", plan_step: 6, plan_points: ["6.1","6.2","6.3","6.4","6.5","6.6","6.7","6.8","6.9","6.10"] },
    { chapter: "Ch 2", title: "Techniques for Proving Inequalities", pages: "59-101", plan_step: 6, plan_points: ["6.1","6.4","6.5","6.8","6.9","6.10"] },
    { chapter: "Ch 3", title: "Geometric Inequalities", pages: "102-161", plan_step: 2, plan_points: ["2.8"] },
    { chapter: "Ch 4", title: "Applications", pages: "162-192", plan_step: 10 },
    { chapter: "Ch 5", title: "Problems", pages: "193-223", plan_step: 10 },
    { chapter: "Ch 6", title: "Solutions", pages: "224-395", plan_step: 10 }
  ],
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
    { step_id: 2, point_ids: ["2.8"], chapters: ["Ch 3"], pages: "102-161" }
  ]
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
{ id: "6.1", bonus: [{ label: "Ch 1.2: AM-GM", pdf: "Материали_EN/book-7", page: 12 }, { label: "Ch 2.2-2.3: Индукция", pdf: "Материали_EN/book-7", page: 59 }] }
{ id: "6.4", bonus: [{ label: "Ch 1.3: Cauchy-Schwarz", pdf: "Материали_EN/book-7", page: 20 }] }
{ id: "6.5", bonus: [{ label: "Ch 1.7: Jensen", pdf: "Материали_EN/book-7", page: 43 }] }
{ id: "6.6", bonus: [{ label: "Ch 1.4: Chebyshev", pdf: "Материали_EN/book-7", page: 26 }] }
{ id: "6.7", bonus: [{ label: "Ch 1.5: Rearrangement", pdf: "Материали_EN/book-7", page: 30 }] }
{ id: "6.8", bonus: [{ label: "Ch 2.9-2.10: Muirhead", pdf: "Материали_EN/book-7", page: 90 }] }
{ id: "6.9", bonus: [{ label: "Ch 2.8: Schur", pdf: "Материали_EN/book-7", page: 88 }, { label: "Ch 2.13: Stolarsky", pdf: "Материали_EN/book-7", page: 99 }] }
{ id: "6.10", bonus: [{ label: "Ch 1.6: Hölder and Minkowski", pdf: "Материали_EN/book-7", page: 36 }] }
{ id: "2.8", bonus: [{ label: "Ch 3: Геометрични неравенства", pdf: "Материали_EN/book-7", page: 102 }] }
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
  title: "Precalculus", author: "Richard Rusczyk", year: 2012, language: "EN", total_pages: 531,
  topics: ["Trigonometry","Complex Numbers","Vectors","Matrices","Geometry"],
  structure: [
    { chapter: "Ch 1", title: "Functions Review", pages: "15-46", plan_step: 7, plan_points: ["7.5"] },
    { chapter: "Ch 2", title: "Intro to Trig Functions", pages: "47-100", plan_step: 1, plan_points: ["1.6","1.7"] },
    { chapter: "Ch 3", title: "Trig Identities", pages: "101-145", plan_step: 1, plan_points: ["1.6","2.8","6.1"] },
    { chapter: "Ch 4", title: "Applications to Geometry", pages: "146-175", plan_step: 1, plan_points: ["1.1","1.2","1.6","1.7"] },
    { chapter: "Ch 5", title: "Parameterization & Trig Coordinate Systems", pages: "176-209", plan_step: 2 },
    { chapter: "Ch 6", title: "Basics of Complex Numbers", pages: "210-236", plan_step: 2, plan_points: ["2.3","2.5"] },
    { chapter: "Ch 7", title: "Trig & Complex Numbers", pages: "237-273", plan_step: 3, plan_points: ["3.7","4.5"] },
    { chapter: "Ch 8", title: "Geometry of Complex Numbers", pages: "274-315", plan_step: 2 },
    { chapter: "Ch 9", title: "Vectors in 2D", pages: "316-352", plan_step: 1 },
    { chapter: "Ch 10", title: "Matrices in 2D", pages: "353-397", plan_step: 5, plan_points: ["5.8"] },
    { chapter: "Ch 11-12", title: "3D Vectors & Matrices", pages: "398-480", plan_step: 2 },
    { chapter: "Ch 13", title: "Vector Geometry", pages: "481-487", plan_step: 1 }
  ],
  recommended_action: "add-as-bonus"
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
{ id: "1.6", bonus: [{ label: "Precalculus — Trig Functions", pdf: "Материали_EN/book-8", page: 47 }] }
{ id: "1.7", bonus: [{ label: "Precalculus — Applications to Geometry", pdf: "Материали_EN/book-8", page: 146 }] }
{ id: "2.3", bonus: [{ label: "Precalculus — Complex Numbers", pdf: "Материали_EN/book-8", page: 210 }] }
{ id: "2.4", bonus: [{ label: "Precalculus — Geometry of Complex Numbers", pdf: "Материали_EN/book-8", page: 274 }] }
{ id: "2.5", bonus: [{ label: "Precalculus — Geometry of Complex Numbers", pdf: "Материали_EN/book-8", page: 274 }] }
{ id: "3.7", bonus: [{ label: "Precalculus — Roots of Unity", pdf: "Материали_EN/book-8", page: 237 }] }
{ id: "5.8", bonus: [{ label: "Precalculus — Matrices", pdf: "Материали_EN/book-8", page: 353 }] }
{ id: "7.5", bonus: [{ label: "Precalculus — Functions Review", pdf: "Материали_EN/book-8", page: 15 }] }
```

---

### book-10.pdf — ✅ ГОТОВО
**Идентификация:** Introduction to Algebra (Rusczyk, 2007)
**Решение:** `add-as-bonus`

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-10.pdf",
  title: "Introduction to Algebra", author: "Richard Rusczyk (AoPS)", year: 2007,
  language: "EN", total_pages: 658, total_book_pages: 636, pdf_offset: 17,
  topics: ["Algebra","Equations","Inequalities","Functions","Sequences","Complex Numbers","Polynomials"],
  level: "introductory — под олимпиадно ниво",
  structure: [
    { chapter: "Ch 4", title: "More Variables", pdf_pages: "101-120", plan_step: 5, plan_points: ["5.3"] },
    { chapter: "Ch 5", title: "Multi-Variable Linear Equations", pdf_pages: "121-154", plan_step: 4, plan_points: ["4.1"] },
    { chapter: "Ch 9", title: "Intro to Inequalities", pdf_pages: "250-283", plan_step: 6, plan_points: ["6.1","6.2","6.3"] },
    { chapter: "Ch 10", title: "Quadratic Equations Part 1", pdf_pages: "284-321", plan_step: 5, plan_points: ["5.1","5.4","5.5"] },
    { chapter: "Ch 11", title: "Special Factorizations", pdf_pages: "322-354", plan_step: 5, plan_points: ["5.3","5.5","5.7"] },
    { chapter: "Ch 15", title: "More Inequalities", pdf_pages: "423-448", plan_step: 6, plan_points: ["6.1","6.10"] },
    { chapter: "Ch 16", title: "Functions", pdf_pages: "449-481", plan_step: 7, plan_points: ["7.1","7.2","7.3","7.4","7.5"] },
    { chapter: "Ch 17", title: "Graphing Functions", pdf_pages: "482-510", plan_step: 7, plan_points: ["7.3","7.4"] },
    { chapter: "Ch 18", title: "Polynomials", pdf_pages: "511-522", plan_step: 5, plan_points: ["5.1","5.3","5.7"] },
    { chapter: "Ch 20", title: "Special Functions", pdf_pages: "557-587", plan_step: 7, plan_points: ["7.2","7.5"] },
    { chapter: "Ch 21", title: "Sequences & Series", pdf_pages: "588-626", plan_step: 7, plan_points: ["7.6","7.7","8.9"] },
    { chapter: "Ch 22", title: "Special Manipulations", pdf_pages: "627-637", plan_step: 7, plan_points: ["7.5","7.8"] }
  ],
  recommended_action: "add-as-bonus"
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
{ id: "5.1", bonus: [{ label: "Rusczyk — Ch 10 (Sums/Products)", pdf: "Материали_EN/book-10", page: 306 }] }
{ id: "5.3", bonus: [{ label: "Rusczyk — Ch 4 (Distribution)", pdf: "Материали_EN/book-10", page: 101 }] }
{ id: "5.5", bonus: [{ label: "Rusczyk — Ch 11 (SFFT)", pdf: "Материали_EN/book-10", page: 322 }] }
{ id: "5.7", bonus: [{ label: "Rusczyk — Ch 11 & 18", pdf: "Материали_EN/book-10", page: 322 }] }
{ id: "6.1", bonus: [{ label: "Rusczyk — Ch 9 & 15", pdf: "Материали_EN/book-10", page: 250 }] }
{ id: "7.1", bonus: [{ label: "Rusczyk — Ch 16", pdf: "Материали_EN/book-10", page: 449 }] }
{ id: "7.5", bonus: [{ label: "Rusczyk — Ch 16, 17, 20", pdf: "Материали_EN/book-10", page: 449 }] }
{ id: "7.6", bonus: [{ label: "Rusczyk — Ch 21 (Telescoping)", pdf: "Материали_EN/book-10", page: 588 }] }
{ id: "7.8", bonus: [{ label: "Rusczyk — Ch 22", pdf: "Материали_EN/book-10", page: 627 }] }
{ id: "4.1", bonus: [{ label: "Rusczyk — Ch 5", pdf: "Материали_EN/book-10", page: 121 }] }
```

---

### book-11.pdf — ✅ ГОТОВО
**Идентификация:** Calculus (Patrick, 2019)
**Решение:** `add-as-step12` (спорно)

```js
// ─── НОВИ ТОЧКИ 12.1–12.9 ───
// 12.1 Множества и функции (стр. 1)
// 12.2 Лимити и непрекъснатост (стр. 37)
// 12.3 Производна (стр. 70)
// 12.4 Приложения на производната (стр. 102)
// 12.5 Интеграли (стр. 139)
// 12.6 Приложения на интеграла (стр. 166)
// 12.7 Редици и редове (стр. 220)
// 12.8 Равнинни криви (стр. 259)
// 12.9 Диференциални уравнения (стр. 279)

// ─── АКТУАЛИЗАЦИЯ ───
{ id: "7.1", bonus: [{ label: "Calculus (Ch 2, 6)", pdf: "Материали_EN/book-11", page: 37 }] }
{ id: "6.4", bonus: [{ label: "Calculus (Ch 3, 4)", pdf: "Материали_EN/book-11", page: 70 }] }
{ id: "7.6", bonus: [{ label: "Calculus (Ch 7)", pdf: "Материали_EN/book-11", page: 220 }] }
```

---

### book-12.pdf — ✅ ГОТОВО
**Идентификация:** Intermediate Counting & Probability (Patrick, 2007)
**Решение:** `add-as-bonus`

```js
// ─── КНИГА ───
{
  file: "Материали_EN/book-12.pdf",
  title: "Intermediate Counting & Probability", author: "David Patrick", year: 2007,
  language: "EN", total_pages: 404,
  topics: ["Combinatorics","Probability","Generating Functions","Graph Theory","Recursion"],
  structure: [
    { chapter: "Ch 1", title: "Review of Counting", pages: "17-26", plan_step: 8, plan_points: ["8.5","8.6"] },
    { chapter: "Ch 3", title: "A Piece of PIE", pages: "65-98", plan_step: 8, plan_points: ["8.2","8.3"] },
    { chapter: "Ch 4", title: "Constructive Counting", pages: "99-133", plan_step: 8, plan_points: ["8.3","8.5"] },
    { chapter: "Ch 5", title: "Pigeonhole", pages: "134-145", plan_step: 8, plan_points: ["8.1"] },
    { chapter: "Ch 7", title: "Distributions", pages: "161-176", plan_step: 8, plan_points: ["8.7"] },
    { chapter: "Ch 8", title: "Mathematical Induction", pages: "177-187", plan_step: 8, plan_points: ["8.10"] },
    { chapter: "Ch 9", title: "Fibonacci Numbers", pages: "188-207", plan_step: 7, plan_points: ["7.6","7.7","7.8"] },
    { chapter: "Ch 10", title: "Recursion", pages: "208-242", plan_step: 7, plan_points: ["7.6","7.7","7.8"] },
    { chapter: "Ch 12", title: "Combinatorial Identities", pages: "259-280", plan_step: 8, plan_points: ["8.4","8.5"] },
    { chapter: "Ch 13", title: "Events With States", pages: "281-313", plan_step: 9, plan_points: ["9.10"] },
    { chapter: "Ch 14", title: "Generating Functions", pages: "314-346", plan_step: 8, plan_points: ["8.9"] },
    { chapter: "Ch 15", title: "Graph Theory", pages: "347-378", plan_step: 9, plan_points: ["9.1","9.2","9.3","9.4","9.5","9.6","9.7","9.8"] },
    { chapter: "Ch 16", title: "Challenge Problems", pages: "379-382", plan_step: 11 }
  ],
  recommended_action: "add-as-bonus"
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
{ id: "8.1", bonus: [{ label: "Ch 5 (Pigeonhole)", pdf: "Материали_EN/book-12", page: 134 }] }
{ id: "8.2", bonus: [{ label: "Ch 3 (PIE)", pdf: "Материали_EN/book-12", page: 65 }] }
{ id: "8.3", bonus: [{ label: "Ch 4 (1-1 Correspondences)", pdf: "Материали_EN/book-12", page: 99 }] }
{ id: "8.4", bonus: [{ label: "Ch 12 (Combinatorial Identities)", pdf: "Материали_EN/book-12", page: 259 }] }
{ id: "8.7", bonus: [{ label: "Ch 7 (Distributions)", pdf: "Материали_EN/book-12", page: 161 }] }
{ id: "8.9", bonus: [{ label: "Ch 14 (Generating Functions)", pdf: "Материали_EN/book-12", page: 314 }] }
{ id: "8.10", bonus: [{ label: "Ch 8 (Induction)", pdf: "Материали_EN/book-12", page: 177 }] }
{ id: "7.6", bonus: [{ label: "Ch 9-10 (Fibonacci, Recursion)", pdf: "Материали_EN/book-12", page: 188 }] }
{ id: "7.8", bonus: [{ label: "Ch 13 (Events with States)", pdf: "Материали_EN/book-12", page: 281 }] }
{ id: "9.1", bonus: [{ label: "Ch 15 (Graph Theory)", pdf: "Материали_EN/book-12", page: 347 }] }
{ id: "9.10", bonus: [{ label: "Ch 13.4 (Two-player Games)", pdf: "Материали_EN/book-12", page: 284 }] }
```

---

## 🚫 DISCOVERED NON-MATH FILES (skip)

### book-3 (1).pdf — ✅ ИДЕНТИФИЦИРАНО (SKIP)
**Идентификация:** Competitive Programming 4, Book 1 (Halim, Halim, Effendy, 2020)
**Решение:** `skip` — НЕ Е математика

```
Книгата е по състезателно програмиране (алгоритми и структури от данни за IOI/ICPC),
не по олимпиадна математика. Нула припокриване с 96-те математически точки.
Съдържание: Fenwick Tree, Segment Tree, Kruskal, Dijkstra, Floyd-Warshall, DP-TSP, SCC.
Препоръка: Премести в Материали_EN/Informatics/.
```

---

### book-4 (1).pdf — ✅ ГОТОВО (SKIP)
**Идентификация:** Competitive Programming 4, Book 2 (Halim, Halim, Effendy, 2020)
**Решение:** `skip` — НЕ Е математика

```
Книгата покрива Number Theory, Combinatorics, Game Theory, Geometry, Graph Theory
от гледна точка на competitive programming, не на олимпиадна математика.
Няколко точки (5.3 NT, 7.2 Basic Geometry) имат минимално припокриване,
но цялостно книгата е нерелевантна.
```

---

### book-9.pdf — ✅ ГОТОВО (SKIP)
**Идентификация:** Prealgebra (Rusczyk, Patrick, Boppana, 2011)
**Решение:** `skip` — под нивото

```
Prealgebra — ниво 6–8 клас (САЩ). Покрива аритметика, дроби, десетични, проценти.
За 11. клас, подготовка за областен/национален — под нивото.
```

---

## 🏆 PAST EXAMS — Областни кръгове 2016–2026 (11/11 готови)

### OLI-2016 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2016-10 ───
{
  source_pdf_probs: "Задачи_Минали_Години/OLI-2-Областен кръг-2016-10 кл-probs.pdf",
  source_pdf_sols: "Задачи_Минали_Години/OLI-2-Областен кръг-2016-10 кл-sol.pdf",
  year: 2016, grade: 10, exam_type: "областен",
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Показателно уравнение с параметър", difficulty: 3, plan_step: 5, plan_point: "5.1", add_as_task_to: ["5.1"], techniques_not_in_plan: ["Разположение на корени"], gap_severity: "minor" },
    { num: 2, topic: "Геометрия", subtopic: "Вписана окръжност и ъглополовяща", difficulty: 4, plan_step: 1, plan_point: "1.10", add_as_task_to: ["1.10","1.5"] },
    { num: 3, topic: "Комбинаторика", subtopic: "Пермутации с ограничения и рекурсия", difficulty: 3, plan_step: 8, plan_point: "8.8", add_as_task_to: ["8.8"] },
    { num: 4, topic: "ТЧ", subtopic: "Антиверига в делителна решетка", difficulty: 4, plan_step: 4, plan_point: "4.7", add_as_task_to: ["4.7","8.3"], techniques_not_in_plan: ["Антиверига (Спернер)"], gap_severity: "major" }
  ]
}

// ─── 2016-11 ───
{
  source_pdf_probs: "Задачи_Минали_Години/OLI-2-Областен кръг-2016-11 кл-probs.pdf",
  year: 2016, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Тригонометрично уравнение с параметър", difficulty: 3, plan_step: 5, plan_point: "5.1", techniques_not_in_plan: ["Тригонометрични уравнения","Разположение на корени"], gap_severity: "major" },
    { num: 2, topic: "Геометрия", subtopic: "Вписани окръжности в трапец", difficulty: 5, plan_step: 1, plan_point: "1.10" },
    { num: 3, topic: "Алгебра", subtopic: "Рекурентна редица и граница", difficulty: 4, plan_step: 7, plan_point: "7.7", techniques_not_in_plan: ["Телескопични произведения"] },
    { num: 4, topic: "Алгебра", subtopic: "Функционално неравенство", difficulty: 5, plan_step: 7, plan_point: "7.5", techniques_not_in_plan: ["Функционални неравенства с итерации"], gap_severity: "major" }
  ]
}

// ─── Нови точки: 10.11, 10.12 ───
{ id: "10.11", title: "Областен кръг 2016 – 10. клас", pdf: "Задачи_Минали_Години/OLI-2-Областен кръг-2016-10 кл-probs", page: 1, problems_page: 1, solutions_page: 1 }
{ id: "10.12", title: "Областен кръг 2016 – 11. клас", pdf: "Задачи_Минали_Години/OLI-2-Областен кръг-2016-11 кл-probs", page: 1, problems_page: 1, solutions_page: 1 }
```

---

### OLI-2017 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2017-10 ───
{
  year: 2017, grade: 10,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Показателни неравенства с параметър", difficulty: 3, plan_step: 6, plan_point: "6.1" },
    { num: 2, topic: "Геометрия", subtopic: "Окръжности с диаметри в ортоцентричен триъгълник", difficulty: 4, plan_step: 1, plan_point: "1.5" },
    { num: 3, topic: "Алгебра", subtopic: "Рекурентна редица с floor", difficulty: 4, plan_step: 7, plan_point: "7.7" },
    { num: 4, topic: "Комбинаторика", subtopic: "Блок-дизайни и двойно броене", difficulty: 5, plan_step: 8, plan_point: "8.3", techniques_not_in_plan: ["Блок-дизайни (2-(11,3,λ))"], gap_severity: "major" }
  ]
}

// ─── 2017-11 ───
{
  year: 2017, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Хомогенни уравнения и тригонометрия", difficulty: 3, plan_step: 5, plan_point: "5.1" },
    { num: 2, topic: "Геометрия", subtopic: "Ортоцентрични конфигурации", difficulty: 5, plan_step: 1, plan_point: "1.2" },
    { num: 3, topic: "Комбинаторика", subtopic: "Игри с делимост", difficulty: 5, plan_step: 9, plan_point: "9.10" },
    { num: 4, topic: "Комбинаторика", subtopic: "Екстремални множества и графи", difficulty: 5, plan_step: 9, plan_point: "9.5" }
  ]
}

// ─── Нови точки: 10.13, 10.14 ───
{ id: "10.13", title: "Областен кръг 2017 – 10 клас", pdf: "Задачи_Минали_Години/OLI-2-Областен кръг-2017-10 кл-probs", page: 1 }
{ id: "10.14", title: "Областен кръг 2017 – 11 клас", pdf: "Задачи_Минали_Години/OLI-2-Областен кръг-2017-11 кл-probs", page: 1 }
```

---

### OLI-2018 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2018-10 ───
{
  year: 2018, grade: 10,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Параметрично уравнение с квадратна функция", difficulty: 3, plan_step: 5, plan_point: "5.1", techniques_not_in_plan: ["Симетрия на квадратна функция с параметър"] },
    { num: 2, topic: "Алгебра", subtopic: "Деление на полиноми с остатък", difficulty: 3, plan_step: 5, plan_point: "5.7" },
    { num: 3, topic: "ТЧ", subtopic: "CRT и взаимно прости числа", difficulty: 5, plan_step: 3, plan_point: "3.6" },
    { num: 4, topic: "Геометрия", subtopic: "Вписани ъгли и вписана окръжност", difficulty: 5, plan_step: 1, plan_point: "1.5" }
  ]
}

// ─── 2018-11 ───
{
  year: 2018, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Експоненциално неравенство", difficulty: 3, plan_step: 7, plan_point: "7.3" },
    { num: 2, topic: "Алгебра", subtopic: "Рационални числа и ГП", difficulty: 4, plan_step: 5, plan_point: "5.4" },
    { num: 3, topic: "Геометрия", subtopic: "Ортоцентър и ъглополовящи", difficulty: 5, plan_step: 1, plan_point: "1.5" },
    { num: 4, topic: "Комбинаторика", subtopic: "Индуктивно оцветяване", difficulty: 5, plan_step: 8, plan_point: "8.10" }
  ]
}

// ─── Нови точки: 10.15, 10.16 ───
```

---

### OLI-2019 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2019-10 ───
{
  year: 2019, grade: 10,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Уравнения с радикали и параметър", difficulty: 3, plan_step: 5, plan_point: "5.4", techniques_not_in_plan: ["Радикални уравнения с параметър"], gap_severity: "major" },
    { num: 2, topic: "Геометрия", subtopic: "Чева, Карно, вписана/външновписана", difficulty: 5, plan_step: 1, plan_point: "1.2", techniques_not_in_plan: ["Теорема на Карно"], gap_severity: "major" },
    { num: 3, topic: "Комбинаторика", subtopic: "Паритет и двойно броене", difficulty: 4, plan_step: 8, plan_point: "8.3" },
    { num: 4, topic: "Алгебра", subtopic: "Полиноми с неотрицателни коефициенти", difficulty: 4, plan_step: 5, plan_point: "5.7" }
  ]
}

// ─── 2019-11 ───
{
  year: 2019, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Аритметична и геометрична прогресия", difficulty: 3, plan_step: 7, plan_point: "7.6" },
    { num: 2, topic: "Геометрия", subtopic: "Тригонометрични уравнения в триъгълник", difficulty: 2, plan_step: 1, plan_point: "1.6" },
    { num: 3, topic: "ТЧ", subtopic: "Рационалност и квадратични класове", difficulty: 5, plan_step: 4, plan_point: "4.5", techniques_not_in_plan: ["F2 векторни пространства"], gap_severity: "major" },
    { num: 4, topic: "Геометрия", subtopic: "Полюси/поляри, степени, хармонично", difficulty: 5, plan_step: 2, plan_point: "2.5" }
  ]
}

// ─── Нови точки: 10.17, 10.18 + Gaps: 2.9 (Карно), 5.11 (Радикални с параметър), 9.11 (F2) ───
```

---

### OLI-2020 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2020-10 ───
{
  year: 2020, grade: 10,
  problems: [
    { num: 1, topic: "Геометрия", subtopic: "Трапец, медицентър, лице", difficulty: 4, plan_step: 1, plan_point: "1.7" },
    { num: 2, topic: "Алгебра", subtopic: "Радикални уравнения, полагане", difficulty: 2, plan_step: 6, plan_point: "6.1" },
    { num: 3, topic: "Комбинаторика", subtopic: "Инварианти, монотонност, индукция", difficulty: 4, plan_step: 9, plan_point: "9.8" },
    { num: 4, topic: "Алгебра", subtopic: "Неравенства, средни, Коши-Шварц", difficulty: 4, plan_step: 6, plan_point: "6.4" }
  ]
}

// ─── 2020-11 ───
{
  year: 2020, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Полиноми, Виет, прогресии", difficulty: 3, plan_step: 5, plan_point: "5.1" },
    { num: 2, topic: "Геометрия", subtopic: "Вписани ъгли, синусова, вписан четириъгълник", difficulty: 4, plan_step: 1, plan_point: "1.5" },
    { num: 3, topic: "ТЧ", subtopic: "Делимост, взаимно прости, оценки", difficulty: 5, plan_step: 3, plan_point: "3.1" },
    { num: 4, topic: "Комбинаторика", subtopic: "Проекции на множества, двойно броене", difficulty: 5, plan_step: 8, plan_point: "8.3", techniques_not_in_plan: ["Проекции на множества"], gap_severity: "minor" }
  ]
}

// ─── Нови точки: 10.19, 10.20 ───
```

---

### OLI-2021 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2021-10 ───
{
  year: 2021, grade: 10,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Параметрична система, дискриминанта", difficulty: 4, plan_step: 5, plan_point: "5.1" },
    { num: 2, topic: "Геометрия", subtopic: "Външновписана окръжност, правоъгълен триъгълник", difficulty: 4, plan_step: 1, plan_point: "1.10" },
    { num: 3, topic: "ТЧ", subtopic: "Прости и съставни числа, рекурсия", difficulty: 4, plan_step: 4, plan_point: "4.5" },
    { num: 4, topic: "Комбинаторика", subtopic: "Инварианти, линейна алгебра над F2", difficulty: 5, plan_step: 9, plan_point: "9.8", techniques_not_in_plan: ["Линейна алгебра над F2"], gap_severity: "major" }
  ]
}

// ─── 2021-11 ───
{
  year: 2021, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Показателно уравнение с параметър", difficulty: 3, plan_step: 5, plan_point: "5.1" },
    { num: 2, topic: "Геометрия", subtopic: "Вписан четириъгълник, подобие", difficulty: 4, plan_step: 1, plan_point: "1.5" },
    { num: 3, topic: "ТЧ", subtopic: "Непрости числа, суми, индукция", difficulty: 4, plan_step: 4, plan_point: "4.5" },
    { num: 4, topic: "Комбинаторика", subtopic: "Инварианти, F2", difficulty: 5, plan_step: 9, plan_point: "9.8", techniques_not_in_plan: ["F2 факторпространство"], gap_severity: "major" }
  ]
}

// ─── Нови точки: 10.21, 10.22 + Gap: 9.11 (Векторни пространства над F2) ───
```

---

### OLI-2022 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2022-10 ───
{
  year: 2022, grade: 10,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Системи с параметър и модул", difficulty: 3, plan_step: 7, plan_point: "7.5" },
    { num: 2, topic: "Геометрия", subtopic: "Вписани ъгли и симетрия", difficulty: 4, plan_step: 1, plan_point: "1.5" },
    { num: 3, topic: "ТЧ", subtopic: "Делимост на произведения", difficulty: 3, plan_step: 3, plan_point: "3.1" },
    { num: 4, topic: "Комбинаторика", subtopic: "Дирихле и покрития", difficulty: 5, plan_step: 8, plan_point: "8.1", techniques_not_in_plan: ["Покриващи кодове"], gap_severity: "minor" }
  ]
}

// ─── 2022-11 ───
{
  year: 2022, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Ирационални неравенства", difficulty: 3, plan_step: 6, plan_point: "6.10", techniques_not_in_plan: ["Ирационални неравенства"], gap_severity: "minor" },
    { num: 2, topic: "Геометрия", subtopic: "Тригонометрия в триъгълник", difficulty: 4, plan_step: 1, plan_point: "1.6" },
    { num: 3, topic: "ТЧ", subtopic: "Делимост на произведения", difficulty: 3, plan_step: 3, plan_point: "3.1" },
    { num: 4, topic: "Комбинаторика", subtopic: "Екстремални множества от редици", difficulty: 5, plan_step: 8, plan_point: "8.1" }
  ]
}

// ─── Нови точки: 10.23, 10.24 + Gap: 6.11 (Ирационални неравенства), 7.9 (Системи с параметър) ───
```

---

### OLI-2023 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2023-10 ───
{
  year: 2023, grade: 10,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Ирационално уравнение с полагане", difficulty: 2, plan_step: 7, plan_point: "7.5" },
    { num: 2, topic: "Геометрия", subtopic: "Вписани ъгли и подобие", difficulty: 3, plan_step: 1, plan_point: "1.5" },
    { num: 3, topic: "Комбинаторика", subtopic: "Броене на прави и снопове", difficulty: 4, plan_step: 8, plan_point: "8.3", techniques_not_in_plan: ["Конфигурации от прави и снопове"], gap_severity: "minor" },
    { num: 4, topic: "Алгебра", subtopic: "Факторизация на полиноми", difficulty: 5, plan_step: 5, plan_point: "5.5", techniques_not_in_plan: ["Критерий на Айзенщайн"], gap_severity: "minor" }
  ]
}

// ─── 2023-11 ───
{
  year: 2023, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Показателно уравнение с параметър", difficulty: 4, plan_step: 7, plan_point: "7.5" },
    { num: 2, topic: "Геометрия", subtopic: "Ъглополовяща и косинусова теорема", difficulty: 4, plan_step: 1, plan_point: "1.6", techniques_not_in_plan: ["Ъглополовяща теорема"], gap_severity: "minor" },
    { num: 3, topic: "ТЧ", subtopic: "Делимост на степени на 2", difficulty: 4, plan_step: 3, plan_point: "3.1" },
    { num: 4, topic: "Комбинаторика", subtopic: "Двойно броене и блок-схеми", difficulty: 4, plan_step: 8, plan_point: "8.3" }
  ]
}

// ─── Нови точки: 10.25, 10.26 + Gaps: Айзенщайн (5.5), Ъглополовяща (1.6) ───
```

---

### OLI-2024 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2024-10 ───
{
  year: 2024, grade: 10,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Аритметична и геометрична прогресия", difficulty: 2, plan_step: 7, plan_point: "7.6" },
    { num: 2, topic: "Геометрия", subtopic: "Фиксирана окръжност и вписани ъгли", difficulty: 3, plan_step: 1, plan_point: "1.5" },
    { num: 3, topic: "ТЧ", subtopic: "Квадратични форми и прости числа", difficulty: 5, plan_step: 4, plan_point: "4.2", techniques_not_in_plan: ["Квадратични форми / суми на квадрати"], gap_severity: "major" },
    { num: 4, topic: "Комбинаторика", subtopic: "Оцветяване на правоъгълници mod 5", difficulty: 4, plan_step: 8, plan_point: "8.1" }
  ]
}

// ─── 2024-11 ───
{
  year: 2024, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Реципрочни уравнения и параметър", difficulty: 3, plan_step: 5, plan_point: "5.3", techniques_not_in_plan: ["Реципрочни уравнения"], gap_severity: "minor" },
    { num: 2, topic: "Геометрия", subtopic: "Вписан трапец и тригонометрия", difficulty: 3, plan_step: 1, plan_point: "1.6" },
    { num: 3, topic: "ТЧ", subtopic: "Делители и точни квадрати", difficulty: 4, plan_step: 3, plan_point: "3.1" },
    { num: 4, topic: "Комбинаторика", subtopic: "Двойно броене и AM-GM", difficulty: 3, plan_step: 8, plan_point: "8.3" }
  ]
}

// ─── Нови точки: 10.27, 10.28 + Gap: 4.10 (Квадратични форми), 5.12 (Реципрочни) ───
```

---

### OLI-2025 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2025-10 ───
{
  year: 2025, grade: 10,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Ирационални уравнения с полагане", difficulty: 3, plan_step: 5, plan_point: "5.1" },
    { num: 2, topic: "Геометрия", subtopic: "Вписани ъгли и степен на точка", difficulty: 5, plan_step: 1, plan_point: "1.5" },
    { num: 3, topic: "Комбинаторика", subtopic: "Вероятностен метод и покрития", difficulty: 5, plan_step: 8, plan_point: "8.3", techniques_not_in_plan: ["Вероятностен метод"], gap_severity: "major" },
    { num: 4, topic: "ТЧ", subtopic: "Прости числа и теореми на Ферма/Ойлер", difficulty: 5, plan_step: 3, plan_point: "3.3" }
  ]
}

// ─── 2025-11 ───
{
  year: 2025, grade: 11,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Полиноми и геометрична прогресия", difficulty: 3, plan_step: 5, plan_point: "5.1" },
    { num: 2, topic: "Геометрия", subtopic: "Степен на точка и подобие", difficulty: 4, plan_step: 1, plan_point: "1.4" },
    { num: 3, topic: "Комбинаторика", subtopic: "Пермутации и максимална сума", difficulty: 3, plan_step: 8, plan_point: "8.6" },
    { num: 4, topic: "ТЧ", subtopic: "Прости числа и теорема на Ферма", difficulty: 5, plan_step: 3, plan_point: "3.3" }
  ]
}

// ─── Нови точки: 10.29, 10.30 + Gap: 8.12 (Вероятностен метод) ───
```

---

### OLI-2026 (10 + 11 кл) — ✅ ГОТОВО

```js
// ─── 2026-10 ───
{
  year: 2026, grade: 10,
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Аритметична прогресия и телескопиране", difficulty: 3, plan_step: 7, plan_point: "7.6" },
    { num: 2, topic: "Геометрия", subtopic: "Правилен петоъгълник, Менелай", difficulty: 5, plan_step: 1, plan_point: "1.1", techniques_not_in_plan: ["Теорема за ъглополовящата"] },
    { num: 3, topic: "ТЧ", subtopic: "Делители и специални числа", difficulty: 4, plan_step: 4, plan_point: "4.5", techniques_not_in_plan: ["Постулат на Бертран"] },
    { num: 4, topic: "Геометрия", subtopic: "Решетъчни многоъгълници, формула на Пик", difficulty: 5, plan_step: 1, plan_point: "1.7", techniques_not_in_plan: ["Формула на Пик"], gap_severity: "major" }
  ]
}

// ─── 2026-11 ───
{
  year: 2026, grade: 11,
  source_pdf_sols: null, // CHECK: липсва 11 кл-sol
  problems: [
    { num: 1, topic: "Алгебра", subtopic: "Ирационално уравнение, факторизация", difficulty: 4, plan_step: 5, plan_point: "5.4" },
    { num: 2, topic: "Геометрия", subtopic: "Равнобедрен трапец, косинусова теорема", difficulty: 4, plan_step: 1, plan_point: "1.6" },
    { num: 3, topic: "Алгебра", subtopic: "Квадратни полиноми, дискриминант", difficulty: 5, plan_step: 5, plan_point: "5.5" },
    { num: 4, topic: "Комбинаторика", subtopic: "Пътища в таблица, сума на числа", difficulty: 5, plan_step: 9, plan_point: "9.1" }
  ]
}

// ─── Нови точки: 10.31, 10.32 + Gap: 1.11 (Формула на Пик) ───
```

---

## 📖 BG MATERIALS — Български сборници (11/11)

### OT_2010.pdf — ✅ ГОТОВО

```js
// ─── КНИГА ───
{
  file: "Материали_БГ/OT_2010.pdf",
  title: "Олимпийски теми 2010",
  language: "BG",
  structure: [
    { chapter: "1. ТЧ", author: "Иванов", pages: "4-7", plan_step: 3, plan_points: ["3.8","4.5"] },
    { chapter: "2. Комб. тъждества", author: "Колев", pages: "8-15", plan_step: 8, plan_points: ["8.4","8.5","8.3"] },
    { chapter: "3. Релации", author: "Кортезов", pages: "16-22", plan_step: 9, plan_points: ["9.5","8.3","9.1"] },
    { chapter: "4. Толкова много квадрати", author: "Събева", pages: "23-30", plan_step: 1, plan_points: ["1.5","2.4","1.7"] },
    { chapter: "5. Вписана окръжност", author: "Белухов", pages: "31-39", plan_step: 1, plan_points: ["1.10","1.4","2.1"] },
    { chapter: "6. ФУ", author: "Николов", pages: "40-45", plan_step: 7, plan_points: ["7.1","7.5","7.7"] },
    { chapter: "7. Задачи по ТЧ", author: "Бойваленков", pages: "46-59", plan_step: 3, plan_points: ["3.2","3.3","3.4","4.4","4.5"] },
    { chapter: "8. Комб. и графи", author: "Герджиков", pages: "60-74", plan_step: 8, plan_points: ["9.1","9.2","9.5","9.6","8.1","8.2"] },
    { chapter: "9. Хармонично отношение", author: "Боев", pages: "75-89", plan_step: 2, plan_points: ["2.1","2.3","2.5","1.4"] }
  ],
  recommended_action: "add-as-bonus + tasks"
}
```

```js
// ─── АКТУАЛИЗАЦИЯ (highlights) ───
{ id: "3.8", bonus: [{ label: "Комплексни числа в крайна аритметика (Иванов)", pdf: "Материали_БГ/OT_2010", page: 4 }, { label: "Теорема на Люка", pdf: "Материали_БГ/OT_2010", page: 5 }],
  tasks: [{ label: "Зад 1 (Шортлист МОМ 2003)", pdf: "Материали_БГ/OT_2010", page: 6, difficulty: 5 },
          { label: "Зад 2 (US National 2009)", pdf: "Материали_БГ/OT_2010", page: 6, difficulty: 4 },
          { label: "Зад 2 (Japan 2008)", pdf: "Материали_БГ/OT_2010", page: 7, difficulty: 4 }] }
{ id: "8.4", bonus: [{ label: "Комбинаторни тъждества (Колев)", pdf: "Материали_БГ/OT_2010", page: 8 }],
  tasks: [{ label: "Зад 1", pdf: "Материали_БГ/OT_2010", page: 8, difficulty: 2 },
          { label: "Зад 2", pdf: "Материали_БГ/OT_2010", page: 11, difficulty: 3 },
          { label: "Зад 3", pdf: "Материали_БГ/OT_2010", page: 11, difficulty: 4 },
          { label: "Зад 6", pdf: "Материали_БГ/OT_2010", page: 13, difficulty: 4 }] }
{ id: "9.5", bonus: [{ label: "Теорема на Туран (Кортезов)", pdf: "Материали_БГ/OT_2010", page: 20 }],
  tasks: [{ label: "Зад 4 (Туран)", pdf: "Материали_БГ/OT_2010", page: 20, difficulty: 5 },
          { label: "Зад 5 (Мантел)", pdf: "Материали_БГ/OT_2010", page: 21, difficulty: 4 }] }
{ id: "1.5", bonus: [{ label: "Квадрати и ротации (Събева)", pdf: "Материали_БГ/OT_2010", page: 23 }],
  tasks: [{ label: "Зад 1 (Московска 2005)", pdf: "Материали_БГ/OT_2010", page: 25, difficulty: 4 },
          { label: "Зад 2 (Сангаку)", pdf: "Материали_БГ/OT_2010", page: 25, difficulty: 4 }] }
{ id: "2.4", bonus: [{ label: "Спирално подобие и квадрати (Събева)", pdf: "Материали_БГ/OT_2010", page: 27 }],
  tasks: [{ label: "Зад 5", pdf: "Материали_БГ/OT_2010", page: 27, difficulty: 4 },
          { label: "Зад 6 (БГ за МОМ)", pdf: "Материали_БГ/OT_2010", page: 28, difficulty: 5 }] }
{ id: "1.10", bonus: [{ label: "Лема за вписаната окръжност (Белухов)", pdf: "Материали_БГ/OT_2010", page: 31 }],
  tasks: [{ label: "Зад (Френски МОМ 2005)", pdf: "Материали_БГ/OT_2010", page: 32, difficulty: 5 },
          { label: "Зад (МОМ 1998)", pdf: "Материали_БГ/OT_2010", page: 32, difficulty: 5 },
          { label: "Зад (Московска 2001)", pdf: "Материали_БГ/OT_2010", page: 34, difficulty: 5 }] }
{ id: "1.4", bonus: [{ label: "Радикална ос (Белухов)", pdf: "Материали_БГ/OT_2010", page: 36 }],
  tasks: [{ label: "Зад (МОМ 2008, Шмаров)", pdf: "Материали_БГ/OT_2010", page: 37, difficulty: 5 }] }
{ id: "7.1", bonus: [{ label: "Обобщение на ФУ (Николов)", pdf: "Материали_БГ/OT_2010", page: 40 }],
  tasks: [{ label: "Зад 1 (МОМ 86)", pdf: "Материали_БГ/OT_2010", page: 40, difficulty: 4 },
          { label: "Зад 2 (МОМ 87)", pdf: "Материали_БГ/OT_2010", page: 42, difficulty: 5 },
          { label: "Зад 3 (МОМ 92)", pdf: "Материали_БГ/OT_2010", page: 43, difficulty: 5 },
          { label: "Зад 4 (МОМ 05)", pdf: "Материали_БГ/OT_2010", page: 44, difficulty: 5 }] }
{ id: "3.2", bonus: [{ label: "Задачи по ТЧ (Бойваленков)", pdf: "Материали_БГ/OT_2010", page: 46 }],
  tasks: [{ label: "Зад 1", pdf: "Материали_БГ/OT_2010", page: 46, difficulty: 2 },
          { label: "Зад 2", pdf: "Материали_БГ/OT_2010", page: 46, difficulty: 4 },
          { label: "Зад 3", pdf: "Материали_БГ/OT_2010", page: 47, difficulty: 4 },
          { label: "Зад 4 (МОМ 2001)", pdf: "Материали_БГ/OT_2010", page: 47, difficulty: 5 }] }
{ id: "3.3", bonus: [{ label: "Ферма (Бойваленков)", pdf: "Материали_БГ/OT_2010", page: 49 }],
  tasks: [{ label: "Зад 5", pdf: "Материали_БГ/OT_2010", page: 48, difficulty: 5 },
          { label: "Зад 8", pdf: "Материали_БГ/OT_2010", page: 49, difficulty: 4 }] }
{ id: "4.4", bonus: [{ label: "Точни квадрати (Бойваленков)", pdf: "Материали_БГ/OT_2010", page: 50 }],
  tasks: [{ label: "Зад 7", pdf: "Материали_БГ/OT_2010", page: 49, difficulty: 4 },
          { label: "Зад 9", pdf: "Материали_БГ/OT_2010", page: 49, difficulty: 5 },
          { label: "Зад 16", pdf: "Материали_БГ/OT_2010", page: 52, difficulty: 4 }] }
{ id: "9.1", bonus: [{ label: "Комб. и графи (Герджиков)", pdf: "Материали_БГ/OT_2010", page: 60 }],
  tasks: [{ label: "Зад 1", pdf: "Материали_БГ/OT_2010", page: 60, difficulty: 3 },
          { label: "Зад 8", pdf: "Материали_БГ/OT_2010", page: 69, difficulty: 5 }] }
{ id: "9.6", bonus: [{ label: "Рамзи и Хол (Герджиков)", pdf: "Материали_БГ/OT_2010", page: 63 }],
  tasks: [{ label: "Зад 4", pdf: "Материали_БГ/OT_2010", page: 63, difficulty: 5 },
          { label: "Зад 5", pdf: "Материали_БГ/OT_2010", page: 65, difficulty: 5 }] }
{ id: "2.1", bonus: [{ label: "Хармонично отношение (Боев)", pdf: "Материали_БГ/OT_2010", page: 75 }],
  tasks: [{ label: "Пример 1", pdf: "Материали_БГ/OT_2010", page: 82, difficulty: 5 },
          { label: "Зад 1 (МОМ 2008)", pdf: "Материали_БГ/OT_2010", page: 84, difficulty: 5 },
          { label: "Зад 2 (НОМ БГ 2003)", pdf: "Материали_БГ/OT_2010", page: 84, difficulty: 5 },
          { label: "Зад 3 (TST Китай 2002)", pdf: "Материали_БГ/OT_2010", page: 85, difficulty: 5 }] }
{ id: "2.5", bonus: [{ label: "Полюси и поляри (Боев)", pdf: "Материали_БГ/OT_2010", page: 81 }] }
```

---

### OT_2012.pdf — ✅ ГОТОВО

```js
// ─── КНИГА ───
{
  file: "Материали_БГ/OT_2012.pdf",
  structure: [
    { article: "Делители на полиноми", author: "Ал. Иванов", pages: "4-7", plan_step: 5, plan_points: ["5.7","5.5","3.1","3.2"] },
    { article: "Комбинаторика", author: "Ем. Колев", pages: "8-12", plan_step: 9, plan_points: ["9.1","9.3","9.7","9.8","8.1"] },
    { article: "Геометрични неравенства", author: "Н. Белухов", pages: "13-24", plan_step: 2, plan_points: ["2.8","1.5","1.6","1.7"] },
    { article: "Неравенства от БОМ/МлБОМ", author: "Н. Николов", pages: "25-33", plan_step: 6, plan_points: ["6.1-6.10"] },
    { article: "RMM 2011-2013", author: "П. Бойваленков", pages: "34-44", plan_step: "mixed" },
    { article: "Неравенство на Фишер", author: "Пл. Пенчев", pages: "45-49", plan_step: 8, new_point: "8.14" },
    { article: "Полиноми", author: "Р. Рафаилов", pages: "50-65", plan_step: 5, plan_points: ["5.5","5.6","5.8"] },
    { article: "Симедиани", author: "Ст. Боев", pages: "66-80", plan_step: 2, plan_points: ["2.2","2.1","1.3","1.4"] }
  ],
  recommended_action: "add-as-bonus + new-point 8.14"
}
```

```js
// ─── АКТУАЛИЗАЦИЯ ───
{ id: "5.7", tasks: [
  { label: "Иванов, Зад 1 (Лема на Шур)", pdf: "Материали_БГ/OT_2012", page: 5, difficulty: 4 },
  { label: "Иванов, Зад 2", pdf: "Материали_БГ/OT_2012", page: 6, difficulty: 4 },
  { label: "Иванов, Зад 3", pdf: "Материали_БГ/OT_2012", page: 7, difficulty: 5 },
  { label: "Иванов, Зад 4", pdf: "Материали_БГ/OT_2012", page: 7, difficulty: 5 }
]}
{ id: "9.1", tasks: [
  { label: "Колев, Зад 1", pdf: "Материали_БГ/OT_2012", page: 8, difficulty: 4 },
  { label: "Колев, Зад 2", pdf: "Материали_БГ/OT_2012", page: 9, difficulty: 4 },
  { label: "Колев, Зад 3", pdf: "Материали_БГ/OT_2012", page: 9, difficulty: 4 },
  { label: "Колев, Зад 4", pdf: "Материали_БГ/OT_2012", page: 10, difficulty: 4 },
  { label: "Колев, Зад 5", pdf: "Материали_БГ/OT_2012", page: 10, difficulty: 5 },
  { label: "Колев, Зад 6", pdf: "Материали_БГ/OT_2012", page: 11, difficulty: 5 },
  { label: "Колев, Зад 7", pdf: "Материали_БГ/OT_2012", page: 12, difficulty: 5 }
]}
{ id: "2.8", tasks: [
  { label: "Белухов, Ескимос", pdf: "Материали_БГ/OT_2012", page: 14, difficulty: 4 },
  { label: "Белухов, Зад 1", pdf: "Материали_БГ/OT_2012", page: 15, difficulty: 4 },
  { label: "Белухов (Квант)", pdf: "Материали_БГ/OT_2012", page: 16, difficulty: 5 },
  { label: "Белухов (МОМ 1990)", pdf: "Материали_БГ/OT_2012", page: 16, difficulty: 5 },
  { label: "Белухов (Туймаада 2005)", pdf: "Материали_БГ/OT_2012", page: 17, difficulty: 5 },
  { label: "Белухов (Ердьош-Мордел)", pdf: "Материали_БГ/OT_2012", page: 18, difficulty: 5 },
  { label: "Белухов (Птолемей, ромб)", pdf: "Материали_БГ/OT_2012", page: 19, difficulty: 5 },
  { label: "Белухов, Зад 2", pdf: "Материали_БГ/OT_2012", page: 20, difficulty: 5 },
  { label: "Белухов, Зад 3", pdf: "Материали_БГ/OT_2012", page: 21, difficulty: 5 }
]}
{ id: "6.1", tasks: [
  { label: "Николов, Зад 1 (МлБОМ 2002)", pdf: "Материали_БГ/OT_2012", page: 26, difficulty: 3 },
  { label: "Николов, Зад 2 (МлБОМ 2003)", pdf: "Материали_БГ/OT_2012", page: 27, difficulty: 4 },
  { label: "Николов, Зад 3 (МлБОМ 2005)", pdf: "Материали_БГ/OT_2012", page: 28, difficulty: 4 },
  { label: "Николов, Зад 4 (МлБОМ 2009)", pdf: "Материали_БГ/OT_2012", page: 28, difficulty: 4 },
  { label: "Николов, Зад 5 (МлБОМ 2011)", pdf: "Материали_БГ/OT_2012", page: 28, difficulty: 4 },
  { label: "Николов, Зад 6 (МлБОМ 2012)", pdf: "Материали_БГ/OT_2012", page: 29, difficulty: 4 },
  { label: "Николов, Зад 7 (БОМ 2005)", pdf: "Материали_БГ/OT_2012", page: 29, difficulty: 4 },
  { label: "Николов, Зад 8 (БОМ 2006)", pdf: "Материали_БГ/OT_2012", page: 31, difficulty: 4 },
  { label: "Николов, Зад 9 (БОМ 2010)", pdf: "Материали_БГ/OT_2012", page: 31, difficulty: 5 },
  { label: "Николов, Зад 10 (БОМ 2011)", pdf: "Материали_БГ/OT_2012", page: 31, difficulty: 5 },
  { label: "Николов, Зад 11 (БОМ 2012)", pdf: "Материали_БГ/OT_2012", page: 32, difficulty: 5 },
  { label: "Николов, Зад 12 (МОМ 2008)", pdf: "Материали_БГ/OT_2012", page: 32, difficulty: 5 }
]}
{ id: "5.5", tasks: [
  { label: "Рафаилов, Зад 5 (Мейсън-Стотер)", pdf: "Материали_БГ/OT_2012", page: 54, difficulty: 5 },
  { label: "Рафаилов, Зад 6", pdf: "Материали_БГ/OT_2012", page: 55, difficulty: 5 },
  { label: "Рафаилов, Зад 7 (Ферма за полиноми)", pdf: "Материали_БГ/OT_2012", page: 56, difficulty: 5 }
]}
{ id: "5.6", tasks: [
  { label: "Рафаилов, Зад 8 (Чебишев)", pdf: "Материали_БГ/OT_2012", page: 56, difficulty: 5 },
  { label: "Рафаилов, Зад 9", pdf: "Материали_БГ/OT_2012", page: 57, difficulty: 5 }
]}
{ id: "5.8", tasks: [
  { label: "Рафаилов, Зад 10 (Амер. 1975)", pdf: "Материали_БГ/OT_2012", page: 58, difficulty: 4 },
  { label: "Рафаилов, Зад 11 (Шортлист МОМ 1983)", pdf: "Материали_БГ/OT_2012", page: 58, difficulty: 5 },
  { label: "Рафаилов, Зад 12 (Иран)", pdf: "Материали_БГ/OT_2012", page: 58, difficulty: 5 }
]}
{ id: "2.2", tasks: [
  { label: "Боев, Зад 1 (Колмогоров)", pdf: "Материали_БГ/OT_2012", page: 75, difficulty: 5 },
  { label: "Боев, Зад 2 (МОМ 2012)", pdf: "Материали_БГ/OT_2012", page: 76, difficulty: 5 },
  { label: "Боев, Зад 3 (TST Иран 2006)", pdf: "Материали_БГ/OT_2012", page: 76, difficulty: 5 },
  { label: "Боев, Зад 4", pdf: "Материали_БГ/OT_2012", page: 78, difficulty: 5 },
  { label: "Боев, Зад 5", pdf: "Материали_БГ/OT_2012", page: 78, difficulty: 5 },
  { label: "Боев, Зад 6", pdf: "Материали_БГ/OT_2012", page: 78, difficulty: 5 },
  { label: "Боев, Зад 7", pdf: "Материали_БГ/OT_2012", page: 78, difficulty: 5 },
  { label: "Боев, Зад 8", pdf: "Материали_БГ/OT_2012", page: 78, difficulty: 5 },
  { label: "Боев, Зад 9", pdf: "Материали_БГ/OT_2012", page: 79, difficulty: 5 },
  { label: "Боев, Зад 10", pdf: "Материали_БГ/OT_2012", page: 79, difficulty: 5 },
  { label: "Боев, Зад 11 (БОМ 2009)", pdf: "Материали_БГ/OT_2012", page: 79, difficulty: 5 },
  { label: "Боев, Зад 12", pdf: "Материали_БГ/OT_2012", page: 79, difficulty: 5 },
  { label: "Боев, Зад 13", pdf: "Материали_БГ/OT_2012", page: 79, difficulty: 5 }
]}

// ─── НОВА ТОЧКА 8.14: Неравенство на Фишер ───
{ id: "8.14", title: "Неравенство на Фишер",
  desc: "Горна граница за размера на L-интересна фамилия от подмножества.",
  source: "OT_2012, Пл. Пенчев", pdf: "Материали_БГ/OT_2012", page: 45,
  explanation: "ФОРМУЛИРОВКА: Нека X = {x1,...,xn}, L = {l1,...,lk} и A = {A1,...,Am} е фамилия от подмножества на X. Ако |Ai ∩ Aj| ∈ L за всички i ≠ j, то |A| ≤ ∑_{i=1}^k C(n,i).\n\nКОГА: Екстремални задачи за множества с ограничения върху сеченията.\n\nСВОЙСТВА: Специален случай L={1} дава m ≤ n.\n\nТРИК: Кодирай множествата като вектори; използвай интерполационен полином g(x) = ∏(x - l_i)." }
```

---

### BMS_2003-2005.pdf — ✅ ГОТОВО

```js
// ─── 17 турнира (2003-2005) ───
// 11 кл задачи ~48 на брой
// Доминиращи точки: 5.4 (8 задачи), 1.10 (5), 7.1 (4), 1.1 (3), 8.1 (3)

// ─── АКТУАЛИЗАЦИЯ (примери) ───
{ id: "7.1", tasks: [
  { label: "Зимни 2003, 11.1 (рекурентна редица)", pdf: "Материали_БГ/BMS_2003-2005", page: 1, difficulty: 4 },
  { label: "Пролетен 2005, 11.1 (редица, граница)", pdf: "Материали_БГ/BMS_2003-2005", page: 35, difficulty: 5 },
  { label: "НОМ областен 2004, 11.1 (геом/триг прогресия)", pdf: "Материали_БГ/BMS_2003-2005", page: 18, difficulty: 4 }
]}
{ id: "5.4", tasks: [
  { label: "НОМ областен 2003, 11.1 (лог. уравнение, параметър)", pdf: "Материали_БГ/BMS_2003-2005", page: 7, difficulty: 4 },
  { label: "НОМ национален 2003, 11.1 (4^x, параметър)", pdf: "Материали_БГ/BMS_2003-2005", page: 22, difficulty: 4 },
  { label: "Зимни 2005, 11.2 (лог. уравнение)", pdf: "Материали_БГ/BMS_2003-2005", page: 32, difficulty: 4 },
  { label: "НОМ областен 2005, 11.1 (уравнение, параметър)", pdf: "Материали_БГ/BMS_2003-2005", page: 38, difficulty: 4 }
]}
{ id: "9.10", tasks: [
  { label: "Зимни 2003, 11.3 (игра с коефициенти)", pdf: "Материали_БГ/BMS_2003-2005", page: 3, difficulty: 5 },
  { label: "Зимни 2005, 11.4 (шахматен турнир)", pdf: "Материали_БГ/BMS_2003-2005", page: 34, difficulty: 5 }
]}
{ id: "4.5", tasks: [
  { label: "НОМ национален 2003, 11.3 (редица, прости)", pdf: "Материали_БГ/BMS_2003-2005", page: 23, difficulty: 5 },
  { label: "Балканска 2004, Зад 2 (p²-p+1 куб)", pdf: "Материали_БГ/BMS_2003-2005", page: 28, difficulty: 4 }
]}

// ─── ПРЕДЛОЖЕНИЕ: Нова точка 5.11 (Разположение на корени) ───
```

---

### BMS_2012-2015.pdf — ✅ ГОТОВО

```js
// ─── Структура: 4 учебни години ───
// НОМ 2012-2015 областен/национален + БОМ/МОМ контролни + Балканска/Международна

// ─── АКТУАЛИЗАЦИЯ ───
{ id: "10.1", tasks: [
  { label: "НОМ 2012, областен, 11.1 (тригонометрия)", pdf: "Материали_БГ/BMS_2012-2015", page: 12, difficulty: 4 },
  { label: "НОМ 2012, национален, Зад 1 (τ(n))", pdf: "Материали_БГ/BMS_2012-2015", page: 14, difficulty: 5 },
  { label: "НОМ 2012, национален, Зад 6 (геом., постоянна)", pdf: "Материали_БГ/BMS_2012-2015", page: 14, difficulty: 5 }
]}
{ id: "10.2", tasks: [
  { label: "НОМ 2013, областен, 11.1 (параметри в кубично)", pdf: "Материали_БГ/BMS_2012-2015", page: 28, difficulty: 4 },
  { label: "НОМ 2013, национален, Зад 1 (прости p,q)", pdf: "Материали_БГ/BMS_2012-2015", page: 30, difficulty: 5 },
  { label: "НОМ 2013, национален, Зад 6 (геометрия)", pdf: "Материали_БГ/BMS_2012-2015", page: 30, difficulty: 5 }
]}
{ id: "10.3", tasks: [
  { label: "НОМ 2014, областен, 11.1 (показателно)", pdf: "Материали_БГ/BMS_2012-2015", page: 44, difficulty: 4 },
  { label: "НОМ 2014, национален, Зад 4 (p²|q³+1)", pdf: "Материали_БГ/BMS_2012-2015", page: 46, difficulty: 5 },
  { label: "НОМ 2014, национален, Зад 6 (впис. окр.)", pdf: "Материали_БГ/BMS_2012-2015", page: 46, difficulty: 5 }
]}
{ id: "10.4", tasks: [
  { label: "НОМ 2015, областен, 11.1 (показателно)", pdf: "Материали_БГ/BMS_2012-2015", page: 59, difficulty: 4 },
  { label: "НОМ 2015, национален, Зад 6 (дъска 19×2015)", pdf: "Материали_БГ/BMS_2012-2015", page: 63, difficulty: 5 },
  { label: "НОМ 2015, национален, Зад 1 (шестоъгълник)", pdf: "Материали_БГ/BMS_2012-2015", page: 61, difficulty: 5 }
]}
{ id: "10.5", tasks: [
  { label: "Контролно БОМ 2012, Зад 1 (геом.)", pdf: "Материали_БГ/BMS_2012-2015", page: 13, difficulty: 5 },
  { label: "Контролно БОМ 2013, Зад 3 (граф)", pdf: "Материали_БГ/BMS_2012-2015", page: 31, difficulty: 5 },
  { label: "Контролно БОМ 2014, Зад 1 (редица)", pdf: "Материали_БГ/BMS_2012-2015", page: 47, difficulty: 5 },
  { label: "Контролно БОМ 2015, Зад 4 (неравенство)", pdf: "Материали_БГ/BMS_2012-2015", page: 63, difficulty: 5 }
]}
{ id: "10.6", tasks: [
  { label: "Контролно МОМ 2012, Зад 1 (геом.)", pdf: "Материали_БГ/BMS_2012-2015", page: 14, difficulty: 5 },
  { label: "Контролно МОМ 2013, Зад 4 (ФУ)", pdf: "Материали_БГ/BMS_2012-2015", page: 32, difficulty: 5 },
  { label: "Контролно МОМ 2014, Зад 3 (полиноми)", pdf: "Материали_БГ/BMS_2012-2015", page: 49, difficulty: 5 },
  { label: "Контролно МОМ 2015, Зад 2 (ФУ неравенство)", pdf: "Материали_БГ/BMS_2012-2015", page: 64, difficulty: 5 }
]}
```

---

### BMC_2003-2006.pdf — ✅ ГОТОВО

```js
// ─── 24 National Round задачи (2003-2006) ───
// Всички подходящи за 11 кл, difficulty ≥ 4

// ─── АКТУАЛИЗАЦИЯ (примерни) ───
{ id: "10.10", tasks: [
  // 2003 National
  { label: "2003 Nat Зад 1 (суми x_p+x_q+x_r)", pdf: "Материали_БГ/BMC_2003-2006", page: 14, difficulty: 4 },
  { label: "2003 Nat Зад 2 (височина, ъгли)", pdf: "Материали_БГ/BMC_2003-2006", page: 14, difficulty: 4 },
  { label: "2003 Nat Зад 3 (рек. редица, кв.)", pdf: "Материали_БГ/BMC_2003-2006", page: 14, difficulty: 5 },
  { label: "2003 Nat Зад 5 (рационални, abc)", pdf: "Материали_БГ/BMC_2003-2006", page: 14, difficulty: 5 },
  { label: "2004 Nat Зад 1 (впис. окр.)", pdf: "Материали_БГ/BMC_2003-2006", page: 24, difficulty: 5 },
  { label: "2004 Nat Зад 2 (харм. сума)", pdf: "Материали_БГ/BMC_2003-2006", page: 24, difficulty: 4 },
  { label: "2004 Nat Зад 5 (наредени двойки)", pdf: "Материали_БГ/BMC_2003-2006", page: 24, difficulty: 5 },
  { label: "2005 Nat Зад 1 (тройки, кв.)", pdf: "Материали_БГ/BMC_2003-2006", page: 41, difficulty: 4 },
  { label: "2005 Nat Зад 3 (мн. M)", pdf: "Материали_БГ/BMC_2003-2006", page: 41, difficulty: 5 },
  { label: "2005 Nat Зад 6 (c(c²-c+1))", pdf: "Материали_БГ/BMC_2003-2006", page: 41, difficulty: 5 },
  { label: "2006 Nat Зад 4 (p² | 2^{p-1}-1)", pdf: "Материали_БГ/BMC_2003-2006", page: 59, difficulty: 5 },
  { label: "2006 Nat Зад 6 (мн. от точки)", pdf: "Материали_БГ/BMC_2003-2006", page: 59, difficulty: 5 }
]}
```

---

### BMO_1984-2006.pdf — ✅ ГОТОВО

```js
// ─── 23 олимпиади × 4 задачи = 92 задачи ───
// Най-използвани: 1.5 (14), 1.7 (10), 6.1 (9), 1.4 (8), 4.4 (8)

// ─── АКТУАЛИЗАЦИЯ (highlights) ───
{ id: "1.4", tasks: [
  { label: "BMO 1986/2 (Сфера през 6 точки)", pdf: "Материали_БГ/BMO_1984-2006", page: 3, difficulty: 4 },
  { label: "BMO 1995/2 (Две окръжности, r1/r2)", pdf: "Материали_БГ/BMO_1984-2006", page: 12, difficulty: 5 }
]}
{ id: "1.5", tasks: [
  { label: "BMO 1984/2 (Ортоцентрове)", pdf: "Материали_БГ/BMO_1984-2006", page: 1, difficulty: 4 },
  { label: "BMO 1993/3 (Допиращи се окръжности)", pdf: "Материали_БГ/BMO_1984-2006", page: 10, difficulty: 4 }
]}
{ id: "1.7", tasks: [
  { label: "BMO 1989/3 (Медицентър, лице)", pdf: "Материали_БГ/BMO_1984-2006", page: 6, difficulty: 4 },
  { label: "BMO 1999/3 (Педален триъгълник)", pdf: "Материали_БГ/BMO_1984-2006", page: 16, difficulty: 5 }
]}
{ id: "1.8", tasks: [
  { label: "BMO 1996/1 (OG ≤ √(R(R−2r)))", pdf: "Материали_БГ/BMO_1984-2006", page: 13, difficulty: 4 }
]}
{ id: "3.1", tasks: [
  { label: "BMO 1989/1 (Делители, сума на квадрати)", pdf: "Материали_БГ/BMO_1984-2006", page: 6, difficulty: 4 },
  { label: "BMO 2001/1 (2ⁿ − 1 = ab)", pdf: "Материали_БГ/BMO_1984-2006", page: 18, difficulty: 4 }
]}
{ id: "3.3", tasks: [
  { label: "BMO 1984/3 (5ⁿ от 5ᵐ с цифри)", pdf: "Материали_БГ/BMO_1984-2006", page: 1, difficulty: 4 }
]}
{ id: "3.4", tasks: [
  { label: "BMO 1992/1 (Делимост на 1992)", pdf: "Материали_БГ/BMO_1984-2006", page: 9, difficulty: 4 }
]}
{ id: "4.2", tasks: [
  { label: "BMO 1991/2 (Херонови триъгълници)", pdf: "Материали_БГ/BMO_1984-2006", page: 8, difficulty: 5 }
]}
{ id: "4.4", tasks: [
  { label: "BMO 2002/2 (1 + 5aₙaₙ₊₁ кв.)", pdf: "Материали_БГ/BMO_1984-2006", page: 19, difficulty: 4 },
  { label: "BMO 2005/2 (p² − p + 1 куб)", pdf: "Материали_БГ/BMO_1984-2006", page: 22, difficulty: 4 }
]}
{ id: "5.1", tasks: [
  { label: "BMO 1988/2 (Полином 2 променливи)", pdf: "Материали_БГ/BMO_1984-2006", page: 5, difficulty: 5 }
]}
{ id: "5.10", tasks: [
  { label: "BMO 1987/3 (Тригонометрично уравнение)", pdf: "Материали_БГ/BMO_1984-2006", page: 4, difficulty: 3 }
]}
{ id: "6.1", tasks: [
  { label: "BMO 1984/1 (Неравенство с αᵢ)", pdf: "Материали_БГ/BMO_1984-2006", page: 1, difficulty: 4 },
  { label: "BMO 2001/3 (a+b+c ≥ abc)", pdf: "Материали_БГ/BMO_1984-2006", page: 18, difficulty: 4 },
  { label: "BMO 2006/1 (1/(a(1+b)) + ...)", pdf: "Материали_БГ/BMO_1984-2006", page: 23, difficulty: 4 }
]}
{ id: "6.4", tasks: [
  { label: "BMO 1998/2 (Радикално неравенство)", pdf: "Материали_БГ/BMO_1984-2006", page: 15, difficulty: 5 },
  { label: "BMO 2005/3 (a²/b + b²/c + c²/a)", pdf: "Материали_БГ/BMO_1984-2006", page: 22, difficulty: 4 }
]}
{ id: "7.1", tasks: [
  { label: "BMO 1987/1 (f(x+y) = f(x)f(a−y)+...)", pdf: "Материали_БГ/BMO_1984-2006", page: 4, difficulty: 5 },
  { label: "BMO 1997/4 (f(xf(x)+f(y)) = ...)", pdf: "Материали_БГ/BMO_1984-2006", page: 14, difficulty: 5 }
]}
{ id: "8.3", tasks: [
  { label: "BMO 1989/4 (Множества от 3-ел. подмн.)", pdf: "Материали_БГ/BMO_1984-2006", page: 6, difficulty: 5 },
  { label: "BMO 1994/3 (Пермутация, max сума)", pdf: "Материали_БГ/BMO_1984-2006", page: 11, difficulty: 4 }
]}
{ id: "9.8", tasks: [
  { label: "BMO 2001/4 (Куб 3×3×3, инвариант)", pdf: "Материали_БГ/BMO_1984-2006", page: 18, difficulty: 5 }
]}
```

---

### NOM_2010.pdf — ✅ ГОТОВО

```js
// ─── Иран, Китай, Русия, САЩ ───
// Русия 11 клас = high priority

// ─── АКТУАЛИЗАЦИЯ ───
{ id: "6.1", tasks: [
  { label: "НОМ 2010, Русия 11.1 (произв. на a+1/a)", pdf: "Материали_БГ/NOM_2010", page: 15, difficulty: 4 }
]}
{ id: "9.8", tasks: [
  { label: "НОМ 2010, Русия 11.2 (таблица със знаци)", pdf: "Материали_БГ/NOM_2010", page: 16, difficulty: 4 },
  { label: "НОМ 2010, Иран I.6 (карти с номера)", pdf: "Материали_БГ/NOM_2010", page: 5, difficulty: 4 },
  { label: "НОМ 2010, САЩ 6 (двойки числа)", pdf: "Материали_БГ/NOM_2010", page: 17, difficulty: 4 }
]}
{ id: "1.9", tasks: [
  { label: "НОМ 2010, Русия 11.3 (вписани окр. в чет.)", pdf: "Материали_БГ/NOM_2010", page: 16, difficulty: 5 }
]}
{ id: "5.8", tasks: [
  { label: "НОМ 2010, Русия 11.4 (интерполация)", pdf: "Материали_БГ/NOM_2010", page: 16, difficulty: 4 }
]}
{ id: "4.5", tasks: [
  { label: "НОМ 2010, Русия 11.5 (произв. послед.)", pdf: "Материали_БГ/NOM_2010", page: 16, difficulty: 4 }
]}
{ id: "5.1", tasks: [
  { label: "НОМ 2010, Русия 11.7 (максимум на полином)", pdf: "Материали_БГ/NOM_2010", page: 16, difficulty: 5 }
]}
{ id: "8.10", tasks: [
  { label: "НОМ 2010, Русия 11.8 (подреждане ученици)", pdf: "Материали_БГ/NOM_2010", page: 16, difficulty: 5 },
  { label: "НОМ 2010, САЩ 2 (размени по височина)", pdf: "Материали_БГ/NOM_2010", page: 17, difficulty: 4 }
]}
{ id: "12.1", tasks: [
  { label: "НОМ 2010, Китай 3 (комплексни)", pdf: "Материали_БГ/NOM_2010", page: 9, difficulty: 5 }
]}
{ id: "3.2", tasks: [
  { label: "НОМ 2010, Китай 2 (редица с прости)", pdf: "Материали_БГ/NOM_2010", page: 9, difficulty: 4 },
  { label: "НОМ 2010, САЩ 5 (1/(k(k+1)(k+2)))", pdf: "Материали_БГ/NOM_2010", page: 17, difficulty: 5 }
]}
{ id: "4.1", tasks: [
  { label: "НОМ 2010, Китай 4 (мн. T)", pdf: "Материали_БГ/NOM_2010", page: 9, difficulty: 4 },
  { label: "НОМ 2010, Иран II.6 (xm un + ...)", pdf: "Материали_БГ/NOM_2010", page: 6, difficulty: 5 }
]}
{ id: "7.5", tasks: [
  { label: "НОМ 2010, Иран III.9 (f((x+f(x))/2+y))", pdf: "Материали_БГ/NOM_2010", page: 8, difficulty: 5 },
  { label: "НОМ 2010, Иран II.4 (f,g неравенство)", pdf: "Материали_БГ/NOM_2010", page: 6, difficulty: 5 }
]}
{ id: "8.6", tasks: [
  { label: "НОМ 2010, Иран II.2 (добри пермутации)", pdf: "Материали_БГ/NOM_2010", page: 6, difficulty: 4 }
]}
{ id: "2.8", tasks: [
  { label: "НОМ 2010, Иран II.1 (геом. неравенства)", pdf: "Материали_БГ/NOM_2010", page: 6, difficulty: 5 }
]}
```

---

### NOM_2011.pdf — ✅ ГОТОВО

```js
// Анализ на Иран, Китай, Русия, САЩ (Тайван/Туймаада/Жаутиков = skip)

const NOM_2011_UPDATES = [
  { id: "1.4", tasks: [
    { label: "Иран Зад 1 (радикална ос)", pdf: "Материали_БГ/NOM_2011", page: 4, difficulty: 4 },
    { label: "Иран Зад 9 (степен)", pdf: "Материали_БГ/NOM_2011", page: 5, difficulty: 4 }
  ]},
  { id: "1.10", tasks: [
    { label: "Иран Зад 6 (впис./външновп.)", pdf: "Материали_БГ/NOM_2011", page: 4, difficulty: 5 },
    { label: "Китай Зад 2 (вписана)", pdf: "Материали_БГ/NOM_2011", page: 6, difficulty: 4 },
    { label: "Русия Зад 11.8 (вписани)", pdf: "Материали_БГ/NOM_2011", page: 12, difficulty: 5 }
  ]},
  { id: "3.1", tasks: [
    { label: "Иран Зад 4 (НОД)", pdf: "Материали_БГ/NOM_2011", page: 4, difficulty: 4 },
    { label: "Русия Зад 11.1 (делители)", pdf: "Материали_БГ/NOM_2011", page: 11, difficulty: 3 },
    { label: "САЩ Зад 4 (остатъци)", pdf: "Материали_БГ/NOM_2011", page: 13, difficulty: 4 }
  ]},
  { id: "5.1", tasks: [
    { label: "Русия 9.6 (Виет)", pdf: "Материали_БГ/NOM_2011", page: 10, difficulty: 4 },
    { label: "Русия 10.2 (кв. тричлен)", pdf: "Материали_БГ/NOM_2011", page: 10, difficulty: 4 }
  ]},
  { id: "5.5", tasks: [
    { label: "Иран Зад 8 (неразложими)", pdf: "Материали_БГ/NOM_2011", page: 5, difficulty: 5 },
    { label: "Русия 9.1 (композиция)", pdf: "Материали_БГ/NOM_2011", page: 9, difficulty: 4 },
    { label: "Русия 11.5 (кубични)", pdf: "Материали_БГ/NOM_2011", page: 12, difficulty: 5 }
  ]},
  { id: "6.1", tasks: [
    { label: "Китай Зад 1 (AM-GM)", pdf: "Материали_БГ/NOM_2011", page: 6, difficulty: 4 },
    { label: "САЩ Зад 1 (AM-GM)", pdf: "Материали_БГ/NOM_2011", page: 12, difficulty: 4 }
  ]},
  { id: "7.5", tasks: [
    { label: "Иран Зад 5 (ФУ)", pdf: "Материали_БГ/NOM_2011", page: 4, difficulty: 5 },
    { label: "Иран Зад 12 (ФУ)", pdf: "Материали_БГ/NOM_2011", page: 5, difficulty: 5 }
  ]},
  { id: "8.3", tasks: [
    { label: "Иран Зад 3 (двойно броене)", pdf: "Материали_БГ/NOM_2011", page: 4, difficulty: 4 },
    { label: "Китай Зад 3 (двойно броене)", pdf: "Материали_БГ/NOM_2011", page: 6, difficulty: 5 },
    { label: "САЩ Зад 6 (обединение)", pdf: "Материали_БГ/NOM_2011", page: 13, difficulty: 5 }
  ]},
  { id: "9.8", tasks: [
    { label: "Русия 11.4 (инварианти)", pdf: "Материали_БГ/NOM_2011", page: 11, difficulty: 5 }
  ]},
  { id: "9.10", tasks: [
    { label: "Русия 11.6 (игри)", pdf: "Материали_БГ/NOM_2011", page: 12, difficulty: 5 },
    { label: "САЩ Зад 2 (инвариант)", pdf: "Материали_БГ/NOM_2011", page: 12, difficulty: 5 }
  ]}
];
```

---

### NOM_2012.pdf — ✅ ГОТОВО

```js
// Анализирани Иран, Китай, Русия, САЩ

// ─── АКТУАЛИЗАЦИЯ (примерни high-priority) ───
{ id: "1.5", tasks: [
  { label: "Иран Зад 2", pdf: "Материали_БГ/NOM_2012", page: 4, difficulty: 5 },
  { label: "Китай Зад 1", pdf: "Материали_БГ/NOM_2012", page: 8, difficulty: 5 },
  { label: "Русия 9.3", pdf: "Материали_БГ/NOM_2012", page: 9, difficulty: 4 },
  { label: "САЩ Зад 5", pdf: "Материали_БГ/NOM_2012", page: 13, difficulty: 5 }
]}
{ id: "1.10", tasks: [
  { label: "Русия 9.6", pdf: "Материали_БГ/NOM_2012", page: 10, difficulty: 5 },
  { label: "Русия 10.2", pdf: "Материали_БГ/NOM_2012", page: 10, difficulty: 5 },
  { label: "Русия 11.6", pdf: "Материали_БГ/NOM_2012", page: 12, difficulty: 5 }
]}
{ id: "3.2", tasks: [
  { label: "Русия 9.1", pdf: "Материали_БГ/NOM_2012", page: 9, difficulty: 4 },
  { label: "Русия 10.1", pdf: "Материали_БГ/NOM_2012", page: 10, difficulty: 4 }
]}
{ id: "5.1", tasks: [
  { label: "Иран Зад 14", pdf: "Материали_БГ/NOM_2012", page: 6, difficulty: 5 },
  { label: "Русия 11.5", pdf: "Материали_БГ/NOM_2012", page: 12, difficulty: 5 }
]}
{ id: "6.4", tasks: [
  { label: "Иран Зад 10", pdf: "Материали_БГ/NOM_2012", page: 5, difficulty: 4 },
  { label: "Китай Зад 4", pdf: "Материали_БГ/NOM_2012", page: 8, difficulty: 4 },
  { label: "САЩ Зад 6", pdf: "Материали_БГ/NOM_2012", page: 13, difficulty: 5 }
]}
{ id: "7.5", tasks: [
  { label: "Иран Зад 5", pdf: "Материали_БГ/NOM_2012", page: 5, difficulty: 5 },
  { label: "Иран Зад 8", pdf: "Материали_БГ/NOM_2012", page: 5, difficulty: 5 },
  { label: "САЩ Зад 4", pdf: "Материали_БГ/NOM_2012", page: 13, difficulty: 5 }
]}
{ id: "8.3", tasks: [
  { label: "Иран Зад 3", pdf: "Материали_БГ/NOM_2012", page: 4, difficulty: 5 },
  { label: "Иран Зад 4", pdf: "Материали_БГ/NOM_2012", page: 4, difficulty: 4 },
  { label: "Иран Зад 12", pdf: "Материали_БГ/NOM_2012", page: 6, difficulty: 5 },
  { label: "Китай Зад 2", pdf: "Материали_БГ/NOM_2012", page: 8, difficulty: 5 },
  { label: "Китай Зад 6", pdf: "Материали_БГ/NOM_2012", page: 9, difficulty: 5 },
  { label: "Русия 11.1", pdf: "Материали_БГ/NOM_2012", page: 11, difficulty: 5 }
]}
{ id: "8.5", tasks: [
  { label: "Иран Зад 1", pdf: "Материали_БГ/NOM_2012", page: 4, difficulty: 4 }
]}
{ id: "9.7", tasks: [
  { label: "Русия 9.2", pdf: "Материали_БГ/NOM_2012", page: 9, difficulty: 4 },
  { label: "Русия 11.3", pdf: "Материали_БГ/NOM_2012", page: 11, difficulty: 5 }
]}
{ id: "9.8", tasks: [
  { label: "Русия 9.5", pdf: "Материали_БГ/NOM_2012", page: 9, difficulty: 4 },
  { label: "Русия 9.7", pdf: "Материали_БГ/NOM_2012", page: 10, difficulty: 5 }
]}
{ id: "9.10", tasks: [
  { label: "Русия 11.7", pdf: "Материали_БГ/NOM_2012", page: 12, difficulty: 5 }
]}
```

---

### NOM_2013.pdf — ✅ ГОТОВО

```js
// Анализирани Русия (high), Китай, Иран, САЩ

// ─── АКТУАЛИЗАЦИЯ към 10.7 ───
{ id: "10.7", tasks: [
  { label: "Русия 11.1 (полиноми)", pdf: "Материали_БГ/NOM_2013", page: 15, difficulty: 4 },
  { label: "Русия 11.2 (сфери в тетраедър)", pdf: "Материали_БГ/NOM_2013", page: 15, difficulty: 5 },
  { label: "Русия 11.3 (произв. на нечетни прости)", pdf: "Материали_БГ/NOM_2013", page: 15, difficulty: 5 },
  { label: "Русия 11.4 (картички)", pdf: "Материали_БГ/NOM_2013", page: 15, difficulty: 5 },
  { label: "Русия 11.5 (разлики ≤100)", pdf: "Материали_БГ/NOM_2013", page: 16, difficulty: 4 },
  { label: "Русия 11.6 (неравенство с abcd)", pdf: "Материали_БГ/NOM_2013", page: 16, difficulty: 4 },
  { label: "Русия 11.7 (номинали монети)", pdf: "Материали_БГ/NOM_2013", page: 16, difficulty: 5 },
  { label: "Русия 11.8 (допиращи се окр.)", pdf: "Материали_БГ/NOM_2013", page: 16, difficulty: 5 },
  { label: "Китай Зад 1 (окръжности)", pdf: "Материали_БГ/NOM_2013", page: 9, difficulty: 5 },
  { label: "Китай Зад 3 (реални t)", pdf: "Материали_БГ/NOM_2013", page: 9, difficulty: 5 },
  { label: "Иран Зад 2 (изпъкнала фигура)", pdf: "Материали_БГ/NOM_2013", page: 6, difficulty: 5 },
  { label: "Иран Зад 3 (ϕ редица)", pdf: "Материали_БГ/NOM_2013", page: 7, difficulty: 5 },
  { label: "САЩ Зад 1 (геометрия)", pdf: "Материали_БГ/NOM_2013", page: 17, difficulty: 5 },
  { label: "САЩ Зад 3 (пулове)", pdf: "Материали_БГ/NOM_2013", page: 17, difficulty: 5 }
],
bonus: [
  { label: "Иран, решения", pdf: "Материали_БГ/NOM_2013", page: 35 },
  { label: "Китай, решения", pdf: "Материали_БГ/NOM_2013", page: 44 },
  { label: "САЩ, решения", pdf: "Материали_БГ/NOM_2013", page: 74 },
  { label: "Русия, решения", pdf: "Материали_БГ/NOM_2013", page: 58 }
]}

// ─── GAP: стереометрия (Русия 11.2) → 1.11 Стереометрия (или бонус към 1.8) ───
```

---

### NOM_2014.pdf — ✅ ГОТОВО

```js
// Анализирани Русия, Китай, Иран, САЩ

// ─── АКТУАЛИЗАЦИЯ ───
{ id: "9.10", tasks: [
  { label: "Русия 11.2 (Петър и Васил)", pdf: "Материали_БГ/NOM_2014", page: 10, difficulty: 4 },
  { label: "Русия 11.8 (игра с карти)", pdf: "Материали_БГ/NOM_2014", page: 10, difficulty: 5 },
  { label: "САЩ 4 (шестоъгълна решетка)", pdf: "Материали_БГ/NOM_2014", page: 11, difficulty: 5 }
]}
{ id: "3.1", tasks: [
  { label: "Русия 11.5 (хубави числа)", pdf: "Материали_БГ/NOM_2014", page: 10, difficulty: 4 },
  { label: "Иран 1 (взаимнопрости)", pdf: "Материали_БГ/NOM_2014", page: 5, difficulty: 4 }
]}
{ id: "5.7", tasks: [
  { label: "Русия 11.7 (полиноми операции)", pdf: "Материали_БГ/NOM_2014", page: 10, difficulty: 4 }
]}
{ id: "7.6", tasks: [
  { label: "Китай 3 (функция f(n))", pdf: "Материали_БГ/NOM_2014", page: 7, difficulty: 5 }
]}
{ id: "7.1", tasks: [
  { label: "САЩ 2 (ФУ в Z)", pdf: "Материали_БГ/NOM_2014", page: 11, difficulty: 5 }
]}
{ id: "4.7", tasks: [
  { label: "Китай 2 (D(n) множества)", pdf: "Материали_БГ/NOM_2014", page: 6, difficulty: 5 },
  { label: "Китай 4 (ω и Ω)", pdf: "Материали_БГ/NOM_2014", page: 7, difficulty: 5 },
  { label: "САЩ 6 (константа c)", pdf: "Материали_БГ/NOM_2014", page: 12, difficulty: 5 }
]}
{ id: "1.10", tasks: [
  { label: "Китай 1 (ъглополовяща)", pdf: "Материали_БГ/NOM_2014", page: 6, difficulty: 5 },
  { label: "Иран 3 (среда на дъга)", pdf: "Материали_БГ/NOM_2014", page: 5, difficulty: 5 },
  { label: "САЩ 5 (ортоцентър)", pdf: "Материали_БГ/NOM_2014", page: 11, difficulty: 5 }
]}
{ id: "1.4", tasks: [
  { label: "Иран 4 (допирателни)", pdf: "Материали_БГ/NOM_2014", page: 5, difficulty: 5 }
]}
{ id: "9.8", tasks: [
  { label: "Иран 5 (таблица n×m)", pdf: "Материали_БГ/NOM_2014", page: 5, difficulty: 5 }
]}
{ id: "7.7", tasks: [
  { label: "Иран 6 (рек. редица)", pdf: "Материали_БГ/NOM_2014", page: 5, difficulty: 5 }
]}
{ id: "5.1", tasks: [
  { label: "САЩ 1 (корени на полином)", pdf: "Материали_БГ/NOM_2014", page: 11, difficulty: 5 }
]}
{ id: "8.2", tasks: [
  { label: "Китай 5 (функция f: X→X)", pdf: "Материали_БГ/NOM_2014", page: 7, difficulty: 5 }
]}
{ id: "8.1", tasks: [
  { label: "Иран 2 (пълно множество от тежести)", pdf: "Материали_БГ/NOM_2014", page: 5, difficulty: 4 }
]}

// ─── НОВИ ТОЧКИ: 5.10 (Тригонометрични уравнения), 8.13 (Адитивна комб.) ───
```

---

### NOM_2015-2016.pdf — ✅ ГОТОВО

```js
// 14 държави: Великобритания, Италия, Китай, Русия, САЩ, Тайланд, Хонг Конг, Южна Корея, Япония
// 100 задачи анализирани

// ─── KEY STATS ───
// 1.5 (12 задачи), 9.10 (11), 8.1 (10), 1.10 (9), 4.4 (8)

// ─── АКТУАЛИЗАЦИЯ (примери) ───
{ id: "1.4", tasks: [
  { label: "Великобритания 2016, Зад 1 (окръжности)", pdf: "Материали_БГ/NOM_2015-2016", page: 3, difficulty: 4 },
  { label: "Иран 2015, Зад 4 (допирателни)", pdf: "Материали_БГ/NOM_2015-2016", page: 5, difficulty: 5 }
]}
{ id: "1.5", tasks: [
  { label: "Великобритания 2016, Зад 3", pdf: "Материали_БГ/NOM_2015-2016", page: 3, difficulty: 4 },
  { label: "Италия 2016, Зад 1 (ъглополовящи)", pdf: "Материали_БГ/NOM_2015-2016", page: 6, difficulty: 3 },
  { label: "Китай 2015, Зад 2 (Паскал)", pdf: "Материали_БГ/NOM_2015-2016", page: 7, difficulty: 5 },
  { label: "Русия 2015, Зад 9.2 (успоредник)", pdf: "Материали_БГ/NOM_2015-2016", page: 10, difficulty: 4 },
  { label: "Русия 2016, Зад 9.2 (допирателни)", pdf: "Материали_БГ/NOM_2015-2016", page: 14, difficulty: 5 }
]}
{ id: "1.10", tasks: [
  { label: "Италия 2016, Зад 3 (външновп.)", pdf: "Материали_БГ/NOM_2015-2016", page: 6, difficulty: 4 },
  { label: "Русия 2015, Зад 11.7", pdf: "Материали_БГ/NOM_2015-2016", page: 13, difficulty: 5 },
  { label: "Русия 2016, Зад 9.7", pdf: "Материали_БГ/NOM_2015-2016", page: 14, difficulty: 5 },
  { label: "САЩ 2016, Зад 5", pdf: "Материали_БГ/NOM_2015-2016", page: 18, difficulty: 5 },
  { label: "Южна Корея 2016, Зад 5", pdf: "Материали_БГ/NOM_2015-2016", page: 25, difficulty: 5 }
]}
{ id: "3.1", tasks: [
  { label: "Русия 2016, Зад 9.3 (НОД)", pdf: "Материали_БГ/NOM_2015-2016", page: 14, difficulty: 4 },
  { label: "Япония 2016, Зад 1 (делители)", pdf: "Материали_БГ/NOM_2015-2016", page: 26, difficulty: 4 }
]}
{ id: "4.4", tasks: [
  { label: "Великобритания 2016, Зад 4", pdf: "Материали_БГ/NOM_2015-2016", page: 3, difficulty: 4 },
  { label: "Русия 2015, Зад 9.3", pdf: "Материали_БГ/NOM_2015-2016", page: 10, difficulty: 4 },
  { label: "Русия 2016, Зад 10.7", pdf: "Материали_БГ/NOM_2015-2016", page: 16, difficulty: 5 }
]}
{ id: "7.1", tasks: [
  { label: "САЩ 2016, Зад 4 (ФУ)", pdf: "Материали_БГ/NOM_2015-2016", page: 18, difficulty: 5 },
  { label: "Южна Корея 2015, Зад 1", pdf: "Материали_БГ/NOM_2015-2016", page: 24, difficulty: 5 },
  { label: "Япония 2016, Зад 4", pdf: "Материали_БГ/NOM_2015-2016", page: 26, difficulty: 5 }
]}
{ id: "8.1", tasks: [
  { label: "Великобритания 2016, Зад 2", pdf: "Материали_БГ/NOM_2015-2016", page: 3, difficulty: 5 },
  { label: "Тайланд 2015, Зад 3", pdf: "Материали_БГ/NOM_2015-2016", page: 21, difficulty: 4 },
  { label: "Южна Корея 2015, Зад 6", pdf: "Материали_БГ/NOM_2015-2016", page: 24, difficulty: 4 }
]}
{ id: "9.10", tasks: [
  { label: "Великобритания 2016, Зад 2", pdf: "Материали_БГ/NOM_2015-2016", page: 3, difficulty: 5 },
  { label: "Италия 2015, Зад 6", pdf: "Материали_БГ/NOM_2015-2016", page: 4, difficulty: 4 },
  { label: "Китай 2016, Зад 6 (турнири)", pdf: "Материали_БГ/NOM_2015-2016", page: 8, difficulty: 5 },
  { label: "Русия 2015, Зад 9.6 (танк)", pdf: "Материали_БГ/NOM_2015-2016", page: 10, difficulty: 5 },
  { label: "Русия 2016, Зад 10.4 (Петя)", pdf: "Материали_БГ/NOM_2015-2016", page: 16, difficulty: 5 }
]}
```

---

## 🎓 LECTURES — Бонус лекции (7/7)

### Група A — NT Training (01-05) — ✅ ГОТОВО

```js
// ─── NT_Training_01-05 ───
// Файлове: lectures-navid/NT_Training_01–05.pdf
// Масови задачи към 3.1, 3.2, 3.3, 4.4, 4.5, 4.6, 4.7

[1,2,3,4,5].forEach(n => {
  STEPS[2].points.find(p => p.id === "3.1").bonus.push({ label: `NT Training 0${n}`, pdf: `Бонус/lectures-navid/NT_Training_0${n}`, page: 1 });
});

{ id: "3.1", tasks: [
  { label: "NT_Training_05, Зад 2 (gcd неравенство)", pdf: "Бонус/lectures-navid/NT_Training_05", page: 1, difficulty: 4 },
  { label: "NT_Training_05, Зад 11", pdf: "Бонус/lectures-navid/NT_Training_05", page: 2, difficulty: 5 }
]}
{ id: "3.3", tasks: [
  { label: "NT_Training_02, Зад 3 (Ферма)", pdf: "Бонус/lectures-navid/NT_Training_02", page: 1, difficulty: 3 }
]}
{ id: "4.4", tasks: [
  { label: "NT_Training_01, Зад 5 (квадрати)", pdf: "Бонус/lectures-navid/NT_Training_01", page: 1, difficulty: 4 },
  { label: "NT_Training_04, Зад 22", pdf: "Бонус/lectures-navid/NT_Training_04", page: 2, difficulty: 4 }
]}
{ id: "4.5", tasks: [
  { label: "NT_Training_01, Зад 1 (прости p,q)", pdf: "Бонус/lectures-navid/NT_Training_01", page: 1, difficulty: 4 },
  { label: "NT_Training_02, Зад 7 (p³+107)", pdf: "Бонус/lectures-navid/NT_Training_02", page: 1, difficulty: 4 }
]}
{ id: "4.7", tasks: [
  { label: "NT_Training_04, Зад 7", pdf: "Бонус/lectures-navid/NT_Training_04", page: 1, difficulty: 5 }
]}
```

---

### Група B — Functional Equations — ✅ ГОТОВО

```js
// ─── Functional_Equations_Lecture_01-03 ───

[1,2,3].forEach(n => {
  STEPS[6].points.find(p => p.id === "7.5").bonus.push({ label: `FE Lecture 0${n}`, pdf: `Бонус/lectures-navid/Functional_Equations_Lecture_0${n}`, page: 1 });
});

{ id: "7.1", tasks: [
  { label: "FE Lecture 01, Problem 4 (Vietnam)", pdf: "Бонус/lectures-navid/Functional_Equations_Lecture_01", page: 3, difficulty: 4 },
  { label: "FE Lecture 03, Problem 11 (AMM)", pdf: "Бонус/lectures-navid/Functional_Equations_Lecture_03", page: 9, difficulty: 4 }
]}
{ id: "7.2", tasks: [
  { label: "FE Lecture 03, Problem 7 (Korean)", pdf: "Бонус/lectures-navid/Functional_Equations_Lecture_03", page: 5, difficulty: 5 }
]}
{ id: "7.3", tasks: [
  { label: "FE Lecture 01, Problem 5 (monotone)", pdf: "Бонус/lectures-navid/Functional_Equations_Lecture_01", page: 4, difficulty: 4 }
]}
{ id: "7.8", tasks: [
  { label: "FE Lecture 01, Problem 12 (Turkish TST)", pdf: "Бонус/lectures-navid/Functional_Equations_Lecture_01", page: 8, difficulty: 5 }
]}
```

---

### Група C — Polynomials/Enumerative/Induction — ✅ ГОТОВО

```js
// ─── Polynomials_Problems, Enumerative_Problems, Induction_Problems×2, Number_Theoretic_Flavor, Exam_01/02 ───

{ id: "5.1", tasks: [
  { label: "Polynomials, Зад 17 (f,g рационални)", pdf: "Бонус/lectures-navid/Polynomials_Problems_2015-16", page: 2, difficulty: 5 }
]}
{ id: "5.4", tasks: [
  { label: "Polynomials, Зад 5 (monic f³-2)", pdf: "Бонус/lectures-navid/Polynomials_Problems_2015-16", page: 1, difficulty: 4 }
]}
{ id: "5.5", tasks: [
  { label: "Polynomials, Зад 9 (ирационални)", pdf: "Бонус/lectures-navid/Polynomials_Problems_2015-16", page: 2, difficulty: 5 }
]}
{ id: "5.7", tasks: [
  { label: "Polynomials, Зад 15 (p(2016) просто)", pdf: "Бонус/lectures-navid/Polynomials_Problems_2015-16", page: 2, difficulty: 5 }
]}
{ id: "5.8", tasks: [
  { label: "Polynomials, Зад 13 (Lagrange)", pdf: "Бонус/lectures-navid/Polynomials_Problems_2015-16", page: 2, difficulty: 5 }
]}
{ id: "8.10", tasks: [
  { label: "Induction Problems, Problem 2 (Полиноми)", pdf: "Бонус/lectures-navid/Induction Problems", page: 5, difficulty: 4 },
  { label: "Induction Problems-2, Problem 1 (Скакалец)", pdf: "Бонус/lectures-navid/Induction Problems-2", page: 1, difficulty: 5 }
]}
{ id: "4.5", tasks: [
  { label: "Enumerative, Problem (infinitely many n)", pdf: "Бонус/lectures-navid/Enumerative_Problems_Final", page: 1, difficulty: 4 }
]}
{ id: "4.8", tasks: [
  { label: "Enumerative, Problem (φ sum)", pdf: "Бонус/lectures-navid/Enumerative_Problems_Final", page: 1, difficulty: 4 }
]}
{ id: "3.7", tasks: [
  { label: "NT Flavor, Problem (primitive roots)", pdf: "Бонус/lectures-navid/Number_Theoretic_Flavor", page: 4, difficulty: 5 }
]}
{ id: "10.1", tasks: [
  { label: "Exam 01, Problem 1 (gcd)", pdf: "Бонус/lectures-navid/Exam_01_Problems", page: 1, difficulty: 4 },
  { label: "Exam 01, Problem 2 (2×2018)", pdf: "Бонус/lectures-navid/Exam_01_Problems", page: 1, difficulty: 4 }
]}
{ id: "7.5", tasks: [
  { label: "Exam 02, Problem 2 (FE)", pdf: "Бонус/lectures-navid/Exam_02_Problems", page: 1, difficulty: 4 }
]}
{ id: "9.10", tasks: [
  { label: "Exam 02, Problem 3 (good/perfect group)", pdf: "Бонус/lectures-navid/Exam_02_Problems", page: 1, difficulty: 5 }
]}
```

---

### Група D — Peter PAMP 2019 — ✅ ГОТОВО

```js
// ─── lekcia1-4-pamp2019 + f_eq_nt_pres-1/2 + qrl_pres-1 ───

{ id: "3.1", bonus: [
  { label: "Целочислени функции и делимост (I)", pdf: "Бонус/lectures-peter/f_eq_nt_pres", page: 1 },
  { label: "Целочислени функции и делимост (II)", pdf: "Бонус/lectures-peter/f_eq_nt_pres-2", page: 1 },
  { label: "МОМ 2019 — лекция 3", pdf: "Бонус/lectures-peter/lekcia3-pamp2019", page: 1 }
], tasks: [
  { label: "f_eq_nt_pres, Зад 1 (Румъния 2004)", pdf: "Бонус/lectures-peter/f_eq_nt_pres", page: 3, difficulty: 4 },
  { label: "f_eq_nt_pres-2, Зад 1 (МОМ 2010)", pdf: "Бонус/lectures-peter/f_eq_nt_pres-2", page: 2, difficulty: 5 },
  { label: "lekcia3, Зад 2 (3^n || m³+17)", pdf: "Бонус/lectures-peter/lekcia3-pamp2019", page: 1, difficulty: 5 }
]}
{ id: "3.2", bonus: [
  { label: "МОМ 2019 — лекция 1", pdf: "Бонус/lectures-peter/lekcia1-pamp2019", page: 1 },
  { label: "МОМ 2019 — лекция 4", pdf: "Бонус/lectures-peter/lekcia4-pamp2019", page: 1 }
], tasks: [
  { label: "lekcia1, Зад 1 (Китай 2008)", pdf: "Бонус/lectures-peter/lekcia1-pamp2019", page: 1, difficulty: 5 },
  { label: "lekcia4, Зад 1 (p³|r-s)", pdf: "Бонус/lectures-peter/lekcia4-pamp2019", page: 3, difficulty: 5 }
]}
{ id: "3.3", tasks: [
  { label: "lekcia1, Зад 2 (Китай 2010)", pdf: "Бонус/lectures-peter/lekcia1-pamp2019", page: 1, difficulty: 4 }
]}
{ id: "3.8", bonus: [
  { label: "Символ на Лежандър", pdf: "Бонус/lectures-peter/qrl_pres-1", page: 1 }
], tasks: [
  { label: "qrl_pres, Зад 1 (СПОКО)", pdf: "Бонус/lectures-peter/qrl_pres-1", page: 11, difficulty: 5 },
  { label: "qrl_pres, Зад 2 (k=2^2^n+1)", pdf: "Бонус/lectures-peter/qrl_pres-1", page: 13, difficulty: 5 }
]}
{ id: "4.4", bonus: [
  { label: "МОМ 2019 — лекция 2", pdf: "Бонус/lectures-peter/lekcia2-pamp2019", page: 1 }
], tasks: [
  { label: "lekcia2, Зад 5 (БОМ 2005)", pdf: "Бонус/lectures-peter/lekcia2-pamp2019", page: 1, difficulty: 4 },
  { label: "lekcia2, Зад 8 (МОМ шортлист 2006)", pdf: "Бонус/lectures-peter/lekcia2-pamp2019", page: 2, difficulty: 5 }
]}
{ id: "4.5", tasks: [
  { label: "lekcia1, Зад 3 (Китай 2011)", pdf: "Бонус/lectures-peter/lekcia1-pamp2019", page: 1, difficulty: 5 },
  { label: "lekcia2, Зад 5 (p²-p+1 куб)", pdf: "Бонус/lectures-peter/lekcia2-pamp2019", page: 1, difficulty: 4 }
]}
{ id: "7.1", bonus: [
  { label: "Целочислени функции и делимост (I)", pdf: "Бонус/lectures-peter/f_eq_nt_pres", page: 1 },
  { label: "Целочислени функции и делимост (II)", pdf: "Бонус/lectures-peter/f_eq_nt_pres-2", page: 1 }
], tasks: [
  { label: "f_eq_nt_pres-2, Зад 3 (БОМ 2017)", pdf: "Бонус/lectures-peter/f_eq_nt_pres-2", page: 11, difficulty: 4 }
]}
{ id: "7.2", tasks: [
  { label: "f_eq_nt_pres-2, Зад 2 (Иран 2011)", pdf: "Бонус/lectures-peter/f_eq_nt_pres-2", page: 6, difficulty: 5 }
]}
{ id: "7.5", tasks: [
  { label: "f_eq_nt_pres-2, Зад 4 (МОМ шортлист 2007)", pdf: "Бонус/lectures-peter/f_eq_nt_pres-2", page: 14, difficulty: 5 },
  { label: "f_eq_nt_pres-2, Зад 5 (БОМ 2012)", pdf: "Бонус/lectures-peter/f_eq_nt_pres-2", page: 18, difficulty: 5 }
]}

// ─── GAPS: 3.11 (Лагранж за сравнения), 3.12 (Сума на цифри), 5.11 (Сравнения по прост модул с полиноми) ───
```

---

### Група E — Weekly Themes — ✅ ГОТОВО

```js
// ─── week1-4-theme + week1-4-solutions ───

{ id: "1.5", bonus: [
  { label: "Седмична тема 1 — геометрия", pdf: "Бонус/tema-na-sedmicata/week1-theme", page: 1 },
  { label: "Седмична тема 2 — геометрия", pdf: "Бонус/tema-na-sedmicata/week2-theme", page: 1 },
  { label: "Седмична тема 4 — геометрия", pdf: "Бонус/tema-na-sedmicata/week4-theme", page: 1 }
], tasks: [
  { label: "week1, Зад 1 (ъглополовящи)", pdf: "Бонус/tema-na-sedmicata/week1-theme", page: 1, difficulty: 4 },
  { label: "week2, Зад 1 (въртяща хомотетия)", pdf: "Бонус/tema-na-sedmicata/week2-theme", page: 1, difficulty: 5 },
  { label: "week4, Зад 3 (хомотетия)", pdf: "Бонус/tema-na-sedmicata/week4-theme", page: 1, difficulty: 5 }
]}
{ id: "3.2", tasks: [
  { label: "week2, Зад 2 (биномни коефициенти)", pdf: "Бонус/tema-na-sedmicata/week2-theme", page: 1, difficulty: 5 },
  { label: "week3, Зад 3 (индукция)", pdf: "Бонус/tema-na-sedmicata/week3-theme", page: 1, difficulty: 4 }
]}
{ id: "5.1", bonus: [
  { label: "Седмична тема 1 — полиноми", pdf: "Бонус/tema-na-sedmicata/week1-theme", page: 1 }
], tasks: [
  { label: "week1, Зад 2 (итерации на полином)", pdf: "Бонус/tema-na-sedmicata/week1-theme", page: 1, difficulty: 5 }
]}
{ id: "7.1", tasks: [
  { label: "week3, Зад 1 (ФУ с дробно-линейни)", pdf: "Бонус/tema-na-sedmicata/week3-theme", page: 1, difficulty: 4 },
  { label: "week4, Зад 2 (инективна функция)", pdf: "Бонус/tema-na-sedmicata/week4-theme", page: 1, difficulty: 4 }
]}
{ id: "8.1", tasks: [
  { label: "week1, Зад 3 (огърлица)", pdf: "Бонус/tema-na-sedmicata/week1-theme", page: 1, difficulty: 4 }
]}
{ id: "9.1", tasks: [
  { label: "week2, Зад 3 (пътища в град)", pdf: "Бонус/tema-na-sedmicata/week2-theme", page: 1, difficulty: 5 }
]}
{ id: "9.10", tasks: [
  { label: "week3, Зад 2 (Ана и Боб)", pdf: "Бонус/tema-na-sedmicata/week3-theme", page: 1, difficulty: 5 }
]}
```

---

### Група F — Теми с Лекции (Tema1-6) — ✅ ГОТОВО

```js
// ─── Tema1 Marin Hristov, Tema2 Borislav Kirilov, Tema3 Petko Lazarov, Tema4 Veselin Markovich, Tema5 Bozhidar Dimitrov, Tema6 Ilias/Bilyana ───

// Tema2 (Борислав Кирилов) — Адитивна комбинаторика
// → Стъпка 13 (ADDITIVE COMBINATORICS): 13.1–13.4
{
  num: 13, title: "ADDITIVE COMBINATORICS",
  points: [
    { id: "13.1", title: "Теорема на Коши-Девънпорт", source: "Tema2 — Б. Кирилов", pdf: "Теми с Лекции/Tema2-BorislavKirilov", page: 1 },
    { id: "13.2", title: "Теорема на Ердьош-Гинзбург-Зив", source: "Tema2 — Б. Кирилов", pdf: "Теми с Лекции/Tema2-BorislavKirilov", page: 1 },
    { id: "13.3", title: "Combinatorial Nullstellensatz", source: "Tema2 — Б. Кирилов", pdf: "Теми с Лекции/Tema2-BorislavKirilov", page: 1 },
    { id: "13.4", title: "Свободни от суми множества", source: "Tema2 — Б. Кирилов", pdf: "Теми с Лекции/Tema2-BorislavKirilov", page: 1 }
  ]
}

// Video bonus (за точки от Стъпки 2, 7, 8, 9):
{ id: "8.3", bonus: [{ type: "video", label: "🎥 Марин Таблици-1", driveId: "1ig_-yC1wAEEqN1sOb0ynDwyClXzn7Y4y" }, { type: "video", label: "🎥 Марин Таблици-2", driveId: "1DH51ttFRV4fiyLcRgwVF4a7iAV7xliJT" }] }
{ id: "2.1", bonus: [{ type: "video", label: "🎥 Петко Двойни Отношения", driveId: "1ssEn17G_Zs-4jhc8oouhqVwb0ue4LcUC" }] }
{ id: "2.8", bonus: [{ type: "video", label: "🎥 Божидар Геометрия", driveId: "1luTnkxdV220-ju2SketR5hyKAIbT2piw" }] }
{ id: "7.5", bonus: [{ type: "video", label: "🎥 Веселин Алгебра", driveId: "1Gmn2mAFrV5QqJin-swhP3Sog_K6cEnx1" }] }
{ id: "9.1", bonus: [{ type: "video", label: "🎥 Биби и Илияс Графи", driveId: "16737y3JVwznj3wMADwzVECVRXGy6TxGg" }] }
```

---

## 📊 SUMMARY STATISTICS

| Категория | Обработени | Общо |
|---|---|---|
| Математически книги | 10 | 10 |
| Non-math книги (skip) | 2 | 2 |
| Областни кръгове | 11 | 11 |
| BG сборници | 11 | 11 |
| Лекции | 6 | 6 |
| **ОБЩО** | **40** | **40** |

**Дубликати за изтриване:**
- [ ] `Материали_EN/Copies/book-8 (1).pdf`
- [ ] `Материали_EN/Copies/book-9 (1).pdf`
- [ ] `Материали_EN/Copies/book-10 (1).pdf`
- [ ] `Материали_EN/Copies/book-11 (1).pdf`
- [ ] `Материали_EN/Copies/book-3 (3).pdf`
- [ ] `Материали_EN/Copies/book-3 (4).pdf`

---

## 🔑 KEY FINDINGS (за финална интеграция)

### ✅ Готови промени в index.html:
- **2 нови стъпки**: Step 12 (Analytic & Projective Geometry) + Step 13 (Additive Combinatorics)
- **Разширена Стъпка 10** с 22 нови точки (10.11–10.32)
- **15 нови точки за откритите gaps**:
  - `1.11` Формула на Пик
  - `2.9` Теорема на Карно
  - `2.10` Теорема за ъглополовящата
  - `3.11` Теорема на Лагранж за сравнения
  - `3.12` Сума на цифри
  - `4.9` Антивериги / Спернер
  - `4.10` Квадратични форми / суми на квадрати
  - `5.9` Разположение на корени
  - `5.10` Тригонометрични уравнения
  - `5.11` Ирационални уравнения с параметър
  - `5.12` Реципрочни уравнения
  - `7.9` Функционални неравенства с итерации
  - `8.11` Блок-дизайни
  - `8.12` Вероятностен метод
  - `8.13` Адитивна комбинаторика (въведение)
  - `8.14` Неравенство на Фишер
  - `9.11` Векторни пространства над F2
- **~450 нови `tasks`** от областни кръгове и BG сборници
- **~120 нови `bonus`** от EN книги и лекции
- **3 нови features**: Library tab, Quick Tools (Alt+T), Video Modal (Google Drive)
- **6 video bonus** записи в точки 2.1, 2.8, 7.5, 8.3×2, 9.1

### 🚩 Gaps (всички вече интегрирани като нови точки):
**Major:** F2 векторни пространства (`9.11`), тригонометрични уравнения (`5.10`), разположение на корени (`5.9`), ирационални уравнения с параметър (`5.11`), функционални неравенства с итерации (`7.9`), формула на Пик (`1.11`), Карно (`2.9`), вероятностен метод (`8.12`)

**Minor:** Спернер (`4.9`), блок-дизайни (`8.11`), квадратични форми (`4.10`), реципрочни уравнения (`5.12`), Айзенщайн (подточка в `5.5`), ъглополовяща (`2.10`), Бертран (бонус в `4.5`), проекции (`8.3`), Лагранж за сравнения (`3.11`), сума на цифри (`3.12`), Фишер (`8.14`)

### 📋 Пълен списък нови точки (общо 44):
| ID | Тема | Източник |
|---|---|---|
| 1.11 | Формула на Пик | 2026.txt |
| 2.9 | Теорема на Карно | 2019.txt |
| 2.10 | Теорема за ъглополовящата | 2023.txt |
| 3.11 | Теорема на Лагранж за сравнения | lekcia4 |
| 3.12 | Сума на цифри | week4/NT_Training_03 |
| 4.9 | Антивериги / Спернер | 2016.txt |
| 4.10 | Квадратични форми | 2024.txt |
| 5.9 | Разположение на корени | 2016/2017/2021 |
| 5.10 | Тригонометрични уравнения | 2016/2017/2019 |
| 5.11 | Ирационални уравнения с параметър | 2019-2026 |
| 5.12 | Реципрочни уравнения | 2024.txt |
| 7.9 | Функционални неравенства с итерации | 2016.txt |
| 8.11 | Блок-дизайни | 2017.txt |
| 8.12 | Вероятностен метод | 2025.txt |
| 8.13 | Адитивна комбинаторика | NOM_2014 |
| 8.14 | Неравенство на Фишер | OT_2012 |
| 9.11 | Векторни пространства над F2 | 2019/2021 |
| 10.11–10.32 | Областни кръгове 2016–2026 | 11 години × 2 класа |
| 12.1 | Комплексни числа в геометрията | book-4 |
| 12.2 | Барицентрични координати | book-4 |
| 12.3 | Проективна геометрия | book-4 |
| 13.1 | Коши-Девънпорт | Tema2 |
| 13.2 | Ердьош-Гинзбург-Зив | Tema2 |
| 13.3 | Combinatorial Nullstellensatz | Tema2 |
| 13.4 | Свободни от суми множества | Tema2 |

### ⚠️ Рискове и забележки:
- **book-4** — два различни AI отговора; приемаме **Опит 1** (Step 12), Опит 2 се игнорира.
- **book-4 (1)** и **book-3 (1)** — Competitive Programming, не математика → отделна папка Informatics.
- **book-9** — skip (Prealgebra, под нивото).
- **book-11** — Calculus за BG олимпиада е рядкост; приема се като Step 12/13 опция.
- **2026-11-sol.pdf** — липсва; 11 кл анализът за 2026 е непълен.
- Всички PDF пътища са без `.pdf` и без начален `/`.
- Всички `requires_also` ID-та съществуват в STEPS.

---

*Файлът се актуализира ръчно след всеки AI чат.*
