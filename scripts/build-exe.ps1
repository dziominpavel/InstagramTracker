#Requires -Version 5.1
# Builds the standalone one-file exe for the store:
#   dist/InstagramTracker-<version>-win-x64.exe  (PyInstaller --onefile)
# Uses the project venv when present (installs requirements + PyInstaller there),
# otherwise falls back to the current python. No system-wide changes.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

$versionFile = Join-Path $root 'version'
if (-not (Test-Path $versionFile)) { Write-Host "[ERROR] missing version file: $versionFile"; exit 1 }
$version = (Get-Content $versionFile -Raw).Trim()
if ($version -notmatch '^\d+\.\d+\.\d+$') { Write-Host "[ERROR] bad version '$version' (expected MAJOR.MINOR.PATCH)"; exit 1 }

$venvPython = Join-Path $root '.venv\Scripts\python.exe'
if (Test-Path $venvPython) { $python = $venvPython } else { $python = 'python' }
Write-Host "python: $python"

& $python -m pip install --quiet --upgrade pip
if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] pip self-upgrade failed"; exit 1 }
& $python -m pip install --quiet -r (Join-Path $root 'requirements.txt') pyinstaller
if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] dependency install failed"; exit 1 }

$name = "InstagramTracker-$version-win-x64"
& $python -m PyInstaller --onefile --name $name `
    --distpath dist --workpath build --specpath build `
    --collect-submodules playwright `
    main.py
if ($LASTEXITCODE -ne 0) { Write-Host "[ERROR] PyInstaller build failed"; exit 1 }

$exe = Join-Path $root "dist\$name.exe"
if (-not (Test-Path $exe)) { Write-Host "[ERROR] expected artifact missing: $exe"; exit 1 }
$size = [math]::Round((Get-Item $exe).Length / 1MB, 1)
Write-Host "built: $exe ($size MB)"
