"""
Models for Inspections app
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
from .onac_fields import ONACInspectionMixin
import uuid


class Inspection(ONACInspectionMixin, models.Model):
    """Main inspection model with ONAC form fields"""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        SCHEDULED = 'SCHEDULED', 'Programada'
        IN_PROGRESS = 'IN_PROGRESS', 'En Progreso'
        COMPLETED = 'COMPLETED', 'Completada'
        REJECTED = 'REJECTED', 'Rechazada'
        CANCELLED = 'CANCELLED', 'Cancelada'
    
    class Result(models.TextChoices):
        APPROVED = 'APPROVED', 'Aprobada'
        CONDITIONAL = 'CONDITIONAL', 'Condicional'
        REJECTED = 'REJECTED', 'Rechazada'
    
    class GasType(models.TextChoices):
        NATURAL = 'NATURAL', 'Gas Natural'
        PROPANE = 'PROPANE', 'Gas Propano'
        LPG = 'LPG', 'GLP'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='requested_inspections', null=True, blank=True)
    inspector = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_inspections')
    
    address = models.CharField(max_length=255)
    neighborhood = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, default='Bogotá')
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    
    gas_type = models.CharField(max_length=20, choices=GasType.choices, default=GasType.NATURAL)
    installation_year = models.PositiveIntegerField(null=True, blank=True)
    pipeline_material = models.CharField(max_length=100, blank=True, null=True)
    pressure = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    result = models.CharField(max_length=20, choices=Result.choices, null=True, blank=True)
    
    scheduled_date = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    total_score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, blank=True)
    priority = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_urgent = models.BooleanField(default=False)
    
    observations = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    client_notes = models.TextField(blank=True, null=True)
    
    report_pdf = models.FileField(upload_to='reports/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Inspección'
        verbose_name_plural = 'Inspecciones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inspección {self.id} - {self.address}"


class InspectionItem(models.Model):
    """Individual inspection checklist items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='items')
    category = models.CharField(max_length=100)
    item_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_compliant = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    observations = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'category']
    
    def __str__(self):
        return f"{self.category} - {self.item_name}"


class InspectionPhoto(models.Model):
    """Photos taken during inspection"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='photos')
    item = models.ForeignKey(InspectionItem, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    photo = models.ImageField(upload_to='inspections/photos/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Foto - {self.inspection.id}"
