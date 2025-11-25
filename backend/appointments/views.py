# appointments/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentCreateSerializer
from datetime import datetime, timedelta

User = get_user_model()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def appointment_list_create(request):
    """
    GET: List all appointments (filtered by user role)
    POST: Create new appointment (Call Center or Admin only)
    """
    
    if request.method == 'GET':
        # Filter based on user role
        if request.user.role == 'ADMIN':
            appointments = Appointment.objects.all()
        elif request.user.role == 'CALL_CENTER':
            # Call center sees all appointments
            appointments = Appointment.objects.all()
        elif request.user.role == 'INSPECTOR':
            # Inspector only sees their assigned appointments
            appointments = Appointment.objects.filter(inspector=request.user)
        else:
            # Regular users see their own appointments
            appointments = Appointment.objects.filter(user=request.user)
        
        # Optional filters
        status_filter = request.GET.get('status')
        if status_filter:
            appointments = appointments.filter(status=status_filter)
        
        date_from = request.GET.get('date_from')
        if date_from:
            appointments = appointments.filter(scheduled_date__gte=date_from)
        
        date_to = request.GET.get('date_to')
        if date_to:
            appointments = appointments.filter(scheduled_date__lte=date_to)
        
        inspector_id = request.GET.get('inspector')
        if inspector_id:
            appointments = appointments.filter(inspector_id=inspector_id)
        
        serializer = AppointmentSerializer(appointments, many=True)
        return Response({
            'success': True,
            'appointments': serializer.data
        })
    
    elif request.method == 'POST':
        # Only Call Center and Admin can create appointments
        if request.user.role not in ['ADMIN', 'CALL_CENTER']:
            return Response({
                'success': False,
                'error': 'No tienes permisos para crear citas'
            }, status=status.HTTP_403_FORBIDDEN)

        # Extract client data
        client_name = request.data.get('client_name')
        client_email = request.data.get('client_email')
        client_phone = request.data.get('client_phone')
        client_dni = request.data.get('client_dni')
        address = request.data.get('address')
        last_inspection = request.data.get('last_inspection_date')

        # Try to find or create client user
        client_user = None
        if client_dni:
            # Try to find by DNI first
            try:
                client_user = User.objects.get(dni=client_dni)
                # Update client info if found
                if client_email and not client_user.email:
                    client_user.email = client_email
                if client_phone and not client_user.phone_number:
                    client_user.phone_number = client_phone
                if address and not client_user.address:
                    client_user.address = address
                if last_inspection:
                    client_user.last_inspection_date = last_inspection
                client_user.save()
            except User.DoesNotExist:
                # Create new client user
                if client_email:
                    # Create with email
                    client_user = User.objects.create(
                        email=client_email,
                        username=client_email,
                        first_name=client_name.split()[0] if client_name else '',
                        last_name=' '.join(client_name.split()[1:]) if client_name and len(client_name.split()) > 1 else '',
                        dni=client_dni,
                        phone_number=client_phone,
                        address=address,
                        role='USER',
                        is_active=True,
                        last_inspection_date=last_inspection
                    )
                    # Set unusable password - client will need to reset
                    client_user.set_unusable_password()
                    client_user.save()
        elif client_email:
            # Try to find by email
            try:
                client_user = User.objects.get(email=client_email)
                # Update client info if found
                if client_dni and not client_user.dni:
                    client_user.dni = client_dni
                if client_phone and not client_user.phone_number:
                    client_user.phone_number = client_phone
                if address and not client_user.address:
                    client_user.address = address
                if last_inspection:
                    client_user.last_inspection_date = last_inspection
                client_user.save()
            except User.DoesNotExist:
                # Create new client user
                client_user = User.objects.create(
                    email=client_email,
                    username=client_email,
                    first_name=client_name.split()[0] if client_name else '',
                    last_name=' '.join(client_name.split()[1:]) if client_name and len(client_name.split()) > 1 else '',
                    dni=client_dni,
                    phone_number=client_phone,
                    address=address,
                    role='USER',
                    is_active=True,
                    last_inspection_date=last_inspection
                )
                # Set unusable password - client will need to reset
                client_user.set_unusable_password()
                client_user.save()

        # Add user to appointment data if found/created
        appointment_data = request.data.copy()
        if client_user:
            appointment_data['user'] = client_user.id

        serializer = AppointmentCreateSerializer(data=appointment_data)
        if serializer.is_valid():
            appointment = serializer.save(created_by=request.user)
            response_serializer = AppointmentSerializer(appointment)
            return Response({
                'success': True,
                'message': 'Cita creada exitosamente y cliente registrado' if client_user else 'Cita creada exitosamente',
                'appointment': response_serializer.data,
                'client_created': client_user is not None
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def appointment_detail(request, appointment_id):
    """
    GET: Retrieve appointment details
    PUT: Update appointment
    DELETE: Cancel appointment
    """
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cita no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions
    if request.user.role not in ['ADMIN', 'CALL_CENTER']:
        if request.user.role == 'INSPECTOR' and appointment.inspector != request.user:
            return Response({
                'success': False,
                'error': 'No tienes permisos para acceder a esta cita'
            }, status=status.HTTP_403_FORBIDDEN)
        elif request.user.role == 'USER' and appointment.user != request.user:
            return Response({
                'success': False,
                'error': 'No tienes permisos para acceder a esta cita'
            }, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'GET':
        serializer = AppointmentSerializer(appointment)
        return Response({
            'success': True,
            'appointment': serializer.data
        })
    
    elif request.method == 'PUT':
        serializer = AppointmentCreateSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = AppointmentSerializer(appointment)
            return Response({
                'success': True,
                'message': 'Cita actualizada exitosamente',
                'appointment': response_serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        reason = request.data.get('reason', 'Sin razón especificada')
        appointment.status = Appointment.Status.CANCELLED
        appointment.cancellation_reason = reason
        appointment.save()
        
        return Response({
            'success': True,
            'message': 'Cita cancelada exitosamente'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_inspectors(request):
    """
    Get list of available inspectors for a given date and time
    """
    
    scheduled_date = request.GET.get('date')
    scheduled_time = request.GET.get('time')
    
    if not scheduled_date or not scheduled_time:
        return Response({
            'success': False,
            'error': 'Fecha y hora son requeridas'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get all active inspectors
    inspectors = User.objects.filter(role='INSPECTOR', is_active=True)
    
    # Filter out inspectors with conflicting appointments
    busy_inspectors = Appointment.objects.filter(
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        status__in=['PENDING', 'CONFIRMED', 'IN_PROGRESS']
    ).values_list('inspector_id', flat=True)
    
    available = inspectors.exclude(id__in=busy_inspectors)
    
    # Serialize inspector data
    inspector_data = [{
        'id': str(inspector.id),
        'name': f"{inspector.first_name} {inspector.last_name}",
        'email': inspector.email,
        'phone': str(inspector.phone_number) if inspector.phone_number else '',
        'license_number': inspector.license_number
    } for inspector in available]
    
    return Response({
        'success': True,
        'inspectors': inspector_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_appointment_status(request, appointment_id):
    """
    Update appointment status
    """
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cita no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    
    if new_status not in dict(Appointment.Status.choices):
        return Response({
            'success': False,
            'error': 'Estado inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    appointment.status = new_status
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    return Response({
        'success': True,
        'message': f'Estado actualizado a {appointment.get_status_display()}',
        'appointment': serializer.data
    })
