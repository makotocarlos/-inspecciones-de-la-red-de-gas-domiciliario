"""
Models for Notifications app
"""
from django.db import models
from users.models import CustomUser
from inspections.models import Inspection
import uuid


class Notification(models.Model):
    """
    General notification model
    """
    
    class Type(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        PUSH = 'PUSH', 'Push Notification'
        IN_APP = 'IN_APP', 'In-App'
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        SENT = 'SENT', 'Enviado'
        FAILED = 'FAILED', 'Fallido'
        READ = 'READ', 'Leído'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuario'
    )
    
    notification_type = models.CharField(
        'Tipo',
        max_length=20,
        choices=Type.choices,
        default=Type.IN_APP
    )
    
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensaje')
    
    # Optional reference to inspection
    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Inspección'
    )
    
    # Email specific
    email_to = models.EmailField('Email destinatario', blank=True)
    email_subject = models.CharField('Asunto email', max_length=200, blank=True)
    
    # Tracking
    sent_at = models.DateTimeField('Enviado en', null=True, blank=True)
    read_at = models.DateTimeField('Leído en', null=True, blank=True)
    error_message = models.TextField('Mensaje de error', blank=True)
    
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Última actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'created_at']),
            models.Index(fields=['notification_type', 'status']),
            models.Index(fields=['inspection']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"


class EmailTemplate(models.Model):
    """
    Email template model for consistent email formatting
    """
    
    class TemplateType(models.TextChoices):
        WELCOME = 'WELCOME', 'Bienvenida'
        VERIFICATION = 'VERIFICATION', 'Verificación de cuenta'
        PASSWORD_RESET = 'PASSWORD_RESET', 'Recuperación de contraseña'
        INSPECTION_SCHEDULED = 'INSPECTION_SCHEDULED', 'Inspección programada'
        INSPECTION_REMINDER = 'INSPECTION_REMINDER', 'Recordatorio de inspección'
        INSPECTION_COMPLETED = 'INSPECTION_COMPLETED', 'Inspección completada'
        INSPECTION_APPROVED = 'INSPECTION_APPROVED', 'Inspección aprobada'
        INSPECTION_REJECTED = 'INSPECTION_REJECTED', 'Inspección rechazada'
        REPORT_READY = 'REPORT_READY', 'Reporte disponible'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField('Nombre', max_length=100, unique=True)
    template_type = models.CharField(
        'Tipo',
        max_length=50,
        choices=TemplateType.choices,
        unique=True
    )
    
    subject = models.CharField('Asunto', max_length=200)
    html_content = models.TextField('Contenido HTML')
    text_content = models.TextField('Contenido texto plano', blank=True)
    
    # Template variables (JSON array)
    variables = models.JSONField(
        'Variables',
        default=list,
        help_text='Lista de variables disponibles: {{ user_name }}, {{ inspection_date }}, etc.'
    )
    
    is_active = models.BooleanField('Activo', default=True)
    
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Última actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Plantilla de Email'
        verbose_name_plural = 'Plantillas de Email'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.get_template_type_display()}"
