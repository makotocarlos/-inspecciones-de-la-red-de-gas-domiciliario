"""
Admin configuration for Notifications app
"""
from django.contrib import admin
from .models import Notification, EmailTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    
    list_display = [
        'title', 'user', 'notification_type', 'status',
        'sent_at', 'created_at'
    ]
    
    list_filter = ['notification_type', 'status', 'created_at', 'sent_at']
    
    search_fields = [
        'title', 'message', 'user__email', 'email_to'
    ]
    
    readonly_fields = [
        'id', 'sent_at', 'read_at', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'user', 'notification_type', 'status')
        }),
        ('Contenido', {
            'fields': ('title', 'message', 'inspection')
        }),
        ('Datos de Email', {
            'fields': ('email_to', 'email_subject'),
            'classes': ('collapse',)
        }),
        ('Seguimiento', {
            'fields': ('sent_at', 'read_at', 'error_message')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Admin interface for EmailTemplate model"""
    
    list_display = ['name', 'template_type', 'subject', 'is_active', 'updated_at']
    
    list_filter = ['template_type', 'is_active', 'created_at']
    
    search_fields = ['name', 'subject', 'html_content']
    
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'name', 'template_type', 'is_active')
        }),
        ('Contenido', {
            'fields': ('subject', 'html_content', 'text_content')
        }),
        ('Variables', {
            'fields': ('variables',),
            'description': 'Variables disponibles para usar en las plantillas'
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
