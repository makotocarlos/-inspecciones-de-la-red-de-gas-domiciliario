"""
Admin configuration for Reports app
"""
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for Report model"""
    
    list_display = [
        'report_number', 'inspection', 'generated_by', 'status',
        'file_size', 'created_at'
    ]
    
    list_filter = ['status', 'created_at', 'include_photos', 'include_signature']
    
    search_fields = [
        'report_number', 'inspection__id', 'generated_by__email',
        'inspection__user__email'
    ]
    
    readonly_fields = [
        'id', 'report_number', 'report_date', 'file_size',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('id', 'report_number', 'report_date', 'status')
        }),
        ('Referencias', {
            'fields': ('inspection', 'generated_by')
        }),
        ('Archivo', {
            'fields': ('file', 'file_size', 'error_message')
        }),
        ('Opciones', {
            'fields': ('include_photos', 'include_signature', 'watermark')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    def has_delete_permission(self, request, obj=None):
        """Only admins can delete reports"""
        return request.user.is_superuser
