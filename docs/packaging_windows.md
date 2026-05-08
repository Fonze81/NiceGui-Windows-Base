# 📦 Windows Packaging

This document explains how the **NiceGui Windows Base** project is packaged as a Windows executable.

---

## 🎯 Current decision

The project now uses **direct PyInstaller packaging only**.

The previous comparison produced similar results:

| Packager     |     Size |    Time |
| ------------ | -------: | ------: |
| nicegui-pack | 41.26 MB | 80.54 s |
| PyInstaller  | 40.37 MB | 78.36 s |

Direct PyInstaller is now preferred and invoked through `python -m PyInstaller` because:

- the executable size was slightly smaller in the comparison;
- the packaging time was slightly faster in the comparison;
- PyInstaller supports Windows version properties directly with `--version-file`;
- PyInstaller supports splash screen configuration through `--splash`;
- PyInstaller supports windowed desktop execution through `--windowed`;
- PyInstaller can bundle the default `settings.toml` template with `--add-data`;
- PyInstaller allows the splash module to be preserved with `--hidden-import pyi_splash`;
- using one packager keeps the script simpler.

The decision is also documented as a comment in:

```text
scripts\package_windows.ps1
```

---

## ▶️ Packaging command

Run from the repository root:

```powershell
.\scripts\package_windows.ps1
```

If PowerShell blocks the script, run it with a process-level execution policy bypass:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\package_windows.ps1
```

---

## 🧱 PyInstaller command

The script invokes PyInstaller through the active Python environment:

```powershell
python -m PyInstaller `
    --onefile `
    --windowed `
    --clean `
    --noconfirm `
    --icon $iconPath `
    --add-data $assetsData `
    --add-data $settingsData `
    --splash $splashImagePath `
    --hidden-import pyi_splash `
    --version-file $versionInfoPath `
    --name $appName `
    $entryPoint
```

The relevant paths are:

```powershell
$appName = "nicegui-windows-base"
$entryPoint = "src\desktop_app\app.py"
$assetsPath = "src\desktop_app\assets"
$iconPath = Join-Path $assetsPath "app_icon.ico"
$splashImagePath = Join-Path $assetsPath "splash_light.png"
$assetsData = "$assetsPath;desktop_app\assets"
$settingsTemplatePath = "src\desktop_app\settings.toml"
$settingsData = "$settingsTemplatePath;desktop_app"
$versionInfoPath = "scripts\version_info.txt"
```

---

## 🧭 Package path and executable name

The PyInstaller entry point uses the stable internal package path:

```powershell
$entryPoint = "src\desktop_app\app.py"
```

The executable name can be changed independently through:

```powershell
$appName = "nicegui-windows-base"
```

When this template is reused, the internal package name should usually remain `desktop_app`. Change the public executable name, project metadata, application title, and assets instead of renaming the package. See the root [README](../README.md#-naming-model) for the complete naming model.

---

## 🪟 Windowed mode

The build uses:

```powershell
--windowed
```

This prevents a console window from opening next to the native desktop window. Keep this option enabled for end-user desktop builds. If you need console output for packaging diagnostics, run the Python source directly or inspect the generated log file instead of removing `--windowed` permanently.

---

## 🏷️ Windows executable properties

Windows executable properties are applied during the PyInstaller build with:

```powershell
--version-file $versionInfoPath
```

The version resource file is:

```text
scripts\version_info.txt
```

This file controls Windows details such as:

- `CompanyName`;
- `FileDescription`;
- `FileVersion`;
- `InternalName`;
- `OriginalFilename`;
- `ProductName`;
- `ProductVersion`.

When the project version changes in `pyproject.toml`, update both the numeric tuples and string values in `scripts\version_info.txt`.

Example:

```text
pyproject.toml: version = "0.3.4"
version_info.txt: filevers=(0, 3, 4, 0)
version_info.txt: FileVersion = "0.3.4.0"
```

When preparing a new release, also update the root [CHANGELOG](../CHANGELOG.md) with the relevant user-facing and maintenance changes.

---

## 🖼️ Assets and icon

The executable uses the icon from:

```text
src\desktop_app\assets\app_icon.ico
```

The same assets directory also includes runtime images such as:

```text
src\desktop_app\assets\page_image.png
src\desktop_app\assets\splash_light.png
```

The assets directory is bundled with:

```powershell
--add-data $assetsData
```

This is required because `ui.run(favicon=...)` and `ui.image(...)` need the files at runtime, including when the application is running as a one-file executable.

## ⚙️ Settings template

The default settings template is bundled from:

```text
src\desktop_app\settings.toml
```

The script passes it to PyInstaller with:

```powershell
--add-data $settingsData
```

At runtime, startup reads an existing persistent `settings.toml` when available. If the file is missing, the application keeps in-memory defaults and does not write anything during load. The persistent file is created next to `dist\nicegui-windows-base.exe` only when a settings save operation is requested. See [Settings and application state](settings.md).

---

## 🖼️ Splash screen

The packaging script uses a dedicated light-background image as the PyInstaller splash screen:

```powershell
$splashImagePath = Join-Path $assetsPath "splash_light.png"
python -m PyInstaller --splash $splashImagePath ...
```

The build also keeps the optional PyInstaller splash module available with:

```powershell
--hidden-import pyi_splash
```

At runtime, `register_splash_handler()` imports `pyi_splash` only when `sys.frozen` is true. If the module is available, it registers `close_splash_once()` with `app.on_connect(...)` before `ui.run(...)` starts. The handler closes the splash screen after the first NiceGUI client connects and avoids repeated close attempts during reconnects.

`app.py` uses the standard Windows-safe packaged entry point:

```python
if __name__ == "__main__":
    freeze_support()
    main()
```

The splash image is intentionally separate from the page image. Use a file with an opaque light background to avoid transparent pixels rendering with an unexpected color in the PyInstaller splash window.

---

## ⏱️ Build time and size report

The script measures elapsed time with:

```powershell
[System.Diagnostics.Stopwatch]::StartNew()
```

After packaging, it creates:

```text
dist\packaging_report.md
```

The report includes:

- generated executable path;
- size in MB;
- packaging time in seconds;
- the reason PyInstaller is the selected packager.

---

## 🧪 PowerShell function output handling

PowerShell functions return every object written to the success output pipeline, not only values passed to `return`.

For that reason, native command output must not leak into the function return pipeline. The script uses `Invoke-NativeCommand` to execute commands, print their output with `Write-Host`, and keep function return values clean.

The function also temporarily changes native command error handling while the external command runs. PyInstaller can write normal progress information to stderr. With `$ErrorActionPreference = "Stop"`, redirected stderr can become a `NativeCommandError` and stop the script even when the native command has not actually failed.

`Invoke-NativeCommand` avoids that by:

- temporarily setting `$ErrorActionPreference` to `"Continue"`;
- disabling `$PSNativeCommandUseErrorActionPreference` when available;
- checking the native process exit code explicitly after the command finishes.

---

## 🔗 Related documents

- [Documentation index](README.md)
- [Execution modes](execution_modes.md)
- [Troubleshooting](troubleshooting.md)
