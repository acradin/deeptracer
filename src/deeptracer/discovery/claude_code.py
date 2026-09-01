"""Discover Claude Code session transcript files."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from deeptracer.discovery.models import SessionRecord

_AGENT_ID = "claude-code"


def default_claude_config_dir() -> Path:
    """
    Return the default Claude Code config directory (~/.claude).

    Args:
        None

    Returns:
        Path.home() / ".claude" on every OS.

    Raises:
        None
    """
    return Path.home() / ".claude"


def claude_projects_roots(*, require_existing: bool = True) -> list[Path]:
    """
    Auto-detect Claude Code `projects` directories.

    Args:
        require_existing: If True, skip paths that are not directories.
            False keeps candidates so the CLI can show where it looked.

    Returns:
        Unique paths, CLAUDE_CONFIG_DIR/projects first when that env is set.

    Raises:
        None
    """
    candidates: list[Path] = []

    # Logs follow CLAUDE_CONFIG_DIR, then ~/.claude — not the CLI install path.
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if config_dir:
        candidates.append(Path(config_dir).expanduser() / "projects")
    candidates.append(default_claude_config_dir() / "projects")

    # Dedupe by resolved path so CLAUDE_CONFIG_DIR=~/.claude is listed once.
    unique: dict[Path, Path] = {}
    for path in candidates:
        try:
            key = path.resolve()
        except OSError:
            key = path
        if key in unique:
            continue
        if require_existing and not path.is_dir():
            continue
        unique[key] = path
    return list(unique.values())


def decode_project_dir_name(name: str) -> str:
    """
    Decode a project folder name into a display path.

    Args:
        name: Directory name under `projects/`, not a full filesystem path.

    Returns:
        Best-effort cwd string. Original hyphens, dots, and spaces are lost.

    Raises:
        None
    """
    # Windows: C:\Users\Brahm\Git → C--Users-Brahm-Git
    if len(name) >= 3 and name[0].isalpha() and name[1:3] == "--":
        drive = name[0].upper()
        rest = name[3:].replace("-", "\\")
        return f"{drive}:\\{rest}"

    # POSIX: /Users/philipp/dev → -Users-philipp-dev
    if name.startswith("-"):
        return "/" + name[1:].replace("-", "/")

    # CLAUDE_CODE_PROJECT_DIR_NAME (for example "work") is not encoded.
    return name


def discover_claude_code_sessions(root: Path | None = None) -> list[SessionRecord]:
    """
    Collect top-level session jsonl files, newest first.

    Args:
        root: If set, scan only this `projects` directory. If omitted,
            scan every auto-detected root from claude_projects_roots().

    Returns:
        SessionRecord list. Metadata only; jsonl bodies are not parsed.

    Raises:
        OSError: If a projects tree exists but cannot be listed or a jsonl
            file cannot be stat'd.
    """
    roots = [root] if root is not None else claude_projects_roots()
    sessions: list[SessionRecord] = []
    seen_logs: set[Path] = set()
    for projects in roots:
        sessions.extend(_sessions_in_projects_dir(projects, seen_logs))
    sessions.sort(key=lambda item: item.modified_at, reverse=True)
    return sessions


def _sessions_in_projects_dir(
    projects: Path, seen_logs: set[Path]
) -> list[SessionRecord]:
    """
    Collect sessions from one `projects` directory.

    Args:
        projects: A `.../projects` directory.
        seen_logs: Resolved jsonl paths already collected from other roots.

    Returns:
        SessionRecord values found under this tree.

    Raises:
        OSError: If `projects` is a directory but iterdir(), glob, or stat
            fails. Path.resolve() errors are caught and the unresolved path
            is used instead.
    """
    # Skip a missing or non-directory root (for example an explicit `root=`).
    if not projects.is_dir():
        return []

    sessions: list[SessionRecord] = []
    for project_dir in projects.iterdir():

        # Skip stray files sitting next to project folders.
        if not project_dir.is_dir():
            continue
        project_label = decode_project_dir_name(project_dir.name)

        # Only `projects/<dir>/*.jsonl` — not nested subagent transcripts.
        for log_path in project_dir.glob("*.jsonl"):
            try:
                log_key = log_path.resolve()
            except OSError:
                log_key = log_path
            if log_key in seen_logs:
                continue
            seen_logs.add(log_key)
            stat = log_path.stat()
            sessions.append(
                SessionRecord(
                    agent_id=_AGENT_ID,
                    session_id=log_path.stem,
                    log_path=log_path,
                    project_label=project_label,
                    modified_at=datetime.fromtimestamp(
                        stat.st_mtime, tz=timezone.utc
                    ).astimezone(),
                    size_bytes=stat.st_size,
                )
            )
    return sessions
