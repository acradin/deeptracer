from __future__ import annotations

import pytest

from deeptracer.web.server import run_foreground


def test_run_foreground_binds_loopback(monkeypatch: pytest.MonkeyPatch) -> None:
    """The foreground server listens on 127.0.0.1 with the given port."""
    captured: dict[str, object] = {}

    def fake_run(app: object, **kwargs: object) -> None:
        captured["host"] = kwargs["host"]
        captured["port"] = kwargs["port"]

    monkeypatch.setattr("deeptracer.web.server.uvicorn.run", fake_run)
    run_foreground(port=9999, open_browser=False)
    assert captured == {"host": "127.0.0.1", "port": 9999}
