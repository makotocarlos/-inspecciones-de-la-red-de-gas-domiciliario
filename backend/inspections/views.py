"""
Views for Inspections
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Inspection, InspectionItem, InspectionPhoto
from .serializers import (
    InspectionListSerializer, InspectionDetailSerializer,
    InspectionCreateSerializer, InspectionUpdateSerializer,
    InspectionItemSerializer, InspectionPhotoSerializer,
    ONACInspectionSerializer
)
from core.utils.permissions import IsAdmin, IsAdminOrInspector, IsOwnerOrInspectorOrAdmin
from core.utils.response import APIResponse
from django.utils import timezone


class InspectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing inspections
    """
    queryset = Inspection.objects.all().select_related('user', 'inspector')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'result', 'gas_type', 'is_urgent']
    search_fields = ['address', 'city', 'user__email']
    ordering_fields = ['created_at', 'scheduled_date', 'priority']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InspectionListSerializer
        elif self.action == 'create':
            return InspectionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InspectionUpdateSerializer
        return InspectionDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return self.queryset
        elif user.is_inspector:
            return self.queryset.filter(inspector=user)
        else:
            return self.queryset.filter(user=user)
    
    def get_permissions(self):
        if self.action in ['assign_inspector', 'destroy']:
            return [IsAdmin()]
        elif self.action in ['update', 'partial_update', 'complete', 'create']:
            return [IsAdminOrInspector()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Create a new inspection - automatically assigns inspector if user is inspector"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Auto-assign inspector if the user creating is an inspector
        inspection = serializer.save()
        if request.user.role == 'INSPECTOR':
            inspection.inspector = request.user
            inspection.save()

        # Link inspection to appointment if appointment_id is provided
        appointment_id = request.data.get('appointment_id')
        if appointment_id:
            try:
                from appointments.models import Appointment
                appointment = Appointment.objects.get(id=appointment_id)
                appointment.inspection = inspection
                appointment.save()
            except Appointment.DoesNotExist:
                pass  # Continue even if appointment doesn't exist

        return Response(
            InspectionDetailSerializer(inspection).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def assign_inspector(self, request, pk=None):
        """Assign inspector to inspection"""
        inspection = self.get_object()
        inspector_id = request.data.get('inspector_id')
        
        try:
            from users.models import CustomUser
            inspector = CustomUser.objects.get(id=inspector_id, role='INSPECTOR')
            inspection.inspector = inspector
            inspection.status = 'SCHEDULED'
            inspection.save()
            
            return APIResponse.success(
                InspectionDetailSerializer(inspection).data,
                'Inspector asignado exitosamente'
            )
        except CustomUser.DoesNotExist:
            return APIResponse.error('Inspector no encontrado', status_code=404)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrInspector])
    def complete(self, request, pk=None):
        """Mark inspection as completed"""
        inspection = self.get_object()
        
        if inspection.status != 'IN_PROGRESS':
            return APIResponse.error('La inspección debe estar en progreso')
        
        inspection.status = 'COMPLETED'
        inspection.completed_at = timezone.now()
        inspection.save()
        
        return APIResponse.success(
            InspectionDetailSerializer(inspection).data,
            'Inspección completada'
        )
    
    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """Generate and download PDF report"""
        inspection = self.get_object()
        # TODO: Implement PDF generation
        return APIResponse.success({'message': 'Generación de PDF pendiente'})

    @action(detail=True, methods=['get', 'patch'], permission_classes=[IsAdminOrInspector])
    def onac_form(self, request, pk=None):
        """
        GET: Retrieve ONAC inspection form data
        PATCH: Update ONAC inspection form data (supports partial updates for multi-step form)
        """
        inspection = self.get_object()

        if request.method == 'GET':
            serializer = ONACInspectionSerializer(inspection)
            return APIResponse.success(serializer.data, 'Datos del formulario ONAC')

        elif request.method == 'PATCH':
            # Support partial updates for multi-step form
            serializer = ONACInspectionSerializer(
                inspection,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                # Update status to IN_PROGRESS if not already
                if inspection.status == 'SCHEDULED' or inspection.status == 'PENDING':
                    inspection.status = 'IN_PROGRESS'
                    if not inspection.started_at:
                        inspection.started_at = timezone.now()

                # Check if form is being completed
                form_percentage = request.data.get('form_completed_percentage', 0)
                if form_percentage == 100 or request.data.get('status') == 'COMPLETED':
                    inspection.status = 'COMPLETED'
                    if not inspection.completed_at:
                        inspection.completed_at = timezone.now()

                    # Update associated appointment status to COMPLETED
                    try:
                        appointment = inspection.appointment
                        if appointment and appointment.status != 'COMPLETED':
                            appointment.status = 'COMPLETED'
                            appointment.save()
                    except Exception as e:
                        # Log error but don't fail the inspection update
                        print(f"Error updating appointment: {e}")

                serializer.save()

                return APIResponse.success(
                    serializer.data,
                    'Formulario ONAC actualizado exitosamente'
                )

            return APIResponse.error(
                'Error de validación',
                errors=serializer.errors,
                status_code=400
            )
