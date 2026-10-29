"""
Live-тест за classify pipeline.

Прави реален API call (~$0.0005 с gpt-oss-120b, ~$0.035 с gpt-6.1-sol).

Пусни:
    pytest --run-live -v                    # 55 pure + 1 live
    pytest -m live --run-live -v -s         # само live + информативен print
    pytest tests/test_classify_live.py --run-live -v -s

Без --run-live този файл се SKIP-ва автоматично.
"""
import pytest
import pdf_chunker

pytestmark = pytest.mark.live


PROBLEM_POWER_OF_POINT = {
    "num": 1,
    "grade": 11,
    "year": 2024,
    "statement": (
        "Точка P лежи на страната AB на триъгълник ABC, като AP·PB = CP². "
        "Докажете, че CP е допирателна към описаната около триъгълника окръжност."
    ),
    "solution": (
        "Решение. Степента на точка P спрямо описаната окръжност е AP·PB. "
        "Ако CP е допирателна, степента е CP². Тъй като AP·PB = CP², "
        "то CP е допирателна."
    ),
}


@pytest.fixture(scope="module")
def chunker():
    c = pdf_chunker.PDFChunker()
    assert len(c.steps_info) >= 100, (
        f"STEPS not loaded ({len(c.steps_info)} points). Провери data/steps.js"
    )
    if not c.ai_classify.headers.get("Authorization"):
        pytest.skip("No API key in config.json")
    return c


class TestClassifyLive:
    """End-to-end validate: API call → schema → persistence → accounting."""

    def test_power_of_point_end_to_end(self, chunker):
        """
        1 API call. Проверява 5 неща:
          1. API работи (не None)
          2. Schema валидна (всички полета + point_id ∈ STEPS)
          3. Accounting правилен (budget delta == classify_cost)
          4. Persistence работи (save() retry)
          5. Accuracy (info only — не failing)
        """
        budget_before = chunker.state.data["budget"]["spent_usd"]
        calls_before = chunker.state.data["budget"]["calls"]

        result = chunker.classify_problem(PROBLEM_POWER_OF_POINT)

        budget_after = chunker.state.data["budget"]["spent_usd"]
        calls_after = chunker.state.data["budget"]["calls"]

        # ── 1. API работи ──
        assert result is not None, (
            "classify_problem returned None.\n"
            "  • API key невалиден? (config.json)\n"
            "  • 402 budget exhausted?\n"
            "  • Модел върна non-JSON?\n"
            "Виж logs/chunker_YYYY-MM-DD.log"
        )
        assert isinstance(result, dict), f"result is {type(result).__name__}, not dict"

        # ── 2. Schema валидна ──
        pid = result.get("point_id")
        assert pid is not None, "point_id is null (моделът не класифицира)"
        assert isinstance(pid, str), f"point_id is {type(pid).__name__}, not str"
        assert pid in chunker.steps_info, (
            f"point_id '{pid}' не е в STEPS. Моделът халюцинира.\n"
            f"Примери: {list(chunker.steps_info.keys())[:10]}"
        )

        difficulty = result.get("difficulty")
        assert difficulty in ("easy", "medium", "hard"), (
            f"difficulty '{difficulty}' not in [easy, medium, hard]"
        )

        confidence = result.get("point_confidence")
        assert confidence in ("exact", "partial", "multiple", "off"), (
            f"point_confidence '{confidence}' invalid"
        )

        techniques = result.get("techniques")
        assert isinstance(techniques, list), f"techniques is {type(techniques).__name__}"
        assert all(isinstance(t, str) for t in techniques), "techniques must be list[str]"

        reasoning = result.get("reasoning")
        assert isinstance(reasoning, str), f"reasoning is {type(reasoning).__name__}"
        assert len(reasoning) > 10, f"reasoning too short ({len(reasoning)} chars)"

        # ── 3. Accounting правилен ──
        assert calls_after == calls_before + 1, (
            f"calls delta {calls_after - calls_before}, expected 1"
        )
        budget_delta = budget_after - budget_before
        assert abs(budget_delta - chunker.classify_cost) < 1e-6, (
            f"budget delta ${budget_delta:.6f} != classify_cost ${chunker.classify_cost:.6f}"
        )

        # ── 4. Persistence (save() retry под реален API) ──
        reloaded = pdf_chunker.ChunkerState()
        assert abs(reloaded.data["budget"]["spent_usd"] - budget_after) < 1e-6, (
            "State не е записан на диск. save() retry може да е счупен."
        )

        # ── 5. Info: accuracy (не failing) ──
        print(f"\n  📊 Result:")
        print(f"     point_id  : {pid} — {chunker.steps_info[pid]['title']}")
        print(f"     difficulty: {difficulty}")
        print(f"     confidence: {confidence}")
        print(f"     techniques: {techniques}")
        print(f"     reasoning : {reasoning[:90]}...")
        print(f"     budget    : +${budget_delta:.6f}")

        if pid == "1.4":
            print(f"  ✓ Accuracy: PERFECT")
        elif pid.startswith("1."):
            print(f"  🟡 Accuracy: близо (geometry, not 1.4)")
        elif pid.startswith("2."):
            print(f"  🟡 Accuracy: advanced geometry")
        else:
            print(f"  ⚠  Accuracy: неочаквана тема {pid}")

        print(f"\n  Model: {chunker.ai_classify.model}")