"""
═══════════════════════════════════════════════════════════════════════════
  test_cost_tracker.py — централен ledger за AI разходи
═══════════════════════════════════════════════════════════════════════════

Покрива:
  • MODEL_PRICING table integrity           — 3 теста
  • compute_cost (exact + substring)        — 5 теста
  • extract_usage (openai + anthropic)      — 5 теста
  • extract_extras (cost_details, reasoning) — 4 теста
  • log_call (JSONL append, thread-safe)    — 6 теста
  • track_call (API cost priority)          — 6 теста
"""
import json
import time
import threading
from decimal import Decimal
from pathlib import Path

import pytest

import cost_tracker


@pytest.fixture
def isolated_ledger(tmp_path, monkeypatch):
    """Ledger в tmp_path — не пипа реалния generated/costs/ledger.jsonl."""
    ledger = tmp_path / "ledger.jsonl"
    monkeypatch.setattr(cost_tracker, "_ledger_path", None)
    cost_tracker.init(ledger)
    yield ledger
    monkeypatch.setattr(cost_tracker, "_ledger_path", None)


def _read_jsonl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


# ═══════════════════════════════════════════════════════════════════════
#  MODEL_PRICING table integrity
# ═══════════════════════════════════════════════════════════════════════

class TestPricingTable:

    def test_has_expected_models(self):
        for m in ("deepseek-r1", "gpt-6.1-sol", "claude-sonnet-5.5"):
            assert m in cost_tracker.MODEL_PRICING

    def test_all_entries_have_input_output(self):
        for name, price in cost_tracker.MODEL_PRICING.items():
            assert "input" in price and "output" in price, f"{name} missing keys"
            assert price["input"] >= 0
            assert price["output"] >= 0

    def test_output_at_least_input(self):
        """Output обикновено е по-скъпо от input."""
        for name, price in cost_tracker.MODEL_PRICING.items():
            assert price["output"] >= price["input"], f"{name} has output < input"


# ═══════════════════════════════════════════════════════════════════════
#  compute_cost — exact, substring, edge cases
# ═══════════════════════════════════════════════════════════════════════

class TestComputeCost:

    def test_exact_model_1m_in(self):
        cost = cost_tracker.compute_cost("deepseek/deepseek-r1", 1_000_000, 0)
        assert cost == pytest.approx(0.55)

    def test_exact_model_1m_out(self):
        cost = cost_tracker.compute_cost("deepseek/deepseek-r1", 0, 1_000_000)
        assert cost == pytest.approx(2.19)

    def test_combined(self):
        cost = cost_tracker.compute_cost("deepseek/deepseek-r1", 1_000_000, 1_000_000)
        assert cost == pytest.approx(0.55 + 2.19)

    def test_substring_match_versioned_model(self):
        """anthropic/claude-sonnet-5.5-20260928 → matched by 'claude-sonnet-5.5'."""
        cost = cost_tracker.compute_cost(
            "anthropic/claude-sonnet-5.5-20260928", 1_000_000, 0)
        assert cost == pytest.approx(3.00)

    def test_unknown_model_zero(self):
        assert cost_tracker.compute_cost("mystery/model-x", 1000, 1000) == 0.0

    def test_empty_model_zero(self):
        assert cost_tracker.compute_cost("", 1000, 1000) == 0.0

    def test_zero_tokens_zero_cost(self):
        assert cost_tracker.compute_cost("deepseek/deepseek-r1", 0, 0) == 0.0


# ═══════════════════════════════════════════════════════════════════════
#  extract_usage
# ═══════════════════════════════════════════════════════════════════════

class TestExtractUsage:

    def test_openai_format(self):
        data = {"usage": {"prompt_tokens": 100, "completion_tokens": 50,
                          "total_tokens": 150}}
        assert cost_tracker.extract_usage(data) == (100, 50, 150, 0.0)

    def test_anthropic_format(self):
        data = {"usage": {"input_tokens": 200, "output_tokens": 100}}
        assert cost_tracker.extract_usage(data, is_anthropic=True) == (200, 100, 300, 0.0)

    def test_cost_field_extracted(self):
        data = {"usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.00123}}
        _, _, _, cost = cost_tracker.extract_usage(data)
        assert cost == pytest.approx(0.00123)

    def test_total_cost_field_used(self):
        data = {"usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_cost": 0.05}}
        _, _, _, cost = cost_tracker.extract_usage(data)
        assert cost == pytest.approx(0.05)

    def test_missing_usage(self):
        assert cost_tracker.extract_usage({}) == (0, 0, 0, 0.0)

    def test_null_usage(self):
        assert cost_tracker.extract_usage({"usage": None}) == (0, 0, 0, 0.0)

    def test_falls_back_to_sum_when_total_missing(self):
        data = {"usage": {"prompt_tokens": 30, "completion_tokens": 20}}
        _, _, total, _ = cost_tracker.extract_usage(data)
        assert total == 50


# ═══════════════════════════════════════════════════════════════════════
#  extract_extras — cost_details + reasoning_tokens
# ═══════════════════════════════════════════════════════════════════════

class TestExtractExtras:

    def test_full_details(self):
        data = {"usage": {
            "cost_details": {
                "upstream_inference_cost": 0.001,
                "upstream_inference_prompt_cost": 0.0001,
                "upstream_inference_completions_cost": 0.0009,
            },
            "completion_tokens_details": {"reasoning_tokens": 42,
                                          "image_tokens": 0, "audio_tokens": 0},
            "prompt_tokens_details": {"cached_tokens": 10, "cache_write_tokens": 5},
            "is_byok": False,
        }}
        e = cost_tracker.extract_extras(data)
        assert e["cost_prompt"] == pytest.approx(0.0001)
        assert e["cost_completion"] == pytest.approx(0.0009)
        assert e["reasoning_tokens"] == 42
        assert e["cached_tokens"] == 10
        assert e["cache_write_tokens"] == 5
        assert e["is_byok"] is False

    def test_missing_details_all_zero(self):
        e = cost_tracker.extract_extras({"usage": {}})
        assert e["cost_prompt"] == 0.0
        assert e["reasoning_tokens"] == 0
        assert e["cached_tokens"] == 0
        assert e["is_byok"] is False

    def test_is_byok_true(self):
        e = cost_tracker.extract_extras({"usage": {"is_byok": True}})
        assert e["is_byok"] is True

    def test_null_cost_details(self):
        e = cost_tracker.extract_extras({"usage": {"cost_details": None}})
        assert e["cost_prompt"] == 0.0


# ═══════════════════════════════════════════════════════════════════════
#  log_call — JSONL append
# ═══════════════════════════════════════════════════════════════════════

class TestLogCall:

    def test_writes_one_line(self, isolated_ledger):
        cost_tracker.log_call("pipeline", "gen", "test/model", 100, 50, 0.01, item_id="1.1")
        recs = _read_jsonl(isolated_ledger)
        assert len(recs) == 1
        assert recs[0]["module"] == "pipeline"
        assert recs[0]["role"] == "gen"
        assert recs[0]["model"] == "test/model"
        assert recs[0]["in_tokens"] == 100
        assert recs[0]["out_tokens"] == 50
        assert recs[0]["tokens"] == 150
        assert recs[0]["cost"] == 0.01
        assert recs[0]["item_id"] == "1.1"

    def test_multiple_appends(self, isolated_ledger):
        for i in range(5):
            cost_tracker.log_call("mod", "gen", "m", 10, 5, 0.001, item_id=f"{i}")
        assert len(_read_jsonl(isolated_ledger)) == 5

    def test_extra_dict_merged(self, isolated_ledger):
        cost_tracker.log_call("m", "r", "mod", 1, 2, 0.001, extra={
            "reasoning_tokens": 5, "custom": "x"
        })
        rec = _read_jsonl(isolated_ledger)[0]
        assert rec["reasoning_tokens"] == 5
        assert rec["custom"] == "x"

    def test_extra_cannot_override_core(self, isolated_ledger):
        cost_tracker.log_call("m", "r", "mod", 1, 2, 0.001,
                              extra={"module": "OVERRIDE", "cost": 999})
        rec = _read_jsonl(isolated_ledger)[0]
        assert rec["module"] == "m"
        assert rec["cost"] == 0.001

    def test_no_init_noop(self, monkeypatch):
        monkeypatch.setattr(cost_tracker, "_ledger_path", None)
        cost_tracker.log_call("m", "r", "mod", 1, 2, 0.001)  # no raise

    def test_thread_safe_append(self, isolated_ledger):
        def worker(n):
            for i in range(20):
                cost_tracker.log_call("m", "r", "mod", 1, 2, 0.001, item_id=f"{n}-{i}")

        threads = [threading.Thread(target=worker, args=(n,)) for n in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert len(_read_jsonl(isolated_ledger)) == 100


# ═══════════════════════════════════════════════════════════════════════
#  track_call — API cost priority, fallback, latency
# ═══════════════════════════════════════════════════════════════════════

class TestTrackCall:

    def test_api_cost_takes_priority(self, isolated_ledger):
        """When API returns cost, use it — do NOT compute from pricing."""
        data = {"usage": {"prompt_tokens": 100, "completion_tokens": 50, "cost": 0.05}}
        cost_tracker.track_call("pipeline", "gen", "deepseek/deepseek-r1", data)
        rec = _read_jsonl(isolated_ledger)[0]
        assert rec["cost"] == 0.05  # API value, not 0.0001183 from pricing

    def test_pricing_fallback_when_api_cost_missing(self, isolated_ledger):
        data = {"usage": {"prompt_tokens": 1_000_000, "completion_tokens": 1_000_000}}
        cost_tracker.track_call("pipeline", "gen", "deepseek/deepseek-r1", data)
        rec = _read_jsonl(isolated_ledger)[0]
        assert rec["cost"] == pytest.approx(2.74)

    def test_unknown_model_zero_cost(self, isolated_ledger):
        data = {"usage": {"prompt_tokens": 100, "completion_tokens": 50}}
        cost_tracker.track_call("pipeline", "gen", "mystery/model", data)
        rec = _read_jsonl(isolated_ledger)[0]
        assert rec["cost"] == 0.0

    def test_latency_measured(self, isolated_ledger):
        t0 = time.time() - 0.5
        data = {"usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.001}}
        cost_tracker.track_call("pipeline", "gen", "test/m", data, t0=t0)
        rec = _read_jsonl(isolated_ledger)[0]
        assert 400 <= rec["latency_ms"] <= 600

    def test_reasoning_tokens_logged(self, isolated_ledger):
        data = {"usage": {
            "prompt_tokens": 10, "completion_tokens": 50, "cost": 0.001,
            "completion_tokens_details": {"reasoning_tokens": 30},
        }}
        cost_tracker.track_call("pipeline", "gen", "test/m", data)
        rec = _read_jsonl(isolated_ledger)[0]
        assert rec["reasoning_tokens"] == 30

    def test_never_raises_on_garbage(self, isolated_ledger):
        # Всякакви странни входове не бива да чупят track_call
        cost_tracker.track_call("pipeline", "gen", "m", {})
        cost_tracker.track_call("pipeline", "gen", "m", {"usage": None})
        cost_tracker.track_call("pipeline", "gen", "m", {"usage": {}})
        # 3 entries logged, all with 0 values
        assert len(_read_jsonl(isolated_ledger)) == 3