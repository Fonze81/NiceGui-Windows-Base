"""Test logger package dependency boundaries."""

import ast
from pathlib import Path

LOGGER_PACKAGE_PATH = Path("src/desktop_app/infrastructure/logger")
FORBIDDEN_IMPORTS: tuple[str, ...] = (
    "desktop_app.constants",
    "desktop_app.infrastructure.byte_size",
    "desktop_app.infrastructure.file_system",
)


def _iter_logger_python_files() -> list[Path]:
    """Return logger package Python files sorted for deterministic assertions."""
    return sorted(LOGGER_PACKAGE_PATH.glob("*.py"))


def _iter_imported_modules(file_path: Path) -> list[str]:
    """Return modules imported by a Python source file.

    Args:
        file_path: Python source file to inspect.

    Returns:
        Imported module names found in import statements.
    """
    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    imported_modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.append(node.module)

    return imported_modules


def test_logger_package_has_no_forbidden_external_imports() -> None:
    """Verify that logger internals stay reusable and self-contained."""
    violations: list[str] = []

    for file_path in _iter_logger_python_files():
        for imported_module in _iter_imported_modules(file_path):
            if imported_module in FORBIDDEN_IMPORTS:
                violations.append(f"{file_path}: {imported_module}")

    assert violations == []


def test_logger_package_guide_is_bundled_as_package_data() -> None:
    """Ensure the package-local logger guide is included in package builds."""
    import tomllib

    pyproject_data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    package_data = pyproject_data["tool"]["setuptools"]["package-data"]

    assert "infrastructure/logger/*.md" in package_data["desktop_app"]
    assert (LOGGER_PACKAGE_PATH / "README.md").is_file()
