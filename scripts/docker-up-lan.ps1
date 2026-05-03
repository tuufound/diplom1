# Docker for phone on same Wi-Fi: writes .env.lan with this PC IP, then compose up.
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $RepoRoot

# Avoid stderr from `docker` becoming a PowerShell error (breaks with $ErrorActionPreference = Stop).
cmd /c "docker info >nul 2>nul"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Docker daemon is not running (npipe / dockerDesktopLinuxEngine)." -ForegroundColor Yellow
    Write-Host "1) Start Docker Desktop from the Start menu." -ForegroundColor Yellow
    Write-Host "2) Wait until the whale icon shows the engine is running (no 'Starting...')." -ForegroundColor Yellow
    Write-Host "3) Run: docker version   (both Client and Server should print)" -ForegroundColor Yellow
    Write-Host "4) Then run this script again." -ForegroundColor Yellow
    exit 1
}

& (Join-Path $PSScriptRoot "write-lan-env.ps1")

if ($args.Count -eq 0) {
    docker compose --env-file .env.lan up --build
}
else {
    docker compose --env-file .env.lan @args
}
