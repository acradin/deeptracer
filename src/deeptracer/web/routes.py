"""HTTP route handlers for the local UI."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import FileResponse

from deeptracer import __version__
from deeptracer.discovery import discover_claude_code_sessions
from deeptracer.discovery.models import SessionRecord
from deeptracer.web.config import STATIC_DIR

router = APIRouter()


def _session_json(session: SessionRecord) -> dict[str, object]:
    """
    Turn one discovery record into JSON-safe primitives.

    Args:
        session: Listing metadata from discovery.

    Returns:
        Dict with a string path and an ISO-8601 timestamp.

    Raises:
        None
    """
    return {
        "agent_id": session.agent_id,
        "session_id": session.session_id,
        "project_label": session.project_label,
        "log_path": str(session.log_path),
        "modified_at": session.modified_at.isoformat(),
        "size_bytes": session.size_bytes,
    }


@router.get("/api/health")
def health() -> dict[str, str]:
    """
    Liveness probe for the local UI process.

    Args:
        None

    Returns:
        Status and package version.

    Raises:
        None
    """
    return {"status": "ok", "version": __version__}


@router.get("/api/sessions")
def api_sessions() -> dict[str, object]:
    """
    List Claude Code sessions.

    Args:
        None

    Returns:
        Sessions newest-first.

    Raises:
        OSError: If a projects tree exists but cannot be listed.
    """
    sessions = discover_claude_code_sessions()
    return {
        "sessions": [_session_json(item) for item in sessions],
    }


@router.get("/")
def index() -> FileResponse:
    """
    Serve the session-picker HTML page.

    Args:
        None

    Returns:
        The packaged picker page.

    Raises:
        None
    """
    return FileResponse(STATIC_DIR / "index.html")
