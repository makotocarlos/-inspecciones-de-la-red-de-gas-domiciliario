# users/models.py
"""
Custom User Model with role-based authentication
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from core.utils.validators import validate_dni
import uuid


class CustomUser(AbstractUser):
    """
    Extended User model with additional fields for gas inspection system
    """
    
    # Role choices
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        CALL_CENTER = 'CALL_CENTER', 'Call Center'
        INSPECTOR = 'INSPECTOR', 'Inspector'
        USER = 'USER', 'Usuario/Cliente'
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('Correo Electrónico', unique=True)
    
    # Personal Information
    first_name = models.CharField('Primer Nombre', max_length=50)
    middle_name = models.CharField('Segundo Nombre', max_length=50, blank=True, null=True)
    last_name = models.CharField('Primer Apellido', max_length=50)
    second_last_name = models.CharField('Segundo Apellido', max_length=50, blank=True, null=True)
    
    dni = models.CharField(
        'Cédula de Ciudadanía',
        max_length=15,
        unique=True,
        null=True,
        blank=True
    )
    
    phone_number = PhoneNumberField(
        'Número de Teléfono',
        region='CO',
        null=True,
        blank=True
    )
    
    birth_date = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    
    # Address Information
    address = models.CharField('Dirección', max_length=255, blank=True, null=True)
    neighborhood = models.CharField('Barrio', max_length=100, blank=True, null=True)
    city = models.CharField('Ciudad', max_length=100, default='Bogotá')
    postal_code = models.CharField('Código Postal', max_length=10, blank=True, null=True)
    
    # Role and Status
    role = models.CharField(
        'Rol',
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    
    is_active = models.BooleanField('Activo', default=True)
    is_verified = models.BooleanField('Email Verificado', default=False)
    
    # Profile
    profile_photo = models.ImageField(
        'Foto de Perfil',
        upload_to='profiles/',
        null=True,
        blank=True
    )
    
    bio = models.TextField('Biografía', max_length=500, blank=True, null=True)
    
    # Inspector Specific Fields
    license_number = models.CharField(
        'Número de Licencia',
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )
    
    license_expiry = models.DateField(
        'Vencimiento de Licencia',
        null=True,
        blank=True
    )
    
    certifications = models.JSONField(
        'Certificaciones',
        default=list,
        blank=True
    )
    
    specializations = models.JSONField(
        'Especializaciones',
        default=list,
        blank=True
    )
    
    years_experience = models.PositiveIntegerField(
        'Años de Experiencia',
        null=True,
        blank=True
    )

    # Client Specific Fields (for role USER)
    last_inspection_date = models.DateField(
        'Fecha de Última Inspección',
        null=True,
        blank=True,
        help_text='Fecha de la última inspección de gas realizada'
    )

    # Security Fields
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password_expires = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('Fecha de Registro', auto_now_add=True)
    updated_at = models.DateTimeField('Última Actualización', auto_now=True)
    last_login_at = models.DateTimeField('Último Acceso', null=True, blank=True)
    
    # Settings
    email_notifications = models.BooleanField('Notificaciones por Email', default=True)
    sms_notifications = models.BooleanField('Notificaciones por SMS', default=False)
    
    # Override username to use email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['dni']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the user's full name"""
        names = [self.first_name, self.middle_name, self.last_name, self.second_last_name]
        return ' '.join(filter(None, names))
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_inspector(self):
        return self.role == self.Role.INSPECTOR
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    """Audit log for tracking user actions"""
    
    class Action(models.TextChoices):
        LOGIN = 'LOGIN', 'Inicio de sesión'
        LOGOUT = 'LOGOUT', 'Cierre de sesión'
        CREATE = 'CREATE', 'Creación'
        UPDATE = 'UPDATE', 'Actualización'
        DELETE = 'DELETE', 'Eliminación'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"
