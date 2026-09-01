"""Foreground HTTP process for the local UI."""

from __future__ import annotations

import threading
import webbrowser

import uvicorn

from deeptracer.web.app import create_app
from deeptracer.web.config import DEFAULT_HOST, DEFAULT_PORT


def run_foreground(*, port: int = DEFAULT_PORT, open_browser: bool = True) -> None:
    """
    Serve the picker on 127.0.0.1 until interrupted.

    Args:
        port: TCP port. Host is always loopback.
        open_browser: If True, open the UI after a short delay.

    Returns:
        None

    Raises:
        SystemExit: uvicorn exits when the port cannot be bound.
    """
    host = DEFAULT_HOST
    url = f"http://{host}:{port}/"
    if open_browser:

        # Delay so the first request does not hit a still-binding socket.
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    uvicorn.run(create_app(), host=host, port=port, log_level="info")
