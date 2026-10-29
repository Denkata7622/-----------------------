"""
═══════════════════════════════════════════════════════════════════════════
  test_integrate.py — HTML article integration
═══════════════════════════════════════════════════════════════════════════
"""
from pathlib import Path

import pytest

import integrate


class TestEscapeForBacktick:

    def test_simple(self):
        assert integrate.escape_for_backtick("hello") == "hello"

    def test_backtick_escaped(self):
        assert integrate.escape_for_backtick("a`b") == "a\\`b"

    def test_dollar_brace_escaped(self):
        assert integrate.escape_for_backtick("${x}") == "\\${x}"

    def test_backslash_escaped(self):
        assert integrate.escape_for_backtick("a\\b") == "a\\\\b"

    def test_script_tag_broken(self):
        assert integrate.escape_for_backtick("</script>") == "<\\/script>"

    def test_newlines_normalized(self):
        assert integrate.escape_for_backtick("a\r\nb\rc") == "a\nb\nc"

    def test_null_byte_stripped(self):
        assert integrate.escape_for_backtick("a\x00b") == "ab"

    def test_unicode_line_sep(self):
        r = integrate.escape_for_backtick("a\u2028b\u2029c")
        assert "\\u2028" in r and "\\u2029" in r


class TestCleanMarkdown:

    def test_headers_removed(self):
        assert integrate.clean_markdown("# H1\n## H2\ntext") == "text"

    def test_bold_stripped(self):
        assert integrate.clean_markdown("**bold** text") == "bold text"

    def test_italic_stripped(self):
        assert integrate.clean_markdown("*it* text") == "it text"

    def test_inline_code_unwrapped(self):
        assert integrate.clean_markdown("`code`") == "code"

    def test_latex_inline_preserved(self):
        assert integrate.clean_markdown("$x^2 + y^2 = z^2$") == "$x^2 + y^2 = z^2$"

    def test_latex_display_preserved(self):
        r = integrate.clean_markdown("$$\\int_0^1 f(x)dx$$")
        assert "$$" in r and "\\int" in r

    def test_links_stripped(self):
        assert integrate.clean_markdown("[text](url)") == "text"

    def test_bullets_normalized(self):
        r = integrate.clean_markdown("- item1\n- item2")
        assert "• item1" in r and "• item2" in r

    def test_empty(self):
        assert integrate.clean_markdown("") == ""


class TestFindObjectEnd:

    def test_simple(self):
        t = '{"a": 1}'
        assert integrate.find_object_end(t, 0) == len(t)

    def test_nested(self):
        t = '{"a": {"b": {"c": 1}}}'
        assert integrate.find_object_end(t, 0) == len(t)

    def test_string_with_brace(self):
        t = '{"a": "}"}'
        assert integrate.find_object_end(t, 0) == len(t)

    def test_escaped_quote(self):
        t = '{"a": "\\""}'
        assert integrate.find_object_end(t, 0) == len(t)

    def test_unclosed(self):
        t = '{"a": 1'
        assert integrate.find_object_end(t, 0) == len(t)


class TestFindPointBlock:

    def test_finds_block(self):
        html = '''const STEPS = [
            {id: "1.4", title: "Test"},
            {id: "2.1", title: "Other"},
        ];'''
        start, end = integrate.find_point_block(html, "1.4")
        assert start != -1
        assert "1.4" in html[start:end]
        assert "2.1" not in html[start:end]

    def test_not_found(self):
        html = 'const STEPS = [{id: "1.4"}];'
        start, _ = integrate.find_point_block(html, "9.9")
        assert start == -1


class TestFindFieldSpan:

    def test_backtick(self):
        span = integrate.find_field_span('title: `Hello`', "title")
        assert span[2] == "Hello"

    def test_double_quote(self):
        span = integrate.find_field_span('title: "Hello"', "title")
        assert span[2] == "Hello"

    def test_single_quote(self):
        span = integrate.find_field_span("title: 'Hello'", "title")
        assert span[2] == "Hello"

    def test_missing_returns_none(self):
        assert integrate.find_field_span("x: 1", "missing") is None

    def test_escaped_quote_in_content(self):
        span = integrate.find_field_span(r'title: "a\"b"', "title")
        assert span[2] == r'a\"b'


class TestReplaceOrInsertField:

    def test_replaces_existing(self):
        block = 'title: `old`, desc: `d`'
        new, action = integrate.replace_or_insert_field(block, "title", "new")
        assert action == "replaced"
        assert "new" in new and "old" not in new

    def test_inserts_after_anchor(self):
        block = 'desc: `d`'
        new, action = integrate.replace_or_insert_field(
            block, "explanation", "text", anchor="desc")
        assert action == "inserted"
        assert "explanation:" in new

    def test_escapes_special_chars(self):
        block = 'title: `old`'
        new, _ = integrate.replace_or_insert_field(block, "title", "a`b ${c}")
        assert "\\`" in new and "\\${" in new


class TestReadMd:

    def test_read_text_strips_frontmatter(self, tmp_path):
        f = tmp_path / "text.md"
        f.write_text("---\nid: 1.4\n---\n# Title\nBody text", encoding="utf-8")
        r = integrate.read_text_md(f)
        assert "id: 1.4" not in r
        assert "Body text" in r

    def test_read_deep_strips_frontmatter_and_h1(self, tmp_path):
        f = tmp_path / "deep.md"
        f.write_text("---\nid: 1.4\n---\n# Title\nBody", encoding="utf-8")
        r = integrate.read_deep_md(f)
        assert "id: 1.4" not in r
        assert "# Title" not in r
        assert "Body" in r