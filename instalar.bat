@echo off
REM ========================================
REM  Instalación Automática del Entorno
REM  Video Steganography
REM ========================================

echo.
echo ========================================
echo   INSTALACION DEL ENTORNO VIRTUAL
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor instala Python desde https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python encontrado
echo.

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo [2/4] Creando entorno virtual...
    python -m venv venv
    echo       Entorno virtual creado!
) else (
    echo [2/4] Entorno virtual ya existe
)
echo.

REM Actualizar pip
echo [3/4] Actualizando pip...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
echo       pip actualizado!
echo.

REM Instalar dependencias
echo [4/4] Instalando dependencias...
echo       Esto puede tomar varios minutos...
venv\Scripts\python.exe -m pip install -r requirements.txt
echo.

if errorlevel 1 (
    echo [ERROR] Hubo un problema al instalar las dependencias
    echo Revisa el archivo SOLUCION_PROBLEMAS.md
    pause
    exit /b 1
)

echo.
echo ========================================
echo   INSTALACION COMPLETADA!
echo ========================================
echo.
echo Para ejecutar la aplicacion:
echo   1. Doble click en run.bat
echo   2. O ejecuta: venv\Scripts\python.exe main.py
echo.
pause
