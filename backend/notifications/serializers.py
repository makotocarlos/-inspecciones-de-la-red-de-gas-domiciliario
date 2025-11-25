"""
Serializers for Notifications app
"""
from rest_framework import serializers
from .models import Notification, EmailTemplate


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    inspection_id = serializers.UUIDField(source='inspection.id', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'notification_type', 'notification_type_display',
            'status', 'status_display', 'title', 'message', 'inspection', 'inspection_id',
            'email_to', 'email_subject', 'sent_at', 'read_at', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'sent_at', 'read_at', 'error_message',
            'created_at', 'updated_at'
        ]


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""
    
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text='Lista de IDs de notificaciones a marcar como leídas'
    )


class EmailTemplateSerializer(serializers.ModelSerializer):
    """Email template serializer"""
    
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'template_type', 'template_type_display',
            'subject', 'html_content', 'text_content', 'variables',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
