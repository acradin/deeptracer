from __future__ import annotations

from fastapi.testclient import TestClient

from deeptracer.web.app import create_app


def test_index_serves_picker_html() -> None:
    """The root path returns the session-picker page."""
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "deeptracer" in response.text


def test_static_is_mounted() -> None:
    """create_app mounts the packaged UI files at /static."""
    client = TestClient(create_app())
    assert client.get("/static/picker.css").status_code == 200
