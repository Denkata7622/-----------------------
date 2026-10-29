"""
═══════════════════════════════════════════════════════════════════════════
  pdf_chunker — unit test suite
═══════════════════════════════════════════════════════════════════════════

Покрива:
  • Name parsing (probs/sol pairing)         — 5 теста
  • Metadata inference from filename          — 6 теста
  • JSON extraction from AI responses         — 6 теста
  • Problem validation                        — 4 теста
  • Topics matching (stmt vs solution)        — 4 теста
  • Merge logic (grade+num key fix)           — 8 теста ← най-важни
  • Dedupe                                    — 2 теста
  • State persistence & budget tracking       — 6 теста
  • Config path integrity                     — 5 теста
  • STEPS loading                             — 3 теста
  • BudgetExhausted exception                 — 2 теста

Всичко е pure — без мрежа, без API, без реални PDF-и.
"""

import pytest
from pathlib import Path

import pdf_chunker


# ═══════════════════════════════════════════════════════════════════════
#  FIXTURES
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def bare_chunker():
    """PDFChunker инстанция без __init__ (без AI clients, без I/O)."""
    return pdf_chunker.PDFChunker.__new__(pdf_chunker.PDFChunker)


def make_problem(num, grade, stmt="", sol=None, page=1, year=2024):
    """Помощна функция за конструиране на problem dict."""
    return {
        "num": num,
        "grade": grade,
        "grade_range": None,
        "year": year,
        "round": "oblasten",
        "statement": stmt,
        "solution": sol,
        "answer": None,
        "page": page,
    }


# ═══════════════════════════════════════════════════════════════════════
#  split_pdf_name — structural parsing на имена
# ═══════════════════════════════════════════════════════════════════════

class TestSplitPdfName:

    def test_oblasten_probs(self):
        r = pdf_chunker.split_pdf_name("OLI-2-Областен кръг-2024-11 кл-probs")
        assert r["base"] == "OLI-2-Областен кръг-2024-11 кл"
        assert r["kind"] == "probs"
        assert r["variant"] == ""

    def test_oblasten_sol(self):
        r = pdf_chunker.split_pdf_name("OLI-2-Областен кръг-2024-11 кл-sol")
        assert r["kind"] == "sol"

    def test_variant_copy_suffix(self):
        r = pdf_chunker.split_pdf_name("OLI-2-Областен кръг-2024-11 кл-sol (1)")
        assert r["base"] == "OLI-2-Областен кръг-2024-11 кл"
        assert r["kind"] == "sol"
        assert r["variant"] == "(1)"

    def test_standalone_book(self):
        r = pdf_chunker.split_pdf_name("BMO_1984-2006")
        assert r["base"] == "BMO_1984-2006"
        assert r["kind"] is None

    def test_ot_no_suffix(self):
        r = pdf_chunker.split_pdf_name("OT_2012")
        assert r["kind"] is None


# ═══════════════════════════════════════════════════════════════════════
#  infer_metadata_from_filename
# ═══════════════════════════════════════════════════════════════════════

class TestInferMetadata:

    @pytest.mark.parametrize("name,year,grade,grade_range,rnd", [
        ("OLI-2-Областен кръг-2024-11 кл-sol",      2024, 11,   None,     "oblasten"),
        ("OLI-2-Областен кръг-1995-10 кл-probs",    1995, 10,   None,     "oblasten"),
        ("OLI-3-Национален кръг-1992-9-12 кл-sol",  1992, None, (9, 12),  "nacionalen"),
        ("NOM_2014",                                2014, None, None,     "nacionalen"),
        ("OT_2012",                                 2012, None, None,     "ot"),
        ("BMO_1984-2006",                           None, None, None,     "bmo"),
    ])
    def test_metadata(self, name, year, grade, grade_range, rnd):
        m = pdf_chunker.infer_metadata_from_filename(name)
        assert m["year"] == year
        assert m["grade"] == grade
        assert m["grade_range"] == grade_range
        assert m["round"] == rnd


# ═══════════════════════════════════════════════════════════════════════
#  parse_json — AI response normalization
# ═══════════════════════════════════════════════════════════════════════

class TestParseJson:

    def test_plain_json(self):
        assert pdf_chunker.parse_json('{"a": 1}') == {"a": 1}

    def test_with_markdown_fences(self):
        assert pdf_chunker.parse_json('```json\n{"a": 1}\n```') == {"a": 1}

    def test_with_trailing_comma(self):
        r = pdf_chunker.parse_json('{"a": 1, "b": [1, 2,],}')
        assert r == {"a": 1, "b": [1, 2]}

    def test_with_prose_around(self):
        assert pdf_chunker.parse_json('Here is the JSON: {"a": 1} end') == {"a": 1}

    def test_empty_returns_none(self):
        assert pdf_chunker.parse_json("") is None
        assert pdf_chunker.parse_json(None) is None

    def test_invalid_returns_none(self):
        assert pdf_chunker.parse_json("no json here") is None


# ═══════════════════════════════════════════════════════════════════════
#  _validate_problem
# ═══════════════════════════════════════════════════════════════════════

class TestValidateProblem:

    def test_valid(self):
        p = {
            "statement": "Да се намери x, ако x + 5 = 10.",
            "solution": "Изваждаме 5: x = 5. Проверка: 5 + 5 = 10. ✓",
        }
        ok, reason = pdf_chunker._validate_problem(p)
        assert ok and reason == "ok"

    def test_short_statement(self):
        p = {"statement": "Кратко", "solution": "A" * 100}
        ok, reason = pdf_chunker._validate_problem(p)
        assert not ok and reason == "statement_too_short"

    def test_no_solution(self):
        p = {"statement": "Да се намери x, ако 2x = 4.", "solution": None}
        ok, reason = pdf_chunker._validate_problem(p)
        assert not ok and reason == "no_solution"

    def test_short_solution(self):
        p = {"statement": "Да се намери x, ако 2x = 4.", "solution": "x=2"}
        ok, reason = pdf_chunker._validate_problem(p)
        assert not ok and reason == "no_solution"


# ═══════════════════════════════════════════════════════════════════════
#  _topics_match — detect кога sol не пасва на stmt
# ═══════════════════════════════════════════════════════════════════════

class TestTopicsMatch:

    def test_same_topic(self):
        stmt = "В триъгълник ABC точка M е среда на AB. Намери CM."
        sol = "Нека триъгълникът е с височина от C. Медианата е CM."
        assert pdf_chunker._topics_match(stmt, sol)

    def test_geo_vs_func_mismatch(self):
        stmt = ("Даден е триъгълник ABC с описана окръжност. "
                "Допирателната от A пресича хордата BC. "
                "Ъглополовящата минава през средата.")
        sol = ("Решение: Нека f(x) = x² + 3x + 2. Функцията е монотонна, "
               "f(x) = 0 дава корени. f(m,n) = f(n,m) е симетрия.")
        assert not pdf_chunker._topics_match(stmt, sol)

    def test_empty_returns_true(self):
        assert pdf_chunker._topics_match("", "anything")
        assert pdf_chunker._topics_match("anything", "")

    def test_weak_signal_does_not_trigger(self):
        # Само 2 geo keywords (< праг 3) → не е mismatch
        stmt = "Даден е триъгълник ABC с окръжност."
        sol = "Решение: f(x) = x + 1."
        assert pdf_chunker._topics_match(stmt, sol)


# ═══════════════════════════════════════════════════════════════════════
#  _merge_pair — КРИТИЧНИ тестове
# ═══════════════════════════════════════════════════════════════════════

class TestMergePair:
    """
    Регресионни тестове за grade+num key fix.

    ВАЖНО: _merge_pair филтрира statement-и < 20 chars.
    Всички test данни трябва да имат statement >= 20 chars.
    """

    def test_probs_and_sols_merged(self, bare_chunker):
        probs = [make_problem(1, 11, stmt="Full statement for grade 11 problem 1")]
        sols  = [make_problem(1, 11, sol="Full solution for grade 11 problem 1")]
        merged = bare_chunker._merge_pair(probs, sols)
        assert len(merged) == 1
        assert merged[0]["statement"] == "Full statement for grade 11 problem 1"
        assert merged[0]["solution"] == "Full solution for grade 11 problem 1"

    def test_grade_num_key_prevents_collision(self, bare_chunker):
        """
        Regression за стария бъг: sols dict comprehension пазеше по num само,
        така че grade-12 #1 overwrite-ваше grade-11 #1 и merge взимаше
        грешен solution за grade-11 statement.

        Очаквано: grade-11 #1 получава grade-11 solution, НЕ grade-12.
        Grade-12 sol се филтрира (няма statement).
        """
        probs = [make_problem(1, 11, stmt="Grade 11 problem 1 full statement here")]
        sols = [
            make_problem(1, 11, sol="Grade 11 solution 1 full text"),
            make_problem(1, 12, sol="Grade 12 solution 1 full text"),
        ]
        merged = bare_chunker._merge_pair(probs, sols)

        # 1 entry (grade-12 без stmt се филтрира)
        assert len(merged) == 1
        # КРИТИЧНО: ползва се grade-11 solution, не grade-12
        assert merged[0]["grade"] == 11
        assert merged[0]["solution"] == "Grade 11 solution 1 full text"

    def test_grade_num_key_both_grades_present(self, bare_chunker):
        """
        Когато и grade-11, и grade-12 имат собствен statement, получаваме 2 entries.
        Това проверява че dict-ът наистина групира по (grade, num), не по num.
        """
        probs = [
            make_problem(1, 11, stmt="Grade 11 problem 1 full statement here"),
            make_problem(1, 12, stmt="Grade 12 problem 1 full statement here"),
        ]
        sols = [
            make_problem(1, 11, sol="Grade 11 solution 1 full text"),
            make_problem(1, 12, sol="Grade 12 solution 1 full text"),
        ]
        merged = bare_chunker._merge_pair(probs, sols)
        assert len(merged) == 2
        g11 = next(m for m in merged if m["grade"] == 11)
        g12 = next(m for m in merged if m["grade"] == 12)
        assert g11["solution"] == "Grade 11 solution 1 full text"
        assert g12["solution"] == "Grade 12 solution 1 full text"

    def test_empty_probs_returns_sols_verbatim(self, bare_chunker):
        sols = [
            make_problem(1, 11, stmt="S1 statement long enough here", sol="Sol 1"),
            make_problem(2, 11, stmt="S2 statement long enough here", sol="Sol 2"),
        ]
        merged = bare_chunker._merge_pair([], sols)
        assert len(merged) == 2

    def test_empty_sols_returns_probs_verbatim(self, bare_chunker):
        probs = [
            make_problem(1, 11, stmt="Stmt 1 statement long enough here"),
            make_problem(2, 11, stmt="Stmt 2 statement long enough here"),
        ]
        merged = bare_chunker._merge_pair(probs, [])
        assert len(merged) == 2

    def test_num_none_empty_filtered(self, bare_chunker):
        probs = [
            make_problem(1, 11, stmt="Stmt 1 full statement long enough", sol="A" * 50),
            {"num": None, "grade": 11, "statement": "", "solution": ""},
        ]
        merged = bare_chunker._merge_pair(probs, [])
        assert len(merged) == 1
        assert all(m["num"] is not None for m in merged)

    def test_duplicate_sols_prefer_solution(self, bare_chunker):
        """При 2 sols с еднакъв (grade, num), този с solution печели."""
        sols = [
            {"num": 1, "grade": 11,
             "statement": "Full statement long enough 20+ chars",
             "solution": None},
            {"num": 1, "grade": 11,
             "statement": "Full statement long enough 20+ chars",
             "solution": "Real solution here that is long enough"},
        ]
        probs = [make_problem(1, 11, stmt="Full statement long enough 20+ chars")]
        merged = bare_chunker._merge_pair(probs, sols)
        assert len(merged) == 1
        assert merged[0]["solution"] == "Real solution here that is long enough"

    def test_short_statement_filtered(self, bare_chunker):
        """Statement < 20 chars → изхвърля се (когато има и sols)."""
        probs = [{"num": 1, "grade": 11, "statement": "Short",
                  "solution": None, "page": 1}]
        sols = [{"num": 1, "grade": 11, "statement": "",
                 "solution": "Some solution text here"}]
        merged = bare_chunker._merge_pair(probs, sols)
        assert len(merged) == 0

    def test_realistic_2024_11_scenario(self, bare_chunker):
        """
        Пълният regression сценарий от 2024-11 кл:
          - 4 grade-11 задачи в probs (stmt само)
          - sols: 4 grade-11 (sol), 2 grade-8, 1 grade-12, 1 orphan
          - Очаквано: всички grade-11 имат solution, grade-12 отделен key,
            orphan филтриран
        """
        probs = (
            [make_problem(1, 8, stmt="Grade 8 problem 1 full statement here"),
             make_problem(2, 8, stmt="Grade 8 problem 2 full statement here")]
            + [make_problem(i, 11, stmt=f"Да се намери x в задача 11.{i}. " + "A" * 20)
               for i in range(1, 5)]
        )
        sols = (
            [make_problem(1, 8, sol="Grade 8 solution " + "X" * 40),
             make_problem(2, 8, sol=None)]
            + [make_problem(i, 11, sol=f"Решение {i}." + "Y" * 40)
               for i in range(1, 5)]
            + [{"num": None, "grade": 11, "statement": "",
                "solution": "", "page": 2},                          # orphan
               make_problem(1, 12,
                            stmt="Grade 12 short stmt 20+ chars " + "Z" * 20,
                            sol=None)]                                # grade 12
        )

        merged = bare_chunker._merge_pair(probs, sols)

        # 4 grade-11 с solution
        grade11 = [m for m in merged if m["grade"] == 11]
        assert len(grade11) == 4
        for m in grade11:
            assert m["solution"], f"Missing solution for 11.{m['num']}"

        # Grade 12 отделен key (без solution — ОК)
        grade12 = [m for m in merged if m["grade"] == 12]
        assert len(grade12) == 1
        assert grade12[0]["solution"] is None

        # Grade 8 — 2 записа
        grade8 = [m for m in merged if m["grade"] == 8]
        assert len(grade8) == 2

        # Orphan филтриран
        orphans = [m for m in merged if m["num"] is None]
        assert len(orphans) == 0

# ═══════════════════════════════════════════════════════════════════════
#  _dedupe_problems
# ═══════════════════════════════════════════════════════════════════════

class TestDedupeProblems:

    def test_keeps_valid_version(self, bare_chunker):
        problems = [
            {"num": 1, "grade": 11, "year": 2024, "page": 1,
             "statement": "A" * 30, "solution": None},        # invalid
            {"num": 1, "grade": 11, "year": 2024, "page": 1,
             "statement": "A" * 30, "solution": "B" * 40},    # valid
        ]
        deduped = bare_chunker._dedupe_problems(problems)
        assert len(deduped) == 1
        assert deduped[0]["solution"] == "B" * 40

    def test_different_keys_kept(self, bare_chunker):
        problems = [
            {"num": 1, "grade": 11, "year": 2024, "page": 1,
             "statement": "A" * 30, "solution": "B" * 40},
            {"num": 1, "grade": 12, "year": 2024, "page": 1,
             "statement": "C" * 30, "solution": "D" * 40},
        ]
        deduped = bare_chunker._dedupe_problems(problems)
        assert len(deduped) == 2


# ═══════════════════════════════════════════════════════════════════════
#  ChunkerState — persistence & budget
# ═══════════════════════════════════════════════════════════════════════

class TestChunkerState:

    def test_fresh_state_defaults(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pdf_chunker, "STATE_FILE", tmp_path / "state.json")
        state = pdf_chunker.ChunkerState()
        assert state.data["extracted"] == {}
        assert state.data["merged"] == {}
        assert state.data["classified"] == {}
        assert state.data["budget"]["spent_usd"] == 0.0

    def test_save_and_reload(self, tmp_path, monkeypatch):
        test_state = tmp_path / "chunker_state.json"
        monkeypatch.setattr(pdf_chunker, "STATE_FILE", test_state)

        state = pdf_chunker.ChunkerState()
        state.data["extracted"]["test"] = {"status": "done", "problems": 5}
        state.save()

        reloaded = pdf_chunker.ChunkerState()
        assert reloaded.data["extracted"]["test"]["problems"] == 5

    def test_add_cost_accumulates(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pdf_chunker, "STATE_FILE", tmp_path / "state.json")
        state = pdf_chunker.ChunkerState()
        state.add_cost(0.05)
        state.add_cost(0.03)
        assert abs(state.data["budget"]["spent_usd"] - 0.08) < 1e-9
        assert state.data["budget"]["calls"] == 2

    def test_mark_extracted(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pdf_chunker, "STATE_FILE", tmp_path / "state.json")
        state = pdf_chunker.ChunkerState()
        state.mark_extracted("OLI-2024-11", 7)
        assert state.is_extracted("OLI-2024-11")
        assert state.data["extracted"]["OLI-2024-11"]["problems"] == 7

    def test_mark_classified(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pdf_chunker, "STATE_FILE", tmp_path / "state.json")
        state = pdf_chunker.ChunkerState()
        state.mark_classified("key1", {"point_id": "1.4", "difficulty": "medium"})
        assert state.is_classified("key1")
        assert state.get_classification("key1")["point_id"] == "1.4"

    def test_budget_exceeded_threshold(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pdf_chunker, "STATE_FILE", tmp_path / "state.json")
        state = pdf_chunker.ChunkerState()
        # Default: budget=3.0, stop=0.9 → threshold 2.7
        state.data["budget"]["spent_usd"] = 2.5
        assert not state.budget_exceeded()
        state.data["budget"]["spent_usd"] = 2.8
        assert state.budget_exceeded()


# ═══════════════════════════════════════════════════════════════════════
#  Config path integrity — пази след migration
# ═══════════════════════════════════════════════════════════════════════

class TestConfigPaths:

    def test_all_runtime_paths_under_generated(self):
        paths = {
            "EXTRACTED":  pdf_chunker.EXTRACTED_DIR,
            "MERGED":     pdf_chunker.MERGED_DIR,
            "CLASSIFIED": pdf_chunker.CLASSIFIED_DIR,
            "ANCHORS":    pdf_chunker.REAL_PROBLEMS_DIR,
            "OCR":        pdf_chunker._OCR_CACHE_DIR,
        }
        for name, p in paths.items():
            assert "generated" in str(p), f"{name} leaked out of generated/: {p}"
            assert Path(p).exists(), f"{name} does not exist: {p}"

    def test_state_file_under_generated_state(self):
        s = str(pdf_chunker.STATE_FILE)
        assert "generated" in s and "state" in s
        assert s.endswith("chunker_state.json")

    def test_steps_file_exists(self):
        assert pdf_chunker.STEPS_FILE.exists(), \
            f"steps.js missing at {pdf_chunker.STEPS_FILE}"

    def test_ocr_cache_dir_has_files(self):
        # Ако е празна — migration не е минал коректно
        cache = pdf_chunker._OCR_CACHE_DIR
        assert cache.exists()
        files = list(cache.iterdir())
        assert len(files) > 0, f"OCR cache is empty — {cache}"

    def test_no_legacy_pipeline_paths(self):
        """Regression guard: нищо не трябва да сочи към pipeline/."""
        for attr in ["EXTRACTED_DIR", "MERGED_DIR", "CLASSIFIED_DIR",
                     "REAL_PROBLEMS_DIR", "_OCR_CACHE_DIR"]:
            path = getattr(pdf_chunker, attr)
            assert "generated" in str(path), f"{attr} still in pipeline/"


# ═══════════════════════════════════════════════════════════════════════
#  STEPS loading
# ═══════════════════════════════════════════════════════════════════════

class TestLoadSteps:

    def test_returns_all_points(self):
        info = pdf_chunker.load_steps_info()
        assert len(info) >= 100, f"Only {len(info)} STEPS loaded"

    def test_known_points_present(self):
        info = pdf_chunker.load_steps_info()
        for pid in ["1.4", "3.2", "5.4"]:
            assert pid in info, f"Missing STEPS point {pid}"

    def test_each_point_has_title(self):
        info = pdf_chunker.load_steps_info()
        for pid, data in info.items():
            assert isinstance(data.get("title"), str)
            assert data["title"]


# ═══════════════════════════════════════════════════════════════════════
#  BudgetExhausted — behavior
# ═══════════════════════════════════════════════════════════════════════

class TestBudgetExhausted:

    def test_is_exception_subclass(self):
        exc = pdf_chunker.BudgetExhausted("test")
        assert isinstance(exc, Exception)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(pdf_chunker.BudgetExhausted):
            raise pdf_chunker.BudgetExhausted("402: limit reached")


# ═══════════════════════════════════════════════════════════════════════
#  safe_name
# ═══════════════════════════════════════════════════════════════════════

class TestSafeName:

    def test_strips_special_chars(self):
        assert pdf_chunker.safe_name("a/b\\c:d") == "a_b_c_d"
        assert pdf_chunker.safe_name("normal name") == "normal name"

    def test_handles_bulgarian(self):
        assert pdf_chunker.safe_name("Име с интервали") == "Име с интервали"

    def test_trims_whitespace(self):
        assert pdf_chunker.safe_name("  spaces  ") == "spaces"


# ═══════════════════════════════════════════════════════════════════════
#  _find_pair — probs ↔ sol matching
# ═══════════════════════════════════════════════════════════════════════

class TestFindPair:

    def test_finds_sol_for_probs(self, bare_chunker):
        extracted = {
            "OLI-2024-11 кл-probs": {},
            "OLI-2024-11 кл-sol": {},
        }
        assert bare_chunker._find_pair(
            "OLI-2024-11 кл-probs", extracted) == "OLI-2024-11 кл-sol"

    def test_finds_probs_for_sol(self, bare_chunker):
        extracted = {
            "OLI-2024-11 кл-probs": {},
            "OLI-2024-11 кл-sol": {},
        }
        assert bare_chunker._find_pair(
            "OLI-2024-11 кл-sol", extracted) == "OLI-2024-11 кл-probs"

    def test_standalone_none(self, bare_chunker):
        assert bare_chunker._find_pair("BMO_1984-2006", {"BMO_1984-2006": {}}) is None

    def test_no_match_none(self, bare_chunker):
        assert bare_chunker._find_pair(
            "OLI-2024-11 кл-probs", {"OLI-2024-11 кл-probs": {}}) is None


# ═══════════════════════════════════════════════════════════════════════
#  Budget reset on new day
# ═══════════════════════════════════════════════════════════════════════

class TestBudgetReset:

    def test_new_day_zeroes_budget(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pdf_chunker, "STATE_FILE", tmp_path / "state.json")
        state = pdf_chunker.ChunkerState()
        state.data["budget"] = {"date": "2020-01-01",
                                 "spent_usd": 100.0, "calls": 50}
        state.check_budget_reset()
        assert state.data["budget"]["spent_usd"] == 0.0
        assert state.data["budget"]["date"] != "2020-01-01"

    def test_same_day_preserves(self, tmp_path, monkeypatch):
        from datetime import date as _date
        monkeypatch.setattr(pdf_chunker, "STATE_FILE", tmp_path / "state.json")
        state = pdf_chunker.ChunkerState()
        today = str(_date.today())
        state.data["budget"] = {"date": today, "spent_usd": 1.5, "calls": 10}
        state.check_budget_reset()
        assert state.data["budget"]["spent_usd"] == 1.5