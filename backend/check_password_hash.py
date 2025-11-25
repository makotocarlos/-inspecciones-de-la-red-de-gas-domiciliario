#!/usr/bin/env python
"""
Check what password hasher the admin user is using
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser

print("=" * 60)
print("CHECKING PASSWORD HASH")
print("=" * 60)

try:
    admin = CustomUser.objects.get(email='admin@inspecgas.com')
    print(f"Usuario: {admin.email}")
    print(f"Password hash: {admin.password[:80]}...")

    # Determine hasher from hash prefix
    if admin.password.startswith('pbkdf2_sha256$'):
        print("Hasher: PBKDF2SHA256 (CORRECTO)")
    elif admin.password.startswith('argon2$'):
        print("Hasher: Argon2 (PROBLEMA - necesita reinstalarse)")
    elif admin.password.startswith('bcrypt'):
        print("Hasher: BCrypt")
    else:
        print(f"Hasher: Desconocido - {admin.password[:20]}")

    print("\n" + "=" * 60)

except CustomUser.DoesNotExist:
    print("ERROR: Usuario admin no encontrado")
except Exception as e:
    print(f"ERROR: {e}")

print("\n")
