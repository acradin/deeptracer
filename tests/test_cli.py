from __future__ import annotations

import pytest
from click.testing import CliRunner

from deeptracer.cli import cli


def test_serve_forwards_port_and_skips_browser(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """serve starts the foreground UI with the given port and --no-open."""
    captured: dict[str, object] = {}

    def fake_run(*, port: int, open_browser: bool) -> None:
        captured["port"] = port
        captured["open_browser"] = open_browser

    monkeypatch.setattr("deeptracer.web.server.run_foreground", fake_run)
    result = CliRunner().invoke(cli, ["serve", "--port", "9999", "--no-open"])
    assert result.exit_code == 0
    assert captured == {"port": 9999, "open_browser": False}
