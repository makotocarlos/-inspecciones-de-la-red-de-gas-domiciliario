#!/usr/bin/env python
"""
Script to update admin password
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser

try:
    admin = CustomUser.objects.get(username='admin')
    admin.set_password('admin123')
    admin.email = 'admin@inspecgas.com'
    admin.role = 'ADMIN'
    admin.first_name = 'Administrador'
    admin.last_name = 'Sistema'
    admin.save()
    
    print('✅ Admin actualizado exitosamente!')
    print('=' * 50)
    print('Usuario: admin')
    print('Email: admin@inspecgas.com')
    print('Contraseña: admin123')
    print('Rol: ADMIN')
    print('=' * 50)
    print('\n🔗 Inicia sesión en: http://localhost:3001/login')
    print('📊 Panel admin: http://localhost:3001/admin')
except CustomUser.DoesNotExist:
    print('❌ Usuario admin no encontrado')
