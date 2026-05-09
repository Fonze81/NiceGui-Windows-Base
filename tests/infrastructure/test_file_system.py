from __future__ import annotations

from os import PathLike
from pathlib import Path

import pytest

from desktop_app.infrastructure.file_system import atomic_write_text, ensure_parent_dir

type _ReplacementTarget = str | PathLike[str]


def test_ensure_parent_dir_creates_missing_parent_directories(
    tmp_path: Path,
) -> None:
    """Ensure missing parent directories are created for a file path."""
    file_path = tmp_path / "config" / "app" / "settings.toml"

    ensure_parent_dir(file_path)

    assert file_path.parent.is_dir()
    assert not file_path.exists()


def test_ensure_parent_dir_accepts_string_paths(tmp_path: Path) -> None:
    """Ensure string paths are accepted by the helper."""
    file_path = tmp_path / "logs" / "app.log"

    ensure_parent_dir(str(file_path))

    assert file_path.parent.is_dir()
    assert not file_path.exists()


def test_atomic_write_text_creates_parent_directory_and_writes_file(
    tmp_path: Path,
) -> None:
    """Ensure text is written after creating the missing parent directory."""
    file_path = tmp_path / "settings" / "app.toml"

    atomic_write_text(file_path, "theme = 'dark'\n")

    assert file_path.read_text(encoding="utf-8") == "theme = 'dark'\n"
    assert not file_path.with_name("app.toml.tmp").exists()


def test_atomic_write_text_accepts_string_paths(tmp_path: Path) -> None:
    """Ensure atomic writes accept string destination paths."""
    file_path = tmp_path / "output" / "result.txt"

    atomic_write_text(str(file_path), "done\n")

    assert file_path.read_text(encoding="utf-8") == "done\n"


def test_atomic_write_text_replaces_existing_file_content(tmp_path: Path) -> None:
    """Ensure an existing file is replaced with the new content."""
    file_path = tmp_path / "state.txt"
    file_path.write_text("old\n", encoding="utf-8")

    atomic_write_text(file_path, "new\n")

    assert file_path.read_text(encoding="utf-8") == "new\n"


def test_atomic_write_text_uses_selected_encoding(tmp_path: Path) -> None:
    """Ensure the configured text encoding is used when writing."""
    file_path = tmp_path / "message.txt"
    content = "ação concluída\n"

    atomic_write_text(file_path, content, encoding="utf-16")

    assert file_path.read_text(encoding="utf-16") == content


def test_atomic_write_text_removes_temporary_file_when_replace_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure temporary files are removed when final replacement fails."""
    file_path = tmp_path / "settings.toml"
    temporary_path = file_path.with_name("settings.toml.tmp")
    original_replace = Path.replace

    file_path.write_text("enabled = false\n", encoding="utf-8")

    def failing_replace(self: Path, target: _ReplacementTarget) -> Path:
        if self == temporary_path:
            raise OSError("simulated replace failure")

        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", failing_replace)

    with pytest.raises(OSError, match="simulated replace failure"):
        atomic_write_text(file_path, "enabled = true\n")

    assert file_path.read_text(encoding="utf-8") == "enabled = false\n"
    assert not temporary_path.exists()
