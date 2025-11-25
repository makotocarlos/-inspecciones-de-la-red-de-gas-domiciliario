# 🚀 Guía de Despliegue a Producción

## 📋 Checklist Pre-Despliegue

### 1. Configuración de Producción

#### ✅ Variables de Entorno
Actualizar `.env` para producción:

```env
# Django Settings
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com,api.tudominio.com
SECRET_KEY=generar-nueva-clave-secreta-larga-y-compleja
JWT_SECRET_KEY=generar-otra-clave-diferente-para-jwt

# Database (PostgreSQL en servidor)
DB_NAME=inspeccion_gas_prod
DB_USER=usuario_prod
DB_PASSWORD=contraseña-segura-generada
DB_HOST=tu-servidor-db.com
DB_PORT=5432

# Email (Producción con SendGrid/SES)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=tu-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@tudominio.com

# Frontend URL
FRONTEND_URL=https://tudominio.com

# CORS (Solo dominios permitidos)
CORS_ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Redis (para Celery)
REDIS_URL=redis://tu-servidor-redis:6379/0

# Sentry (Monitoreo de errores - opcional)
SENTRY_DSN=tu-sentry-dsn
```

#### ✅ Seguridad
```python
# En core/settings.py ya configurado:
- DEBUG = False
- ALLOWED_HOSTS verificado
- CORS_ALLOWED_ORIGINS solo dominios seguros
- SECURE_SSL_REDIRECT = True
- CSRF_COOKIE_SECURE = True
- SESSION_COOKIE_SECURE = True
- SECURE_HSTS configurado
```

### 2. Base de Datos

#### Crear Base de Datos PostgreSQL
```sql
CREATE DATABASE inspeccion_gas_prod;
CREATE USER usuario_prod WITH PASSWORD 'contraseña-segura';
ALTER ROLE usuario_prod SET client_encoding TO 'utf8';
ALTER ROLE usuario_prod SET default_transaction_isolation TO 'read committed';
ALTER ROLE usuario_prod SET timezone TO 'America/Bogota';
GRANT ALL PRIVILEGES ON DATABASE inspeccion_gas_prod TO usuario_prod;
```

#### Ejecutar Migraciones
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

#### Crear Plantillas de Email
```bash
python manage.py shell < create_email_templates.py
```

### 3. Archivos Estáticos y Media

#### Configurar Almacenamiento

**Opción A: AWS S3 (Recomendado)**

Instalar:
```bash
pip install django-storages boto3
```

Agregar a `settings.py`:
```python
# AWS S3 Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = None
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

# Static files
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

# Media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

**Opción B: Servidor Local con Nginx**
```bash
python manage.py collectstatic
```

## 🌐 Opciones de Despliegue

### Opción 1: Railway (Más Fácil)

#### 1. Preparar proyecto
Crear `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn core.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Crear `Procfile`:
```
web: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A core worker -l info
```

#### 2. Instalar Railway CLI
```bash
npm install -g @railway/cli
railway login
```

#### 3. Desplegar
```bash
cd backend
railway init
railway add  # Agregar PostgreSQL y Redis
railway up
```

#### 4. Configurar Variables
En Railway Dashboard, agregar todas las variables de `.env`

### Opción 2: Heroku

#### 1. Preparar proyecto
```bash
pip install gunicorn whitenoise
pip freeze > requirements.txt
```

Crear `Procfile`:
```
web: gunicorn core.wsgi:application
worker: celery -A core worker -l info
```

Crear `runtime.txt`:
```
python-3.11.7
```

#### 2. Desplegar
```bash
heroku login
heroku create nombre-app
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=tu-secret-key
# ... configurar todas las variables

git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py shell < create_email_templates.py
```

### Opción 3: DigitalOcean (VPS)

#### 1. Crear Droplet Ubuntu 22.04

#### 2. Configurar Servidor
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3.11 python3.11-venv python3-pip nginx postgresql postgresql-contrib redis-server -y

# Configurar PostgreSQL
sudo -u postgres psql
CREATE DATABASE inspeccion_gas_prod;
CREATE USER usuario_prod WITH PASSWORD 'contraseña-segura';
GRANT ALL PRIVILEGES ON DATABASE inspeccion_gas_prod TO usuario_prod;
\q
```

#### 3. Clonar y Configurar Proyecto
```bash
cd /var/www
sudo git clone <tu-repo> inspeccion-gas
cd inspeccion-gas/backend
sudo python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configurar .env
sudo nano .env
# Copiar configuración de producción

# Migraciones
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 4. Configurar Gunicorn
Crear `/etc/systemd/system/inspeccion-gas.service`:
```ini
[Unit]
Description=Inspeccion Gas Django App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/inspeccion-gas/backend
Environment="PATH=/var/www/inspeccion-gas/backend/venv/bin"
ExecStart=/var/www/inspeccion-gas/backend/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/inspeccion-gas/backend/gunicorn.sock \
          core.wsgi:application

[Install]
WantedBy=multi-user.target
```

Iniciar servicio:
```bash
sudo systemctl start inspeccion-gas
sudo systemctl enable inspeccion-gas
```

#### 5. Configurar Nginx
Crear `/etc/nginx/sites-available/inspeccion-gas`:
```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/inspeccion-gas/backend/static/;
    }
    
    location /media/ {
        alias /var/www/inspeccion-gas/backend/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/inspeccion-gas/backend/gunicorn.sock;
    }
}
```

Activar sitio:
```bash
sudo ln -s /etc/nginx/sites-available/inspeccion-gas /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Configurar SSL (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

### Opción 4: AWS (EC2 + RDS + S3)

#### 1. Crear Infraestructura
- **EC2**: Instancia t3.medium (Ubuntu 22.04)
- **RDS**: PostgreSQL 15
- **S3**: Bucket para static y media
- **ElastiCache**: Redis

#### 2. Configurar igual que DigitalOcean + AWS S3 Storage

## 🔄 Configurar Celery (Tareas Asíncronas)

### 1. Crear archivo `core/celery.py`:
```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 2. Actualizar `core/__init__.py`:
```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 3. Configurar en `settings.py`:
```python
# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Bogota'
```

### 4. Iniciar Workers
```bash
# Development
celery -A core worker -l info

# Production (con Supervisor)
# Crear /etc/supervisor/conf.d/celery.conf
```

## 📊 Monitoreo y Logging

### 1. Sentry (Monitoreo de Errores)
```bash
pip install sentry-sdk
```

En `settings.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=config('SENTRY_DSN', ''),
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True,
    environment='production'
)
```

### 2. Logging a Archivo
Ya configurado en `settings.py`:
```python
LOGGING = {
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
        },
    },
}
```

## ✅ Checklist Post-Despliegue

- [ ] Base de datos migrada
- [ ] Superusuario creado
- [ ] Plantillas de email creadas
- [ ] Static files colectados
- [ ] SSL configurado (HTTPS)
- [ ] Variables de entorno configuradas
- [ ] Backup de base de datos configurado
- [ ] Monitoring (Sentry) configurado
- [ ] DNS apuntando al servidor
- [ ] Email funcionando (enviar test)
- [ ] PDFs generándose correctamente
- [ ] Celery workers ejecutándose
- [ ] Logs rotándose correctamente

## 🔐 Backups

### Script de Backup Automático
Crear `backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="inspeccion_gas_prod"

# Backup de base de datos
pg_dump $DB_NAME > $BACKUP_DIR/db_$DATE.sql

# Backup de media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/inspeccion-gas/backend/media/

# Eliminar backups antiguos (>30 días)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Cron job (diario a las 2 AM):
```bash
crontab -e
0 2 * * * /path/to/backup.sh
```

## 📞 Soporte y Mantenimiento

### Logs Importantes
```bash
# Django logs
tail -f /var/www/inspeccion-gas/backend/logs/django.log

# Gunicorn logs
sudo journalctl -u inspeccion-gas -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Reiniciar Servicios
```bash
sudo systemctl restart inspeccion-gas
sudo systemctl restart nginx
sudo systemctl restart redis
```

¡Backend listo para producción! 🚀
