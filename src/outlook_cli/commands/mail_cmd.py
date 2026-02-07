"""Mail commands: search, read, send, reply, mark."""

from datetime import datetime
from typing import Optional

import typer

from outlook_cli.auth import get_account
from outlook_cli.display import console, print_error, print_mail_detail, print_mail_table, print_success

app = typer.Typer(help="Read and send email.")


@app.command()
def search(
    query: Optional[str] = typer.Argument(None, help="Search terms to filter messages"),
    folder: str = typer.Option("Inbox", "--folder", help="Folder name to search in"),
    limit: int = typer.Option(25, "--limit", help="Maximum number of messages to return"),
    sender: Optional[str] = typer.Option(None, "--from", "--sender", help="Filter by sender email address"),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="Messages received after this date (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="Messages received before this date (YYYY-MM-DD)"),
    unread: bool = typer.Option(False, "--unread", help="Show only unread messages"),
    important: bool = typer.Option(False, "--important", help="Show only high-importance messages"),
    has_attachments: bool = typer.Option(False, "--has-attachments", help="Show only messages with attachments"),
) -> None:
    """Search for messages in a mail folder."""
    account = get_account()
    mailbox = account.mailbox()

    if folder == "Inbox":
        mail_folder = mailbox.inbox_folder()
    else:
        mail_folder = mailbox.get_folder(folder_name=folder)
        if mail_folder is None:
            print_error(f"Folder not found: {folder}")
            raise typer.Exit(1)

    has_filters = any([sender, start_date, end_date, unread, important, has_attachments])

    params = {"limit": limit}
    if query:
        params["query"] = mailbox.q().search(query)
        if has_filters:
            console.print(
                "[bold yellow]Warning:[/] Filters are ignored when using text search. "
                "Microsoft Graph API does not support combining search with OData filters."
            )
    elif has_filters:
        odata_query = mailbox.new_query()
        first_filter = True

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            clause = odata_query.on_attribute("receivedDateTime") if first_filter else odata_query.chain("and").on_attribute("receivedDateTime")
            clause.greater_equal(start_dt)
            first_filter = False

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            clause = odata_query.on_attribute("receivedDateTime") if first_filter else odata_query.chain("and").on_attribute("receivedDateTime")
            clause.less_equal(end_dt)
            first_filter = False

        if unread:
            clause = odata_query.on_attribute("isRead") if first_filter else odata_query.chain("and").on_attribute("isRead")
            clause.equals(False)
            first_filter = False

        if important:
            clause = odata_query.on_attribute("importance") if first_filter else odata_query.chain("and").on_attribute("importance")
            clause.equals("high")
            first_filter = False

        if has_attachments:
            clause = odata_query.on_attribute("hasAttachments") if first_filter else odata_query.chain("and").on_attribute("hasAttachments")
            clause.equals(True)
            first_filter = False

        if sender:
            clause = odata_query.on_attribute("from/emailAddress/address") if first_filter else odata_query.chain("and").on_attribute("from/emailAddress/address")
            clause.contains(sender)
            first_filter = False

        params["query"] = odata_query

    messages = list(mail_folder.get_messages(**params))

    if not messages:
        console.print("No messages found.")
        return

    print_mail_table(messages)


@app.command()
def read(
    message_id: str = typer.Argument(..., help="ID of the message to read"),
) -> None:
    """Read a single message by ID."""
    account = get_account()
    mailbox = account.mailbox()

    msg = mailbox.get_message(object_id=message_id)
    if msg is None:
        print_error(f"Message not found: {message_id}")
        raise typer.Exit(1)

    print_mail_detail(msg)


@app.command()
def send(
    to: str = typer.Option(..., "--to", help="Recipient email address"),
    subject: str = typer.Option(..., "--subject", help="Message subject"),
    body: str = typer.Option(..., "--body", help="Message body text"),
    cc: Optional[str] = typer.Option(None, "--cc", help="CC email address"),
) -> None:
    """Compose and send a new message."""
    account = get_account()
    new_message = account.new_message()

    new_message.to.add(to)
    if cc:
        new_message.cc.add(cc)
    new_message.subject = subject
    new_message.body = body

    if new_message.send():
        print_success("Message sent.")
    else:
        print_error("Failed to send message.")
        raise typer.Exit(1)


@app.command()
def reply(
    message_id: str = typer.Argument(..., help="ID of the message to reply to"),
    body: str = typer.Option(..., "--body", help="Reply body text"),
    reply_all: bool = typer.Option(False, "--reply-all", help="Reply to all recipients"),
) -> None:
    """Reply to a message by ID."""
    account = get_account()
    mailbox = account.mailbox()

    msg = mailbox.get_message(object_id=message_id)
    if msg is None:
        print_error(f"Message not found: {message_id}")
        raise typer.Exit(1)

    reply_msg = msg.reply_all() if reply_all else msg.reply()
    reply_msg.body = body
    reply_msg.send()

    target = "all recipients" if reply_all else str(msg.sender)
    print_success(f"Reply sent to {target}.")


@app.command()
def mark(
    message_id: str = typer.Argument(..., help="ID of the message to mark"),
    read_flag: bool = typer.Option(True, "--read/--unread", help="Mark as read (default) or unread"),
) -> None:
    """Mark a message as read or unread."""
    account = get_account()
    mailbox = account.mailbox()

    msg = mailbox.get_message(object_id=message_id)
    if msg is None:
        print_error(f"Message not found: {message_id}")
        raise typer.Exit(1)

    if read_flag:
        msg.mark_as_read()
        print_success("Message marked as read.")
    else:
        msg.mark_as_unread()
        print_success("Message marked as unread.")
