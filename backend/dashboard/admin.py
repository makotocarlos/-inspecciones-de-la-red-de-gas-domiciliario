"""
Admin configuration for Dashboard app
"""
from django.contrib import admin
from .models import DashboardCache


@admin.register(DashboardCache)
class DashboardCacheAdmin(admin.ModelAdmin):
    """Admin interface for DashboardCache model"""
    
    list_display = ['cache_type', 'user', 'created_at', 'expires_at']
    
    list_filter = ['cache_type', 'created_at', 'expires_at']
    
    search_fields = ['user__email', 'cache_type']
    
    readonly_fields = ['id', 'created_at']
    
    date_hierarchy = 'created_at'
