from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class SessionRecord:
    """Pointer to a session transcript on disk, not a parsed event or span."""

    agent_id: str              # Which agent wrote the log (currently "claude-code")
    session_id: str            # jsonl file stem (Claude Code session UUID)
    log_path: Path             # Path to the transcript file
    project_label: str         # Decoded or custom project folder name for display
    modified_at: datetime      # Local mtime of the transcript file
    size_bytes: int            # File size; unused by list, kept for later UI
