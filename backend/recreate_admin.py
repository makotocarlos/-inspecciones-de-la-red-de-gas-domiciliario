#!/usr/bin/env python
"""
Script to recreate admin user with correct password hasher
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser

print('=' * 50)
print('RECREANDO USUARIO ADMIN')
print('=' * 50)

# Delete existing admin if exists
try:
    admin = CustomUser.objects.get(email='admin@inspecgas.com')
    admin.delete()
    print('✅ Usuario admin anterior eliminado')
except CustomUser.DoesNotExist:
    print('ℹ️  No había usuario admin previo')

# Create new admin user
admin = CustomUser.objects.create_superuser(
    username='admin',
    email='admin@inspecgas.com',
    password='admin123'
)
admin.role = 'ADMIN'
admin.first_name = 'Administrador'
admin.last_name = 'Sistema'
admin.save()

print('✅ Admin recreado exitosamente!')
print('=' * 50)
print('Usuario: admin')
print('Email: admin@inspecgas.com')
print('Contraseña: admin123')
print('Rol: ADMIN')
print('=' * 50)
print('\n🔗 Inicia sesión en: http://localhost:3000/login')
print('📊 Panel admin: http://localhost:3000/admin')
print('\n✅ Ahora el login debería funcionar correctamente')
