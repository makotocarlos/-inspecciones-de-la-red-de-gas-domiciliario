# appointments/models.py
"""
Appointment model for scheduling gas inspections
"""
from django.db import models
from django.conf import settings
import uuid


class Appointment(models.Model):
    """
    Represents a scheduled appointment for gas inspection
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        CONFIRMED = 'CONFIRMED', 'Confirmada'
        IN_PROGRESS = 'IN_PROGRESS', 'En Progreso'
        COMPLETED = 'COMPLETED', 'Completada'
        CANCELLED = 'CANCELLED', 'Cancelada'
        RESCHEDULED = 'RESCHEDULED', 'Reagendada'
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Client information (can be created on-the-fly or existing user)
    client_name = models.CharField('Nombre del Cliente', max_length=200)
    client_phone = models.CharField('Teléfono del Cliente', max_length=20)
    client_email = models.EmailField('Email del Cliente', blank=True, null=True)
    client_dni = models.CharField('DNI del Cliente', max_length=15, blank=True, null=True)
    
    # User reference (if client is registered user)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments_as_client',
        verbose_name='Usuario Registrado'
    )
    
    # Address information
    address = models.CharField('Dirección', max_length=300)
    neighborhood = models.CharField('Barrio', max_length=100, blank=True, null=True)
    city = models.CharField('Ciudad', max_length=100, default='Montería')
    
    # Appointment details
    scheduled_date = models.DateField('Fecha Programada')
    scheduled_time = models.TimeField('Hora Programada')
    
    # Assignment
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments_as_inspector',
        limit_choices_to={'role': 'INSPECTOR'},
        verbose_name='Inspector Asignado'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='appointments_created',
        verbose_name='Creado Por'
    )
    
    # Status and notes
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    notes = models.TextField('Notas', blank=True, null=True)
    cancellation_reason = models.TextField('Razón de Cancelación', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Última Actualización', auto_now=True)
    
    # Inspection reference (once completed)
    inspection = models.OneToOneField(
        'inspections.Inspection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointment',
        verbose_name='Inspección Realizada'
    )
    
    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-scheduled_date', '-scheduled_time']
        indexes = [
            models.Index(fields=['scheduled_date', 'scheduled_time']),
            models.Index(fields=['status']),
            models.Index(fields=['inspector']),
        ]
    
    def __str__(self):
        return f"{self.client_name} - {self.scheduled_date} {self.scheduled_time}"
    
    @property
    def is_past_due(self):
        """Check if appointment is past its scheduled time"""
        from django.utils import timezone
        from datetime import datetime
        
        scheduled_datetime = datetime.combine(self.scheduled_date, self.scheduled_time)
        return timezone.now() > timezone.make_aware(scheduled_datetime)
