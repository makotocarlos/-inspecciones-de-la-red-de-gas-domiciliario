# 🚀 GUÍA DE INSTALACIÓN Y EJECUCIÓN COMPLETA

## Sistema de Gestión de Inspecciones de Gas Domiciliario v2.0

---

## 📋 REQUISITOS PREVIOS

### Software Necesario
- **Python 3.10+** ([Descargar](https://www.python.org/downloads/))
- **PostgreSQL 13+** ([Descargar](https://www.postgresql.org/download/))
- **Node.js 18+** y npm ([Descargar](https://nodejs.org/))
- **Git** ([Descargar](https://git-scm.com/))

### Verificar Instalaciones
```bash
python --version
psql --version
node --version
npm --version
```

---

## ⚙️ INSTALACIÓN DEL BACKEND

### Paso 1: Configurar PostgreSQL

1. **Abrir pgAdmin o psql** y ejecutar:

```sql
-- Crear base de datos
CREATE DATABASE base;

-- Crear usuario (si no existe)
CREATE USER person WITH PASSWORD 'CaMa897';

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE base TO person;

-- Conectarse a la base de datos
\c base

-- Otorgar permisos en el schema public
GRANT ALL ON SCHEMA public TO person;
```

### Paso 2: Configurar el Entorno de Python

```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Verificar que el entorno esté activo (debe aparecer (venv) en el prompt)
```

### Paso 3: Instalar Dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar todas las dependencias
pip install -r requirements.txt

# Si hay errores, instalar uno por uno:
pip install Django==5.0.1
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.1
pip install django-cors-headers==4.3.1
pip install psycopg2-binary==2.9.9
pip install python-decouple==3.8
pip install django-phonenumber-field==7.3.0
pip install phonenumbers==8.13.27
pip install Pillow==10.2.0
pip install drf-spectacular==0.27.0
pip install django-filter==23.5
```

### Paso 4: Configurar Variables de Entorno

```bash
# Crear archivo .env en el directorio backend/
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Editar .env con tus configuraciones
notepad .env  # Windows
# nano .env   # Linux/Mac
```

**Contenido mínimo del .env:**
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui-cambiala-en-produccion
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=base
DB_USER=person
DB_PASSWORD=CaMa897
DB_HOST=localhost
DB_PORT=5432

JWT_SECRET_KEY=jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=7

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
FRONTEND_URL=http://localhost:3000
```

### Paso 5: Ejecutar Migraciones

```bash
# Crear migraciones
python manage.py makemigrations users
python manage.py makemigrations inspections
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Si hay errores, verificar:
# 1. Que PostgreSQL esté corriendo
# 2. Que la base de datos 'base' exista
# 3. Que las credenciales en .env sean correctas
```

### Paso 6: Crear Superusuario

```bash
python manage.py createsuperuser

# Ingresar:
# - Email: admin@gasinspection.com
# - Username: admin
# - Password: (tu contraseña segura)
# - First name: Admin
# - Last name: System
```

### Paso 7: Crear Usuarios de Prueba (Opcional)

```python
# Abrir shell de Django
python manage.py shell

# Ejecutar este código:
from users.models import CustomUser

# Crear inspector
inspector = CustomUser.objects.create_user(
    email='inspector@test.com',
    username='inspector1',
    password='Inspector123!',
    first_name='Juan',
    last_name='Inspector',
    role='INSPECTOR',
    license_number='INS-2024-001'
)

# Crear usuario regular
user = CustomUser.objects.create_user(
    email='user@test.com',
    username='user1',
    password='User123!',
    first_name='María',
    last_name='Usuario',
    role='USER'
)

print("✅ Usuarios de prueba creados")
exit()
```

### Paso 8: Recopilar Archivos Estáticos

```bash
python manage.py collectstatic --no-input
```

### Paso 9: Ejecutar el Servidor

```bash
# Modo desarrollo
python manage.py runserver

# El servidor estará disponible en: http://localhost:8000
```

### Verificar Instalación del Backend

Abrir en el navegador:
- **Admin Panel**: http://localhost:8000/admin
- **API Docs (Swagger)**: http://localhost:8000/api/docs
- **API Redoc**: http://localhost:8000/api/redoc

---

## 🎨 INSTALACIÓN DEL FRONTEND

### Paso 1: Instalar Dependencias

```bash
# Navegar al directorio del frontend
cd frontend

# Instalar dependencias
npm install

# Si hay errores, intentar:
npm install --legacy-peer-deps
```

### Paso 2: Configurar Variables de Entorno

```bash
# Crear archivo .env.local
copy .env.example .env.local  # Windows
# cp .env.example .env.local  # Linux/Mac
```

**Contenido del .env.local:**
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_MEDIA_URL=http://localhost:8000/media
```

### Paso 3: Ejecutar el Frontend

```bash
# Modo desarrollo
npm start

# El frontend estará disponible en: http://localhost:3000
```

### Construir para Producción

```bash
npm run build

# Los archivos se generarán en el directorio build/
```

---

## 🧪 PRUEBAS

### Backend
```bash
cd backend
python manage.py test

# Con cobertura
pip install pytest pytest-django pytest-cov
pytest --cov=. --cov-report=html
```

### Frontend
```bash
cd frontend
npm test
npm test -- --coverage
```

---

## 🔍 SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Error: "django.db.utils.OperationalError: FATAL: database does not exist"
```sql
-- En psql o pgAdmin:
CREATE DATABASE base;
```

### Error: "Port 8000 is already in use"
```bash
# Usar otro puerto
python manage.py runserver 8001

# O encontrar y matar el proceso en Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# En Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### Error: "CORS policy" en el frontend
- Verificar que `CORS_ALLOWED_ORIGINS` en `.env` incluya la URL del frontend
- Verificar que `django-cors-headers` esté instalado
- Verificar que `'corsheaders.middleware.CorsMiddleware'` esté en `MIDDLEWARE`

### Error al cargar imágenes
```bash
# Crear directorios de media
mkdir media
mkdir media\profiles
mkdir media\inspections
mkdir media\reports
```

---

## 📊 DATOS DE PRUEBA

### Credenciales por Defecto

#### Administrador
- **Email**: admin@gasinspection.com
- **Password**: (el que configuraste)
- **Rol**: ADMIN

#### Inspector
- **Email**: inspector@test.com
- **Password**: Inspector123!
- **Rol**: INSPECTOR

#### Usuario
- **Email**: user@test.com
- **Password**: User123!
- **Rol**: USER

---

## 🚀 COMANDOS ÚTILES

### Backend
```bash
# Crear nueva app
python manage.py startapp nombre_app

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell interactivo
python manage.py shell

# Crear superusuario
python manage.py createsuperuser

# Limpiar base de datos
python manage.py flush

# Ver SQL de migraciones
python manage.py sqlmigrate app_name migration_name
```

### Frontend
```bash
# Instalar nueva dependencia
npm install nombre-paquete

# Actualizar dependencias
npm update

# Limpiar caché
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Ver dependencias desactualizadas
npm outdated
```

---

## 📦 ESTRUCTURA DE ARCHIVOS IMPORTANTE

```
proyecto/
├── backend/
│   ├── core/
│   │   ├── settings.py     ← Configuración principal
│   │   ├── urls.py         ← URLs principales
│   │   └── utils/          ← Utilidades
│   ├── users/              ← Gestión de usuarios
│   ├── inspections/        ← Gestión de inspecciones
│   ├── media/              ← Archivos subidos
│   ├── logs/               ← Logs de aplicación
│   ├── .env                ← Variables de entorno ⚠️
│   ├── requirements.txt    ← Dependencias Python
│   └── manage.py           ← CLI de Django
│
└── frontend/
    ├── src/
    │   ├── components/     ← Componentes React
    │   ├── pages/          ← Páginas
    │   ├── services/       ← Servicios de API
    │   └── App.js          ← Componente principal
    ├── public/
    ├── .env.local          ← Variables de entorno ⚠️
    └── package.json        ← Dependencias Node
```

---

## 🔐 SEGURIDAD

### Antes de Producción
1. ✅ Cambiar `SECRET_KEY` y `JWT_SECRET_KEY`
2. ✅ Configurar `DEBUG=False`
3. ✅ Configurar `ALLOWED_HOSTS` correctamente
4. ✅ Usar HTTPS
5. ✅ Configurar firewall
6. ✅ Usar variables de entorno seguras
7. ✅ Activar SSL en PostgreSQL
8. ✅ Configurar backups automáticos

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisar los logs en `backend/logs/`
2. Consultar la consola del navegador (F12)
3. Verificar que todos los servicios estén corriendo
4. Revisar las configuraciones en `.env`

---

## ✅ CHECKLIST DE INSTALACIÓN

### Backend
- [ ] Python 3.10+ instalado
- [ ] PostgreSQL instalado y corriendo
- [ ] Base de datos 'base' creada
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Archivo `.env` configurado
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Servidor corriendo en puerto 8000

### Frontend
- [ ] Node.js 18+ instalado
- [ ] Dependencias instaladas con npm
- [ ] Archivo `.env.local` configurado
- [ ] Aplicación corriendo en puerto 3000
- [ ] Puede conectarse al backend

---

**¡Listo! El sistema está funcionando profesionalmente.**

Para cualquier duda, consulta el README.md principal.
