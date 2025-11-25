"""
Script to generate all necessary backend files for Gas Inspection System
Run this with: python generate_backend.py
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Apps to create
APPS = ['inspections', 'reports', 'notifications', 'dashboard']

# Create apps
for app in APPS:
    app_dir = BASE_DIR / app
    app_dir.mkdir(exist_ok=True)
    
    # Create __init__.py
    (app_dir / '__init__.py').write_text('')
    
    # Create apps.py
    apps_content = f"""from django.apps import AppConfig


class {app.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app}'
"""
    (app_dir / 'apps.py').write_text(apps_content)
    
    # Create admin.py
    admin_content = f"""from django.contrib import admin
from .models import *

# Register your models here.
"""
    (app_dir / 'admin.py').write_text(admin_content)
    
    # Create models.py placeholder
    models_content = """from django.db import models

# Create your models here.
"""
    (app_dir / 'models.py').write_text(models_content)
    
    # Create views.py
    views_content = """from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

# Create your views here.
"""
    (app_dir / 'views.py').write_text(views_content)
    
    # Create serializers.py
    serializers_content = """from rest_framework import serializers

# Create your serializers here.
"""
    (app_dir / 'serializers.py').write_text(serializers_content)
    
    # Create urls.py
    urls_content = """from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
"""
    (app_dir / 'urls.py').write_text(urls_content)
    
    # Create migrations folder
    migrations_dir = app_dir / 'migrations'
    migrations_dir.mkdir(exist_ok=True)
    (migrations_dir / '__init__.py').write_text('')

print("✅ All apps created successfully!")
print(f"Created apps: {', '.join(APPS)}")
