# -----------------------------------------------------------------------------
# File: src/nicegui_hello_world/app.py
# Purpose:
# Define the NiceGUI Hello World application entry point and shared runtime helpers.
# Behavior:
# Builds the main UI, resolves bundled assets for normal and PyInstaller execution,
# starts NiceGUI in native mode by default, and supports browser reload mode through
# the development runner.
# Notes:
# The optional pyi_splash module exists only inside a PyInstaller executable
# built with splash support. It is loaded during frozen startup and reused later
# by the NiceGUI connection callback.
# -----------------------------------------------------------------------------

import logging
import sys
from functools import partial
from pathlib import Path
from types import ModuleType

from nicegui import app, native, ui

APPLICATION_TITLE = "NiceGUI Hello World"
APP_ICON_FILENAME = "app_icon.ico"
PAGE_IMAGE_FILENAME = "page_image.png"
DEFAULT_WEB_PORT = 8080
PACKAGED_ASSETS_DIR = Path("nicegui_hello_world") / "assets"
LOCAL_ASSETS_DIR = "assets"

logger = logging.getLogger(__name__)
_splash_close_attempted = False


def configure_logging() -> None:
    """Configure basic application logging for command-line diagnostics."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def is_frozen_executable() -> bool:
    """Return whether the application is running from a frozen executable.

    Returns:
        True when PyInstaller marks the process as frozen; otherwise False.
    """
    return bool(getattr(sys, "frozen", False))


def get_runtime_root() -> Path:
    """Return the root directory used to resolve runtime files.

    Returns:
        The PyInstaller extraction directory when available, the executable folder
        for other frozen cases, or the package directory during normal execution.
    """
    pyinstaller_temp_dir = getattr(sys, "_MEIPASS", None)

    if pyinstaller_temp_dir is not None:
        return Path(str(pyinstaller_temp_dir))

    if is_frozen_executable():
        return Path(sys.executable).parent

    return Path(__file__).parent


def resolve_asset_path(filename: str) -> str:
    """Return an absolute path for an application asset.

    Args:
        filename: Asset filename stored in the package assets directory.

    Returns:
        Absolute path to the requested asset file.
    """
    runtime_root = get_runtime_root()

    if is_frozen_executable():
        return str(runtime_root / PACKAGED_ASSETS_DIR / filename)

    return str(runtime_root / LOCAL_ASSETS_DIR / filename)


def get_application_icon_path() -> str:
    """Return the application icon path.

    Returns:
        Absolute path to the application icon file.
    """
    return resolve_asset_path(APP_ICON_FILENAME)


def load_pyinstaller_splash() -> ModuleType | None:
    """Load the optional PyInstaller splash module during frozen startup.

    Returns:
        The optional PyInstaller splash module in packaged execution, or None
        during normal Python execution and builds without splash support.
    """
    if not is_frozen_executable():
        return None

    try:
        import pyi_splash as splash_module  # pyright: ignore[reportMissingModuleSource]
    except ImportError:
        return None

    return splash_module


_pyinstaller_splash = load_pyinstaller_splash()


def close_pyinstaller_splash_once(*_args: object) -> None:
    """Close the PyInstaller splash screen once after a client connects."""
    global _splash_close_attempted

    if _splash_close_attempted:
        return

    _splash_close_attempted = True

    if _pyinstaller_splash is None:
        return

    close_splash = getattr(_pyinstaller_splash, "close", None)

    if not callable(close_splash):
        logger.warning("PyInstaller splash module does not expose a callable close().")
        return

    try:
        close_splash()
    except RuntimeError:
        logger.exception("Could not close PyInstaller splash screen.")


def register_pyinstaller_splash_handler() -> None:
    """Register splash closing after the first NiceGUI client connection."""
    app.on_connect(close_pyinstaller_splash_once)


def detect_startup_source(*, development_mode: bool) -> str:
    """Detect how the application was started.

    Args:
        development_mode: Whether startup was requested by the development runner.

    Returns:
        A readable startup source name for diagnostic output.
    """
    if development_mode:
        return "dev_run.py"

    if is_frozen_executable():
        return "package"

    entry_name = Path(sys.argv[0]).name.lower()

    if entry_name in {"nicegui-hello-world", "nicegui-hello-world.exe"}:
        return "pyproject command"

    if entry_name == "__main__.py":
        return "module"

    if entry_name == "app.py":
        return "script"

    return entry_name or "unknown source"


def format_startup_message(
    *,
    startup_source: str,
    native_mode: bool,
    reload_enabled: bool,
) -> str:
    """Format the startup diagnostic message.

    Args:
        startup_source: Source used to start the application.
        native_mode: Whether the application is running in native mode.
        reload_enabled: Whether NiceGUI reload mode is enabled.

    Returns:
        The startup diagnostic message used by the terminal and UI.
    """
    mode_name = "native" if native_mode else "web"
    reload_status = "active" if reload_enabled else "inactive"

    return (
        "Initializing NiceGUI Hello World "
        f"from {startup_source} in {mode_name} mode "
        f"with reload {reload_status}."
    )


def get_nicegui_modes(*, development_mode: bool) -> tuple[bool, bool]:
    """Return NiceGUI native and reload settings.

    Args:
        development_mode: Whether to run in browser development mode.

    Returns:
        A tuple containing native mode and reload status.
    """
    if development_mode:
        return False, True

    return True, False


def get_runtime_port(*, native_mode: bool) -> int:
    """Return the port used by NiceGUI for the selected runtime mode.

    Args:
        native_mode: Whether the application runs in NiceGUI native mode.

    Returns:
        A free dynamic port for native mode or the stable development web port.
    """
    if native_mode:
        return native.find_open_port()

    return DEFAULT_WEB_PORT


def build_main_page(*, startup_message: str) -> None:
    """Build the main NiceGUI interface.

    Args:
        startup_message: Startup diagnostic message shown in the page.
    """
    ui.query("body").classes("bg-slate-100")

    with (
        ui.column().classes(
            "fixed inset-0 items-center justify-center "
            "bg-gradient-to-br from-slate-50 via-white to-blue-50 p-6"
        ),
        ui.card().classes(
            "w-full max-w-2xl items-center gap-5 rounded-2xl p-8 text-center shadow-xl"
        ),
    ):
        ui.image(resolve_asset_path(PAGE_IMAGE_FILENAME)).classes(
            "h-40 w-40 rounded-2xl object-contain"
        )
        ui.label("Hello, NiceGUI!").classes(
            "text-4xl font-bold tracking-tight text-slate-800"
        )
        ui.label("A minimal native and web Hello World template.").classes(
            "text-base text-slate-500"
        )

        with ui.card().classes(
            "w-full rounded-xl bg-slate-50 p-4 text-left shadow-none"
        ):
            ui.label("Startup status").classes(
                "text-sm font-semibold uppercase tracking-wide text-slate-500"
            )
            ui.label(startup_message).classes(
                "mt-1 text-sm leading-relaxed text-slate-700"
            )


def main(*, development_mode: bool = False) -> None:
    """Run the NiceGUI application.

    Args:
        development_mode: Whether to run in web development mode with reload.
    """
    configure_logging()

    native_mode, reload_enabled = get_nicegui_modes(development_mode=development_mode)
    startup_source = detect_startup_source(development_mode=development_mode)
    startup_message = format_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
    )

    print(startup_message, flush=True)
    register_pyinstaller_splash_handler()

    # NiceGUI receives a callable that builds the UI later. partial keeps the
    # startup message bound without calling build_main_page before ui.run starts.
    ui.run(
        partial(build_main_page, startup_message=startup_message),
        native=native_mode,
        reload=reload_enabled,
        title=APPLICATION_TITLE,
        favicon=get_application_icon_path(),
        port=get_runtime_port(native_mode=native_mode),
    )


if __name__ == "__main__":
    main()
