# Script PowerShell para ejecutar la aplicación
# Uso: .\run.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Video Steganography Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que existe el entorno virtual
if (!(Test-Path "venv\Scripts\python.exe")) {
    Write-Host "✗ Error: No se encontró el entorno virtual" -ForegroundColor Red
    Write-Host "Por favor ejecuta primero: python -m venv venv" -ForegroundColor Yellow
    Write-Host "Y luego: venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✓ Entorno virtual encontrado" -ForegroundColor Green
Write-Host ""
Write-Host "Ejecutando aplicación..." -ForegroundColor Yellow
Write-Host ""

# Ejecutar la aplicación usando el Python del entorno virtual
& "venv\Scripts\python.exe" "main.py"

Write-Host ""
Write-Host "Aplicación cerrada." -ForegroundColor Cyan
