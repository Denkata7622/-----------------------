"""
═══════════════════════════════════════════════════════════════════════════
  test_classify_paired.py — paired classify pipeline tests
═══════════════════════════════════════════════════════════════════════════

Pure (без API):
  • TestGradeFromFilenameOrText  — 8 теста
  • TestBuildPairedEntries        — 10 теста
  • TestPriorityKeyPaired         — 3 теста
  • TestFormatProblemsList        — 3 теста
  • TestRunAggregate              — 6 теста

Live (1 API call, ~$0.002):
  • TestClassifyPairedLive        — 1 тест (--run-live)
"""
import json
import pytest
from pathlib import Path

import pdf_chunker


# ═══════════════════════════════════════════════════════════════════════
#  FIXTURES
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def bare_chunker():
    """PDFChunker инстанция без __init__ (без AI, без I/O)."""
    c = pdf_chunker.PDFChunker.__new__(pdf_chunker.PDFChunker)
    # run_aggregate() проверява self.steps_info — сложи минимален stub
    c.steps_info = {"1.4": {"title": "Test Point"}}
    return c


@pytest.fixture(scope="module")
def chunker():
    """Пълен chunker — само за live тестове."""
    c = pdf_chunker.PDFChunker()
    assert len(c.steps_info) >= 100, f"STEPS not loaded ({len(c.steps_info)})"
    if not c.ai_classify.headers.get("Authorization"):
        pytest.skip("No API key in config.json")
    return c


def make_problem(num, grade=11, stmt="", sol=None, year=2024,
                 page=1, grade_range=None):
    return {
        "num": num, "grade": grade, "grade_range": grade_range,
        "year": year, "round": "oblasten",
        "statement": stmt, "solution": sol, "answer": None, "page": page,
    }


# ═══════════════════════════════════════════════════════════════════════
#  TestGradeFromFilenameOrText
# ═══════════════════════════════════════════════════════════════════════

class TestGradeFromFilenameOrText:
    """
    Precedence: text_evidence > filename.grade > filename.grade_range > unknown.

    Връща (grade, source, is_uncertain).
    """

    def test_filename_specific_grade(self, bare_chunker):
        r = bare_chunker._grade_from_filename_or_text(
            "OLI-2-Областен кръг-2024-11 кл",
            {"statement": "x", "solution": "y"}
        )
        assert r == (11, 'filename', False)

    def test_filename_grade_range(self, bare_chunker):
        r = bare_chunker._grade_from_filename_or_text(
            "OLI-3-Национален кръг-2024-9-12 кл",
            {"statement": "x", "solution": "y"}
        )
        assert r == (None, 'grade_range', False)

    def test_text_evidence_overrides_filename(self, bare_chunker):
        p = {"statement": "Задача 9.6. Нека a > 1...", "solution": "Решение..."}
        r = bare_chunker._grade_from_filename_or_text(
            "OLI-2-Областен кръг-2024-11 кл", p
        )
        assert r == (9, 'text_evidence', False)

    def test_starts_with_digit_marker(self, bare_chunker):
        p = {"statement": "9.6. Нека a > 1...", "solution": "Решение..."}
        r = bare_chunker._grade_from_filename_or_text(
            "OLI-2-Областен кръг-2024-11 кл", p
        )
        assert r == (9, 'text_evidence', False)

    def test_zad_prefix_variant(self, bare_chunker):
        p = {"statement": "Зад. 10.5 Нещо...", "solution": "..."}
        r = bare_chunker._grade_from_filename_or_text(
            "OLI-2-Областен кръг-2024-11 кл", p
        )
        assert r == (10, 'text_evidence', False)

    def test_no_grade_info_uncertain(self, bare_chunker):
        r = bare_chunker._grade_from_filename_or_text(
            "BMO_1984-2006",
            {"statement": "Нещо", "solution": "Нещо"}
        )
        assert r == (None, 'unknown', True)

    def test_grade_out_of_range_ignored(self, bare_chunker):
        """'20.5' в началото — grade 20 е невалиден, пада на filename."""
        p = {"statement": "20.5. Some text...", "solution": "..."}
        r = bare_chunker._grade_from_filename_or_text(
            "OLI-2-Областен кръг-2024-11 кл", p
        )
        assert r == (11, 'filename', False)

    def test_empty_text_falls_to_filename(self, bare_chunker):
        r = bare_chunker._grade_from_filename_or_text(
            "OLI-2-Областен кръг-2024-11 кл",
            {"statement": "", "solution": ""}
        )
        assert r == (11, 'filename', False)


# ═══════════════════════════════════════════════════════════════════════
#  TestBuildPairedEntries
# ═══════════════════════════════════════════════════════════════════════

class TestBuildPairedEntries:
    """
    result[matched|orphan_sols_with_statement|orphan_sols_without_statement|unmatched_probs]
      → list[entry]

    Проверява: tags, bounds checking, grade source, empty result.
    """

    def test_empty_result_returns_empty(self, bare_chunker):
        entries = bare_chunker._build_paired_entries(
            "OLI-2-Областен кръг-2024-11 кл", [], [], {}
        )
        assert entries == []

    def test_single_matched(self, bare_chunker):
        base = "OLI-2-Областен кръг-2024-11 кл"
        probs = [make_problem(1, stmt="stmt " + "A" * 30)]
        sols = [make_problem(1, sol="sol " + "B" * 30)]
        result = {"matched": [{
            "stmt_num": 1, "sol_num": 1,
            "point_id": "1.4", "difficulty": "medium",
            "techniques": ["power_of_point"], "reasoning": "test"
        }]}
        entries = bare_chunker._build_paired_entries(base, probs, sols, result)
        assert len(entries) == 1
        e = entries[0]
        assert e["_paired"] is True
        assert e["_orphan"] if "_orphan" in e else True
        assert e["_grade_source"] == "filename"
        assert e["grade"] == 11
        assert e["point_id"] == "1.4"

    def test_single_orphan_with_statement(self, bare_chunker):
        base = "OLI-2-Областен кръг-2024-11 кл"
        sols = [make_problem(1, stmt="orphan stmt long enough here",
                             sol="orphan sol long enough here")]
        result = {"orphan_sols_with_statement": [{
            "sol_num": 1, "point_id": "2.3", "difficulty": "medium",
            "techniques": [], "reasoning": "test"
        }]}
        entries = bare_chunker._build_paired_entries(base, [], sols, result)
        assert len(entries) == 1
        e = entries[0]
        assert e["_orphan"] is True
        assert e["_grade_source"] == "filename"
        assert e["grade"] == 11

    def test_single_unmatched_prob(self, bare_chunker):
        base = "OLI-2-Областен кръг-2024-11 кл"
        probs = [make_problem(1, stmt="unmatched stmt long enough here")]
        result = {"unmatched_probs": [{
            "stmt_num": 1, "point_id": "3.2", "difficulty": "hard",
            "techniques": [], "reasoning": "test"
        }]}
        entries = bare_chunker._build_paired_entries(base, probs, [], result)
        assert len(entries) == 1
        e = entries[0]
        assert e["_no_solution"] is True
        assert e["point_id"] == "3.2"

    def test_orphan_without_statement_skipped(self, bare_chunker):
        sols = [make_problem(1, stmt=None, sol=None)]
        result = {"orphan_sols_without_statement": [
            {"sol_num": 1, "reason": "no statement"}
        ]}
        entries = bare_chunker._build_paired_entries(
            "OLI-2-Областен кръг-2024-11 кл", [], sols, result
        )
        assert entries == []

    def test_invalid_stmt_num_out_of_bounds(self, bare_chunker):
        """stmt_num=10 но има само 2 probs → skip."""
        probs = [make_problem(1, stmt="A"*30), make_problem(2, stmt="B"*30)]
        sols = [make_problem(1, sol="C"*30)]
        result = {"matched": [{"stmt_num": 10, "sol_num": 1,
                               "point_id": "1.4", "difficulty": "medium"}]}
        entries = bare_chunker._build_paired_entries(
            "OLI-2-Областен кръг-2024-11 кл", probs, sols, result
        )
        assert entries == []

    def test_invalid_sol_num_out_of_bounds(self, bare_chunker):
        probs = [make_problem(1, stmt="A"*30)]
        sols = [make_problem(1, sol="B"*30)]
        result = {"matched": [{"stmt_num": 1, "sol_num": 99,
                               "point_id": "1.4", "difficulty": "medium"}]}
        entries = bare_chunker._build_paired_entries(
            "OLI-2-Областен кръг-2024-11 кл", probs, sols, result
        )
        assert entries == []

    def test_grade_range_applied_to_matched(self, bare_chunker):
        """Base '9-12 кл' → entry.grade=None, grade_range=[9,12]."""
        base = "OLI-3-Национален кръг-2024-9-12 кл"
        probs = [make_problem(1, grade=None, grade_range=[9, 12],
                              stmt="stmt " + "A"*30)]
        sols = [make_problem(1, grade=None, grade_range=[9, 12],
                             sol="sol " + "B"*30)]
        result = {"matched": [{"stmt_num": 1, "sol_num": 1,
                               "point_id": "2.1", "difficulty": "medium"}]}
        entries = bare_chunker._build_paired_entries(base, probs, sols, result)
        assert len(entries) == 1
        e = entries[0]
        assert e["grade"] is None
        assert e["grade_range"] == [9, 12]
        assert e["_grade_source"] == "grade_range"

    def test_grade_range_applied_to_orphan(self, bare_chunker):
        base = "OLI-3-Национален кръг-2024-9-12 кл"
        sols = [make_problem(1, grade=None, grade_range=[9, 12],
                             stmt="orphan stmt long enough here",
                             sol="orphan sol long enough here")]
        result = {"orphan_sols_with_statement": [{
            "sol_num": 1, "point_id": "1.4", "difficulty": "medium",
            "techniques": [], "reasoning": "test"
        }]}
        entries = bare_chunker._build_paired_entries(base, [], sols, result)
        assert len(entries) == 1
        e = entries[0]
        assert e["grade"] is None
        assert e["grade_range"] == [9, 12]
        assert e["_grade_source"] == "grade_range"

    def test_full_scenario_matched_orphan_nosol(self, bare_chunker):
        """Matched + orphan + no_sol в един резултат → 3 entries."""
        base = "OLI-2-Областен кръг-2024-11 кл"
        probs = [
            make_problem(1, stmt="prob1 stmt " + "A"*30),
            make_problem(2, stmt="prob2 stmt " + "B"*30),
            make_problem(3, stmt="prob3 stmt " + "C"*30),
        ]
        sols = [
            make_problem(1, sol="sol1 " + "X"*30),
            make_problem(2, stmt="orphan stmt " + "Y"*30, sol="orphan " + "Z"*30),
        ]
        result = {
            "matched": [{"stmt_num": 1, "sol_num": 1,
                         "point_id": "1.4", "difficulty": "medium"}],
            "orphan_sols_with_statement": [{"sol_num": 2, "point_id": "2.3",
                                            "difficulty": "easy"}],
            "unmatched_probs": [{"stmt_num": 3, "point_id": "3.1",
                                 "difficulty": "hard"}],
        }
        entries = bare_chunker._build_paired_entries(base, probs, sols, result)
        assert len(entries) == 3
        tags = sorted(
            (e.get("_paired") and "matched") or
            (e.get("_orphan") and "orphan") or
            (e.get("_no_solution") and "no_sol") or "?"
            for e in entries
        )
        assert tags == ["matched", "no_sol", "orphan"]


# ═══════════════════════════════════════════════════════════════════════
#  TestPriorityKeyPaired
# ═══════════════════════════════════════════════════════════════════════

class TestPriorityKeyPaired:

    def test_11th_oblasten_first(self, bare_chunker):
        k1 = bare_chunker._priority_key_paired(
            "OLI-2-Областен кръг-2024-11 кл")
        k2 = bare_chunker._priority_key_paired(
            "OLI-2-Областен кръг-2024-10 кл")
        assert k1 < k2

    def test_newest_before_older(self, bare_chunker):
        k_new = bare_chunker._priority_key_paired(
            "OLI-2-Областен кръг-2024-11 кл")
        k_old = bare_chunker._priority_key_paired(
            "OLI-2-Областен кръг-2015-11 кл")
        assert k_new < k_old

    def test_non_11th_after_11th(self, bare_chunker):
        """Non-11th or non-oblasten sort after 11th oblasten."""
        k_11 = bare_chunker._priority_key_paired(
            "OLI-2-Областен кръг-2024-11 кл")
        k_9 = bare_chunker._priority_key_paired(
            "OLI-3-Национален кръг-2024-9-12 кл")
        assert k_11 < k_9


# ═══════════════════════════════════════════════════════════════════════
#  TestFormatProblemsList
# ═══════════════════════════════════════════════════════════════════════

class TestFormatProblemsList:

    def test_empty_list(self, bare_chunker):
        assert bare_chunker._format_problems_list([], "S") == ""

    def test_single_problem(self, bare_chunker):
        p = make_problem(1, grade=11,
                         stmt="Точка P лежи...", sol=None)
        out = bare_chunker._format_problems_list([p], "S")
        assert "[S1]" in out
        assert "num=1" in out
        assert "grade=11" in out
        assert "Точка P лежи" in out
        assert "(няма)" in out  # solution is None

    def test_multiple_joined(self, bare_chunker):
        ps = [make_problem(i, stmt=f"stmt{i} " + "x"*25) for i in range(1, 4)]
        out = bare_chunker._format_problems_list(ps, "A")
        assert out.count("[A") == 3


# ═══════════════════════════════════════════════════════════════════════
#  TestRunAggregate
# ═══════════════════════════════════════════════════════════════════════

class TestRunAggregate:
    """
    run_aggregate чете CLASSIFIED_DIR/*/all_problems.json
    и пише в REAL_PROBLEMS_DIR/<pid>.json.
    """

    def _setup_dirs(self, tmp_path, monkeypatch):
        classified = tmp_path / "classified"
        anchors = tmp_path / "anchors"
        classified.mkdir()
        anchors.mkdir()
        monkeypatch.setattr(pdf_chunker, "CLASSIFIED_DIR", classified)
        monkeypatch.setattr(pdf_chunker, "REAL_PROBLEMS_DIR", anchors)
        return classified, anchors

    def _write_classified(self, classified_dir, name, problems):
        sub = classified_dir / name
        sub.mkdir()
        data = {"pdf": name, "problems": problems}
        (sub / "all_problems.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_groups_by_point(self, bare_chunker, tmp_path, monkeypatch):
        cls, anc = self._setup_dirs(tmp_path, monkeypatch)
        self._write_classified(cls, "olympiad1", [
            {"num": 1, "grade": 11, "year": 2024, "point_id": "1.4",
             "statement": "Full stmt " + "A"*30,
             "solution": "Full sol " + "B"*40,
             "difficulty": "medium", "techniques": ["x"]},
            {"num": 2, "grade": 11, "year": 2024, "point_id": "1.4",
             "statement": "Another stmt " + "C"*30,
             "solution": "Another sol " + "D"*40,
             "difficulty": "easy", "techniques": []},
        ])
        bare_chunker.run_aggregate()
        f = anc / "1_4.json"
        assert f.exists()
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["point_id"] == "1.4"
        assert data["total"] == 2
        assert data["by_difficulty"]["medium"] == 1
        assert data["by_difficulty"]["easy"] == 1

    def test_skips_no_solution(self, bare_chunker, tmp_path, monkeypatch):
        cls, anc = self._setup_dirs(tmp_path, monkeypatch)
        self._write_classified(cls, "olympiad1", [
            {"num": 1, "grade": 11, "year": 2024, "point_id": "1.4",
             "statement": "Full stmt " + "A"*30,
             "solution": None,  # no solution → skip
             "difficulty": "medium", "techniques": []},
            {"num": 2, "grade": 11, "year": 2024, "point_id": "1.4",
             "statement": "Another stmt " + "C"*30,
             "solution": "Real solution " + "D"*40,
             "difficulty": "easy", "techniques": []},
        ])
        bare_chunker.run_aggregate()
        f = anc / "1_4.json"
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["total"] == 1  # само втората

    def test_dedupes_exact_duplicates(self, bare_chunker, tmp_path, monkeypatch):
        cls, anc = self._setup_dirs(tmp_path, monkeypatch)
        # Два пъти една и съща задача (същата stmt[:100]) → dedupe
        # Две версии на една и съща задача в един и същ source → dedupe
        self._write_classified(cls, "olympiad1", [
            {"num": 1, "grade": 11, "year": 2024, "point_id": "1.4",
             "statement": "Identical statement " + "A"*30,
             "solution": "Solution " + "B"*40,
             "difficulty": "medium", "techniques": []},
            {"num": 1, "grade": 11, "year": 2024, "point_id": "1.4",
             "statement": "Identical statement " + "A"*30,  # same stmt
             "solution": "Solution " + "B"*40,  # same solution
             "difficulty": "medium", "techniques": []},
        ])
        bare_chunker.run_aggregate()
        f = anc / "1_4.json"
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["total"] == 1

    def test_null_pid_goes_to_unclassified(self, bare_chunker, tmp_path, monkeypatch):
        cls, anc = self._setup_dirs(tmp_path, monkeypatch)
        self._write_classified(cls, "olympiad1", [
            {"num": 1, "grade": 11, "year": 2024, "point_id": None,
             "statement": "Stmt " + "A"*30,
             "solution": "Sol " + "B"*40,
             "difficulty": "medium", "techniques": []},
        ])
        bare_chunker.run_aggregate()
        f = anc / "_unclassified.json"
        assert f.exists()
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["total"] == 1

    def test_sorts_by_difficulty_then_source(self, bare_chunker, tmp_path, monkeypatch):
        cls, anc = self._setup_dirs(tmp_path, monkeypatch)
        self._write_classified(cls, "olympiad1", [
            {"num": 1, "grade": 11, "year": 2024, "point_id": "1.4",
             "statement": "Hard stmt " + "A"*30,
             "solution": "Hard sol " + "B"*40,
             "difficulty": "hard", "techniques": []},
            {"num": 2, "grade": 11, "year": 2024, "point_id": "1.4",
             "statement": "Easy stmt " + "C"*30,
             "solution": "Easy sol " + "D"*40,
             "difficulty": "easy", "techniques": []},
            {"num": 3, "grade": 11, "year": 2024, "point_id": "1.4",
             "statement": "Medium stmt " + "E"*30,
             "solution": "Medium sol " + "F"*40,
             "difficulty": "medium", "techniques": []},
        ])
        bare_chunker.run_aggregate()
        data = json.loads((anc / "1_4.json").read_text(encoding="utf-8"))
        diffs = [p["difficulty"] for p in data["problems"]]
        assert diffs == ["easy", "medium", "hard"]

    def test_empty_classified_dir_writes_nothing(self, bare_chunker, tmp_path, monkeypatch):
        cls, anc = self._setup_dirs(tmp_path, monkeypatch)
        bare_chunker.run_aggregate()
        assert list(anc.iterdir()) == []


# ═══════════════════════════════════════════════════════════════════════
#  TestClassifyPairedLive — 1 API call, ~$0.002
# ═══════════════════════════════════════════════════════════════════════

class TestClassifyPairedLive:
    pytestmark = pytest.mark.live

    def test_paired_returns_valid_schema(self, chunker):
        """1 paired call with 2 probs + 2 sols → schema + matching."""
        base = "OLI-2-Областен кръг-2024-11 кл"
        stmt1 = ("Точка P лежи на страната AB на триъгълник ABC, "
                 "като AP·PB = CP². Докажете, че CP е допирателна.")
        stmt2 = ("Да се намерят всички стойности на a, за които "
                 "уравнението x² + ax + a = 0 има два различни корена.")
        probs = [
            make_problem(1, stmt=stmt1),
            make_problem(2, stmt=stmt2),
        ]
        sols = [
            make_problem(1, stmt=stmt1,
                         sol="Степента на P е AP·PB = CP², значи CP е допирателна."),
            make_problem(2, stmt=stmt2,
                         sol="D = a² − 4a > 0, значи a < 0 или a > 4."),
        ]

        budget_before = chunker.state.data["budget"]["spent_usd"]
        result = chunker._classify_paired(base, probs, sols)
        budget_after = chunker.state.data["budget"]["spent_usd"]

        # 1. API работи
        assert result is not None, (
            "_classify_paired returned None.\n"
            "  • API key валиден?\n"
            "  • Budget exhausted?\n"
            "Виж logs/chunker_YYYY-MM-DD.log"
        )
        assert isinstance(result, dict)

        # 2. Schema
        for key in ("matched", "orphan_sols_with_statement",
                    "orphan_sols_without_statement", "unmatched_probs"):
            assert key in result, f"Missing key '{key}'"
            assert isinstance(result[key], list), f"'{key}' not list"

        # 3. Matching happened (2 probs + 2 sols → поне 1 match)
        matched = result.get("matched", [])
        assert len(matched) >= 1, "No matches found even for identical problems"

        # 4. Bounds checking
        for m in matched:
            assert isinstance(m.get("stmt_num"), int)
            assert 1 <= m["stmt_num"] <= len(probs)
            assert isinstance(m.get("sol_num"), int)
            assert 1 <= m["sol_num"] <= len(sols)
            pid = m.get("point_id")
            assert pid is None or pid in chunker.steps_info, (
                f"Hallucinated point_id '{pid}' not in STEPS"
            )

        # 5. Accounting
        delta = budget_after - budget_before
        expected = chunker.classify_cost * 2
        assert abs(delta - expected) < 1e-6, (
            f"Budget delta ${delta:.6f} != 2×classify_cost ${expected:.6f}"
        )

        print(f"\n  📊 Paired result:")
        print(f"     matched:              {len(matched)}")
        print(f"     orphan_with_stmt:     {len(result['orphan_sols_with_statement'])}")
        print(f"     orphan_without_stmt:  {len(result['orphan_sols_without_statement'])}")
        print(f"     unmatched_probs:      {len(result['unmatched_probs'])}")
        for m in matched:
            pid = m.get("point_id", "?")
            title = chunker.steps_info.get(pid, {}).get("title", "?")[:50]
            print(f"     #{m['stmt_num']}→#{m['sol_num']} = {pid} ({title})")
        print(f"     Budget: +${delta:.6f}")