$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$ApiBase = "http://127.0.0.1:8000"
$LoginUrl = "$ApiBase/api/v1/identity/auth/login"
$RegisterUrl = "$ApiBase/api/v1/identity/auth/register"

$LoginBody = @{
    email = "testuser@example.com"
    password = "Test@12345678"
    tenant_slug = "test-company"
} | ConvertTo-Json

Write-Host "`n[1/2] Checking demo account..." -ForegroundColor Cyan
try {
    $login = Invoke-RestMethod -UseBasicParsing -Method Post -Uri $LoginUrl `
        -ContentType "application/json" -Body $LoginBody
    if ($login.mfa_required -eq $true) {
        throw "Demo account requires MFA. Disable MFA for this development-only account or use another test account."
    }
    Write-Host "Demo account already exists and credentials are valid." -ForegroundColor Green
    exit 0
}
catch {
    $status = 0
    if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
    if ($status -ne 401 -and $status -ne 404) {
        Write-Host "Login check returned HTTP $status. Continuing to registration check..." -ForegroundColor Yellow
    }
}

Write-Host "[2/2] Creating demo tenant/user if missing..." -ForegroundColor Cyan
$registerFile = Join-Path $Root "register.json"
if (-not (Test-Path $registerFile)) {
    throw "Missing register.json"
}

$registerBody = Get-Content $registerFile -Raw
try {
    $registration = Invoke-RestMethod -UseBasicParsing -Method Post -Uri $RegisterUrl `
        -ContentType "application/json" -Body $registerBody
    Write-Host "Demo tenant/user created successfully." -ForegroundColor Green
}
catch {
    $status = 0
    if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
    if ($status -eq 409) {
        Write-Host "Demo tenant/user already exists." -ForegroundColor Green
    } else {
        $body = ""
        try { $body = (New-Object IO.StreamReader($_.Exception.Response.GetResponseStream())).ReadToEnd() } catch {}
        throw "Registration failed (HTTP $status). $body"
    }
}
