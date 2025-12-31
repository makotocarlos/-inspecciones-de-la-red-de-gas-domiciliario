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
        NEEDS_RESCHEDULE = 'NEEDS_RESCHEDULE', 'Requiere Reprogramación'
    
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
    
    # Campos de control de tiempo real
    actual_start_time = models.DateTimeField('Hora Real de Inicio', null=True, blank=True)
    actual_end_time = models.DateTimeField('Hora Real de Fin', null=True, blank=True)
    
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
    
    @property
    def punctuality_minutes(self):
        """
        Calcula la diferencia en minutos entre la hora agendada y la hora real de inicio.
        Positivo = llegó tarde, Negativo = llegó temprano, None = no ha iniciado
        """
        if not self.actual_start_time:
            return None
        
        from datetime import datetime, timezone as tz
        from django.utils import timezone
        
        # Combinar fecha y hora programada
        scheduled_datetime = datetime.combine(self.scheduled_date, self.scheduled_time)
        scheduled_datetime = timezone.make_aware(scheduled_datetime)
        
        # Calcular diferencia
        diff = self.actual_start_time - scheduled_datetime
        return int(diff.total_seconds() / 60)  # minutos
    
    @property
    def punctuality_status(self):
        """
        Estado de puntualidad: ON_TIME, EARLY, LATE
        """
        minutes = self.punctuality_minutes
        if minutes is None:
            return 'NOT_STARTED'
        if minutes <= -5:
            return 'EARLY'  # 5+ minutos antes
        elif minutes <= 10:
            return 'ON_TIME'  # Entre 5 min antes y 10 min después
        else:
            return 'LATE'  # Más de 10 minutos tarde
    
    @property
    def duration_minutes(self):
        """Duración de la inspección en minutos"""
        if not self.actual_start_time or not self.actual_end_time:
            return None
        diff = self.actual_end_time - self.actual_start_time
        return int(diff.total_seconds() / 60)


class CallTask(models.Model):
    """
    Tareas asignadas por Call Center Admin a Call Centers normales
    para contactar clientes que necesitan inspección
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        IN_PROGRESS = 'IN_PROGRESS', 'En Progreso'
        COMPLETED = 'COMPLETED', 'Completada'
        APPOINTMENT_SCHEDULED = 'APPOINTMENT_SCHEDULED', 'Cita Agendada'
        CLIENT_REFUSED = 'CLIENT_REFUSED', 'Cliente Rechazó'
        NO_ANSWER = 'NO_ANSWER', 'No Contestó'
    
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Baja'
        MEDIUM = 'MEDIUM', 'Media'
        HIGH = 'HIGH', 'Alta'
        URGENT = 'URGENT', 'Urgente'
    
    class TaskType(models.TextChoices):
        INSPECTION_CALL = 'INSPECTION_CALL', 'Llamada de Inspección'
        RESCHEDULE = 'RESCHEDULE', 'Reprogramación'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Tipo de tarea
    task_type = models.CharField(
        'Tipo de Tarea',
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.INSPECTION_CALL
    )
    
    # Cita relacionada (para reprogramaciones)
    source_appointment = models.ForeignKey(
        'Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reschedule_tasks',
        verbose_name='Cita a Reprogramar'
    )
    
    # Cliente a contactar
    client_name = models.CharField('Nombre del Cliente', max_length=200)
    client_phone = models.CharField('Teléfono del Cliente', max_length=20)
    client_email = models.EmailField('Email del Cliente', blank=True, null=True)
    client_dni = models.CharField('DNI del Cliente', max_length=15, blank=True, null=True)
    client_address = models.CharField('Dirección', max_length=300)
    
    # Referencia al usuario si existe
    client_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='call_tasks_as_client',
        verbose_name='Usuario Cliente'
    )
    
    # Información de inspección anterior
    last_inspection_date = models.DateField('Última Inspección', null=True, blank=True)
    next_inspection_due = models.DateField('Próxima Inspección', null=True, blank=True)
    days_until_due = models.IntegerField('Días para Vencimiento', default=0)
    
    # Asignaciones
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='tasks_created',
        verbose_name='Asignado Por'
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned',
        limit_choices_to={'role': 'CALL_CENTER'},
        verbose_name='Asignado A'
    )
    
    # Estado y prioridad
    status = models.CharField(
        'Estado',
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    priority = models.CharField(
        'Prioridad',
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    
    # Notas y seguimiento
    notes = models.TextField('Notas', blank=True, null=True)
    call_attempts = models.PositiveIntegerField('Intentos de Llamada', default=0)
    last_call_date = models.DateTimeField('Última Llamada', null=True, blank=True)
    
    # Cita resultante (si se agenda)
    resulting_appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_task',
        verbose_name='Cita Resultante'
    )
    
    # Timestamps
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Tarea de Llamada'
        verbose_name_plural = 'Tareas de Llamada'
        ordering = ['priority', 'days_until_due', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['priority']),
            models.Index(fields=['next_inspection_due']),
        ]
    
    def __str__(self):
        return f"Tarea: {self.client_name} - {self.get_status_display()}"
