"""Settings for the local web UI."""

from __future__ import annotations

from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
