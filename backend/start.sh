#!/bin/bash
# ================================================
# SCRIPT DE INICIO RÁPIDO - BACKEND
# Sistema de Gestión de Inspecciones de Gas v2.0
# ================================================

echo ""
echo "===================================="
echo " INICIANDO BACKEND"
echo "===================================="
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "[ERROR] No se encontró el entorno virtual."
    echo ""
    echo "Ejecuta primero:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Activar entorno virtual
echo "[1/4] Activando entorno virtual..."
source venv/bin/activate

# Verificar base de datos
echo "[2/4] Verificando base de datos..."
python manage.py check --database default
if [ $? -ne 0 ]; then
    echo ""
    echo "[ADVERTENCIA] No se pudo conectar a la base de datos."
    echo "Verifica que PostgreSQL esté corriendo y las credenciales en .env sean correctas."
    echo ""
fi

# Aplicar migraciones pendientes
echo "[3/4] Aplicando migraciones..."
python manage.py migrate --no-input

# Iniciar servidor
echo "[4/4] Iniciando servidor de desarrollo..."
echo ""
echo "===================================="
echo " SERVIDOR LISTO"
echo "===================================="
echo ""
echo "Backend API: http://localhost:8000"
echo "Admin Panel: http://localhost:8000/admin"
echo "API Docs: http://localhost:8000/api/docs"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python manage.py runserver
