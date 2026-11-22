$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

docker compose -f docker-compose.yml down
Write-Host "VertexERP AI V2 development containers stopped. Volumes were preserved." -ForegroundColor Green
