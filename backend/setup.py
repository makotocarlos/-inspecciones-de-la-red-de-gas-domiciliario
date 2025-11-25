#!/usr/bin/env python
"""
🚀 SCRIPT DE INSTALACIÓN Y CONFIGURACIÓN PROFESIONAL
Sistema de Gestión de Inspecciones de Gas Domiciliario v2.0

Este script:
1. Instala todas las dependencias
2. Configura la base de datos
3. Crea las migraciones
4. Carga datos iniciales
5. Crea superusuario
"""

import os
import subprocess
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"📌 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e.stderr}")
        return False

def main():
    print_header("INSTALACIÓN DEL SISTEMA DE GESTIÓN DE INSPECCIONES DE GAS")
    
    # 1. Verificar Python
    print_header("1. Verificando Python")
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("❌ Se requiere Python 3.10 o superior")
        sys.exit(1)
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detectado")
    
    # 2. Crear entorno virtual
    print_header("2. Configurando entorno virtual")
    if not Path("venv").exists():
        run_command("python -m venv venv", "Creando entorno virtual")
    else:
        print("   ℹ️  Entorno virtual ya existe")
    
    # 3. Activar entorno virtual y instalar dependencias
    print_header("3. Instalando dependencias")
    
    if os.name == 'nt':  # Windows
        pip_cmd = ".\\venv\\Scripts\\pip"
        python_cmd = ".\\venv\\Scripts\\python"
    else:  # Linux/Mac
        pip_cmd = "./venv/bin/pip"
        python_cmd = "./venv/bin/python"
    
    run_command(f"{pip_cmd} install --upgrade pip", "Actualizando pip")
    run_command(f"{pip_cmd} install -r requirements.txt", "Instalando dependencias de Python")
    
    # 4. Crear archivo .env si no existe
    print_header("4. Configurando variables de entorno")
    if not Path(".env").exists():
        print("   📝 Creando archivo .env...")
        with open(".env", "w") as f:
            f.write("""# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production-xyz123-abc
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=base
DB_USER=person
DB_PASSWORD=CaMa897
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_SECRET_KEY=jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7

# Email (Configure with your credentials)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@gasinspection.com

# Frontend
FRONTEND_URL=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0
""")
        print("   ✅ Archivo .env creado")
        print("   ⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones")
    else:
        print("   ℹ️  Archivo .env ya existe")
    
    # 5. Crear directorios necesarios
    print_header("5. Creando estructura de directorios")
    dirs = ['logs', 'media', 'media/profiles', 'media/inspections', 'media/inspections/photos', 
            'media/reports', 'static', 'staticfiles', 'templates']
    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    print("   ✅ Directorios creados")
    
    # 6. Ejecutar migraciones
    print_header("6. Configurando base de datos")
    print("   ⚠️  Asegúrate de que PostgreSQL esté corriendo y la base de datos 'base' exista")
    
    input("   Presiona ENTER cuando PostgreSQL esté listo...")
    
    run_command(f"{python_cmd} manage.py makemigrations", "Generando migraciones")
    run_command(f"{python_cmd} manage.py migrate", "Aplicando migraciones")
    
    # 7. Crear superusuario
    print_header("7. Creando superusuario")
    print("   A continuación se te pedirán los datos del administrador:")
    os.system(f"{python_cmd} manage.py createsuperuser")
    
    # 8. Recopilar archivos estáticos
    print_header("8. Recopilando archivos estáticos")
    run_command(f"{python_cmd} manage.py collectstatic --no-input", "Recopilando archivos estáticos")
    
    # 9. Resumen final
    print_header("✅ INSTALACIÓN COMPLETADA")
    print("""
    🎉 ¡El sistema está listo para usar!
    
    📝 PRÓXIMOS PASOS:
    
    1. Revisa y actualiza el archivo .env con tus configuraciones
    2. Para iniciar el servidor de desarrollo:
       
       Windows:
       .\\venv\\Scripts\\activate
       python manage.py runserver
       
       Linux/Mac:
       source venv/bin/activate
       python manage.py runserver
    
    3. Accede al sistema en: http://localhost:8000
    4. Panel de administración: http://localhost:8000/admin
    5. Documentación API: http://localhost:8000/api/docs
    
    📚 DOCUMENTACIÓN:
    - README.md: Guía completa del sistema
    - API Endpoints: Ver README.md sección "API Endpoints"
    
    🔐 SEGURIDAD:
    - Cambia SECRET_KEY y JWT_SECRET_KEY en producción
    - Configura las variables de email
    - Usa HTTPS en producción
    
    ⚠️  RECUERDA:
    - PostgreSQL debe estar corriendo
    - Configura el frontend por separado (ver frontend/README.md)
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error durante la instalación: {e}")
        sys.exit(1)
