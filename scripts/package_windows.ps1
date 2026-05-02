Set-StrictMode -Version Latest

$ErrorActionPreference = "Stop"

$appName = "nicegui-hello-world"
$entryPoint = "src\nicegui_hello_world\app.py"
$exePath = Join-Path "dist" "$appName.exe"

Write-Host "Installing project in editable mode with packaging dependencies..."
python -m pip install -e ".[packaging]"

if ($LASTEXITCODE -ne 0) {
    throw "Editable installation failed with exit code $LASTEXITCODE."
}

Write-Host "Checking PyInstaller availability..."
$pyInstallerCommand = Get-Command pyinstaller -ErrorAction SilentlyContinue

if (-not $pyInstallerCommand) {
    throw 'PyInstaller was not found in the active environment. Activate .venv and run: python -m pip install -e ".[packaging]"'
}

Write-Host "Removing previous packaging outputs..."
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue

Write-Host "Packaging $appName with nicegui-pack..."
nicegui-pack `
    --onefile `
    --windowed `
    --clean `
    --noconfirm `
    --name $appName `
    $entryPoint

if ($LASTEXITCODE -ne 0) {
    throw "nicegui-pack failed with exit code $LASTEXITCODE."
}

if (-not (Test-Path $exePath)) {
    throw "Packaging finished without creating the expected executable: $exePath"
}

Write-Host "Executable created at: $exePath"
