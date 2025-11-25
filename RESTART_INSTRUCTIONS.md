# 🔧 Instrucciones para Resolver el Error de Autenticación

## Problema Identificado
El error "El token dado no es valido" y los errores 500 en el login se deben a que Django intentaba usar Argon2 para verificar contraseñas, pero el módulo no está instalado.

## ✅ Solución Aplicada
He eliminado Argon2 de los hashers de contraseñas en `backend/core/settings.py`. Ahora solo usa PBKDF2, que es seguro y está disponible.

## 📋 Pasos para Aplicar la Solución

### 1. Detener el Servidor Django
Si el servidor está corriendo, detenlo presionando `Ctrl+C` en la terminal donde está corriendo.

### 2. Reiniciar el Servidor Django
```bash
cd backend
python manage.py runserver
```

### 3. Reiniciar el Frontend (si está corriendo)
En otra terminal:
```bash
cd frontend
npm start
```

### 4. Probar el Login
1. Abre tu navegador en: http://localhost:3000/login
2. Usa las credenciales:
   - **Email:** admin@inspecgas.com
   - **Contraseña:** admin123
3. Deberías poder iniciar sesión exitosamente

### 5. Crear Usuarios Call Center o Inspectores
1. Una vez logueado como admin, ve a: http://localhost:3000/admin
2. Haz clic en las pestañas "Call Center" o "Inspectores"
3. Haz clic en "Crear Call Center" o "Crear Inspector"
4. Llena el formulario y envía
5. Se mostrará una ventana modal con la contraseña temporal generada
6. Copia las credenciales para compartirlas con el nuevo usuario

## 🧪 Verificación de la Solución

He creado varios scripts de prueba que confirman que todo funciona:

```bash
cd backend

# Verificar admin
python check_password_hash.py

# Probar generación de tokens JWT
python test_jwt.py

# Probar flujo completo de autenticación
python test_full_auth.py
```

Todos estos tests pasan exitosamente, lo que confirma que:
- ✅ El usuario admin existe
- ✅ La contraseña funciona correctamente
- ✅ Los tokens JWT se generan correctamente
- ✅ Los tokens se validan correctamente
- ✅ Los permisos de admin funcionan

## 🔍 Cambios Realizados

### `backend/core/settings.py` (línea 266-269)
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]
```

**Antes tenía Argon2 y BCrypt, que causaban errores porque no estaban instalados.**

## ❓ Si Aún Tienes Problemas

1. **Error 500 en login:** Asegúrate de haber reiniciado el servidor Django después del cambio
2. **Token inválido:** Borra localStorage en el navegador:
   - Abre DevTools (F12)
   - Ve a Application > Local Storage
   - Borra todas las entradas
   - Intenta hacer login de nuevo
3. **Usuario no encontrado:** Ejecuta `python recreate_admin.py` para recrear el admin

## 📝 Notas Importantes

- La contraseña del admin es: **admin123**
- Los call centers e inspectores reciben contraseñas temporales de 12 caracteres
- Las contraseñas incluyen mayúsculas, minúsculas, números y símbolos especiales (@#$%&*)
- Los usuarios pueden cambiar su contraseña después del primer login
- Las contraseñas se almacenan con PBKDF2-SHA256, que es muy seguro (720,000 iteraciones)

## ✨ Sistema Listo

Una vez reiniciado el servidor, el sistema debería funcionar completamente:
- ✅ Login de admin
- ✅ Panel de administrador
- ✅ Creación de call centers
- ✅ Creación de inspectores
- ✅ Generación automática de contraseñas
- ✅ Modal con credenciales temporales
- ✅ Copiar al portapapeles
