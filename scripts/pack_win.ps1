# PyInstaller Build Script for Windows

Write-Host "Virtual Fashion Try-On - Windows Build Script" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# Check virtual environment
if (-not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "Error: Virtual environment not found." -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check PyInstaller installation
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Clean previous build
Write-Host "`nCleaning previous build..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force build
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force dist
}

# Build executable
Write-Host "`nBuilding executable..." -ForegroundColor Yellow

pyinstaller --clean `
    --name="VirtualFashionTryOn" `
    --windowed `
    --onefile `
    --add-data "app/assets;assets" `
    --hidden-import=PySide6 `
    --hidden-import=PySide6.QtCore `
    --hidden-import=PySide6.QtGui `
    --hidden-import=PySide6.QtWidgets `
    --hidden-import=cv2 `
    --hidden-import=sklearn `
    --hidden-import=sklearn.cluster `
    --hidden-import=lpips `
    --hidden-import=google.generativeai `
    --hidden-import=google.genai `
    --hidden-import=ui `
    --hidden-import=ui.main_window `
    --hidden-import=ui.widgets `
    --hidden-import=ui.widgets.garment_slot `
    --hidden-import=ui.widgets.gallery_view `
    --hidden-import=ui.widgets.api_key_dialog `
    --hidden-import=ui.widgets.info_dialog `
    --hidden-import=models `
    --hidden-import=core `
    --hidden-import=core.adapters `
    --hidden-import=core.pipeline `
    --hidden-import=core.vton `
    --hidden-import=utils `
    --paths=app `
    --exclude-module=verification `
    --exclude-module=tests `
    --exclude-module=pytest `
    app/main.py

# Check build result
if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild successful!" -ForegroundColor Green
    Write-Host "Executable: dist\VirtualFashionTryOn.exe" -ForegroundColor Green
    
    # Create distribution package
    Write-Host "`nCreating distribution package..." -ForegroundColor Yellow
    $distFolder = "VirtualFashionTryOn_v2.0"
    
    if (Test-Path $distFolder) {
        Remove-Item -Recurse -Force $distFolder
    }
    
    New-Item -ItemType Directory -Path $distFolder | Out-Null
    Copy-Item "dist\VirtualFashionTryOn.exe" $distFolder
    
    if (Test-Path "使い方ガイド.txt") {
        Copy-Item "使い方ガイド.txt" $distFolder
    }
    
    if (Test-Path "README.md") {
        Copy-Item "README.md" "$distFolder\README.txt"
    }
    
    Write-Host "`nPackage created: $distFolder\" -ForegroundColor Green
    Write-Host "Contents:" -ForegroundColor Cyan
    Write-Host "  - VirtualFashionTryOn.exe (実行ファイル)" -ForegroundColor Cyan
    Write-Host "  - 使い方ガイド.txt (使用方法)" -ForegroundColor Cyan
    Write-Host "  - README.txt (概要)" -ForegroundColor Cyan
    Write-Host "`nNote: 単一ファイル形式（起動に20-60秒かかります）" -ForegroundColor Yellow
    Write-Host "Note: verificationディレクトリは除外されました" -ForegroundColor Yellow
    
    # Create ZIP
    Write-Host "`nCreating ZIP archive..." -ForegroundColor Yellow
    $zipFile = "VirtualFashionTryOn_v2.0.zip"
    if (Test-Path $zipFile) {
        Remove-Item -Force $zipFile
    }
    Compress-Archive -Path $distFolder -DestinationPath $zipFile
    Write-Host "ZIP created: $zipFile" -ForegroundColor Green
    
} else {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`nBuild completed!" -ForegroundColor Green

