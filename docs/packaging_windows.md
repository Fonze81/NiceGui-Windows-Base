# 📦 Windows Packaging

This document explains how the **NiceGUI Hello World** project is packaged as a Windows executable.

---

## 🎯 Current decision

The project now uses **direct PyInstaller packaging only**.

The previous comparison produced similar results:

| Packager | Size | Time |
|---|---:|---:|
| nicegui-pack | 41.26 MB | 80.54 s |
| PyInstaller | 40.37 MB | 78.36 s |

Direct PyInstaller is now preferred because:

- the executable size was slightly smaller in the comparison;
- the packaging time was slightly faster in the comparison;
- PyInstaller supports Windows version properties directly with `--version-file`;
- PyInstaller keeps the path open for future splash screen configuration;
- using one packager keeps the script simpler.

The decision is also documented as a comment in:

```text
scripts/package_windows.ps1
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

The script uses direct PyInstaller packaging:

```powershell
pyinstaller `
    --onefile `
    --windowed `
    --clean `
    --noconfirm `
    --icon $iconPath `
    --add-data $assetsData `
    --version-file $versionInfoPath `
    --name $appName `
    $entryPoint
```

The relevant paths are:

```powershell
$appName = "nicegui-hello-world"
$entryPoint = "src\nicegui_hello_world\app.py"
$assetsPath = "src\nicegui_hello_world\assets"
$iconPath = Join-Path $assetsPath "app_icon.ico"
$assetsData = "$assetsPath;nicegui_hello_world\assets"
$versionInfoPath = "scripts\version_info.txt"
```

---

## 🏷️ Windows executable properties

Windows executable properties are applied during the PyInstaller build with:

```powershell
--version-file $versionInfoPath
```

The version resource file is:

```text
scripts/version_info.txt
```

This file controls Windows details such as:

- `CompanyName`;
- `FileDescription`;
- `FileVersion`;
- `InternalName`;
- `OriginalFilename`;
- `ProductName`;
- `ProductVersion`.

When the project version changes in `pyproject.toml`, update both the numeric tuples and string values in `scripts/version_info.txt`.

Example:

```text
pyproject.toml: version = "0.1.0"
version_info.txt: filevers=(0, 1, 0, 0)
version_info.txt: FileVersion = "0.1.0.0"
```

---

## 🖼️ Assets and icon

The executable uses the icon from:

```text
src\nicegui_hello_world\assets\app_icon.ico
```

The same assets directory also includes:

```text
src\nicegui_hello_world\assets\page_image.png
```

The assets directory is bundled with:

```powershell
--add-data $assetsData
```

This is required because `ui.run(favicon=...)` and `ui.image(...)` need the files at runtime, including when the application is running as a one-file executable.

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
