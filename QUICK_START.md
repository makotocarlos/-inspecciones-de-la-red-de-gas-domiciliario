# 🚀 INICIO RÁPIDO

## Para empezar a trabajar AHORA MISMO:

### Windows

```bash
cd backend
start.bat
```

### Linux/Mac

```bash
cd backend
chmod +x start.sh
./start.sh
```

## Si es la primera vez:

```bash
# 1. Instalar dependencias
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 2. Configurar .env
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
# Edita .env con tus credenciales de PostgreSQL

# 3. Crear base de datos en PostgreSQL
# Abre pgAdmin o psql y ejecuta:
# CREATE DATABASE base;

# 4. Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Iniciar servidor
python manage.py runserver
```

## Accede a:

- 🌐 **API**: http://localhost:8000
- 📚 **Documentación**: http://localhost:8000/api/docs
- 👑 **Admin**: http://localhost:8000/admin

## Usuarios de prueba:

Ver `INSTALLATION_GUIDE.md` sección "Crear Usuarios de Prueba"

---

**¿Problemas?** Consulta `INSTALLATION_GUIDE.md` para guía detallada.
