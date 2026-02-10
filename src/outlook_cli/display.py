"""Rich formatting helpers for CLI output."""

import html
import re

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


# ── Utilities ─────────────────────────────────────────────────


def _strip_html(text: str) -> str:
    """Strip HTML tags for plain text display."""
    clean = re.sub(r"<br\s*/?>", "\n", text)
    clean = re.sub(r"<p[^>]*>", "\n", clean)
    clean = re.sub(r"</p>", "", clean)
    clean = re.sub(r"<[^>]+>", "", clean)
    clean = re.sub(r"&nbsp;", " ", clean)
    clean = html.unescape(clean)
    return clean.strip()


def _looks_like_html(text: str) -> bool:
    """Return True if text appears to contain HTML markup."""
    return bool(re.search(r"<(html|div|p|br|table)\b", text, re.IGNORECASE))


# ── Styled output ──────────────────────────────────────────────


def print_error(msg: str) -> None:
    console.print(f"[bold red]Error:[/] {msg}")


def print_success(msg: str) -> None:
    console.print(f"[bold green]OK:[/] {msg}")


# ── Mail ───────────────────────────────────────────────────────


def print_mail_table(messages: list) -> None:
    table = Table(title="Messages", show_lines=False)
    table.add_column("", max_width=1)  # unread dot
    table.add_column("Imp", max_width=1)
    table.add_column("Att", max_width=2)
    table.add_column("From", style="cyan", max_width=30)
    table.add_column("Subject", style="white")
    table.add_column("Date", style="green", max_width=20)
    table.add_column("ID", style="dim", max_width=36)

    for msg in messages:
        is_read = getattr(msg, "is_read", True)
        importance = getattr(msg, "importance", None)
        has_attachments = getattr(msg, "has_attachments", False)

        status = "[bold blue]●[/]" if not is_read else ""
        imp = "[bold red]![/]" if str(importance).lower() == "high" else ""
        att = "📎" if has_attachments else ""

        sender = str(msg.sender) if msg.sender else ""
        date = msg.received.strftime("%Y-%m-%d %H:%M") if msg.received else ""
        table.add_row(
            status, imp, att, sender, msg.subject or "", date, msg.object_id or ""
        )

    console.print(table)


def print_mail_detail(msg) -> None:
    sender = str(msg.sender) if msg.sender else "Unknown"
    to_list = ", ".join(str(r) for r in (msg.to or []))
    cc_list = ", ".join(str(r) for r in (msg.cc or []))
    date = msg.received.strftime("%Y-%m-%d %H:%M") if msg.received else ""

    header = f"[bold]From:[/] {sender}\n" f"[bold]To:[/] {to_list}\n"
    if cc_list:
        header += f"[bold]CC:[/] {cc_list}\n"
    header += f"[bold]Date:[/] {date}"

    body = msg.body or "(empty)"
    if _looks_like_html(body):
        body = _strip_html(body)

    console.print(
        Panel(header, title=msg.subject or "(no subject)", border_style="blue")
    )
    console.print(body)


# ── Calendar ───────────────────────────────────────────────────


def print_event_table(events: list) -> None:
    table = Table(title="Events", show_lines=False)
    table.add_column("Subject", style="white")
    table.add_column("Start", style="green", max_width=20)
    table.add_column("End", style="green", max_width=20)
    table.add_column("Location", style="cyan", max_width=25)
    table.add_column("Info", style="yellow", max_width=20)
    table.add_column("ID", style="dim", max_width=36)

    for ev in events:
        start = ev.start.strftime("%Y-%m-%d %H:%M") if ev.start else ""
        end = ev.end.strftime("%Y-%m-%d %H:%M") if ev.end else ""
        location = (
            ev.location.get("displayName", "")
            if isinstance(ev.location, dict)
            else str(ev.location or "")
        )

        info_parts = []
        if getattr(ev, "is_all_day", False):
            info_parts.append("All-day")
        if getattr(ev, "recurrence", None) is not None:
            info_parts.append("Recurring")
        info = ", ".join(info_parts)

        table.add_row(
            ev.subject or "", start, end, location, info, ev.object_id or ""
        )

    console.print(table)


def _format_attendee(att) -> str:
    """Format a single attendee for display."""
    if isinstance(att, dict):
        email_info = att.get("emailAddress", {})
        name = email_info.get("name", "")
        address = email_info.get("address", "")
        status = att.get("status", {}).get("response", "")
    else:
        name = getattr(att, "name", "")
        address = getattr(att, "address", "")
        status = getattr(att, "response_status", "")

    label = f"{name} <{address}>" if name and address else name or address or "?"
    if status:
        label += f" ({status})"
    return label


def print_event_detail(event) -> None:
    start = event.start.strftime("%Y-%m-%d %H:%M") if event.start else ""
    end = event.end.strftime("%Y-%m-%d %H:%M") if event.end else ""
    location = (
        event.location.get("displayName", "")
        if isinstance(event.location, dict)
        else str(event.location or "")
    )

    header = (
        f"[bold]Start:[/] {start}\n"
        f"[bold]End:[/] {end}\n"
        f"[bold]Location:[/] {location}"
    )

    organizer = getattr(event, "organizer", None)
    if organizer:
        if isinstance(organizer, dict):
            org_email = organizer.get("emailAddress", {})
            org_name = org_email.get("name", "")
            org_addr = org_email.get("address", "")
            org_display = (
                f"{org_name} <{org_addr}>" if org_name and org_addr else org_name or org_addr
            )
        else:
            org_display = str(organizer)
        header += f"\n[bold]Organizer:[/] {org_display}"

    is_all_day = getattr(event, "is_all_day", False)
    if is_all_day:
        header += "\n[bold]All-day:[/] Yes"

    recurrence = getattr(event, "recurrence", None)
    if recurrence is not None:
        header += f"\n[bold]Recurring:[/] {recurrence}"

    attendees = getattr(event, "attendees", []) or []
    if attendees:
        header += "\n[bold]Attendees:[/]"
        for att in attendees:
            header += f"\n  \u2022 {_format_attendee(att)}"

    body = event.body or "(no description)"
    if _looks_like_html(body):
        body = _strip_html(body)

    console.print(
        Panel(header, title=event.subject or "(no subject)", border_style="green")
    )
    console.print(body)
