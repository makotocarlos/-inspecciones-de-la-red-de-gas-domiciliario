"""
Models for Reports app
"""
from django.db import models
from inspections.models import Inspection
from users.models import CustomUser
import uuid


class Report(models.Model):
    """
    PDF Report model for inspections
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        GENERATING = 'GENERATING', 'Generando'
        COMPLETED = 'COMPLETED', 'Completado'
        FAILED = 'FAILED', 'Fallido'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.CASCADE,
        related_name='generated_reports',
        verbose_name='Inspección'
    )
    
    generated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports',
        verbose_name='Generado por'
    )
    
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    file = models.FileField(
        'Archivo PDF',
        upload_to='reports/pdfs/',
        null=True,
        blank=True
    )
    
    file_size = models.PositiveIntegerField('Tamaño (bytes)', null=True, blank=True)
    
    error_message = models.TextField('Mensaje de error', blank=True)
    
    # Report metadata
    report_number = models.CharField('Número de reporte', max_length=50, unique=True)
    report_date = models.DateTimeField('Fecha del reporte', auto_now_add=True)
    
    # Options
    include_photos = models.BooleanField('Incluir fotos', default=True)
    include_signature = models.BooleanField('Incluir firma', default=True)
    watermark = models.BooleanField('Marca de agua', default=False)
    
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    updated_at = models.DateTimeField('Última actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inspection', 'created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Reporte {self.report_number} - {self.inspection.id}"
    
    def save(self, *args, **kwargs):
        if not self.report_number:
            # Generate unique report number
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            count = Report.objects.filter(
                report_number__startswith=f'RPT-{date_str}'
            ).count()
            self.report_number = f'RPT-{date_str}-{count + 1:04d}'
        super().save(*args, **kwargs)
