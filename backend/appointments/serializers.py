# appointments/serializers.py
from rest_framework import serializers
from .models import Appointment
from users.serializers import UserSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    inspector_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client_name', 'client_phone', 'client_email', 'client_dni',
            'user', 'address', 'neighborhood', 'city',
            'scheduled_date', 'scheduled_time',
            'inspector', 'inspector_name',
            'created_by', 'created_by_name',
            'status', 'status_display',
            'notes', 'cancellation_reason',
            'created_at', 'updated_at',
            'inspection'
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
