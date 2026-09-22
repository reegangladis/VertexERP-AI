$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " VertexERP AI V2 - Windows Local Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI was not found. Install/start Docker Desktop first."
}

docker info | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop is not running or Docker is not reachable."
}

Write-Host "`nStarting PostgreSQL, Redis, MinIO, migrations, API, worker and frontend..." -ForegroundColor Cyan
docker compose -f docker-compose.yml up -d --build
if ($LASTEXITCODE -ne 0) { throw "Docker Compose failed." }

function Wait-Http($Url, $Name, $Attempts = 60) {
    for ($i = 1; $i -le $Attempts; $i++) {
        try {
            $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5
            if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) {
                Write-Host "$Name is reachable: $Url" -ForegroundColor Green
                return
            }
        } catch {}
        Start-Sleep -Seconds 2
    }
    throw "$Name did not become reachable: $Url"
}

Wait-Http "http://127.0.0.1:8000/health/live" "Backend API"
Wait-Http "http://127.0.0.1:3000/" "Frontend"

& "$Root\scripts\bootstrap-demo-user.ps1"

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host " VertexERP AI V2 is running" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Frontend : http://localhost:3000/login"
Write-Host "API      : http://localhost:8000/docs"
Write-Host "MinIO    : http://localhost:9001"
Write-Host ""
Write-Host "Demo login:" -ForegroundColor Yellow
Write-Host "  Email    : testuser@example.com"
Write-Host "  Password : Test@12345678"
Write-Host "  Tenant   : test-company"
Write-Host ""
Write-Host "Run .\scripts\verify-local.ps1 for an automated login/session check."
Start-Process "http://localhost:3000/login"
