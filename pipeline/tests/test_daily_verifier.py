"""
═══════════════════════════════════════════════════════════════════════════
  test_daily_verifier.py — дневен одит
═══════════════════════════════════════════════════════════════════════════

  ⚠ Първият тест FAIL-ва, ако PIPELINE_DIR не е сменен с BASE_DIR
    в STATE_FILES (NameError при import).
"""
import json
from datetime import date
from pathlib import Path

import pytest


class TestModuleImports:

    def test_imports_without_nameerror(self):
        """Regression: PIPELINE_DIR undefined in STATE_FILES."""
        import daily_verifier
        assert len(daily_verifier.STATE_FILES) == 4
        for f in daily_verifier.STATE_FILES:
            assert isinstance(f, Path)

    def test_constants(self):
        import daily_verifier
        assert daily_verifier.VERIFIER_DAILY_CAP_USD == 0.35
        assert daily_verifier.GLOBAL_SAFE_LIMIT_USD == 2.70

    def test_default_samples(self):
        import daily_verifier
        assert "anchors" in daily_verifier.DEFAULT_SAMPLES
        assert "articles" in daily_verifier.DEFAULT_SAMPLES


class TestBudgetUsed:

    def test_empty_states_zero(self, tmp_path, monkeypatch):
        import daily_verifier
        f1 = tmp_path / "s1.json"
        f2 = tmp_path / "s2.json"
        f1.write_text("{}", encoding="utf-8")
        f2.write_text("{}", encoding="utf-8")
        monkeypatch.setattr(daily_verifier, "STATE_FILES", [f1, f2])

        v = daily_verifier.DailyVerifier.__new__(daily_verifier.DailyVerifier)
        assert v._budget_used() == 0.0

    def test_today_budget_summed(self, tmp_path, monkeypatch):
        import daily_verifier
        today = str(date.today())
        f1 = tmp_path / "s1.json"
        f1.write_text(json.dumps({
            "budget": {"date": today, "spent_usd": 0.50, "calls": 5}
        }), encoding="utf-8")
        f2 = tmp_path / "s2.json"
        f2.write_text(json.dumps({
            "budget": {"date": today, "spent_usd": 0.30, "calls": 3}
        }), encoding="utf-8")
        monkeypatch.setattr(daily_verifier, "STATE_FILES", [f1, f2])

        v = daily_verifier.DailyVerifier.__new__(daily_verifier.DailyVerifier)
        assert v._budget_used() == pytest.approx(0.80)

    def test_yesterday_ignored(self, tmp_path, monkeypatch):
        import daily_verifier
        f = tmp_path / "s.json"
        f.write_text(json.dumps({
            "budget": {"date": "2020-01-01", "spent_usd": 100.0}
        }), encoding="utf-8")
        monkeypatch.setattr(daily_verifier, "STATE_FILES", [f])

        v = daily_verifier.DailyVerifier.__new__(daily_verifier.DailyVerifier)
        assert v._budget_used() == 0.0

    def test_missing_files_skipped(self, tmp_path, monkeypatch):
        import daily_verifier
        monkeypatch.setattr(daily_verifier, "STATE_FILES", [
            tmp_path / "nonexistent.json"
        ])
        v = daily_verifier.DailyVerifier.__new__(daily_verifier.DailyVerifier)
        assert v._budget_used() == 0.0

    def test_corrupted_file_skipped(self, tmp_path, monkeypatch):
        import daily_verifier
        f = tmp_path / "bad.json"
        f.write_text("not json", encoding="utf-8")
        monkeypatch.setattr(daily_verifier, "STATE_FILES", [f])
        v = daily_verifier.DailyVerifier.__new__(daily_verifier.DailyVerifier)
        assert v._budget_used() == 0.0


class TestCanAfford:

    def test_under_cap_allowed(self, tmp_path, monkeypatch):
        import daily_verifier
        monkeypatch.setattr(daily_verifier, "STATE_FILES", [])
        v = daily_verifier.DailyVerifier.__new__(daily_verifier.DailyVerifier)
        v._session_cost = 0.10
        # 0.10 + 0.05 = 0.15 < 0.35 cap → OK
        assert v._can_afford(0.05) is True

    def test_over_cap_blocked(self, tmp_path, monkeypatch):
        import daily_verifier
        monkeypatch.setattr(daily_verifier, "STATE_FILES", [])
        v = daily_verifier.DailyVerifier.__new__(daily_verifier.DailyVerifier)
        v._session_cost = 0.30
        # 0.30 + 0.10 = 0.40 > 0.35 → false
        assert v._can_afford(0.10) is False


class TestBudgetExhausted:

    def test_is_exception(self):
        import daily_verifier
        assert isinstance(daily_verifier.BudgetExhausted("x"), Exception)

    def test_raise_and_catch(self):
        import daily_verifier
        with pytest.raises(daily_verifier.BudgetExhausted):
            raise daily_verifier.BudgetExhausted("402")