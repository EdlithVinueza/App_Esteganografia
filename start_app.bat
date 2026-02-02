@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo    Video Steganography App - Iniciar / Instalar
echo ======================================================

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado o no se encuentra en el PATH.
    echo Por favor, instala Python 3.10 o superior.
    pause
    exit /b 1
)

:: Crear venv si no existe
if not exist "venv" (
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

:: Instalar dependencias
echo [INFO] Verificando e instalando dependencias...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Error al instalar las dependencias.
    pause
    exit /b 1
)

:: Ejecutar aplicación
echo [INFO] Iniciando aplicación...
venv\Scripts\python.exe main.py

if %errorlevel% neq 0 (
    echo [AVISO] La aplicación se cerró con un error.
    pause
)

endlocal
