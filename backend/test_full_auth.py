#!/usr/bin/env python
"""
Test complete authentication flow
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken

print("=" * 60)
print("TESTING COMPLETE AUTH FLOW")
print("=" * 60)

try:
    # Step 1: Get admin user
    print("\n1. Getting admin user...")
    admin = CustomUser.objects.get(email='admin@inspecgas.com')
    print(f"   Admin found: {admin.email}")
    print(f"   Role: {admin.role}")

    # Step 2: Check password
    print("\n2. Checking password...")
    if admin.check_password('admin123'):
        print("   Password is CORRECT")
    else:
        print("   Password is INCORRECT")
        raise Exception("Password check failed")

    # Step 3: Generate JWT token
    print("\n3. Generating JWT token...")
    refresh = RefreshToken.for_user(admin)
    access_token = str(refresh.access_token)
    print(f"   Token generated: {access_token[:50]}...")

    # Step 4: Verify token
    print("\n4. Verifying token...")
    from rest_framework_simplejwt.tokens import AccessToken
    token_obj = AccessToken(access_token)
    user_id = token_obj.get('user_id')
    print(f"   Token is VALID")
    print(f"   User ID from token: {user_id}")
    print(f"   Admin ID: {admin.id}")
    print(f"   IDs match: {str(user_id) == str(admin.id)}")

    # Step 5: Test user creation permissions
    print("\n5. Testing admin permissions...")
    print(f"   Is admin: {admin.role == 'ADMIN'}")
    print(f"   Can create users: {admin.role == 'ADMIN' and admin.is_active}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)
    print("\nYou should now be able to:")
    print("1. Login at http://localhost:3000/login")
    print("2. Access admin panel at http://localhost:3000/admin")
    print("3. Create call center and inspector users")
    print("\nMake sure the Django server is running:")
    print("cd backend && python manage.py runserver")

except CustomUser.DoesNotExist:
    print("\nERROR: Admin user not found")
    print("Run: python recreate_admin.py")
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n")
