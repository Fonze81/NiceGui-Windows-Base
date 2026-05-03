Set-StrictMode -Version Latest

$ErrorActionPreference = "Stop"

$niceGuiPackName = "nicegui-hello-world-nicegui-pack"
$pyInstallerName = "nicegui-hello-world-pyinstaller"
$entryPoint = "src\nicegui_hello_world\app.py"
$assetsPath = "src\nicegui_hello_world\assets"
$iconPath = Join-Path $assetsPath "app_icon.ico"
$assetsData = "$assetsPath;nicegui_hello_world\assets"
$versionInfoPath = "scripts\version_info.txt"
$niceGuiPackExePath = Join-Path "dist" "$niceGuiPackName.exe"
$pyInstallerExePath = Join-Path "dist" "$pyInstallerName.exe"
$comparisonReportPath = Join-Path "dist" "packaging_comparison.md"

function Test-LastExitCode {
    param(
        [Parameter(Mandatory = $true)]
        [string]$StepName
    )

    if ($LASTEXITCODE -ne 0) {
        throw "$StepName failed with exit code $LASTEXITCODE."
    }
}

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

function Invoke-NiceGuiPackBuild {
    Write-Host "Packaging with nicegui-pack..."

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    Invoke-NativeCommand `
        -StepName "nicegui-pack" `
        -Command "nicegui-pack" `
        -Arguments @(
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--icon",
        $iconPath,
        "--add-data",
        $assetsData,
        "--name",
        $niceGuiPackName,
        $entryPoint
    )

    if (-not (Test-Path $niceGuiPackExePath)) {
        throw "nicegui-pack finished without creating the expected executable: $niceGuiPackExePath"
    }

    Write-Host "Applying Windows version resource to nicegui-pack executable..."

    Invoke-NativeCommand `
        -StepName "pyi-set_version for nicegui-pack" `
        -Command "pyi-set_version" `
        -Arguments @(
        $versionInfoPath,
        $niceGuiPackExePath
    )

    $stopwatch.Stop()

    return $stopwatch.Elapsed
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
        "--version-file",
        $versionInfoPath,
        "--name",
        $pyInstallerName,
        $entryPoint
    )

    if (-not (Test-Path $pyInstallerExePath)) {
        throw "PyInstaller finished without creating the expected executable: $pyInstallerExePath"
    }

    $stopwatch.Stop()

    return $stopwatch.Elapsed
}

function Write-PackagingComparisonReport {
    param(
        [Parameter(Mandatory = $true)]
        [TimeSpan]$NiceGuiPackElapsed,

        [Parameter(Mandatory = $true)]
        [TimeSpan]$PyInstallerElapsed
    )

    $niceGuiPackFile = Get-Item $niceGuiPackExePath
    $pyInstallerFile = Get-Item $pyInstallerExePath

    $niceGuiPackSizeMb = Format-Bytes -Bytes $niceGuiPackFile.Length
    $pyInstallerSizeMb = Format-Bytes -Bytes $pyInstallerFile.Length

    $differenceBytes = $pyInstallerFile.Length - $niceGuiPackFile.Length
    $differenceMb = Format-Bytes -Bytes ([math]::Abs($differenceBytes))

    if ($differenceBytes -lt 0) {
        $sizeSummary = "PyInstaller generated the smaller executable by $differenceMb MB."
    }
    elseif ($differenceBytes -gt 0) {
        $sizeSummary = "nicegui-pack generated the smaller executable by $differenceMb MB."
    }
    else {
        $sizeSummary = "Both executables have the same size."
    }

    $niceGuiPackSeconds = [math]::Round($NiceGuiPackElapsed.TotalSeconds, 2)
    $pyInstallerSeconds = [math]::Round($PyInstallerElapsed.TotalSeconds, 2)

    $report = @"
# Windows Packaging Comparison

Generated at: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

| Packager | Executable | Size (MB) | Time (s) |
|---|---|---:|---:|
| nicegui-pack | $niceGuiPackExePath | $niceGuiPackSizeMb | $niceGuiPackSeconds |
| PyInstaller | $pyInstallerExePath | $pyInstallerSizeMb | $pyInstallerSeconds |

$sizeSummary

## Notes

- The nicegui-pack executable receives Windows version properties after build with `pyi-set_version`.
- The PyInstaller executable receives Windows version properties during build with `--version-file`.
- Both builds use the same icon, assets directory, entry point, one-file mode, and windowed mode.
"@

    $report | Set-Content -Path $comparisonReportPath -Encoding UTF8

    Write-Host ""
    Write-Host "Packaging comparison:"
    Write-Host "nicegui-pack: $niceGuiPackSizeMb MB in $niceGuiPackSeconds seconds"
    Write-Host "PyInstaller:   $pyInstallerSizeMb MB in $pyInstallerSeconds seconds"
    Write-Host $sizeSummary
    Write-Host "Comparison report created at: $comparisonReportPath"
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

Write-Host "Checking nicegui-pack availability..."
$niceGuiPackCommand = Get-Command nicegui-pack -ErrorAction SilentlyContinue

if (-not $niceGuiPackCommand) {
    throw 'nicegui-pack was not found in the active environment. Activate .venv and run: python -m pip install -e ".[packaging]"'
}

Write-Host "Checking pyi-set_version availability..."
$pyiSetVersionCommand = Get-Command pyi-set_version -ErrorAction SilentlyContinue

if (-not $pyiSetVersionCommand) {
    throw 'pyi-set_version was not found in the active environment. Activate .venv and run: python -m pip install -e ".[packaging]"'
}

if (-not (Test-Path $iconPath)) {
    throw "Application icon was not found: $iconPath"
}

if (-not (Test-Path (Join-Path $assetsPath "page_image.png"))) {
    throw "Page image was not found: $(Join-Path $assetsPath "page_image.png")"
}

if (-not (Test-Path $versionInfoPath)) {
    throw "Windows version info file was not found: $versionInfoPath"
}

Write-Host "Removing previous packaging outputs..."
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue

[TimeSpan]$niceGuiPackElapsed = Invoke-NiceGuiPackBuild
[TimeSpan]$pyInstallerElapsed = Invoke-PyInstallerBuild

Write-PackagingComparisonReport `
    -NiceGuiPackElapsed $niceGuiPackElapsed `
    -PyInstallerElapsed $pyInstallerElapsed

Write-Host ""
Write-Host "Executables created:"
Write-Host "- $niceGuiPackExePath"
Write-Host "- $pyInstallerExePath"