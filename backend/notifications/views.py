"""
Views for Notifications app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from core.utils.permissions import IsAdmin
from core.utils.response import APIResponse
from .models import Notification, EmailTemplate
from .serializers import (
    NotificationSerializer, NotificationMarkReadSerializer,
    EmailTemplateSerializer
)
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing notifications
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users can only see their own notifications"""
        return Notification.objects.filter(user=self.request.user).select_related(
            'user', 'inspection'
        )
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        unread = self.get_queryset().filter(
            status__in=[Notification.Status.PENDING, Notification.Status.SENT]
        )
        
        serializer = self.get_serializer(unread, many=True)
        return APIResponse.success(
            serializer.data,
            message=f"{unread.count()} notificaciones no leídas"
        )
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """Mark notifications as read"""
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data['notification_ids']
        
        # Update notifications
        updated = Notification.objects.filter(
            id__in=notification_ids,
            user=request.user
        ).update(
            status=Notification.Status.READ,
            read_at=timezone.now()
        )
        
        return APIResponse.success(
            {'updated_count': updated},
            message=f"{updated} notificaciones marcadas como leídas"
        )
    
    @action(detail=True, methods=['post'])
    def mark_read_single(self, request, pk=None):
        """Mark single notification as read"""
        notification = self.get_object()
        
        notification.status = Notification.Status.READ
        notification.read_at = timezone.now()
        notification.save()
        
        return APIResponse.success(
            self.get_serializer(notification).data,
            message="Notificación marcada como leída"
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get notification statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'unread': queryset.filter(status__in=[Notification.Status.PENDING, Notification.Status.SENT]).count(),
            'read': queryset.filter(status=Notification.Status.READ).count(),
            'failed': queryset.filter(status=Notification.Status.FAILED).count(),
            'by_type': {}
        }
        
        # Count by type
        for notif_type in Notification.Type.choices:
            count = queryset.filter(notification_type=notif_type[0]).count()
            stats['by_type'][notif_type[0]] = count
        
        return APIResponse.success(stats)


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing email templates (Admin only)
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdmin]
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate an email template"""
        template = self.get_object()
        
        # Create duplicate
        new_template = EmailTemplate.objects.create(
            name=f"{template.name} (Copia)",
            template_type=template.template_type,
            subject=template.subject,
            html_content=template.html_content,
            text_content=template.text_content,
            variables=template.variables,
            is_active=False
        )
        
        return APIResponse.created(
            self.get_serializer(new_template).data,
            message="Plantilla duplicada exitosamente"
        )
