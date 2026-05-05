# -----------------------------------------------------------------------------
# File: src/desktop_app/app.py
# Purpose:
# Define the NiceGui Windows Base application entry point and runtime helpers.
# Behavior:
# Builds the main UI, resolves bundled assets for normal and PyInstaller
# execution, starts NiceGUI in native mode by default, and supports browser
# reload mode through the development runner.
# Notes:
# The optional pyi_splash module exists only inside a PyInstaller executable
# built with splash support. It is imported dynamically after logging is
# configured so startup diagnostics are persisted during packaged execution.
# -----------------------------------------------------------------------------

import importlib
import logging
import os
import sys
from functools import partial
from multiprocessing import freeze_support
from pathlib import Path
from types import ModuleType

from nicegui import app, native, ui

APPLICATION_TITLE = "NiceGui Windows Base"
APP_ICON_FILENAME = "app_icon.ico"
PAGE_IMAGE_FILENAME = "page_image.png"
DEFAULT_WEB_PORT = 8080
PACKAGED_ASSETS_DIR = Path("desktop_app") / "assets"
LOCAL_ASSETS_DIR = "assets"
LOG_FILE_PATH = Path("logs") / "desktop_app.log"
LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


def is_frozen_executable() -> bool:
    """Return whether the application is running from a frozen executable.

    Returns:
        True when PyInstaller marks the process as frozen; otherwise False.
    """
    frozen = bool(getattr(sys, "frozen", False))
    logger.debug("Runtime frozen check completed: frozen=%s", frozen)
    return frozen


def get_log_file_path() -> Path:
    """Return the log file path for the current runtime.

    Returns:
        A writable log path near the executable in frozen mode or in the current
        working directory during normal development.
    """
    if bool(getattr(sys, "frozen", False)):
        return Path(sys.executable).resolve().parent / LOG_FILE_PATH

    return Path.cwd() / LOG_FILE_PATH


def configure_logging() -> Path:
    """Configure application logging for terminal and file diagnostics.

    Returns:
        The configured log file path.
    """
    log_file_path = get_log_file_path()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

    logger.info("Application logging is ready.")
    logger.debug("Log file path: %s", log_file_path)
    logger.debug("Current working directory: %s", Path.cwd())
    logger.debug("sys.executable: %s", sys.executable)
    logger.debug("sys.argv: %s", sys.argv)
    logger.debug("sys.frozen: %s", getattr(sys, "frozen", None))
    logger.debug("sys._MEIPASS: %s", getattr(sys, "_MEIPASS", None))
    logger.debug("Process ID: %s", os.getpid())

    return log_file_path


class PyInstallerSplashController:
    """Control the optional PyInstaller splash screen lifecycle."""

    def __init__(self) -> None:
        """Initialize the controller and load the splash module when available."""
        logger.info("Preparing PyInstaller splash integration.")
        self._splash_module = self._load_splash_module()
        self._close_attempted = False

        if self.is_available:
            logger.info("PyInstaller splash integration is ready.")
        else:
            logger.debug("PyInstaller splash integration is not available.")

    @property
    def is_available(self) -> bool:
        """Return whether PyInstaller splash support is available."""
        return self._splash_module is not None

    def close_once(self, *args: object) -> None:
        """Close the PyInstaller splash screen once.

        Args:
            *args: Optional callback arguments passed by NiceGUI.
        """
        logger.debug(
            "Splash close requested: close_attempted=%s, is_available=%s, args=%s",
            self._close_attempted,
            self.is_available,
            args,
        )

        if self._close_attempted:
            logger.debug("Splash close skipped because it was already attempted.")
            return

        self._close_attempted = True
        logger.debug("Splash close attempt flag set to True.")

        if self._splash_module is None:
            logger.debug("Splash close skipped because pyi_splash is not loaded.")
            return

        close_splash = getattr(self._splash_module, "close", None)
        logger.debug("Resolved pyi_splash.close: callable=%s", callable(close_splash))

        if not callable(close_splash):
            logger.warning("PyInstaller splash module does not expose close().")
            return

        try:
            logger.info("NiceGUI client connected; closing the splash screen.")
            close_splash()
            logger.info("PyInstaller splash screen closed successfully.")
        except RuntimeError:
            logger.exception("Could not close PyInstaller splash screen.")
        except Exception:
            logger.exception(
                "Unexpected error while closing PyInstaller splash screen."
            )

    @staticmethod
    def _load_splash_module() -> ModuleType | None:
        """Load the optional PyInstaller splash module during frozen startup.

        Returns:
            The optional PyInstaller splash module in packaged execution, or None
            during normal Python execution and builds without splash support.
        """
        logger.debug("Checking whether PyInstaller splash support is available.")

        if not is_frozen_executable():
            logger.debug("Skipping pyi_splash import because runtime is not frozen.")
            return None

        try:
            splash_module = importlib.import_module("pyi_splash")
            logger.debug("pyi_splash imported successfully: %s", splash_module)
            logger.debug(
                "pyi_splash.close exists: %s",
                callable(getattr(splash_module, "close", None)),
            )
            return splash_module
        except ImportError:
            logger.warning(
                "Packaged execution detected, but pyi_splash is not available."
            )
            return None
        except Exception:
            logger.exception("Unexpected error while importing pyi_splash.")
            return None


def get_runtime_root() -> Path:
    """Return the root directory used to resolve runtime files.

    Returns:
        The PyInstaller extraction directory when available, the executable folder
        for other frozen cases, or the package directory during normal execution.
    """
    pyinstaller_temp_dir = getattr(sys, "_MEIPASS", None)
    logger.debug("Detected sys._MEIPASS: %s", pyinstaller_temp_dir)

    if pyinstaller_temp_dir is not None:
        runtime_root = Path(str(pyinstaller_temp_dir))
        logger.debug("Runtime root resolved from sys._MEIPASS: %s", runtime_root)
        return runtime_root

    if is_frozen_executable():
        runtime_root = Path(sys.executable).parent
        logger.debug("Runtime root resolved from executable parent: %s", runtime_root)
        return runtime_root

    runtime_root = Path(__file__).parent
    logger.debug("Runtime root resolved from package directory: %s", runtime_root)
    return runtime_root


def resolve_asset_path(filename: str) -> str:
    """Return an absolute path for an application asset.

    Args:
        filename: Asset filename stored in the package assets directory.

    Returns:
        Absolute path to the requested asset file.
    """
    runtime_root = get_runtime_root()

    if is_frozen_executable():
        asset_path = runtime_root / PACKAGED_ASSETS_DIR / filename
    else:
        asset_path = runtime_root / LOCAL_ASSETS_DIR / filename

    logger.debug("Resolved asset path for %s: %s", filename, asset_path)
    logger.debug("Asset exists: %s", asset_path.exists())

    return str(asset_path)


def get_application_icon_path() -> str:
    """Return the application icon path.

    Returns:
        Absolute path to the application icon file.
    """
    icon_path = resolve_asset_path(APP_ICON_FILENAME)
    logger.debug("Application icon path resolved: %s", icon_path)
    return icon_path


def register_pyinstaller_splash_handler(
    splash_controller: PyInstallerSplashController,
) -> None:
    """Register splash closing after the first NiceGUI client connection.

    Args:
        splash_controller: Controller responsible for closing PyInstaller splash.
    """
    if not splash_controller.is_available:
        logger.debug(
            "Splash close handler was not registered because splash is unavailable."
        )
        return

    app.on_connect(splash_controller.close_once)
    logger.info("Splash screen will close after the first NiceGUI client connects.")


def detect_startup_source(*, development_mode: bool) -> str:
    """Detect how the application was started.

    Args:
        development_mode: Whether startup was requested by the development runner.

    Returns:
        A readable startup source name for diagnostic output.
    """
    logger.debug("Detecting startup source: development_mode=%s", development_mode)

    if development_mode:
        return "dev_run.py"

    if is_frozen_executable():
        return "package"

    entry_name = Path(sys.argv[0]).name.lower()
    logger.debug("Startup entry name: %s", entry_name)

    if entry_name in {"nicegui-windows-base", "nicegui-windows-base.exe"}:
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
        "Initializing NiceGui Windows Base "
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
        port = native.find_open_port()
        logger.debug("Native runtime port resolved: %s", port)
        return port

    logger.debug("Web development runtime port resolved: %s", DEFAULT_WEB_PORT)
    return DEFAULT_WEB_PORT


def build_main_page(*, startup_message: str) -> None:
    """Build the main NiceGUI interface.

    Args:
        startup_message: Startup diagnostic message shown in the page.
    """
    logger.info("Building the main page.")

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
        page_image_path = resolve_asset_path(PAGE_IMAGE_FILENAME)
        logger.debug("Adding page image to UI: %s", page_image_path)

        ui.image(page_image_path).classes("h-40 w-40 rounded-2xl object-contain")

        ui.label("NiceGui Windows Base").classes(
            "text-4xl font-bold tracking-tight text-slate-800"
        )
        ui.label("A minimal native and web Windows base template.").classes(
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

    logger.info("Main page is ready.")


def main(*, development_mode: bool = False) -> None:
    """Run the NiceGUI application.

    Args:
        development_mode: Whether to run in web development mode with reload.
    """
    configure_logging()
    logger.info("Application startup begins.")

    splash_controller = PyInstallerSplashController()

    native_mode, reload_enabled = get_nicegui_modes(development_mode=development_mode)
    startup_source = detect_startup_source(development_mode=development_mode)
    startup_message = format_startup_message(
        startup_source=startup_source,
        native_mode=native_mode,
        reload_enabled=reload_enabled,
    )

    if startup_source == "package":
        logger.info("Running as packaged executable.")
    elif development_mode:
        logger.info("Running in browser development mode.")
    else:
        logger.info("Running from %s.", startup_source)

    print(startup_message, flush=True)
    logger.debug("Startup message printed to terminal: %s", startup_message)

    register_pyinstaller_splash_handler(splash_controller)

    icon_path = get_application_icon_path()
    runtime_port = get_runtime_port(native_mode=native_mode)

    logger.info(
        "Starting NiceGUI in %s mode on port %s.",
        "native" if native_mode else "web",
        runtime_port,
    )

    # NiceGUI receives a callable that builds the UI later. partial keeps the
    # startup message bound without calling build_main_page before ui.run starts.
    ui.run(
        partial(build_main_page, startup_message=startup_message),
        native=native_mode,
        reload=reload_enabled,
        title=APPLICATION_TITLE,
        favicon=icon_path,
        port=runtime_port,
    )


if __name__ == "__main__":
    freeze_support()
    main()
