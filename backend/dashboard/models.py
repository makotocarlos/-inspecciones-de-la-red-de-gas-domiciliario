"""
Models for Dashboard app
"""
from django.db import models
from users.models import CustomUser
import uuid


class DashboardCache(models.Model):
    """
    Cache model for dashboard statistics
    """
    
    class CacheType(models.TextChoices):
        ADMIN_STATS = 'ADMIN_STATS', 'Admin Statistics'
        INSPECTOR_STATS = 'INSPECTOR_STATS', 'Inspector Statistics'
        USER_STATS = 'USER_STATS', 'User Statistics'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='dashboard_caches',
        verbose_name='Usuario',
        null=True,
        blank=True
    )
    
    cache_type = models.CharField(
        'Tipo de cache',
        max_length=50,
        choices=CacheType.choices
    )
    
    data = models.JSONField('Datos', default=dict)
    
    created_at = models.DateTimeField('Fecha de creación', auto_now_add=True)
    expires_at = models.DateTimeField('Expira en')
    
    class Meta:
        verbose_name = 'Cache de Dashboard'
        verbose_name_plural = 'Caches de Dashboard'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'cache_type', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.get_cache_type_display()} - {self.user.email if self.user else 'Global'}"
