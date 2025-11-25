#!/usr/bin/env python
"""
Script para probar el login y ver qué error ocurre
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser
from users.serializers import UserSerializer

print("=" * 60)
print("VERIFICANDO USUARIO ADMIN")
print("=" * 60)

try:
    # Buscar usuario admin
    admin = CustomUser.objects.get(email='admin@inspecgas.com')
    print(f"✅ Usuario encontrado:")
    print(f"   Email: {admin.email}")
    print(f"   Username: {admin.username}")
    print(f"   Rol: {admin.role}")
    print(f"   Activo: {admin.is_active}")

    # Verificar contraseña
    print(f"\n🔑 Verificando contraseña...")
    if admin.check_password('admin123'):
        print(f"   ✅ Contraseña correcta")
    else:
        print(f"   ❌ Contraseña incorrecta")

    # Probar serializer
    print(f"\n📦 Probando serializer...")
    try:
        serializer = UserSerializer(admin)
        print(f"   ✅ Serializer funcionó correctamente")
        print(f"   Datos: {serializer.data}")
    except Exception as e:
        print(f"   ❌ Error en serializer: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()

except CustomUser.DoesNotExist:
    print("❌ Usuario admin NO encontrado")
    print("\nEjecuta: python create_admin.py")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
