from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.table import Table

from deeptracer import __version__
from deeptracer.discovery import claude_projects_roots, discover_claude_code_sessions


def _configure_stdio() -> None:
    """
    Force UTF-8 on stdout/stderr so Windows consoles do not scramble
    Unicode CLI text.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


@click.group()
@click.version_option(version=__version__, prog_name="deeptracer")
def cli() -> None:
    """Debug AI agent failures at the semantic-span level."""


@cli.command()
def setup() -> None:
    """Register the user daemon and enable start-on-login."""
    _not_implemented("setup")


@cli.command()
def start() -> None:
    """Start the background daemon."""
    _not_implemented("start")


@cli.command()
def stop() -> None:
    """Stop the daemon."""
    _not_implemented("stop")


@cli.command()
def status() -> None:
    """Show daemon status (port / pid)."""
    _not_implemented("status")


@cli.command()
def serve() -> None:
    """Run the local web UI in the foreground."""
    _not_implemented("serve")


@cli.command("list")
def list_sessions() -> None:
    """List discovered agent sessions."""
    sessions = discover_claude_code_sessions()
    console = Console()
    if not sessions:
        looked = claude_projects_roots(require_existing=False)
        locations = "\n".join(f"  {path}" for path in looked)
        console.print("No Claude Code sessions found. Looked in:")
        console.print(locations)
        return

    table = Table(title=f"Claude Code sessions ({len(sessions)})")
    table.add_column("Session ID", no_wrap=True)
    table.add_column("Project")
    table.add_column("Modified", no_wrap=True)
    for session in sessions:
        table.add_row(
            session.session_id,
            session.project_label,
            session.modified_at.strftime("%Y-%m-%d %H:%M"),
        )
    console.print(table)


@cli.command()
@click.argument("session_id")
def open(session_id: str) -> None:
    """Open a session graph in the browser."""
    _not_implemented("open")


def _not_implemented(name: str) -> None:
    """
    Abort a CLI command that is still a stub.

    Args:
        name: Subcommand name shown in the error.

    Returns:
        None

    Raises:
        click.ClickException: Always.
    """
    raise click.ClickException(f"'{name}' is not implemented yet.")


def main() -> None:
    """
    Console-script entry point wired in pyproject.toml.

    Args:
        None

    Returns:
        None

    Raises:
        click.ClickException: From stub commands.
        SystemExit: Click exits after --help, --version, or a usage error.
    """
    _configure_stdio()
    cli()
