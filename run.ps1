# Virtual Fashion Try-On Launch Script
# Usage: .\run.ps1
# Encoding: UTF-8 with BOM

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Starting Virtual Fashion Try-On..." -ForegroundColor Cyan

# Check virtual environment
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found." -ForegroundColor Red
    Write-Host "Please run setup.ps1 first:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1" -ForegroundColor Cyan
    exit 1
}

# Activate virtual environment (if not already activated)
if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment is already activated." -ForegroundColor Green
} else {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Could not activate via script." -ForegroundColor Yellow
        Write-Host "Trying alternative method..." -ForegroundColor Yellow
    }
}

# Launch application using venv's Python directly
Write-Host "Launching application..." -ForegroundColor Green
$pythonPath = if (Test-Path "venv\Scripts\python.exe") { "venv\Scripts\python.exe" } else { "python" }
& $pythonPath app/main.py

# Exit handling
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Application exited with an error." -ForegroundColor Red
    Write-Host "Please check the error message above." -ForegroundColor Yellow
}

