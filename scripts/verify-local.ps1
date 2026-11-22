$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "VertexERP AI V2 - Local Verification" -ForegroundColor Cyan

function Assert-Http($Url, $Name) {
    $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 10
    if ($r.StatusCode -ne 200) { throw "$Name returned HTTP $($r.StatusCode)" }
    Write-Host "[PASS] $Name -> HTTP 200" -ForegroundColor Green
    return $r
}

Assert-Http "http://127.0.0.1:8000/health/live" "API liveness" | Out-Null
Assert-Http "http://127.0.0.1:8000/health/ready" "API readiness" | Out-Null
Assert-Http "http://127.0.0.1:8000/openapi.json" "OpenAPI" | Out-Null
Assert-Http "http://127.0.0.1:3000/" "Frontend" | Out-Null

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$loginBody = @{
    email = "testuser@example.com"
    password = "Test@12345678"
    tenant_slug = "test-company"
} | ConvertTo-Json

$login = Invoke-WebRequest -UseBasicParsing -Method Post `
    -Uri "http://127.0.0.1:8000/api/v1/identity/auth/login" `
    -ContentType "application/json" `
    -Body $loginBody `
    -WebSession $session

if ($login.StatusCode -ne 200) { throw "Login returned HTTP $($login.StatusCode)" }
Write-Host "[PASS] Login -> HTTP 200" -ForegroundColor Green

$accessCookie = $session.Cookies.GetCookies("http://127.0.0.1:8000/")["access_token"]
$refreshCookie = $session.Cookies.GetCookies("http://127.0.0.1:8000/")["refresh_token"]
if ($null -eq $accessCookie) { throw "access_token cookie was not set." }
if ($null -eq $refreshCookie) { throw "refresh_token cookie was not set." }

$accessBytes = [Text.Encoding]::UTF8.GetByteCount($accessCookie.Value)
$refreshBytes = [Text.Encoding]::UTF8.GetByteCount($refreshCookie.Value)
Write-Host "[PASS] access_token cookie value size: $accessBytes bytes" -ForegroundColor Green
Write-Host "[PASS] refresh_token cookie value size: $refreshBytes bytes" -ForegroundColor Green

if ($accessBytes -ge 4096) { throw "access_token cookie exceeds browser 4096-byte value limit." }

$me = Invoke-WebRequest -UseBasicParsing -Method Get `
    -Uri "http://127.0.0.1:8000/api/v1/identity/auth/me" `
    -WebSession $session

if ($me.StatusCode -ne 200) { throw "/me returned HTTP $($me.StatusCode)" }
$meJson = $me.Content | ConvertFrom-Json
if ($meJson.email -ne "testuser@example.com") { throw "/me returned unexpected user." }
if ($meJson.permissions.Count -lt 1) { throw "/me returned no effective permissions." }

Write-Host "[PASS] /me -> HTTP 200; effective permissions: $($meJson.permissions.Count)" -ForegroundColor Green

Write-Host "`nLOCAL VERIFICATION PASSED" -ForegroundColor Green
