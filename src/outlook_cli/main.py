"""CLI for Microsoft Outlook — main app assembly."""

import typer

from outlook_cli.commands import auth_cmd, cal_cmd, mail_cmd


def version_callback(value: bool) -> None:
    if value:
        print("outlook-cli 0.1.0")
        raise typer.Exit()


app = typer.Typer(help="CLI for Microsoft Outlook")
app.add_typer(auth_cmd.app, name="auth", help="Authentication commands")
app.add_typer(mail_cmd.app, name="mail", help="Email commands")
app.add_typer(cal_cmd.app, name="cal", help="Calendar commands")


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
) -> None:
    pass
