# -----------------------------------------------------------------------------
# File: src/nicegui_hello_world/app.py
# Purpose:
# Define the minimal NiceGUI Hello World application entry point.
# Behavior:
# Builds the main UI and starts NiceGUI in native mode by default. Development
# scripts can request development mode, which runs the same UI in web mode with
# reload enabled.
# Notes:
# Uses pywebview through NiceGUI native mode. The explicit root function avoids
# NiceGUI script mode issues when the app is packaged as an executable.
# -----------------------------------------------------------------------------

import sys
from functools import partial
from multiprocessing import freeze_support
from pathlib import Path

from nicegui import native, ui

APP_ICON_FILENAME = "app_icon.ico"
PAGE_IMAGE_FILENAME = "page_image.png"


def create_ui(*, startup_message: str) -> None:
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
        ui.image(get_asset_path(PAGE_IMAGE_FILENAME)).classes(
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


def is_packaged() -> bool:
    """Return whether the application is running from a packaged executable."""
    return bool(getattr(sys, "frozen", False))


def get_asset_path(filename: str) -> str:
    """Return an application asset path for normal and packaged execution.

    Args:
        filename: Asset filename stored in the package assets directory.

    Returns:
        Absolute path to the requested asset file.
    """
    if is_packaged():
        base_path = Path(sys._MEIPASS)
        return str(base_path / "nicegui_hello_world" / "assets" / filename)

    return str(Path(__file__).parent / "assets" / filename)


def get_app_icon_path() -> str:
    """Return the application icon path.

    Returns:
        Absolute path to the application icon file.
    """
    return get_asset_path(APP_ICON_FILENAME)


def identify_startup_source(*, development_mode: bool) -> str:
    """Identify how the application was started.

    Args:
        development_mode: Whether startup was requested by the development runner.

    Returns:
        A readable startup source name for diagnostic output.
    """
    if development_mode:
        return "dev_run.py"

    if is_packaged():
        return "package"

    entry_name = Path(sys.argv[0]).name.lower()

    if entry_name in {"nicegui-hello-world", "nicegui-hello-world.exe"}:
        return "pyproject command"

    if entry_name == "__main__.py":
        return "module"

    if entry_name == "app.py":
        return "script"

    return entry_name or "unknown source"


def build_startup_message(
    *,
    startup_source: str,
    native_mode: bool,
    reload_enabled: bool,
) -> str:
    """Build the startup diagnostic message.

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


def main(*, development_mode: bool = False) -> None:
    """Run the NiceGUI application.

    Args:
        development_mode: Whether to run in web development mode with reload.
    """
    if development_mode:
        native_mode = False
        reload_enabled = True
    else:
        native_mode = True
        reload_enabled = False

    startup_source = identify_startup_source(development_mode=development_mode)
    startup_message = build_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
    )

    print(startup_message)

    ui.run(
        partial(create_ui, startup_message=startup_message),
        native=native_mode,
        reload=reload_enabled,
        title="NiceGUI Hello World",
        favicon=get_app_icon_path(),
        port=native.find_open_port(),
    )


if __name__ == "__main__":
    freeze_support()
    main()
