import sys
from pathlib import Path

from pytest import MonkeyPatch

from desktop_app.constants import DEFAULT_LOG_FILE_PATH
from desktop_app.infrastructure.logger.paths import resolve_log_file_path


def test_absolute_log_path_is_preserved(tmp_path: Path) -> None:
    absolute_path = tmp_path / "custom" / "app.log"

    resolved_path = resolve_log_file_path(
        log_file_path=absolute_path,
        frozen_executable=True,
        executable_path=tmp_path / "dist" / "app.exe",
        working_directory=tmp_path / "ignored",
    )

    assert resolved_path == absolute_path


def test_relative_log_path_uses_explicit_working_directory(
    tmp_path: Path,
) -> None:
    working_directory = tmp_path / "project"

    resolved_path = resolve_log_file_path(
        log_file_path="logs/app.log",
        frozen_executable=False,
        working_directory=working_directory,
    )

    assert resolved_path == working_directory.resolve() / "logs" / "app.log"


def test_relative_log_path_uses_current_working_directory(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    resolved_path = resolve_log_file_path(frozen_executable=False)

    assert resolved_path == tmp_path.resolve() / DEFAULT_LOG_FILE_PATH


def test_relative_log_path_uses_explicit_executable_directory(
    tmp_path: Path,
) -> None:
    executable_path = tmp_path / "dist" / "app.exe"

    resolved_path = resolve_log_file_path(
        log_file_path=Path("logs") / "app.log",
        frozen_executable=True,
        executable_path=executable_path,
        working_directory=tmp_path / "ignored",
    )

    assert resolved_path == executable_path.resolve().parent / "logs" / "app.log"


def test_relative_log_path_uses_sys_executable_when_executable_path_is_omitted(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    executable_path = tmp_path / "dist" / "app.exe"
    monkeypatch.setattr(sys, "executable", str(executable_path))

    resolved_path = resolve_log_file_path(
        log_file_path="logs/app.log",
        frozen_executable=True,
    )

    assert resolved_path == executable_path.resolve().parent / "logs" / "app.log"


def test_omitted_frozen_state_reads_sys_frozen(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    executable_path = tmp_path / "dist" / "app.exe"
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    resolved_path = resolve_log_file_path(
        log_file_path="app.log",
        executable_path=executable_path,
    )

    assert resolved_path == executable_path.resolve().parent / "app.log"


def test_omitted_frozen_state_defaults_to_not_frozen(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delattr(sys, "frozen", raising=False)

    resolved_path = resolve_log_file_path(
        log_file_path="app.log",
        working_directory=tmp_path,
    )

    assert resolved_path == tmp_path.resolve() / "app.log"
