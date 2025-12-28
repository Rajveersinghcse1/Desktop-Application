#!/usr/bin/env pwsh
# Docker Management Script for AI Avatar Studio

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('build', 'up', 'down', 'restart', 'logs', 'shell', 'clean', 'status')]
    [string]$Action = 'status'
)

$ErrorActionPreference = "Stop"
$PROJECT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n=== AI Avatar Studio - Docker Manager ===" -ForegroundColor Cyan
Write-Host "Action: $Action`n" -ForegroundColor Yellow

Set-Location $PROJECT_DIR

function Test-DockerRunning {
    try {
        docker info | Out-Null
        return $true
    } catch {
        Write-Host "[ERROR] Docker is not running or not installed!" -ForegroundColor Red
        Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
        return $false
    }
}

function Build-Container {
    Write-Host "[*] Building Docker image..." -ForegroundColor Green
    docker-compose build --no-cache
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Docker image built successfully!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Docker build failed!" -ForegroundColor Red
        exit 1
    }
}

function Start-Container {
    Write-Host "[*] Starting container..." -ForegroundColor Green
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Container started successfully!" -ForegroundColor Green
        Start-Sleep -Seconds 3
        docker-compose logs --tail=20
    } else {
        Write-Host "[ERROR] Failed to start container!" -ForegroundColor Red
        exit 1
    }
}

function Stop-Container {
    Write-Host "[*] Stopping container..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "[OK] Container stopped!" -ForegroundColor Green
}

function Restart-Container {
    Write-Host "[*] Restarting container..." -ForegroundColor Yellow
    docker-compose restart
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Container restarted!" -ForegroundColor Green
        Start-Sleep -Seconds 2
        docker-compose logs --tail=20
    }
}

function Show-Logs {
    Write-Host "[*] Showing container logs (Ctrl+C to exit)..." -ForegroundColor Cyan
    docker-compose logs -f
}

function Open-Shell {
    Write-Host "[*] Opening shell in container..." -ForegroundColor Cyan
    docker-compose exec ai-avatar-studio /bin/bash
}

function Clean-Docker {
    Write-Host "[*] Cleaning Docker resources..." -ForegroundColor Yellow
    docker-compose down -v
    docker system prune -f
    Write-Host "[OK] Cleanup complete!" -ForegroundColor Green
}

function Show-Status {
    Write-Host "[*] Container Status:" -ForegroundColor Cyan
    docker-compose ps
    Write-Host "`n[*] Docker Images:" -ForegroundColor Cyan
    docker images | Select-String "ai-avatar"
    Write-Host "`n[*] Volume Status:" -ForegroundColor Cyan
    Get-ChildItem -Path "docker_volumes" -Recurse -Depth 1 | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
}

# Main execution
if (-not (Test-DockerRunning)) {
    exit 1
}

switch ($Action) {
    'build' { Build-Container }
    'up' { Start-Container }
    'down' { Stop-Container }
    'restart' { Restart-Container }
    'logs' { Show-Logs }
    'shell' { Open-Shell }
    'clean' { Clean-Docker }
    'status' { Show-Status }
}

Write-Host "`n=== Done! ===" -ForegroundColor Cyan
