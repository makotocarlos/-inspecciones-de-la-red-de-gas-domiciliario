@echo off
REM ================================================
REM SCRIPT DE INICIO RÁPIDO - BACKEND
REM Sistema de Gestión de Inspecciones de Gas v2.0
REM ================================================

echo.
echo ====================================
echo  INICIANDO BACKEND
echo ====================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv\" (
    echo [ERROR] No se encontró el entorno virtual.
    echo.
    echo Ejecuta primero:
    echo   python -m venv venv
    echo   .\venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [1/4] Activando entorno virtual...
call .\venv\Scripts\activate

REM Verificar base de datos
echo [2/4] Verificando base de datos...
python manage.py check --database default
if errorlevel 1 (
    echo.
    echo [ADVERTENCIA] No se pudo conectar a la base de datos.
    echo Verifica que PostgreSQL esté corriendo y las credenciales en .env sean correctas.
    echo.
)

REM Aplicar migraciones pendientes
echo [3/4] Aplicando migraciones...
python manage.py migrate --no-input

REM Iniciar servidor
echo [4/4] Iniciando servidor de desarrollo...
echo.
echo ====================================
echo  SERVIDOR LISTO
echo ====================================
echo.
echo Backend API: http://localhost:8000
echo Admin Panel: http://localhost:8000/admin
echo API Docs: http://localhost:8000/api/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python manage.py runserver

pause
