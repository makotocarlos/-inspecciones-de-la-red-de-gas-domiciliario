#!/usr/bin/env python
"""
Script to create admin user for the system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser

# Check if admin already exists
if CustomUser.objects.filter(username='admin').exists():
    print('❌ El usuario admin ya existe')
    admin = CustomUser.objects.get(username='admin')
    print(f'Usuario: {admin.username}')
    print(f'Email: {admin.email}')
    print(f'Rol: {admin.role}')
else:
    # Create admin user
    admin = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@inspecgas.com',
        password='admin123'
    )
    admin.role = 'ADMIN'
    admin.first_name = 'Administrador'
    admin.last_name = 'Sistema'
    admin.save()
    
    print('✅ Admin creado exitosamente!')
    print('=' * 50)
    print('Usuario: admin')
    print('Email: admin@inspecgas.com')
    print('Contraseña: admin123')
    print('Rol: ADMIN')
    print('=' * 50)
    print('\n🔗 Inicia sesión en: http://localhost:3001/login')
    print('📊 Panel admin: http://localhost:3001/admin')
