$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is required for repository validation."
}

python scripts/verify_source.py
if ($LASTEXITCODE -ne 0) { throw "Source verification failed." }

python scripts/validate_infra.py
if ($LASTEXITCODE -ne 0) { throw "Infrastructure validation failed." }

python -m compileall -q app
if ($LASTEXITCODE -ne 0) { throw "Python compilation failed." }

Write-Host "Repository release validation completed successfully." -ForegroundColor Green
Write-Host "Note: full pytest/frontend build require their dependencies to be installed." -ForegroundColor Yellow
