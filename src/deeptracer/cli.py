from __future__ import annotations

import sys

import click

from deeptracer import __version__
from deeptracer.web.config import DEFAULT_PORT


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
@click.option("--port", default=DEFAULT_PORT, show_default=True, type=int)
@click.option("--open/--no-open", "open_browser", default=True, show_default=True)
def serve(port: int, open_browser: bool) -> None:
    """Run the local web UI in the foreground."""
    from deeptracer.web.server import run_foreground

    run_foreground(port=port, open_browser=open_browser)


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
