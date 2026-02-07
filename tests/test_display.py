"""Unit tests for display.py."""

from io import StringIO

from rich.console import Console

from outlook_cli import display


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
