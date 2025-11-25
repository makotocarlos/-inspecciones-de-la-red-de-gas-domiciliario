#!/usr/bin/env python
"""
Script to test authenticated request simulation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import RequestFactory
from users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from users.views import manage_call_center
from rest_framework.test import force_authenticate

print("=" * 60)
print("TESTING AUTHENTICATED REQUEST")
print("=" * 60)

try:
    # Get admin user
    admin = CustomUser.objects.get(email='admin@inspecgas.com')
    print(f"Usuario admin: {admin.email}")

    # Generate token
    refresh = RefreshToken.for_user(admin)
    access_token = str(refresh.access_token)
    print(f"Token generado: {access_token[:50]}...")

    # Create a test request
    factory = RequestFactory()

    # Simulate POST request to create call center
    data = {
        'username': 'testcallcenter',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'phone': '1234567890'
    }

    print(f"\nSimulando request POST a /api/auth/admin/call-center/")
    print(f"Datos: {data}")

    request = factory.post(
        '/api/auth/admin/call-center/',
        data=data,
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )

    # Force authenticate
    force_authenticate(request, user=admin, token=access_token)

    print(f"\nRequest user: {request.user}")
    print(f"Request user role: {request.user.role}")
    print(f"Request auth: {request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")

    # Call the view
    print("\nLlamando a manage_call_center view...")
    response = manage_call_center(request)

    print(f"\nResponse status: {response.status_code}")
    print(f"Response data: {response.data}")

    print("\n" + "=" * 60)
    print("TEST COMPLETADO")
    print("=" * 60)

except CustomUser.DoesNotExist:
    print("ERROR: Usuario admin no encontrado")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n")
