$ErrorActionPreference = "Stop"

$python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
& $python -m PyInstaller --noconfirm --clean WorkDesk.spec

$archive = "dist\WorkDesk-windows-x64.zip"
if (Test-Path $archive) {
    Remove-Item $archive -Force
}

Compress-Archive -Path "dist\WorkDesk.exe" -DestinationPath $archive
Write-Host "Created $archive"