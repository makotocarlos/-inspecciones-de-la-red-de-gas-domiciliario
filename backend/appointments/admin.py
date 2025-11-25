# appointments/admin.py
from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'client_name', 'scheduled_date', 'scheduled_time',
        'inspector', 'status', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'scheduled_date', 'city']
    search_fields = ['client_name', 'client_phone', 'client_email', 'address']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('client_name', 'client_phone', 'client_email', 'client_dni', 'user')
        }),
        ('Dirección', {
            'fields': ('address', 'neighborhood', 'city')
        }),
        ('Programación', {
            'fields': ('scheduled_date', 'scheduled_time', 'inspector')
        }),
        ('Estado', {
            'fields': ('status', 'notes', 'cancellation_reason')
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at', 'inspection'),
            'classes': ('collapse',)
        }),
    )
