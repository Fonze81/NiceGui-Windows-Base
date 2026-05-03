Set-StrictMode -Version Latest

$ErrorActionPreference = "Stop"

# PyInstaller is used directly instead of nicegui-pack because both approaches
# produced similar executable size and build time in this project:
# - nicegui-pack: 41.26 MB in 80.54 seconds
# - PyInstaller: 40.37 MB in 78.36 seconds
#
# Direct PyInstaller also exposes packaging options that nicegui-pack does not
# currently expose in this project flow, such as --version-file and --splash.
$appName = "nicegui-hello-world"
$entryPoint = "src\nicegui_hello_world\app.py"
$assetsPath = "src\nicegui_hello_world\assets"
$iconPath = Join-Path $assetsPath "app_icon.ico"
$splashImagePath = Join-Path $assetsPath "splash_light.png"
$assetsData = "$assetsPath;nicegui_hello_world\assets"
$versionInfoPath = "scripts\version_info.txt"
$exePath = Join-Path "dist" "$appName.exe"
$packagingReportPath = Join-Path "dist" "packaging_report.md"

function Format-Bytes {
    param(
        [Parameter(Mandatory = $true)]
        [long]$Bytes
    )

    return [math]::Round($Bytes / 1MB, 2)
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$StepName,

        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $nativeErrorPreferenceVariable = Get-Variable `
        -Name PSNativeCommandUseErrorActionPreference `
        -ErrorAction SilentlyContinue
    $previousNativeErrorPreference = $null

    try {
        $ErrorActionPreference = "Continue"

        if ($nativeErrorPreferenceVariable) {
            $previousNativeErrorPreference = $PSNativeCommandUseErrorActionPreference
            $PSNativeCommandUseErrorActionPreference = $false
        }

        & $Command @Arguments 2>&1 | ForEach-Object {
            Write-Host $_
        }

        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference

        if ($nativeErrorPreferenceVariable) {
            $PSNativeCommandUseErrorActionPreference = $previousNativeErrorPreference
        }
    }

    if ($exitCode -ne 0) {
        throw "$StepName failed with exit code $exitCode."
    }
}

function Invoke-PyInstallerBuild {
    Write-Host "Packaging with PyInstaller..."

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    Invoke-NativeCommand `
        -StepName "PyInstaller" `
        -Command "pyinstaller" `
        -Arguments @(
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--icon",
        $iconPath,
        "--add-data",
        $assetsData,
        "--splash",
        $splashImagePath,
        "--version-file",
        $versionInfoPath,
        "--name",
        $appName,
        $entryPoint
    )

    if (-not (Test-Path $exePath)) {
        throw "PyInstaller finished without creating the expected executable: $exePath"
    }

    $stopwatch.Stop()

    return $stopwatch.Elapsed
}

function Write-PackagingReport {
    param(
        [Parameter(Mandatory = $true)]
        [TimeSpan]$Elapsed
    )

    $executableFile = Get-Item $exePath
    $sizeMb = Format-Bytes -Bytes $executableFile.Length
    $elapsedSeconds = [math]::Round($Elapsed.TotalSeconds, 2)

    $report = @"
# Windows Packaging Report

Generated at: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

| Packager | Executable | Size (MB) | Time (s) |
|---|---|---:|---:|
| PyInstaller | $exePath | $sizeMb | $elapsedSeconds |

## Packaging decision

PyInstaller is now used directly because the comparison between nicegui-pack and
PyInstaller showed similar results:

| Packager | Size (MB) | Time (s) |
|---|---:|---:|
| nicegui-pack | 41.26 | 80.54 |
| PyInstaller | 40.37 | 78.36 |

Direct PyInstaller keeps the packaging flow simpler and exposes options needed by
this project, including `--version-file` and `--splash`.

## Notes

- The executable receives Windows version properties during build with `--version-file`.
- The build uses the project icon, splash image, assets directory, entry point, one-file mode, and windowed mode.
- The previous nicegui-pack comparison flow was removed after confirming that file size and build time were similar.
"@

    $report | Set-Content -Path $packagingReportPath -Encoding UTF8

    Write-Host ""
    Write-Host "Packaging result:"
    Write-Host "PyInstaller: $sizeMb MB in $elapsedSeconds seconds"
    Write-Host "Packaging report created at: $packagingReportPath"
}

Write-Host "Installing project in editable mode with packaging dependencies..."
Invoke-NativeCommand `
    -StepName "Editable installation" `
    -Command "python" `
    -Arguments @(
    "-m",
    "pip",
    "install",
    "-e",
    ".[packaging]"
)

Write-Host "Checking PyInstaller availability..."
$pyInstallerCommand = Get-Command pyinstaller -ErrorAction SilentlyContinue

if (-not $pyInstallerCommand) {
    throw 'PyInstaller was not found in the active environment. Activate .venv and run: python -m pip install -e ".[packaging]"'
}

if (-not (Test-Path $iconPath)) {
    throw "Application icon was not found: $iconPath"
}

if (-not (Test-Path $splashImagePath)) {
    throw "Splash image was not found: $splashImagePath"
}

if (-not (Test-Path $versionInfoPath)) {
    throw "Windows version info file was not found: $versionInfoPath"
}

Write-Host "Removing previous packaging outputs..."
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue

[TimeSpan]$pyInstallerElapsed = Invoke-PyInstallerBuild

Write-PackagingReport -Elapsed $pyInstallerElapsed

Write-Host ""
Write-Host "Executable created:"
Write-Host "- $exePath"
