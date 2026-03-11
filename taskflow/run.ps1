# TaskFlow AI Agent - Windows Quick Start Script
# Usage: Right-click → "Run with PowerShell"  OR  powershell -ExecutionPolicy Bypass -File run.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  TaskFlow AI Agent - Windows Quick Start  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check that Docker is available
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Docker not found in PATH." -ForegroundColor Red
    Write-Host "        Install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host "        Then restart this script." -ForegroundColor Yellow
    exit 1
}

# Verify Docker daemon is running
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker daemon is not reachable." -ForegroundColor Red
    Write-Host "        Details: $dockerInfo" -ForegroundColor Yellow
    Write-Host "        Please start Docker Desktop and wait until it shows 'Docker Desktop is running'." -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Docker is available." -ForegroundColor Green

# 2. Change to the directory that contains this script (the taskflow folder)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "[OK] Working directory: $scriptDir" -ForegroundColor Green

# 3. Copy .env.example → .env if .env is missing
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host ""
        Write-Host "[INFO] .env file created from .env.example." -ForegroundColor Yellow
        Write-Host "       Open taskflow\.env and set OPENAI_API_KEY before proceeding." -ForegroundColor Yellow
        Write-Host ""
        $answer = Read-Host "       Continue anyway? (y/N)"
        if ($answer -notin @("y", "Y")) {
            Write-Host "Aborted. Edit .env and run this script again." -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "[WARN] Neither .env nor .env.example found. Continuing without environment file." -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] .env file found." -ForegroundColor Green
}

# 4. Launch the full stack
Write-Host ""
Write-Host "Starting all services with 'docker compose up --build'..." -ForegroundColor Cyan
Write-Host "This may take a few minutes on the first run while images are pulled/built." -ForegroundColor Gray
Write-Host ""

docker compose up --build

# 5. If we reach here the compose process exited (user pressed Ctrl+C or error)
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Services have stopped." -ForegroundColor Cyan
Write-Host "  To remove containers and networks, run:" -ForegroundColor Gray
Write-Host "    docker compose down" -ForegroundColor White
Write-Host "  To also delete all data volumes, run:" -ForegroundColor Gray
Write-Host "    docker compose down -v" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Default service URLs (when running):" -ForegroundColor Cyan
Write-Host "  Frontend UI  ->  http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API  ->  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Temporal UI  ->  http://localhost:8080" -ForegroundColor White
Write-Host "  Langfuse     ->  http://localhost:3001" -ForegroundColor White
Write-Host ""
