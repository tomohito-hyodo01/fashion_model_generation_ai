# Virtual Fashion Try-On Setup Script
# Usage: .\setup.ps1
# Encoding: UTF-8 with BOM

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Virtual Fashion Try-On Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Python version check
Write-Host "Step 1: Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host $pythonVersion -ForegroundColor Green

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed." -ForegroundColor Red
    Write-Host "Please install from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Step 2: Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Step 3: Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Execution policy error detected." -ForegroundColor Yellow
    Write-Host "Please run the following command:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    exit 1
}

Write-Host "Virtual environment activated." -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow
Write-Host "(This may take several minutes)" -ForegroundColor Gray

pip install --upgrade pip

# 必須パッケージをインストール
Write-Host "Installing core dependencies..." -ForegroundColor Gray
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "Core dependencies installed successfully." -ForegroundColor Green
    
    # オプショナルパッケージ（mediapipe）を試みる
    Write-Host ""
    Write-Host "Step 4.5: Installing optional packages..." -ForegroundColor Yellow
    Write-Host "(MediaPipe for pose detection - may fail on Python 3.12)" -ForegroundColor Gray
    
    pip install mediapipe==0.10.9 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MediaPipe installed successfully." -ForegroundColor Green
    } else {
        Write-Host "MediaPipe installation skipped (compatibility issue)." -ForegroundColor Yellow
        Write-Host "Note: Pose detection from custom images will not be available." -ForegroundColor Gray
        Write-Host "      But all other features will work normally." -ForegroundColor Gray
    }
} else {
    Write-Host "ERROR: Failed to install dependencies." -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Red
    exit 1
}

# Copy .env.example if needed
Write-Host ""
Write-Host "Step 5: Checking configuration files..." -ForegroundColor Yellow
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env file created (you can edit it later)." -ForegroundColor Green
} else {
    Write-Host "Configuration file exists or is not needed." -ForegroundColor Green
}

# Create assets directory
if (-not (Test-Path "app/assets/icons")) {
    New-Item -ItemType Directory -Path "app/assets/icons" -Force | Out-Null
    Write-Host "Assets directory created." -ForegroundColor Green
}

# Completion message
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  python app/main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Start the application" -ForegroundColor White
Write-Host "  2. Configure API keys (dialog will appear on first launch)" -ForegroundColor White
Write-Host "  3. Upload clothing images and try it out!" -ForegroundColor White
Write-Host ""
Write-Host "If you encounter any issues, refer to USAGE.md" -ForegroundColor Gray
Write-Host ""

