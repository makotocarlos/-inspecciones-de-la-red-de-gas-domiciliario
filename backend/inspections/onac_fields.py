"""
Extended ONAC Form Fields for Inspection Model
This file contains additional fields to match the official ONAC inspection form
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ONACInspectionMixin(models.Model):
    """
    Mixin to add all ONAC form fields to the Inspection model
    Based on ONAC 17020-2013 / RUIS format
    """

    class Meta:
        abstract = True

    # ==================== IDENTIFICACIÓN DE LA INSTALACIÓN ====================
    account_number = models.CharField('Número de Cuenta', max_length=50, blank=True, null=True)
    meter_number = models.CharField('Número de Medidor', max_length=50, blank=True, null=True)
    last_revision_date = models.DateField('Fecha Última Revisión', blank=True, null=True)
    expiration_date = models.DateField('Fecha de Vencimiento', blank=True, null=True)

    # ==================== ORGANISMO DE INSPECCIÓN ====================
    inspection_org_name = models.CharField('Razón Social', max_length=200, default='RUIS - Redes Urbanas Inspecciones S.A.S.')
    inspection_org_nit = models.CharField('NIT', max_length=50, default='901 563 111-9')
    inspection_org_address = models.CharField('Dirección Org', max_length=255, blank=True, null=True)
    inspection_org_email = models.EmailField('Email Org', blank=True, null=True)

    inspection_start_time = models.TimeField('Hora de Inicio', blank=True, null=True)
    inspection_end_time = models.TimeField('Hora Final', blank=True, null=True)

    # Tipo de presión
    PRESSURE_TYPE_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
    ]
    pressure_type = models.CharField('Tipo de Presión', max_length=10, choices=PRESSURE_TYPE_CHOICES, default='BAJA')

    # ==================== TIPO DE INSPECCIÓN ====================
    service_start_date = models.DateField('Fecha Puesta en Servicio', blank=True, null=True)
    inspection_type_periodic = models.BooleanField('Revisión Periódica (10 años)', default=False)
    inspection_type_modification = models.BooleanField('Modificación y Reforma', default=False)
    inspection_type_user_request = models.BooleanField('Solicitud del Usuario', default=False)
    inspection_type_follow_up = models.BooleanField('Seguimiento', default=False)
    user_request_date = models.DateField('Fecha Solicitud Usuario', blank=True, null=True)

    # ==================== INFORMACIÓN DE RECINTO ====================
    # Store as JSON for multiple rooms
    rooms_data = models.JSONField('Datos de Recintos', default=list, blank=True)
    # Example structure:
    # [{
    #   "id": 1,
    #   "type": "COCINA",  # COCINA, CALENTADOR, SALA, etc.
    #   "measurements": {"length": 3.90, "width": 3.80, "height": 2.60},
    #   "volume": 31.12,
    #   "total_power": 14.1,
    #   "complies_standard": true,
    #   "upper_ventilation_area": 0.5,
    #   "lower_ventilation_area": 0.5,
    #   "sketch": "base64_image_data"  # Drawing of the room
    # }]

    # ==================== ARTEFACTOS ====================
    appliances_data = models.JSONField('Datos de Artefactos', default=list, blank=True)
    # Example structure:
    # [{
    #   "id": 1,
    #   "room_id": 1,
    #   "name": "COCINA",
    #   "type": "COCINA",  # COCINA, CALENTADOR, HORNO, etc.
    #   "power_btu": 3000,
    #   "normalized_coupling": true,
    #   "ventilation_type": "NATURAL",
    #   "dimensions": {"trans": 0.5, "dism": 0.4, "long": 0.3},
    #   "material": "CIR"  # CF: Cobre Flexible, CIR: Cobre rígido, etc.
    # }]

    # Edificación
    has_internal_void = models.BooleanField('Cuenta con Vacío Interno', default=False)
    has_property_certificate = models.BooleanField('Certificado de Tradición y Libertad', default=False)
    property_aspect = models.CharField('Aspecto Inmueble', max_length=100, blank=True, null=True)

    # ==================== INSPECCIÓN DE INSTALACIÓN ====================
    # Hermeticidad
    leak_test_method = models.CharField('Método Prueba Hermeticidad', max_length=20,
                                       choices=[('DETECTOR', 'Detector'), ('ESPUMA', 'Espuma/Agua Jabón')],
                                       blank=True, null=True)
    leak_test_pressure = models.DecimalField('Presión de Prueba (mbar)', max_digits=6, decimal_places=2, blank=True, null=True)
    leak_test_meter = models.BooleanField('Test en Medidor', default=False)
    leak_test_appliances = models.BooleanField('Test en Artefactos', default=False)

    # Checklist items (store as JSON for flexibility)
    checklist_items = models.JSONField('Items de Verificación', default=dict, blank=True)
    # Example: {"270": true, "271": false, "272": true, ...}

    # ==================== DEFECTOS ====================
    critical_defects = models.JSONField('Defectos Críticos', default=list, blank=True)
    # Example: ["270", "271", "275"]

    non_critical_defects = models.JSONField('Defectos No Críticos', default=list, blank=True)
    # Example: ["310", "311", "318"]

    # ==================== DATOS DEL EQUIPO ====================
    co_detector_serial = models.CharField('Serie Detector CO', max_length=50, blank=True, null=True)
    co_detector_brand = models.CharField('Marca Detector CO', max_length=50, blank=True, null=True)
    co_detector_model = models.CharField('Modelo Detector CO', max_length=50, blank=True, null=True)

    manometer_serial = models.CharField('Serie Manómetro', max_length=50, blank=True, null=True)
    manometer_brand = models.CharField('Marca Manómetro', max_length=50, blank=True, null=True)
    manometer_model = models.CharField('Modelo Manómetro', max_length=50, blank=True, null=True)

    has_calibration_pattern = models.BooleanField('Patrón de Rx', default=False)
    calibration_serial = models.CharField('Serie Patrón', max_length=50, blank=True, null=True)
    seal_number = models.CharField('Número de Sello', max_length=50, blank=True, null=True)

    # ==================== RESULTADO ====================
    has_no_defects = models.BooleanField('Sin Defectos', default=False)
    has_non_critical_defect = models.BooleanField('Defecto No Crítico', default=False)
    has_critical_defect = models.BooleanField('Defecto Crítico', default=False)

    installation_continues_service = models.BooleanField('Instalación Continúa en Servicio', default=True)
    meter_reading = models.DecimalField('Lectura Medidor (m³)', max_digits=10, decimal_places=2, blank=True, null=True)
    supply_situation = models.CharField('Situación de Suministro', max_length=100, blank=True, null=True)

    inspector_affirms_safe = models.BooleanField('Inspector Afirma Condiciones Seguras', default=True)

    # ==================== FIRMAS DIGITALES ====================
    client_signature = models.TextField('Firma Digital Cliente', blank=True, null=True)  # Base64 image
    inspector_signature = models.TextField('Firma Digital Inspector', blank=True, null=True)  # Base64 image

    client_phone = models.CharField('Teléfono Cliente', max_length=20, blank=True, null=True)
    client_email_form = models.EmailField('Email Cliente Formulario', blank=True, null=True)

    inspector_name = models.CharField('Nombre Inspector', max_length=200, blank=True, null=True)
    inspector_competence_id = models.CharField('Cédula Competencia Laboral', max_length=50, blank=True, null=True)
    inspector_specialty = models.CharField('Especialidad', max_length=100, blank=True, null=True)

    # ==================== OBSERVACIONES ====================
    observations = models.TextField('Observaciones Generales', blank=True, null=True)

    # ==================== CAMPOS DE CONTROL ====================
    form_completed_percentage = models.IntegerField('Porcentaje Completado', default=0,
                                                    validators=[MinValueValidator(0), MaxValueValidator(100)])
    current_step = models.IntegerField('Paso Actual del Formulario', default=1)
