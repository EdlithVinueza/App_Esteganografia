# Script para configurar el entorno virtual y ejecutar la aplicación
# Windows PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Video Steganography - Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python está instalado
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "✗ Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor instala Python desde https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Crear entorno virtual si no existe
Write-Host ""
Write-Host "[2/5] Configurando entorno virtual..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✓ Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "✓ Entorno virtual ya existe" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host ""
Write-Host "[3/5] Activando entorno virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host "✓ Entorno virtual activado" -ForegroundColor Green

# Actualizar pip
Write-Host ""
Write-Host "[4/5] Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip actualizado" -ForegroundColor Green

# Instalar dependencias
Write-Host ""
Write-Host "[5/5] Instalando dependencias..." -ForegroundColor Yellow
Write-Host "Esto puede tomar varios minutos..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet
Write-Host "✓ Dependencias instaladas" -ForegroundColor Green

# Mensaje final
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ Configuración completada" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ejecutar la aplicación:" -ForegroundColor Yellow
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANTE: Asegúrate de tener FFmpeg instalado" -ForegroundColor Red
Write-Host "Descarga desde: https://ffmpeg.org/download.html" -ForegroundColor Cyan
Write-Host ""
