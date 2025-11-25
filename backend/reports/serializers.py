"""
Serializers for Reports app
"""
from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    """Report serializer"""
    
    inspection_id = serializers.UUIDField(source='inspection.id', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'inspection', 'inspection_id', 'generated_by', 'generated_by_name',
            'status', 'status_display', 'file', 'file_size', 'error_message',
            'report_number', 'report_date', 'include_photos', 'include_signature',
            'watermark', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'generated_by', 'status', 'file', 'file_size',
            'error_message', 'report_number', 'report_date', 'created_at', 'updated_at'
        ]


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reports"""
    
    class Meta:
        model = Report
        fields = ['inspection', 'include_photos', 'include_signature', 'watermark']
    
    def validate_inspection(self, value):
        """Validate that inspection is completed"""
        if value.status != 'COMPLETED':
            raise serializers.ValidationError(
                "Solo se pueden generar reportes para inspecciones completadas."
            )
        return value
