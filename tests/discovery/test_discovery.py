from __future__ import annotations

import os
from pathlib import Path

import pytest

from deeptracer.discovery.claude_code import (
    claude_projects_roots,
    decode_project_dir_name,
    discover_claude_code_sessions,
)


def test_decode_posix_project_dir() -> None:
    """macOS/Linux encoded folder names decode to a POSIX display path."""
    assert decode_project_dir_name("-Users-philipp-dev") == "/Users/philipp/dev"
    assert (
        decode_project_dir_name("-home-you-work-myproject")
        == "/home/you/work/myproject"
    )


def test_decode_windows_project_dir() -> None:
    """Windows encoded folder names decode to a drive-letter display path."""
    assert decode_project_dir_name("C--Users-Brahm-Git") == r"C:\Users\Brahm\Git"


def test_decode_custom_project_dir_name() -> None:
    """Unencoded CLAUDE_CODE_PROJECT_DIR_NAME labels are returned unchanged."""
    assert decode_project_dir_name("work") == "work"


def test_discover_lists_jsonl_newest_first(tmp_path: Path) -> None:
    """Session listing returns jsonl files newest-first with decoded project labels."""
    older = tmp_path / "C--Users-acrad-Vault"
    newer = tmp_path / "-Users-philipp-dev"
    older.mkdir()
    newer.mkdir()
    old_log = older / "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa.jsonl"
    new_log = newer / "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb.jsonl"
    old_log.write_text("{}\n", encoding="utf-8")
    new_log.write_text("{}\n", encoding="utf-8")
    os.utime(old_log, (1_700_000_000, 1_700_000_000))
    os.utime(new_log, (1_800_000_000, 1_800_000_000))

    sessions = discover_claude_code_sessions(tmp_path)

    assert [item.session_id for item in sessions] == [
        "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    ]
    assert sessions[0].agent_id == "claude-code"
    assert sessions[0].project_label == "/Users/philipp/dev"
    assert sessions[1].project_label == r"C:\Users\acrad\Vault"


def test_discover_missing_root(tmp_path: Path) -> None:
    """A missing projects directory yields an empty session list."""
    assert discover_claude_code_sessions(tmp_path / "missing") == []


def test_roots_use_claude_config_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CLAUDE_CONFIG_DIR is preferred over the default ~/.claude location."""
    custom = tmp_path / "srv" / "tenant" / "projects"
    custom.mkdir(parents=True)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "srv" / "tenant"))
    monkeypatch.setattr(
        "deeptracer.discovery.claude_code.default_claude_config_dir",
        lambda: tmp_path / "unused-home" / ".claude",
    )
    roots = claude_projects_roots()
    assert [path.resolve() for path in roots] == [custom.resolve()]


def test_roots_keep_missing_candidates_when_not_required(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """require_existing=False still returns planned paths that are not on disk yet."""
    missing_home = tmp_path / "no-home" / ".claude"
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    monkeypatch.setattr(
        "deeptracer.discovery.claude_code.default_claude_config_dir",
        lambda: missing_home,
    )
    existing = claude_projects_roots(require_existing=True)
    planned = claude_projects_roots(require_existing=False)
    assert existing == []
    assert planned == [missing_home / "projects"]
