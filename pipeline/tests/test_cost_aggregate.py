"""
═══════════════════════════════════════════════════════════════════════════
  test_cost_aggregate.py — historical + live combining
═══════════════════════════════════════════════════════════════════════════
"""
import json
import sys
from pathlib import Path

import pytest

import cost_aggregate


# ═══════════════════════════════════════════════════════════════════════
#  read_ledger / read_json_entries
# ═══════════════════════════════════════════════════════════════════════

class TestReadLedger:

    def test_reads_valid_jsonl(self, tmp_path):
        p = tmp_path / "l.jsonl"
        p.write_text(
            '{"ts": "2026-10-29T10:00:00", "cost": 0.01}\n'
            '{"ts": "2026-10-29T11:00:00", "cost": 0.02}\n',
            encoding="utf-8")
        assert len(cost_aggregate.read_ledger(p)) == 2

    def test_skips_invalid_lines(self, tmp_path):
        p = tmp_path / "l.jsonl"
        p.write_text(
            '{"valid": 1}\n'
            'not json\n'
            '\n'
            '{"valid": 2}\n',
            encoding="utf-8")
        assert len(cost_aggregate.read_ledger(p)) == 2

    def test_since_filter_excludes_old(self, tmp_path):
        p = tmp_path / "l.jsonl"
        p.write_text(
            '{"ts": "2026-10-20T10:00:00"}\n'
            '{"ts": "2026-10-29T10:00:00"}\n',
            encoding="utf-8")
        assert len(cost_aggregate.read_ledger(p, since="2026-10-25")) == 1

    def test_missing_file_returns_empty(self, tmp_path):
        assert cost_aggregate.read_ledger(tmp_path / "no.jsonl") == []


class TestReadJsonEntries:

    def test_list_format(self, tmp_path):
        p = tmp_path / "d.json"
        p.write_text(json.dumps([{"a": 1}, {"b": 2}]), encoding="utf-8")
        assert len(cost_aggregate.read_json_entries(p)) == 2

    def test_entries_key_format(self, tmp_path):
        p = tmp_path / "d.json"
        p.write_text(json.dumps({"entries": [{"a": 1}]}), encoding="utf-8")
        assert len(cost_aggregate.read_json_entries(p)) == 1

    def test_missing_file_empty(self, tmp_path):
        assert cost_aggregate.read_json_entries(tmp_path / "no.json") == []


# ═══════════════════════════════════════════════════════════════════════
#  aggregate — бъкети по model / day / role
# ═══════════════════════════════════════════════════════════════════════

class TestAggregate:

    def test_empty(self):
        r = cost_aggregate.aggregate([])
        assert r["by_model"] == {}
        assert r["by_day"] == {}
        assert r["by_role"] == {}
        assert r["totals"]["cost"] == 0.0
        assert r["totals"]["calls"] == 0

    def test_single_entry(self):
        entries = [{
            "ts": "2026-10-29T10:00:00", "model": "m1", "role": "gen",
            "cost": 0.05, "tokens": 1000,
        }]
        r = cost_aggregate.aggregate(entries)
        assert r["by_model"]["m1"]["calls"] == 1
        assert r["by_model"]["m1"]["cost"] == 0.05
        assert r["by_day"]["2026-10-29"]["cost"] == 0.05
        assert r["by_role"]["gen"]["cost"] == 0.05
        assert r["totals"]["calls"] == 1

    def test_multiple_groups(self):
        entries = [
            {"ts": "2026-10-29T10:00:00", "model": "m1", "role": "gen", "cost": 0.10, "tokens": 100},
            {"ts": "2026-10-29T11:00:00", "model": "m1", "role": "ver", "cost": 0.05, "tokens": 50},
            {"ts": "2026-10-30T10:00:00", "model": "m2", "role": "gen", "cost": 0.20, "tokens": 200},
        ]
        r = cost_aggregate.aggregate(entries)
        assert r["by_model"]["m1"]["calls"] == 2
        assert r["by_model"]["m1"]["cost"] == pytest.approx(0.15)
        assert r["by_day"]["2026-10-29"]["cost"] == pytest.approx(0.15)
        assert r["by_day"]["2026-10-30"]["cost"] == pytest.approx(0.20)
        assert r["by_role"]["gen"]["calls"] == 2
        assert r["by_role"]["ver"]["calls"] == 1

    def test_errors_counted(self):
        entries = [
            {"ts": "2026-10-29T10:00:00", "model": "m", "cost": 0.01, "status": "ok"},
            {"ts": "2026-10-29T11:00:00", "model": "m", "cost": 0.0, "status": "error"},
        ]
        r = cost_aggregate.aggregate(entries)
        assert r["by_model"]["m"]["errors"] == 1
        assert r["totals"]["errors"] == 1

    def test_reasoning_tokens_summed(self):
        entries = [
            {"ts": "2026-10-29T10:00:00", "model": "m",
             "reasoning_tokens": 100, "cached_tokens": 10, "cost": 0},
            {"ts": "2026-10-29T11:00:00", "model": "m",
             "reasoning_tokens": 200, "cached_tokens": 20, "cost": 0},
        ]
        r = cost_aggregate.aggregate(entries)
        assert r["totals"]["reasoning_tokens"] == 300
        assert r["totals"]["cached_tokens"] == 30

    def test_cost_split_summed(self):
        entries = [{
            "ts": "2026-10-29T10:00:00", "model": "m", "cost": 0.10,
            "cost_prompt": 0.03, "cost_completion": 0.07,
        }]
        r = cost_aggregate.aggregate(entries)
        assert r["totals"]["cost_prompt"] == pytest.approx(0.03)
        assert r["totals"]["cost_completion"] == pytest.approx(0.07)

    def test_by_model_sorted_cost_desc(self):
        entries = [
            {"ts": "2026-10-29T10:00:00", "model": "cheap", "cost": 0.01},
            {"ts": "2026-10-29T10:00:00", "model": "expensive", "cost": 0.10},
        ]
        r = cost_aggregate.aggregate(entries)
        assert list(r["by_model"].keys()) == ["expensive", "cheap"]

    def test_by_day_sorted_asc(self):
        entries = [
            {"ts": "2026-10-30T10:00:00", "model": "m", "cost": 0.02},
            {"ts": "2026-10-28T10:00:00", "model": "m", "cost": 0.01},
            {"ts": "2026-10-29T10:00:00", "model": "m", "cost": 0.03},
        ]
        r = cost_aggregate.aggregate(entries)
        assert list(r["by_day"].keys()) == ["2026-10-28", "2026-10-29", "2026-10-30"]

    def test_missing_optional_fields_zero(self):
        entries = [{"ts": "2026-10-29T10:00:00", "model": "m", "cost": 0.01}]
        r = cost_aggregate.aggregate(entries)
        assert r["totals"]["tokens"] == 0
        assert r["totals"]["reasoning_tokens"] == 0
        assert r["totals"]["cost_prompt"] == 0.0

    def test_role_falls_back_to_module(self):
        entries = [{"ts": "2026-10-29T10:00:00", "module": "pdf_chunker",
                    "cost": 0.01}]
        r = cost_aggregate.aggregate(entries)
        assert "pdf_chunker" in r["by_role"]


# ═══════════════════════════════════════════════════════════════════════
#  End-to-end: historical + live
# ═══════════════════════════════════════════════════════════════════════

class TestEndToEnd:

    def test_combines_historical_and_live(self, tmp_path, monkeypatch):
        hist = tmp_path / "hist.json"
        hist.write_text(json.dumps([
            {"ts": "2026-10-01T00:00:00", "model": "old", "cost": 1.0, "tokens": 100},
        ]), encoding="utf-8")
        ledger = tmp_path / "ledger.jsonl"
        ledger.write_text(
            '{"ts": "2026-10-29T10:00:00", "model": "new", "role": "gen", '
            '"cost": 0.05, "tokens": 50}\n', encoding="utf-8")
        out = tmp_path / "combined.json"

        monkeypatch.setattr(sys, "argv", [
            "cost_aggregate.py",
            "--historical", str(hist),
            "--ledger", str(ledger),
            "--out", str(out),
        ])
        cost_aggregate.main()

        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["sources"]["historical"] == 1
        assert data["sources"]["live"] == 1
        assert data["sources"]["combined"] == 2
        assert data["totals"]["cost"] == pytest.approx(1.05)
        assert "old" in data["by_model"]
        assert "new" in data["by_model"]