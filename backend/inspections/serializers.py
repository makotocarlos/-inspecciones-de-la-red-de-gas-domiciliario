"""
Serializers for Inspections
"""
from rest_framework import serializers
from .models import Inspection, InspectionItem, InspectionPhoto
from users.serializers import UserSerializer, InspectorSerializer


class InspectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class InspectionPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionPhoto
        fields = '__all__'
        read_only_fields = ('id', 'uploaded_at')


class InspectionListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    inspector_name = serializers.CharField(source='inspector.get_full_name', read_only=True)
    
    class Meta:
        model = Inspection
        fields = [
            'id', 'user', 'user_name', 'inspector', 'inspector_name',
            'address', 'city', 'status', 'result', 'scheduled_date',
            'is_urgent', 'priority', 'created_at'
        ]


class InspectionDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    inspector = InspectorSerializer(read_only=True)
    items = InspectionItemSerializer(many=True, read_only=True)
    photos = InspectionPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Inspection
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class InspectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = [
            'user', 'address', 'neighborhood', 'city', 'postal_code',
            'gas_type', 'installation_year', 'pipeline_material',
            'client_notes'
        ]
        extra_kwargs = {
            'user': {'required': False, 'allow_null': True},
            'neighborhood': {'required': False, 'allow_blank': True}
        }

    def create(self, validated_data):
        request = self.context.get('request')

        # If no user is provided in validated_data
        if 'user' not in validated_data or validated_data.get('user') is None:
            # If request user is a regular user (not inspector), use them
            if request and request.user and request.user.role not in ['INSPECTOR', 'ADMIN', 'CALL_CENTER']:
                validated_data['user'] = request.user
            # For inspector/admin/call_center creating inspections, user field is optional
            # It will be set later or remain null if no client user exists yet

        return super().create(validated_data)


class InspectionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = [
            'status', 'result', 'scheduled_date', 'observations',
            'recommendations', 'total_score', 'priority', 'is_urgent'
        ]


class ONACInspectionSerializer(serializers.ModelSerializer):
    """
    Complete serializer for ONAC inspection form
    Handles all fields from the official ONAC document
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    inspector_name = serializers.CharField(source='inspector.get_full_name', read_only=True)

    class Meta:
        model = Inspection
        fields = [
            # Basic inspection fields
            'id', 'user', 'user_name', 'inspector', 'inspector_name',
            'address', 'neighborhood', 'city', 'postal_code',
            'status', 'result', 'scheduled_date', 'started_at', 'completed_at',

            # IDENTIFICACIÓN DE LA INSTALACIÓN
            'account_number', 'meter_number', 'last_revision_date', 'expiration_date',

            # ORGANISMO DE INSPECCIÓN
            'inspection_org_name', 'inspection_org_nit', 'inspection_org_address',
            'inspection_org_email', 'inspection_start_time', 'inspection_end_time',
            'pressure_type',

            # TIPO DE INSPECCIÓN
            'service_start_date', 'inspection_type_periodic', 'inspection_type_modification',
            'inspection_type_user_request', 'inspection_type_follow_up', 'user_request_date',

            # INFORMACIÓN DE RECINTO
            'rooms_data',

            # ARTEFACTOS
            'appliances_data',

            # EDIFICACIÓN
            'has_internal_void', 'has_property_certificate', 'property_aspect',

            # INSPECCIÓN DE INSTALACIÓN
            'leak_test_method', 'leak_test_pressure', 'leak_test_meter', 'leak_test_appliances',
            'checklist_items',

            # DEFECTOS
            'critical_defects', 'non_critical_defects',

            # DATOS DEL EQUIPO
            'co_detector_serial', 'co_detector_brand', 'co_detector_model',
            'manometer_serial', 'manometer_brand', 'manometer_model',
            'has_calibration_pattern', 'calibration_serial', 'seal_number',

            # RESULTADO
            'has_no_defects', 'has_non_critical_defect', 'has_critical_defect',
            'installation_continues_service', 'meter_reading', 'supply_situation',
            'inspector_affirms_safe',

            # FIRMAS DIGITALES
            'client_signature', 'inspector_signature',
            'client_phone', 'client_email_form',
            'inspector_name', 'inspector_competence_id', 'inspector_specialty',

            # OBSERVACIONES
            'observations',

            # CONTROL
            'form_completed_percentage', 'current_step',

            # Other fields
            'gas_type', 'installation_year', 'pipeline_material', 'pressure',
            'total_score', 'priority', 'is_urgent', 'recommendations', 'client_notes',
            'report_pdf', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_rooms_data(self, value):
        """Validate rooms data structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("rooms_data debe ser una lista")
        return value

    def validate_appliances_data(self, value):
        """Validate appliances data structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("appliances_data debe ser una lista")
        return value

    def validate_checklist_items(self, value):
        """Validate checklist items structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("checklist_items debe ser un diccionario")
        return value

    def validate_critical_defects(self, value):
        """Validate critical defects structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("critical_defects debe ser una lista")
        return value

    def validate_non_critical_defects(self, value):
        """Validate non-critical defects structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("non_critical_defects debe ser una lista")
        return value
