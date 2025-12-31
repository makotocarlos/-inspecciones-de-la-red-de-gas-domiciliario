# appointments/serializers.py
from rest_framework import serializers
from .models import Appointment
from users.serializers import UserSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    inspector_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    inspection_status = serializers.SerializerMethodField()
    inspection_completed_percentage = serializers.SerializerMethodField()
    punctuality_minutes = serializers.ReadOnlyField()
    punctuality_status = serializers.ReadOnlyField()
    duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client_name', 'client_phone', 'client_email', 'client_dni',
            'user', 'address', 'neighborhood', 'city',
            'scheduled_date', 'scheduled_time',
            'actual_start_time', 'actual_end_time',
            'inspector', 'inspector_name',
            'created_by', 'created_by_name',
            'status', 'status_display',
            'notes', 'cancellation_reason',
            'created_at', 'updated_at',
            'inspection', 'inspection_status', 'inspection_completed_percentage',
            'punctuality_minutes', 'punctuality_status', 'duration_minutes'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_inspector_name(self, obj):
        if obj.inspector:
            return f"{obj.inspector.first_name} {obj.inspector.last_name}"
        return None
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
    
    def get_inspection_status(self, obj):
        """Return inspection status if linked"""
        if obj.inspection:
            return obj.inspection.status
        return None
    
    def get_inspection_completed_percentage(self, obj):
        """Return inspection completion percentage if linked"""
        if obj.inspection:
            return obj.inspection.form_completed_percentage
        return 0


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'client_name', 'client_phone', 'client_email', 'client_dni',
            'user', 'address', 'neighborhood', 'city',
            'scheduled_date', 'scheduled_time',
            'inspector', 'notes'
        ]
    
    def validate(self, data):
        """Validate appointment data"""
        # Check if inspector is available at that time
        scheduled_date = data.get('scheduled_date')
        scheduled_time = data.get('scheduled_time')
        inspector = data.get('inspector')
        
        if inspector and scheduled_date and scheduled_time:
            # Check for conflicting appointments
            conflicts = Appointment.objects.filter(
                inspector=inspector,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
            )
            
            # Exclude current instance if updating
            if self.instance:
                conflicts = conflicts.exclude(id=self.instance.id)
            
            if conflicts.exists():
                raise serializers.ValidationError(
                    "El inspector ya tiene una cita programada a esta hora"
                )
        
        return data


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appointments - includes status, inspection, and time tracking fields"""
    class Meta:
        model = Appointment
        fields = [
            'client_name', 'client_phone', 'client_email', 'client_dni',
            'user', 'address', 'neighborhood', 'city',
            'scheduled_date', 'scheduled_time',
            'actual_start_time', 'actual_end_time',
            'inspector', 'notes', 'status', 'inspection', 'cancellation_reason'
        ]
        extra_kwargs = {
            'status': {'required': False},
            'inspection': {'required': False},
            'cancellation_reason': {'required': False},
            'actual_start_time': {'required': False},
            'actual_end_time': {'required': False},
        }


# ==================== CALL TASK SERIALIZERS ====================
from .models import CallTask

class CallTaskSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    
    class Meta:
        model = CallTask
        fields = [
            'id', 'task_type', 'task_type_display', 'source_appointment',
            'client_name', 'client_phone', 'client_email', 'client_dni',
            'client_address', 'client_user',
            'last_inspection_date', 'next_inspection_due', 'days_until_due',
            'assigned_by', 'assigned_by_name',
            'assigned_to', 'assigned_to_name',
            'status', 'status_display',
            'priority', 'priority_display',
            'notes', 'call_attempts', 'last_call_date',
            'resulting_appointment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'assigned_by']
    
    def get_assigned_by_name(self, obj):
        if obj.assigned_by:
            return f"{obj.assigned_by.first_name} {obj.assigned_by.last_name}"
        return None
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None


class CallTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallTask
        fields = [
            'task_type', 'source_appointment',
            'client_name', 'client_phone', 'client_email', 'client_dni',
            'client_address', 'client_user',
            'last_inspection_date', 'next_inspection_due', 'days_until_due',
            'assigned_to', 'priority', 'notes'
        ]
