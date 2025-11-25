from django.contrib import admin
from .models import Inspection, InspectionItem, InspectionPhoto


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'inspector', 'status', 'scheduled_date', 'created_at']
    list_filter = ['status', 'result', 'gas_type', 'created_at']
    search_fields = ['address', 'user__email', 'inspector__email']
    date_hierarchy = 'created_at'


@admin.register(InspectionItem)
class InspectionItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'inspection', 'is_compliant', 'score']
    list_filter = ['category', 'is_compliant']


@admin.register(InspectionPhoto)
class InspectionPhotoAdmin(admin.ModelAdmin):
    list_display = ['inspection', 'caption', 'uploaded_at']
