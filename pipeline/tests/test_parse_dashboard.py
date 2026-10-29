"""
═══════════════════════════════════════════════════════════════════════════
  test_parse_dashboard.py — historical Dashboard.txt parser
═══════════════════════════════════════════════════════════════════════════
"""
import json
import sys
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

import parse_dashboard


# ═══════════════════════════════════════════════════════════════════════
#  Latency parsing
# ═══════════════════════════════════════════════════════════════════════

class TestParseLatency:

    @pytest.mark.parametrize("text,expected_ms", [
        ("OK 56s", 56_000),
        ("OK 1m 30s", 90_000),
        ("OK 3m 04s", 184_000),
        ("OK 699ms", 699),
        ("OK 3m 04s extra", 184_000),
        ("Error 0ms", 0),
        ("", 0),
        ("OK 1h 30m 15s", 5_415_000),
    ])
    def test_latency(self, text, expected_ms):
        assert parse_dashboard._parse_latency_ms(text) == expected_ms


# ═══════════════════════════════════════════════════════════════════════
#  Time parsing
# ═══════════════════════════════════════════════════════════════════════

class TestParseTime:

    @pytest.mark.parametrize("text,kwargs", [
        ("13h ago", {"hours": 13}),
        ("1d ago", {"days": 1}),
        ("30m ago", {"minutes": 30}),
    ])
    def test_relative(self, text, kwargs):
        ref = datetime(2026, 10, 29, 12, 0, 0)
        assert parse_dashboard._parse_time(text, ref) == ref - timedelta(**kwargs)

    def test_absolute_short_month(self):
        r = parse_dashboard._parse_time("21 Oct 2026", datetime.now())
        assert r == datetime(2026, 10, 21)

    def test_absolute_full_month(self):
        r = parse_dashboard._parse_time("21 October 2026", datetime.now())
        assert r == datetime(2026, 10, 21)

    def test_invalid_returns_none(self):
        assert parse_dashboard._parse_time("garbage", datetime.now()) is None

    def test_invalid_date_none(self):
        assert parse_dashboard._parse_time("31 Feb 2026", datetime.now()) is None


class TestTimeKind:

    def test_relative(self):
        assert parse_dashboard._time_kind("13h ago") == "relative"
        assert parse_dashboard._time_kind("2d ago") == "relative"
        assert parse_dashboard._time_kind("45m ago") == "relative"

    def test_absolute(self):
        assert parse_dashboard._time_kind("21 Oct 2026") == "absolute"

    def test_invalid(self):
        assert parse_dashboard._time_kind("garbage") is None


# ═══════════════════════════════════════════════════════════════════════
#  Row splitting
# ═══════════════════════════════════════════════════════════════════════

class TestSplitTabRow:

    def test_valid_row(self):
        line = "13h ago ●\tR1 0528\t10,061 in / 1,451 out\t$0.008193\tOK 56s\n"
        bi, parts = parse_dashboard._split_tab_row(line)
        assert bi == 0
        assert len(parts) == 5

    def test_no_bullet_returns_none(self):
        bi, parts = parse_dashboard._split_tab_row("no bullet\there\n")
        assert bi is None and parts is None

    def test_too_few_parts(self):
        bi, parts = parse_dashboard._split_tab_row("13h ago ●\tonly\n")
        assert bi is None

    def test_no_tabs(self):
        bi, parts = parse_dashboard._split_tab_row("13h ago ● R1 0528\n")
        assert bi is None


# ═══════════════════════════════════════════════════════════════════════
#  parse_line — full row parsing
# ═══════════════════════════════════════════════════════════════════════

class TestParseLine:

    @pytest.fixture
    def ref(self):
        return datetime(2026, 10, 29, 12, 0, 0)

    def test_ok_row(self, ref):
        line = "13h ago ●\tR1 0528\t10,061 in / 1,451 out\t$0.008193\tOK 56s\n"
        e = parse_dashboard.parse_line(line, ref)
        assert e["model"] == "R1 0528"
        assert e["in_tokens"] == 10061
        assert e["out_tokens"] == 1451
        assert e["tokens"] == 11512
        assert e["cost"] == Decimal("0.008193")
        assert e["status"] == "ok"
        assert e["latency_ms"] == 56_000
        assert e["ts"].startswith("2026-10-28T23:00")

    def test_no_usage_error(self, ref):
        line = "16h ago ●\tm\tNo usage\t–\tError 0ms\n"
        e = parse_dashboard.parse_line(line, ref)
        assert e["status"] == "error"
        assert e["cost"] == Decimal("0")
        assert e["tokens"] == 0

    def test_free_cost(self, ref):
        line = "2d ago ●\tgpt-oss\t10 in / 5 out\tFree\tOK 3m 33s\n"
        e = parse_dashboard.parse_line(line, ref)
        assert e["cost"] == Decimal("0")
        assert e["status"] == "ok"

    def test_absolute_date(self, ref):
        line = "21 Oct 2026 ●\tGPT\t5 in / 3 out\t$0.05\tOK 53s\n"
        e = parse_dashboard.parse_line(line, ref)
        assert e["ts"].startswith("2026-10-21")
        assert e["cost"] == Decimal("0.05")

    def test_error_with_cost_zeroes_it(self, ref):
        line = "13h ago ●\tm\t10 in / 5 out\t$0.05\tError 100ms\n"
        e = parse_dashboard.parse_line(line, ref)
        assert e["status"] == "error"
        assert e["cost"] == Decimal("0")

    def test_no_bullet_returns_none(self, ref):
        assert parse_dashboard.parse_line("plain text\n", ref) is None

    def test_bad_tokens_returns_none(self, ref):
        line = "13h ago ●\tm\tgarbage\t$0.01\tOK 1s\n"
        assert parse_dashboard.parse_line(line, ref) is None

    def test_dash_cost_treated_as_zero(self, ref):
        line = "13h ago ●\tm\t10 in / 5 out\t–\tOK 1s\n"
        e = parse_dashboard.parse_line(line, ref)
        assert e["cost"] == Decimal("0")


# ═══════════════════════════════════════════════════════════════════════
#  auto_calibrate_now
# ═══════════════════════════════════════════════════════════════════════

class TestAutoCalibrate:

    def test_mixed_absolute_relative(self):
        lines = [
            "13h ago ●\tm\t10 in / 5 out\t$0.01\tOK 1s\n",
            "6d ago ●\tm\t10 in / 5 out\t$0.01\tOK 1s\n",
            "21 Oct 2026 ●\tm\t10 in / 5 out\t$0.01\tOK 1s\n",
        ]
        ref, src = parse_dashboard.auto_calibrate_now(lines)
        assert src == "auto"
        # newest_abs = 2026-10-21, rel_max=6 → 21 + 6+1 = 2026-10-28
        assert ref.date().isoformat() == "2026-10-28"

    def test_only_relative_uses_system_now(self):
        lines = ["13h ago ●\tm\t10 in / 5 out\t$0.01\tOK 1s\n"]
        _, src = parse_dashboard.auto_calibrate_now(lines)
        assert src == "system clock"

    def test_empty_uses_system_now(self):
        _, src = parse_dashboard.auto_calibrate_now([])
        assert src == "system clock"


# ═══════════════════════════════════════════════════════════════════════
#  JSON serialization
# ═══════════════════════════════════════════════════════════════════════

class TestJsonDefault:

    def test_decimal_to_float(self):
        assert parse_dashboard._json_default(Decimal("0.123")) == 0.123

    def test_other_raises(self):
        with pytest.raises(TypeError):
            parse_dashboard._json_default(object())


# ═══════════════════════════════════════════════════════════════════════
#  End-to-end: file → JSON
# ═══════════════════════════════════════════════════════════════════════

class TestEndToEnd:

    def test_parse_file_to_json(self, tmp_path, monkeypatch):
        inp = tmp_path / "Dashboard.txt"
        inp.write_text(
            "Time\tModel\tTokens\tCost\tResult\n"
            "13h ago ●\tR1\t10 in / 5 out\t$0.01\tOK 1s\n"
            "6d ago ●\tR1\t20 in / 10 out\t$0.02\tOK 2s\n"
            "21 Oct 2026 ●\tGPT\t5 in / 3 out\t$0.05\tOK 3s\n",
            encoding="utf-8",
        )
        out = tmp_path / "out.json"
        monkeypatch.setattr(sys, "argv", [
            "parse_dashboard.py", str(inp), str(out),
            "--now", "2026-10-29T12:00",
        ])
        parse_dashboard.main()

        data = json.loads(out.read_text(encoding="utf-8"))
        assert len(data) == 3
        assert all("ts" in e and "cost" in e for e in data)
        # Сортирани newest-first
        assert data[0]["ts"] > data[-1]["ts"]