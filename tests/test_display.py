"""Unit tests for display.py."""

from io import StringIO

from rich.console import Console

from outlook_cli import display
from outlook_cli.display import _looks_like_html, _strip_html


def _capture_console():
    """Replace the module console with one that captures output."""
    buf = StringIO()
    console = Console(file=buf, force_terminal=True, width=120)
    display.console = console
    return buf


def test_print_error():
    buf = _capture_console()
    display.print_error("something broke")
    assert "Error:" in buf.getvalue()
    assert "something broke" in buf.getvalue()


def test_print_success():
    buf = _capture_console()
    display.print_success("it worked")
    assert "OK:" in buf.getvalue()
    assert "it worked" in buf.getvalue()


def test_print_mail_table(mock_message):
    buf = _capture_console()
    display.print_mail_table([mock_message])
    output = buf.getvalue()
    assert "Test Subject" in output
    assert "msg-123" in output


def test_print_mail_detail(mock_message):
    buf = _capture_console()
    display.print_mail_detail(mock_message)
    output = buf.getvalue()
    assert "Test Subject" in output
    assert "Hello, world!" in output


def test_print_event_table(mock_event):
    buf = _capture_console()
    display.print_event_table([mock_event])
    output = buf.getvalue()
    assert "Team Meeting" in output
    assert "Room 1" in output


def test_print_event_detail(mock_event):
    buf = _capture_console()
    display.print_event_detail(mock_event)
    output = buf.getvalue()
    assert "Team Meeting" in output
    assert "Weekly sync" in output


def test_print_mail_table_empty():
    buf = _capture_console()
    display.print_mail_table([])
    output = buf.getvalue()
    assert "Messages" in output


# ── _strip_html / _looks_like_html ──────────────────────────


def test_strip_html_removes_tags():
    assert _strip_html("<p>hello</p>") == "hello"


def test_strip_html_converts_br():
    assert "line1\nline2" in _strip_html("line1<br>line2")


def test_strip_html_unescapes_entities():
    assert _strip_html("&amp; &lt; &gt; &quot;") == '& < > "'


def test_strip_html_handles_nbsp():
    assert _strip_html("word&nbsp;word") == "word word"


def test_strip_html_handles_numeric_entities():
    assert _strip_html("&#39;quoted&#39;") == "'quoted'"


def test_looks_like_html_true():
    assert _looks_like_html("<html><body>hi</body></html>") is True
    assert _looks_like_html("<div>content</div>") is True
    assert _looks_like_html("<p>paragraph</p>") is True


def test_looks_like_html_false():
    assert _looks_like_html("just plain text") is False
    assert _looks_like_html("no <tags here") is False
