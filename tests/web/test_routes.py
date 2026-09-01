from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from deeptracer.discovery.models import SessionRecord
from deeptracer.web.app import create_app


def test_health_ok() -> None:
    """The local UI process reports it is alive."""
    client = TestClient(create_app())
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_sessions_serializes_records(monkeypatch: pytest.MonkeyPatch) -> None:
    """The sessions API returns discovery records as JSON."""
    record = SessionRecord(
        agent_id="claude-code",
        session_id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        log_path=Path("/tmp/session.jsonl"),
        project_label="/Users/philipp/dev",
        modified_at=datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc),
        size_bytes=2048,
    )
    monkeypatch.setattr(
        "deeptracer.web.routes.discover_claude_code_sessions",
        lambda: [record],
    )
    client = TestClient(create_app())
    payload = client.get("/api/sessions").json()
    assert payload == {
        "sessions": [
            {
                "agent_id": "claude-code",
                "session_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "project_label": "/Users/philipp/dev",
                "log_path": str(Path("/tmp/session.jsonl")),
                "modified_at": "2026-04-01T12:00:00+00:00",
                "size_bytes": 2048,
            }
        ]
    }


def test_api_sessions_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty listing is an empty sessions array."""
    monkeypatch.setattr(
        "deeptracer.web.routes.discover_claude_code_sessions",
        lambda: [],
    )
    client = TestClient(create_app())
    assert client.get("/api/sessions").json() == {"sessions": []}
