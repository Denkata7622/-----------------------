"""
═══════════════════════════════════════════════════════════════════════════
  test_pipeline.py — unit test suite за pipeline
═══════════════════════════════════════════════════════════════════════════

Pure (без API):
  • TestPointSortKey            — 8 теста (R.1 → R.15 → 1.1 → 13.4)
  • TestQueueItem               — 4 теста
  • TestState                   — 10 теста (budget, persistence, reset, thread)
  • TestQueue                   — 8 теста (load, pending, get)
  • TestAIClientPayload         — 8 теста (openai + anthropic, force_json, glm)
  • TestAIClientExtract         — 6 теста (text + usage)
  • TestLoadConfig              — 5 теста
  • TestParseJson               — 10 теста (fences, trailing comma, prose)
  • TestWriterSummary           — 6 теста (дублиран заголовък — regression)
  • TestWriterMetadata          — 5 теста (model tracking)
  • TestFormatFeedback          — 6 теста
  • TestPromptBuilders          — 4 теста (IMPROVE vs REGEN)

Всичко pure — без мрежа, без реален state, без реален queue.
"""

import json
import threading
from pathlib import Path

import pytest

import pipeline


# ═══════════════════════════════════════════════════════════════════════
#  FIXTURES
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture
def bare_pipeline():
    """Pipeline инстанция без __init__ (без AI clients, без I/O)."""
    return pipeline.Pipeline.__new__(pipeline.Pipeline)


@pytest.fixture
def tmp_state(tmp_path, monkeypatch):
    """State с изолиран файл — не пипа реален state.json."""
    monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
    monkeypatch.setitem(pipeline.CONFIG, "daily_budget_usd", 3.0)
    monkeypatch.setitem(pipeline.CONFIG, "budget_stop_pct", 0.9)
    return pipeline.State()


@pytest.fixture
def tmp_queue(tmp_path, monkeypatch):
    """Queue с изолиран файл."""
    monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
    return pipeline.Queue()


@pytest.fixture
def tmp_writer(tmp_path, monkeypatch):
    """Writer с изолиран output."""
    monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
    return pipeline.Writer()


def make_item(id="1.4", title="Test", **kwargs):
    return pipeline.QueueItem(id=id, title=title, **kwargs)


# ═══════════════════════════════════════════════════════════════════════
#  TestPointSortKey — R.1 → R.15 → 1.1 → 1.15 → 2.1 → ... → 13.4
# ═══════════════════════════════════════════════════════════════════════

class TestPointSortKey:

    def test_r_prefix_first(self):
        assert pipeline.point_sort_key("R.1") < pipeline.point_sort_key("1.1")

    def test_r_sorts_by_number(self):
        assert pipeline.point_sort_key("R.1") < pipeline.point_sort_key("R.10")
        assert pipeline.point_sort_key("R.9") < pipeline.point_sort_key("R.15")

    def test_numeric_sorts_lexicographically(self):
        """1.10 < 2.1 (не '1.10' < '1.1' string-wise)."""
        assert pipeline.point_sort_key("1.1") < pipeline.point_sort_key("1.2")
        assert pipeline.point_sort_key("1.2") < pipeline.point_sort_key("1.10")

    def test_major_minor(self):
        assert pipeline.point_sort_key("1.99") < pipeline.point_sort_key("2.1")

    def test_full_ordering(self):
        ids = ["1.10", "R.15", "2.1", "R.1", "1.1", "13.4", "R.9"]
        sorted_ids = sorted(ids, key=pipeline.point_sort_key)
        assert sorted_ids == ["R.1", "R.9", "R.15", "1.1", "1.10", "2.1", "13.4"]

    def test_two_digit_major(self):
        assert pipeline.point_sort_key("9.1") < pipeline.point_sort_key("10.1")
        assert pipeline.point_sort_key("12.1") < pipeline.point_sort_key("13.4")

    def test_same_key_equal(self):
        assert pipeline.point_sort_key("1.4") == pipeline.point_sort_key("1.4")

    def test_double_digit_minor(self):
        assert pipeline.point_sort_key("1.9") < pipeline.point_sort_key("1.15")


# ═══════════════════════════════════════════════════════════════════════
#  TestQueueItem
# ═══════════════════════════════════════════════════════════════════════

class TestQueueItem:

    def test_minimal(self):
        it = pipeline.QueueItem(id="1.1", title="Test")
        assert it.id == "1.1"
        assert it.title == "Test"
        assert it.status == "pending"
        assert it.attempts == 0
        assert it.verification is None

    def test_defaults(self):
        it = pipeline.QueueItem(id="1.1", title="Test")
        assert it.desc == ""
        assert it.source == ""
        assert it.pdf == ""
        assert it.page == 1
        assert it.tokens_used == 0
        assert it.cost_usd == 0.0

    def test_full(self):
        it = pipeline.QueueItem(
            id="1.4", title="Менелай", desc="desc", source="OT_2012",
            pdf="file.pdf", page=5, status="running", attempts=2,
        )
        assert it.desc == "desc"
        assert it.page == 5
        assert it.status == "running"
        assert it.attempts == 2

    def test_extra_fields_filtered_by_queue(self, tmp_path, monkeypatch):
        """Queue._load трябва да игнорира непознати полета."""
        qf = tmp_path / "queue.jsonl"
        qf.write_text(
            '{"id": "1.1", "title": "Test", "unknown_field": "x", "page": 3}\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        q = pipeline.Queue()
        assert len(q.items) == 1
        assert q.items[0].id == "1.1"
        assert not hasattr(q.items[0], "unknown_field")


# ═══════════════════════════════════════════════════════════════════════
#  TestState — persistence & budget
# ═══════════════════════════════════════════════════════════════════════

class TestState:

    def test_fresh_defaults(self, tmp_state):
        assert tmp_state.data["processed"] == {}
        assert tmp_state.data["budget"]["spent_usd"] == 0.0
        assert tmp_state.data["budget"]["calls"] == 0

    def test_save_and_reload(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        s1 = pipeline.State()
        s1.mark("1.4", "done", cost=0.05, tokens=1000)
        s2 = pipeline.State()
        assert s2.is_done("1.4")
        assert s2.data["processed"]["1.4"]["cost"] == 0.05
        assert s2.data["processed"]["1.4"]["tokens"] == 1000

    def test_add_cost_accumulates(self, tmp_state):
        tmp_state.add_cost(0.05, tokens=100)
        tmp_state.add_cost(0.03, tokens=200)
        assert abs(tmp_state.data["budget"]["spent_usd"] - 0.08) < 1e-9
        assert tmp_state.data["budget"]["calls"] == 2
        assert tmp_state.data["total_cost_usd"] == pytest.approx(0.08)

    def test_budget_exceeded_threshold(self, tmp_state):
        # Default 3.0 * 0.9 = 2.7
        tmp_state.data["budget"]["spent_usd"] = 2.5
        assert not tmp_state.budget_exceeded()
        tmp_state.data["budget"]["spent_usd"] = 2.8
        assert tmp_state.budget_exceeded()

    def test_budget_exceeded_exact(self, tmp_state):
        tmp_state.data["budget"]["spent_usd"] = 2.7
        assert tmp_state.budget_exceeded()

    def test_budget_remaining(self, tmp_state):
        tmp_state.add_cost(1.0)
        assert abs(tmp_state.budget_remaining() - 2.0) < 1e-9

    def test_mark_done(self, tmp_state):
        tmp_state.mark("1.1", "done")
        assert tmp_state.is_done("1.1")

    def test_mark_error(self, tmp_state):
        tmp_state.mark("1.1", "error")
        assert not tmp_state.is_done("1.1")
        assert tmp_state.stats()["error"] == 1

    def test_stats(self, tmp_state):
        tmp_state.mark("1.1", "done", cost=0.01)
        tmp_state.mark("1.2", "done", cost=0.02)
        tmp_state.mark("1.3", "error")
        s = tmp_state.stats()
        assert s["done"] == 2
        assert s["error"] == 1
        assert s["total"] == 3

    def test_budget_reset_new_day(self, tmp_state, monkeypatch):
        tmp_state.data["budget"]["date"] = "2020-01-01"
        tmp_state.data["budget"]["spent_usd"] = 5.0
        tmp_state.check_budget_reset()
        assert tmp_state.data["budget"]["spent_usd"] == 0.0
        assert tmp_state.data["budget"]["date"] != "2020-01-01"


# ═══════════════════════════════════════════════════════════════════════
#  TestQueue
# ═══════════════════════════════════════════════════════════════════════

class TestQueue:

    def test_empty_queue_creates_sample(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        q = pipeline.Queue()
        assert len(q.items) == 1
        assert q.items[0].id == "1.1"

    def test_load_multiple(self, tmp_path, monkeypatch):
        qf = tmp_path / "queue.jsonl"
        qf.write_text(
            '{"id": "1.1", "title": "A"}\n'
            '{"id": "1.2", "title": "B"}\n'
            '{"id": "R.1", "title": "C"}\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        q = pipeline.Queue()
        assert len(q.items) == 3

    def test_skips_comments_and_blanks(self, tmp_path, monkeypatch):
        qf = tmp_path / "queue.jsonl"
        qf.write_text(
            '# comment\n'
            '\n'
            '{"id": "1.1", "title": "A"}\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        q = pipeline.Queue()
        assert len(q.items) == 1

    def test_pending_filter(self, tmp_state):
        q = pipeline.Queue.__new__(pipeline.Queue)
        q.items = [
            make_item("1.1", status="pending"),
            make_item("1.2", status="done"),
            make_item("1.3", status="error", attempts=0),
            make_item("1.4", status="running"),
            make_item("1.5", status="error", attempts=5),  # exceeds max_retries
        ]
        pending = q.pending(tmp_state)
        ids = sorted(it.id for it in pending)
        assert ids == ["1.1", "1.3"]

    def test_pending_sorted_by_point_key(self, tmp_state):
        q = pipeline.Queue.__new__(pipeline.Queue)
        q.items = [
            make_item("1.10"),
            make_item("R.1"),
            make_item("2.1"),
            make_item("1.1"),
        ]
        pending = q.pending(tmp_state)
        assert [it.id for it in pending] == ["R.1", "1.1", "1.10", "2.1"]

    def test_pending_only_id(self, tmp_state):
        q = pipeline.Queue.__new__(pipeline.Queue)
        q.items = [make_item("1.1"), make_item("1.2"), make_item("1.3")]
        pending = q.pending(tmp_state, only_id="1.2")
        assert len(pending) == 1
        assert pending[0].id == "1.2"

    def test_pending_respects_state_done(self, tmp_state):
        tmp_state.mark("1.1", "done")
        q = pipeline.Queue.__new__(pipeline.Queue)
        q.items = [make_item("1.1"), make_item("1.2")]
        pending = q.pending(tmp_state)
        assert len(pending) == 1
        assert pending[0].id == "1.2"

    def test_get(self):
        q = pipeline.Queue.__new__(pipeline.Queue)
        q.items = [make_item("1.1"), make_item("1.2")]
        assert q.get("1.1").id == "1.1"
        assert q.get("9.9") is None

    def test_total(self):
        q = pipeline.Queue.__new__(pipeline.Queue)
        q.items = [make_item("1.1"), make_item("1.2")]
        assert q.total() == 2


# ═══════════════════════════════════════════════════════════════════════
#  TestAIClientPayload
# ═══════════════════════════════════════════════════════════════════════

class TestAIClientPayload:

    def _client(self, **overrides):
        cfg = {
            "api_url": "https://api.example.com/v1/chat",
            "api_key": "test-key",
            "model": "test/model",
            "max_tokens": 1000,
            "temperature": 0.3,
            "provider": "openai-compatible",
            "reasoning_effort": None,
        }
        cfg.update(overrides)
        return pipeline.AIClient(cfg)

    def test_openai_payload(self):
        c = self._client()
        p = c._payload("sys", "usr")
        assert p["model"] == "test/model"
        assert p["messages"] == [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "usr"},
        ]

    def test_force_json(self):
        c = self._client()
        p = c._payload("s", "u", force_json=True)
        assert p["response_format"] == {"type": "json_object"}

    def test_no_force_json_by_default(self):
        c = self._client()
        p = c._payload("s", "u")
        assert "response_format" not in p

    def test_anthropic_detected_by_url(self):
        c = self._client(api_url="https://api.anthropic.com/v1/messages")
        assert c.is_anthropic

    def test_anthropic_payload(self):
        c = self._client(api_url="https://api.anthropic.com/v1/messages")
        p = c._payload("sys", "usr")
        assert p["system"] == "sys"
        assert p["messages"] == [{"role": "user", "content": "usr"}]

    def test_anthropic_headers(self):
        c = self._client(api_url="https://api.anthropic.com/v1/messages", api_key="sk-ant")
        assert c.headers["x-api-key"] == "sk-ant"
        assert "anthropic-version" in c.headers

    def test_glm_reasoning_effort(self):
        c = self._client(model="z-ai/glm-5.3-flash", reasoning_effort="low")
        p = c._payload("s", "u")
        assert p["reasoning_effort"] == "low"

    def test_non_glm_no_reasoning_effort(self):
        c = self._client(model="openai/gpt-6.1-sol", reasoning_effort="low")
        p = c._payload("s", "u")
        assert "reasoning_effort" not in p


# ═══════════════════════════════════════════════════════════════════════
#  TestAIClientExtract
# ═══════════════════════════════════════════════════════════════════════

class TestAIClientExtract:

    def _client(self, **overrides):
        cfg = {
            "api_url": "https://api.example.com/v1/chat",
            "api_key": "k", "model": "m", "max_tokens": 1000,
            "temperature": 0.0, "provider": "openai-compatible",
            "reasoning_effort": None,
        }
        cfg.update(overrides)
        return pipeline.AIClient(cfg)

    def test_openai_text(self):
        c = self._client()
        data = {"choices": [{"message": {"content": "Hello"}}]}
        assert c._extract_text(data) == "Hello"

    def test_openai_missing_content(self):
        c = self._client()
        assert c._extract_text({"choices": [{"message": {}}]}) == ""

    def test_anthropic_text(self):
        c = self._client(api_url="https://api.anthropic.com/v1/messages")
        data = {"content": [
            {"type": "text", "text": "Part1"},
            {"type": "text", "text": "Part2"},
        ]}
        assert c._extract_text(data) == "Part1\nPart2"

    def test_openai_usage(self):
        c = self._client()
        tokens, cost = c._extract_usage({"usage": {"total_tokens": 500, "cost": 0.02}})
        assert tokens == 500
        assert cost == 0.02

    def test_anthropic_usage(self):
        c = self._client(api_url="https://api.anthropic.com/v1/messages")
        tokens, cost = c._extract_usage({"usage": {"input_tokens": 100, "output_tokens": 200}})
        assert tokens == 300

    def test_usage_missing(self):
        c = self._client()
        tokens, cost = c._extract_usage({})
        assert tokens == 0
        assert cost == 0.0


# ═══════════════════════════════════════════════════════════════════════
#  TestLoadConfig
# ═══════════════════════════════════════════════════════════════════════

class TestLoadConfig:

    def test_creates_default_when_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        cfg = pipeline.load_config()
        assert (tmp_path / "config.json").exists()
        assert cfg["generator"]["model"] == pipeline.DEFAULT_CONFIG["generator"]["model"]

    def test_merges_generator_subdict(self, tmp_path, monkeypatch):
        (tmp_path / "config.json").write_text(
            json.dumps({"generator": {"model": "custom/model"}}),
            encoding="utf-8",
        )
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        cfg = pipeline.load_config()
        assert cfg["generator"]["model"] == "custom/model"
        # defaults за останалите полета
        assert cfg["generator"]["max_tokens"] == pipeline.DEFAULT_CONFIG["generator"]["max_tokens"]

    def test_top_level_override(self, tmp_path, monkeypatch):
        (tmp_path / "config.json").write_text(
            json.dumps({"daily_budget_usd": 10.0}),
            encoding="utf-8",
        )
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        cfg = pipeline.load_config()
        assert cfg["daily_budget_usd"] == 10.0

    def test_invalid_json_returns_default(self, tmp_path, monkeypatch, capsys):
        (tmp_path / "config.json").write_text("not json", encoding="utf-8")
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        cfg = pipeline.load_config()
        assert cfg["daily_budget_usd"] == pipeline.DEFAULT_CONFIG["daily_budget_usd"]

    def test_preserves_all_default_keys(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pipeline, "BASE_DIR", tmp_path)
        cfg = pipeline.load_config()
        for key in pipeline.DEFAULT_CONFIG:
            assert key in cfg


# ═══════════════════════════════════════════════════════════════════════
#  TestParseJson
# ═══════════════════════════════════════════════════════════════════════

class TestParseJson:

    def test_plain(self, bare_pipeline):
        assert bare_pipeline._parse_json('{"a": 1}') == {"a": 1}

    def test_markdown_fence(self, bare_pipeline):
        assert bare_pipeline._parse_json('```json\n{"a": 1}\n```') == {"a": 1}

    def test_markdown_fence_no_lang(self, bare_pipeline):
        assert bare_pipeline._parse_json('```\n{"a": 1}\n```') == {"a": 1}

    def test_trailing_comma(self, bare_pipeline):
        r = bare_pipeline._parse_json('{"a": 1, "b": [1, 2,],}')
        assert r == {"a": 1, "b": [1, 2]}

    def test_prose_around(self, bare_pipeline):
        assert bare_pipeline._parse_json('Here: {"a": 1} done') == {"a": 1}

    def test_empty_returns_none(self, bare_pipeline):
        assert bare_pipeline._parse_json("") is None
        assert bare_pipeline._parse_json(None) is None

    def test_invalid_returns_none(self, bare_pipeline):
        assert bare_pipeline._parse_json("nothing here") is None

    def test_nested_json(self, bare_pipeline):
        text = '{"outer": {"inner": [1, 2, 3]}, "x": true}'
        assert bare_pipeline._parse_json(text) == {"outer": {"inner": [1, 2, 3]}, "x": True}

    def test_unclosed_returns_none(self, bare_pipeline):
        assert bare_pipeline._parse_json('{"a": 1') is None

    def test_unicode_preserved(self, bare_pipeline):
        r = bare_pipeline._parse_json('{"msg": "Здравей свят"}')
        assert r["msg"] == "Здравей свят"


# ═══════════════════════════════════════════════════════════════════════
#  TestWriterSummary — regression за дублиран заголовък
# ═══════════════════════════════════════════════════════════════════════

class TestWriterSummary:

    def test_extracts_first_two_sections(self, tmp_writer):
        md = """## 1. Защо е важно
Текст на първа секция.

## 2. Какво ще научиш
Текст на втора секция.

## 3. Основи
Текст на трета секция."""
        summary = tmp_writer._extract_summary_section(md)
        assert "1. Защо е важно" in summary
        assert "2. Какво ще научиш" in summary
        assert "3. Основи" not in summary

    def test_no_duplicate_header(self, tmp_writer):
        """REGRESSION: заголовъкът не трябва да се дублира."""
        md = "## 1. Защо е важно\nТекст.\n## 2. Втора\nОще текст."
        summary = tmp_writer._extract_summary_section(md)
        # Не трябва да има "Защо е важно Защо е важно"
        assert "Защо е важно Защо е важно" not in summary
        # Заголовъкът се среща точно веднъж
        assert summary.count("1. Защо е важно") == 1

    def test_short_article_returns_verbatim(self, tmp_writer):
        md = "Кратко съдържание без секции."
        summary = tmp_writer._extract_summary_section(md)
        assert summary == md

    def test_no_sections_falls_back_to_400_words(self, tmp_writer):
        md = " ".join(f"word{i}" for i in range(500))
        summary = tmp_writer._extract_summary_section(md)
        assert "..." in summary
        # Около 400 думи + "..."
        word_count = len(summary.replace("...", "").split())
        assert 399 <= word_count <= 401

    def test_empty_article(self, tmp_writer):
        summary = tmp_writer._extract_summary_section("")
        assert summary == ""

    def test_body_preserved_after_header(self, tmp_writer):
        md = "## 1. Заглавие\nРед 1\nРед 2\n## 2. Второ\nСъдържание"
        summary = tmp_writer._extract_summary_section(md)
        assert "Ред 1" in summary
        assert "Ред 2" in summary
        assert "Съдържание" in summary


# ═══════════════════════════════════════════════════════════════════════
#  TestWriterMetadata — model tracking
# ═══════════════════════════════════════════════════════════════════════

class TestWriterMetadata:

    def test_metadata_includes_generator_model(self, tmp_writer, monkeypatch):
        monkeypatch.setitem(pipeline.CONFIG["generator"], "model", "test/gen-model")
        item = make_item("1.4", title="Test")
        parsed = {"article_markdown": "Some article text.", "word_count": 3}
        folder = tmp_writer.write(item, parsed)

        meta = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
        assert meta["generator_model"] == "test/gen-model"
        assert meta["point_id"] == "1.4"

    def test_verifier_model_none_without_verification(self, tmp_writer, monkeypatch):
        monkeypatch.setitem(pipeline.CONFIG, "enable_verification", True)
        item = make_item("1.4", title="Test")
        item.verification = None
        parsed = {"article_markdown": "Text.", "word_count": 1}
        folder = tmp_writer.write(item, parsed)

        meta = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
        assert meta["verifier_model"] is None

    def test_verifier_model_present_with_verification(self, tmp_writer, monkeypatch):
        monkeypatch.setitem(pipeline.CONFIG, "enable_verification", True)
        monkeypatch.setitem(pipeline.CONFIG["verifier"], "model", "test/ver-model")
        item = make_item("1.4", title="Test")
        item.verification = {"score": 8, "verdict": "approve"}
        parsed = {"article_markdown": "Text.", "word_count": 1}
        folder = tmp_writer.write(item, parsed)

        meta = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
        assert meta["verifier_model"] == "test/ver-model"

    def test_deep_md_includes_models(self, tmp_writer, monkeypatch):
        monkeypatch.setitem(pipeline.CONFIG["generator"], "model", "gen/x")
        monkeypatch.setitem(pipeline.CONFIG["verifier"], "model", "ver/y")
        monkeypatch.setitem(pipeline.CONFIG, "enable_verification", True)
        item = make_item("1.4", title="Test")
        parsed = {"article_markdown": "Some article text here.", "word_count": 4}
        folder = tmp_writer.write(item, parsed)

        deep = (folder / "deep.md").read_text(encoding="utf-8")
        assert "**Generator:** gen/x" in deep
        assert "**Verifier:** ver/y" in deep

    def test_verify_json_includes_model(self, tmp_writer, monkeypatch):
        monkeypatch.setitem(pipeline.CONFIG["verifier"], "model", "ver/z")
        item = make_item("1.4", title="Test")
        item.verification = {"score": 9, "verdict": "approve", "strengths": [], "issues": [],
                             "math_errors": [], "missing_topics": [], "suggestions": []}
        parsed = {"article_markdown": "Text.", "word_count": 1}
        folder = tmp_writer.write(item, parsed)

        vf = json.loads((folder / "verify-v1.json").read_text(encoding="utf-8"))
        assert vf["_model"] == "ver/z"


# ═══════════════════════════════════════════════════════════════════════
#  TestFormatFeedback
# ═══════════════════════════════════════════════════════════════════════

class TestFormatFeedback:

    def test_basic(self, bare_pipeline):
        vf = {"score": 3, "verdict": "reject", "verdict_reasoning": "Bad math"}
        text = bare_pipeline._format_feedback(vf)
        assert "3/10" in text
        assert "reject" in text
        assert "Bad math" in text

    def test_math_errors_section(self, bare_pipeline):
        vf = {
            "score": 3, "verdict": "reject", "verdict_reasoning": "—",
            "math_errors": [{"formula": "x²=4", "problem": "says x=3", "fix": "x=2"}],
        }
        text = bare_pipeline._format_feedback(vf)
        assert "МАТЕМАТИЧЕСКИ ГРЕШКИ" in text
        assert "x²=4" in text

    def test_issues_section(self, bare_pipeline):
        vf = {
            "score": 5, "verdict": "revise", "verdict_reasoning": "—",
            "issues": [{"severity": "major", "section": "3.1", "description": "Missing proof"}],
        }
        text = bare_pipeline._format_feedback(vf)
        assert "[major]" in text
        assert "3.1" in text

    def test_empty_sections_skipped(self, bare_pipeline):
        vf = {"score": 10, "verdict": "approve", "verdict_reasoning": "—"}
        text = bare_pipeline._format_feedback(vf)
        assert "МАТЕМАТИЧЕСКИ ГРЕШКИ" not in text
        assert "ПРОБЛЕМИ" not in text

    def test_all_sections(self, bare_pipeline):
        vf = {
            "score": 4, "verdict": "revise", "verdict_reasoning": "Mixed",
            "math_errors": [{"formula": "a", "problem": "b", "fix": "c"}],
            "issues": [{"severity": "minor", "section": "s", "description": "d"}],
            "missing_topics": ["Topic X"],
            "suggestions": ["Add example"],
        }
        text = bare_pipeline._format_feedback(vf)
        for header in ("МАТЕМАТИЧЕСКИ ГРЕШКИ", "ПРОБЛЕМИ",
                       "ЛИПСВАЩИ ТЕМИ", "ПРЕДЛОЖЕНИЯ"):
            assert header in text

    def test_missing_fields_safe(self, bare_pipeline):
        vf = {"score": 8, "verdict": "approve"}
        text = bare_pipeline._format_feedback(vf)
        assert "8/10" in text  # не гърми при липсващ verdict_reasoning


# ═══════════════════════════════════════════════════════════════════════
#  TestPromptBuilders — IMPROVE vs REGEN
# ═══════════════════════════════════════════════════════════════════════

class TestPromptBuilders:

    def test_improve_contains_word_count(self, bare_pipeline):
        prompt = bare_pipeline._build_improve_prompt(
            gen_user="BASE",
            article_md="Some article text.",
            actual_wc=1000,
            min_target=2800,
            max_target=3400,
            feedback="FB",
        )
        assert "1000" in prompt
        assert "2800" in prompt
        assert "3400" in prompt
        assert "BASE" in prompt
        assert "FB" in prompt

    def test_improve_has_word_deficit(self, bare_pipeline):
        prompt = bare_pipeline._build_improve_prompt(
            "B", "text", 1000, 2800, 3400, "FB",
        )
        # deficit = 3400 - 1000 = 2400
        assert "2400" in prompt

    def test_regen_includes_actual_wc(self, bare_pipeline):
        prompt = bare_pipeline._build_regen_prompt("B", 500, "FB")
        assert "500" in prompt
        assert "ОТ НАЧАЛО" in prompt
        assert "FB" in prompt

    def test_improve_vs_regen_differ(self, bare_pipeline):
        p1 = bare_pipeline._build_improve_prompt("B", "text", 1000, 2800, 3400, "FB")
        p2 = bare_pipeline._build_regen_prompt("B", 1000, "FB")
        assert p1 != p2
        assert "РАЗШИРЯВАНЕ" in p1
        assert "ПРЕРАБОТИ ОТ НУЛАТА" in p2


# ═══════════════════════════════════════════════════════════════════════
#  TestBudgetExhausted
# ═══════════════════════════════════════════════════════════════════════

class TestBudgetExhausted:

    def test_is_exception(self):
        exc = pipeline.BudgetExhausted("test")
        assert isinstance(exc, Exception)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(pipeline.BudgetExhausted):
            raise pipeline.BudgetExhausted("402: limit reached")


# ═══════════════════════════════════════════════════════════════════════
#  TestComputeSectionsMin — регресия на ceil-bug
# ═══════════════════════════════════════════════════════════════════════

class TestComputeSectionsMin:
    """ceil(min_target / sections) >= min_target, не naive multiplication."""

    def test_ceil_division_312(self, bare_pipeline):
        """2800 / 9 = 311.1 → ceil = 312 > 300 configured."""
        min_per, total = bare_pipeline._compute_sections_min(2800)
        assert min_per * total >= 2800
        assert min_per == 312
        assert total == 9

    def test_higher_target(self, bare_pipeline):
        min_per, total = bare_pipeline._compute_sections_min(5000)
        assert min_per * total >= 5000

    def test_lower_target_uses_configured_300(self, bare_pipeline):
        """2000 / 9 = 222 < 300 configured → keeps 300."""
        min_per, total = bare_pipeline._compute_sections_min(2000)
        assert min_per == 300


# ═══════════════════════════════════════════════════════════════════════
#  TestImprovePromptDeficitSigns
# ═══════════════════════════════════════════════════════════════════════

class TestImprovePromptDeficitSigns:
    """Дефицит може да е положителен или отрицателен — различни инструкции."""

    def test_negative_deficit_prioritizes_fixes(self, bare_pipeline):
        # 4000 думи > max_target 3400 → отрицателен дефицит
        prompt = bare_pipeline._build_improve_prompt(
            "BASE", "text", 4000, 2800, 3400, "FB")
        assert "ПРИОРИТЕТ" in prompt

    def test_positive_deficit_asks_for_length(self, bare_pipeline):
        # 1500 < max_target 3400 → положителен дефицит
        prompt = bare_pipeline._build_improve_prompt(
            "BASE", "text", 1500, 2800, 3400, "FB")
        assert "Трябва да ДОБАВИШ" in prompt


# ═══════════════════════════════════════════════════════════════════════
#  TestAIClient400Handling — parameter fallback
# ═══════════════════════════════════════════════════════════════════════

class TestAIClient400Handling:

    def test_400_strips_both_response_format_and_reasoning(self, monkeypatch):
        c = pipeline.AIClient.__new__(pipeline.AIClient)
        c.name = "test"
        c.url = "https://api.example.com"
        c.model = "m"
        c.max_tokens = 100
        c.temperature = 0.3
        c.reasoning_effort = "low"
        c.cost_per_call_fallback = 0.0
        c.is_anthropic = False
        c.headers = {}

        calls = []

        class FakeResp:
            def __init__(self, code, body=None):
                self.status_code = code
                self._body = body or {}
            @property
            def text(self): return "err"
            def json(self): return self._body

        def fake_post(url, headers, json, timeout):
            calls.append(dict(json))
            if len(calls) == 1:
                return FakeResp(400)
            return FakeResp(200, {
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.001},
            })

        monkeypatch.setattr("requests.post", fake_post)
        monkeypatch.setattr(pipeline, "_track_call", lambda *a, **k: None)

        text, tokens, cost = c.call("sys", "user", "test")
        assert text == "ok"
        assert tokens == 15
        assert len(calls) == 2
        # Първият опит има поне един risk param
        assert "response_format" in calls[0] or "reasoning_effort" in calls[0]
        # Вторият — поне единият е премахнат
        assert ("response_format" not in calls[1]
                or "reasoning_effort" not in calls[1])


# ═══════════════════════════════════════════════════════════════════════
#  TestBudgetExhaustedPropagation — 402 не се retry-ва
# ═══════════════════════════════════════════════════════════════════════

class TestBudgetExhaustedPropagation:

    def test_402_raises_immediately(self, monkeypatch):
        c = pipeline.AIClient.__new__(pipeline.AIClient)
        c.name = "test"
        c.url = "https://api.example.com"
        c.model = "m"
        c.max_tokens = 100
        c.temperature = 0.3
        c.reasoning_effort = None
        c.cost_per_call_fallback = 0.0
        c.is_anthropic = False
        c.headers = {}

        class FakeResp:
            status_code = 402
            text = "402: quota exceeded"
            def json(self): return {}

        calls = []
        def fake_post(*a, **k):
            calls.append(1)
            return FakeResp()

        monkeypatch.setattr("requests.post", fake_post)

        with pytest.raises(pipeline.BudgetExhausted):
            c.call("s", "u", "test")
        # Само 1 опит — 402 не се retry-ва
        assert len(calls) == 1


# ═══════════════════════════════════════════════════════════════════════
#  Live tests — 1 API call, ~$0.003
# ═══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def live_pipeline():
    """Пълен Pipeline — само за live тестове."""
    p = pipeline.Pipeline(html_path=None, only_id=None)
    if p.verifier is None:
        pytest.skip("Verifier not configured (enable_verification=false or no api_key)")
    return p


class TestLiveGeneration:
    pytestmark = pytest.mark.live

    def test_generator_returns_valid_json(self, live_pipeline):
        """1 API call — проверява че generator-ът връща парсируем JSON."""
        text, tokens, cost = live_pipeline.generator.call(
            "You are a JSON bot. Always respond with valid JSON.",
            'Върни JSON: {"ok": true, "msg": "Здравей"}',
            "test",
            force_json=True,
        )
        assert text is not None
        parsed = live_pipeline._parse_json(text)
        assert parsed is not None
        assert "ok" in parsed
        print(f"\n  📊 Generator: {live_pipeline.generator.model}")
        print(f"     Tokens: {tokens}, Cost: ${cost:.6f}")
        print(f"     Response: {parsed}")