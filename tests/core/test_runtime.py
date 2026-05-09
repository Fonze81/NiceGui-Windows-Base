# -----------------------------------------------------------------------------
# File: tests/core/test_runtime.py
# Purpose:
# Validate runtime detection helpers.
# Behavior:
# Exercises execution-mode detection, runtime root resolution, and startup
# message formatting without relying on the real process command line.
# Notes:
# Tests inject runtime markers explicitly to keep PyInstaller and CLI behavior
# deterministic in normal test execution.
# -----------------------------------------------------------------------------

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from desktop_app.core import runtime


def test_is_frozen_executable_uses_explicit_value() -> None:
    """Explicit frozen values must override the real process state."""
    assert runtime.is_frozen_executable(frozen=True) is True
    assert runtime.is_frozen_executable(frozen=False) is False


def test_is_frozen_executable_reads_sys_frozen(monkeypatch: pytest.MonkeyPatch) -> None:
    """The default frozen state must come from sys.frozen."""
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    assert runtime.is_frozen_executable() is True


def test_is_frozen_executable_defaults_to_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing sys.frozen must be treated as normal Python execution."""
    monkeypatch.delattr(sys, "frozen", raising=False)

    assert runtime.is_frozen_executable() is False


def test_get_runtime_root_uses_explicit_meipass(tmp_path: Path) -> None:
    """An explicit PyInstaller extraction directory has highest priority."""
    meipass_dir = tmp_path / "pyinstaller-extract"
    meipass_dir.mkdir()

    assert runtime.get_runtime_root(meipass=meipass_dir) == meipass_dir.resolve()


def test_get_runtime_root_reads_sys_meipass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When no explicit value is provided, sys._MEIPASS must be supported."""
    meipass_dir = tmp_path / "sys-meipass"
    meipass_dir.mkdir()
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass_dir), raising=False)

    assert runtime.get_runtime_root() == meipass_dir.resolve()


def test_get_runtime_root_uses_frozen_executable_folder(tmp_path: Path) -> None:
    """Frozen execution must resolve files relative to the executable folder."""
    executable_path = tmp_path / "dist" / "nicegui-windows-base.exe"
    executable_path.parent.mkdir()
    executable_path.touch()

    result = runtime.get_runtime_root(executable=executable_path, frozen=True)

    assert result == executable_path.resolve().parent


def test_get_runtime_root_uses_package_root_for_normal_execution(
    tmp_path: Path,
) -> None:
    """Normal execution must resolve to the package root from the module file."""
    module_file = tmp_path / "src" / "desktop_app" / "core" / "runtime.py"
    module_file.parent.mkdir(parents=True)
    module_file.touch()

    result = runtime.get_runtime_root(module_file=module_file, frozen=False)

    assert result == (tmp_path / "src" / "desktop_app").resolve()


def test_get_nicegui_modes_returns_web_reload_for_development() -> None:
    """Development mode must use browser mode with reload enabled."""
    assert runtime.get_nicegui_modes(development_mode=True) == (False, True)


def test_get_nicegui_modes_returns_native_without_reload_for_normal_use() -> None:
    """Normal mode must use native desktop mode with reload disabled."""
    assert runtime.get_nicegui_modes(development_mode=False) == (True, False)


def test_detect_startup_source_prioritizes_development_mode() -> None:
    """Development mode must be classified before other runtime hints."""
    assert (
        runtime.detect_startup_source(development_mode=True, argv=[], frozen=True)
        == "dev_run.py"
    )


def test_detect_startup_source_detects_packaged_execution() -> None:
    """Frozen execution must be reported as a packaged executable."""
    assert (
        runtime.detect_startup_source(
            development_mode=False, argv=["app.py"], frozen=True
        )
        == "package"
    )


def test_detect_startup_source_returns_unknown_for_empty_argv() -> None:
    """An empty argv sequence must not crash startup source detection."""
    assert runtime.detect_startup_source(development_mode=False, argv=[]) == (
        "unknown source"
    )


def test_detect_startup_source_returns_unknown_for_blank_entry() -> None:
    """A blank argv entry must be treated as an unknown startup source."""
    assert runtime.detect_startup_source(development_mode=False, argv=["  "]) == (
        "unknown source"
    )


def test_detect_startup_source_reads_sys_argv(monkeypatch: pytest.MonkeyPatch) -> None:
    """When argv is omitted, startup detection must read sys.argv."""
    monkeypatch.setattr(sys, "argv", ["custom-runner.py"])

    assert runtime.detect_startup_source(development_mode=False) == "custom-runner.py"


def test_detect_startup_source_detects_pyproject_command() -> None:
    """Configured console script names must be mapped to pyproject command."""
    result = runtime.detect_startup_source(
        development_mode=False,
        argv=[r"C:\Apps\NiceGui-Windows-Base.EXE"],
        pyproject_command_names=("nicegui-windows-base.exe",),
    )

    assert result == "pyproject command"


def test_detect_startup_source_detects_module_execution() -> None:
    """__main__.py must be mapped to module execution."""
    result = runtime.detect_startup_source(
        development_mode=False,
        argv=["/project/src/desktop_app/__main__.py"],
    )

    assert result == "module"


def test_detect_startup_source_detects_direct_script_execution() -> None:
    """app.py must be mapped to direct script execution."""
    result = runtime.detect_startup_source(
        development_mode=False,
        argv=[r"C:\project\src\desktop_app\app.py"],
    )

    assert result == "script"


def test_detect_startup_source_returns_unknown_entry_name() -> None:
    """Unknown executable names must be returned as normalized names."""
    result = runtime.detect_startup_source(
        development_mode=False,
        argv=["/tools/CustomRunner.PY"],
    )

    assert result == "customrunner.py"


def test_describe_startup_source_returns_known_description() -> None:
    """Known startup sources must be converted to readable descriptions."""
    assert runtime.describe_startup_source("package") == "the packaged executable"


def test_describe_startup_source_keeps_unknown_value() -> None:
    """Unknown startup sources must remain readable as originally detected."""
    assert runtime.describe_startup_source("customrunner.py") == "customrunner.py"


@pytest.mark.parametrize(
    ("native_mode", "reload_enabled", "expected"),
    [
        (True, False, "native mode with reload disabled"),
        (False, True, "web mode with reload enabled"),
    ],
)
def test_describe_runtime_mode(
    native_mode: bool,
    reload_enabled: bool,
    expected: str,
) -> None:
    """Runtime mode descriptions must combine UI mode and reload state."""
    assert (
        runtime.describe_runtime_mode(
            native_mode=native_mode,
            reload_enabled=reload_enabled,
        )
        == expected
    )


def test_build_startup_message_uses_known_source_description() -> None:
    """Startup messages must use friendly descriptions for known sources."""
    result = runtime.build_startup_message(
        startup_source="dev_run.py",
        native_mode=False,
        reload_enabled=True,
        application_title="Test App",
    )

    assert result == (
        "Test App is starting from the development runner "
        "in web mode with reload enabled."
    )


def test_build_startup_message_keeps_unknown_source() -> None:
    """Startup messages must keep unknown source names visible for diagnostics."""
    result = runtime.build_startup_message(
        startup_source="customrunner.py",
        native_mode=True,
        reload_enabled=False,
        application_title="Test App",
    )

    assert result == (
        "Test App is starting from customrunner.py in native mode with reload disabled."
    )


def test_get_startup_message_combines_detection_and_mode_selection() -> None:
    """The high-level startup helper must compose all runtime diagnostics."""
    result = runtime.get_startup_message(
        development_mode=False,
        argv=["__main__.py"],
        frozen=False,
        application_title="Test App",
    )

    assert result == (
        "Test App is starting from module execution "
        "in native mode with reload disabled."
    )
