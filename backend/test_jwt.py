#!/usr/bin/env python
"""
Script to test JWT token generation and validation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

print("=" * 60)
print("TESTING JWT TOKEN GENERATION")
print("=" * 60)

try:
    # Get admin user
    admin = CustomUser.objects.get(email='admin@inspecgas.com')
    print(f"Usuario encontrado: {admin.email}")
    print(f"Username: {admin.username}")
    print(f"Rol: {admin.role}")
    print(f"Activo: {admin.is_active}")

    # Generate JWT token
    print("\nGenerando token JWT...")
    refresh = RefreshToken.for_user(admin)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    print(f"Access Token generado: {access_token[:50]}...")
    print(f"Refresh Token generado: {refresh_token[:50]}...")

    # Verify token
    print("\nVerificando token...")
    from rest_framework_simplejwt.tokens import AccessToken
    try:
        token_obj = AccessToken(access_token)
        print(f"Token valido!")
        print(f"User ID en token: {token_obj.get('user_id')}")
        print(f"Token type: {token_obj.get('token_type')}")
    except Exception as e:
        print(f"Error validando token: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)

except CustomUser.DoesNotExist:
    print("ERROR: Usuario admin no encontrado")
    print("Ejecuta: python recreate_admin.py")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n")
