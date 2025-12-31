# appointments/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentCreateSerializer, AppointmentUpdateSerializer
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
        client_name = request.data.get('client_name', '').strip()
        client_email = request.data.get('client_email', '').strip().lower() if request.data.get('client_email') else None
        client_phone = request.data.get('client_phone', '').strip()
        client_dni = request.data.get('client_dni', '').strip() if request.data.get('client_dni') else None
        address = request.data.get('address', '').strip()
        last_inspection = request.data.get('last_inspection_date')

        # Try to find or create client user
        client_user = None
        
        # First try to find existing client by DNI or email
        if client_dni:
            try:
                client_user = User.objects.get(dni=client_dni)
            except User.DoesNotExist:
                pass
        
        if not client_user and client_email:
            try:
                client_user = User.objects.get(email__iexact=client_email)
            except User.DoesNotExist:
                pass
        
        # If found, update info
        if client_user:
            updated = False
            if client_email and not client_user.email:
                client_user.email = client_email
                updated = True
            if client_phone and not client_user.phone_number:
                client_user.phone_number = client_phone
                updated = True
            if address and not client_user.address:
                client_user.address = address
                updated = True
            if last_inspection:
                client_user.last_inspection_date = last_inspection
                updated = True
            if updated:
                client_user.save()
        else:
            # Create new client user only if we have enough info
            if client_dni or client_email:
                try:
                    # Generate unique username
                    if client_email:
                        base_username = client_email.split('@')[0]
                    elif client_dni:
                        base_username = f"cliente_{client_dni}"
                    else:
                        base_username = f"cliente_{client_phone or 'unknown'}"
                    
                    # Ensure username is unique
                    username = base_username
                    counter = 1
                    while User.objects.filter(username__iexact=username).exists():
                        username = f"{base_username}_{counter}"
                        counter += 1
                    
                    # Parse name
                    name_parts = client_name.split() if client_name else []
                    first_name = name_parts[0] if name_parts else 'Cliente'
                    last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                    
                    client_user = User.objects.create(
                        email=client_email if client_email else f"{username}@temporal.local",
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        dni=client_dni,
                        phone_number=client_phone if client_phone else None,
                        address=address,
                        role='USER',
                        is_active=True,
                        last_inspection_date=last_inspection
                    )
                    client_user.set_unusable_password()
                    client_user.save()
                    print(f"Created new client user: {client_user.username}")
                except Exception as e:
                    print(f"Error creating client user: {e}")
                    # Continue without user - appointment can still be created
                    client_user = None

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


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def appointment_detail(request, appointment_id):
    """
    GET: Retrieve appointment details
    PUT/PATCH: Update appointment
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
    
    elif request.method == 'PUT' or request.method == 'PATCH':
        # Use AppointmentUpdateSerializer for updates - includes status and inspection fields
        serializer = AppointmentUpdateSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Refresh from database to get updated data
            appointment.refresh_from_db()
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


# ==================== CALL TASK VIEWS (Call Center Admin) ====================
from .models import CallTask
from .serializers import CallTaskSerializer, CallTaskCreateSerializer
from datetime import date


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clients_needing_inspection(request):
    """
    Lista de clientes que necesitan inspección próximamente.
    Solo para CALL_CENTER_ADMIN y ADMIN.
    """
    if request.user.role not in ['ADMIN', 'CALL_CENTER_ADMIN']:
        return Response({"error": "No autorizado"}, status=403)
    
    # Obtener usuarios con próxima inspección dentro de 6 meses
    from datetime import timedelta
    today = date.today()
    six_months_later = today + timedelta(days=180)
    
    # Clientes que necesitan inspección (próximos a vencer o vencidos)
    clients = User.objects.filter(
        role='USER',
        is_active=True,
        next_inspection_due__isnull=False,
        next_inspection_due__lte=six_months_later
    ).order_by('next_inspection_due')
    
    # También incluir clientes sin próxima inspección pero con última inspección hace más de 4 años
    four_years_ago = today - timedelta(days=4*365)
    clients_old = User.objects.filter(
        role='USER',
        is_active=True,
        next_inspection_due__isnull=True,
        last_inspection_date__lte=four_years_ago
    )
    
    # Clientes sin inspección registrada
    clients_never = User.objects.filter(
        role='USER',
        is_active=True,
        last_inspection_date__isnull=True
    )
    
    clients_data = []
    
    # Procesar clientes próximos a vencer
    for client in clients:
        days_until = (client.next_inspection_due - today).days
        clients_data.append({
            'id': str(client.id),
            'full_name': client.get_full_name(),
            'email': client.email,
            'phone': str(client.phone_number) if client.phone_number else '',
            'dni': client.dni,
            'address': client.address or '',
            'city': client.city or '',
            'last_inspection_date': client.last_inspection_date.isoformat() if client.last_inspection_date else None,
            'next_inspection_due': client.next_inspection_due.isoformat() if client.next_inspection_due else None,
            'days_until_due': days_until,
            'status': 'OVERDUE' if days_until < 0 else ('WARNING' if days_until <= 90 else 'OK'),
            'priority': 'URGENT' if days_until < 0 else ('HIGH' if days_until <= 30 else ('MEDIUM' if days_until <= 90 else 'LOW'))
        })
    
    # Procesar clientes con inspección antigua
    for client in clients_old:
        days_since = (today - client.last_inspection_date).days if client.last_inspection_date else 9999
        clients_data.append({
            'id': str(client.id),
            'full_name': client.get_full_name(),
            'email': client.email,
            'phone': str(client.phone_number) if client.phone_number else '',
            'dni': client.dni,
            'address': client.address or '',
            'city': client.city or '',
            'last_inspection_date': client.last_inspection_date.isoformat() if client.last_inspection_date else None,
            'next_inspection_due': None,
            'days_until_due': -days_since,
            'status': 'OVERDUE',
            'priority': 'HIGH'
        })
    
    # Ordenar por prioridad
    priority_order = {'URGENT': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    clients_data.sort(key=lambda x: (priority_order.get(x['priority'], 4), x['days_until_due']))
    
    return Response({
        'success': True,
        'total': len(clients_data),
        'clients': clients_data
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def call_task_list_create(request):
    """
    GET: Lista tareas de llamada
    POST: Crear nueva tarea (Call Center Admin asigna a Call Center)
    """
    if request.method == 'GET':
        if request.user.role == 'CALL_CENTER_ADMIN':
            # CC Admin ve todas las tareas
            tasks = CallTask.objects.all()
        elif request.user.role == 'CALL_CENTER':
            # CC normal solo ve sus tareas asignadas
            tasks = CallTask.objects.filter(assigned_to=request.user)
        elif request.user.role == 'ADMIN':
            tasks = CallTask.objects.all()
        else:
            return Response({"error": "No autorizado"}, status=403)
        
        # Filtros
        status_filter = request.GET.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        priority_filter = request.GET.get('priority')
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        
        serializer = CallTaskSerializer(tasks, many=True)
        return Response({'success': True, 'tasks': serializer.data})
    
    elif request.method == 'POST':
        if request.user.role not in ['ADMIN', 'CALL_CENTER_ADMIN']:
            return Response({"error": "Solo Call Center Admin puede crear tareas"}, status=403)
        
        serializer = CallTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save(assigned_by=request.user)
            return Response({
                'success': True,
                'task': CallTaskSerializer(task).data,
                'message': 'Tarea creada exitosamente'
            }, status=201)
        return Response({'success': False, 'errors': serializer.errors}, status=400)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def call_task_detail(request, task_id):
    """
    GET: Detalle de tarea
    PATCH: Actualizar tarea (estado, notas, etc.)
    DELETE: Eliminar tarea
    """
    try:
        task = CallTask.objects.get(id=task_id)
    except CallTask.DoesNotExist:
        return Response({"error": "Tarea no encontrada"}, status=404)
    
    if request.method == 'GET':
        serializer = CallTaskSerializer(task)
        return Response({'success': True, 'task': serializer.data})
    
    elif request.method == 'PATCH':
        # CC normal solo puede actualizar sus tareas
        if request.user.role == 'CALL_CENTER' and task.assigned_to != request.user:
            return Response({"error": "No autorizado"}, status=403)
        
        # Actualizar campos permitidos
        allowed_fields = ['status', 'notes', 'call_attempts', 'resulting_appointment']
        if request.user.role in ['ADMIN', 'CALL_CENTER_ADMIN']:
            allowed_fields.extend(['assigned_to', 'priority'])
        
        for field in allowed_fields:
            if field in request.data:
                setattr(task, field, request.data[field])
        
        # Si se actualiza el estado a "llamando", registrar fecha
        if request.data.get('status') == 'IN_PROGRESS':
            from django.utils import timezone
            task.last_call_date = timezone.now()
            task.call_attempts += 1
        
        task.save()
        serializer = CallTaskSerializer(task)
        return Response({'success': True, 'task': serializer.data})
    
    elif request.method == 'DELETE':
        if request.user.role not in ['ADMIN', 'CALL_CENTER_ADMIN']:
            return Response({"error": "No autorizado"}, status=403)
        task.delete()
        return Response({'success': True, 'message': 'Tarea eliminada'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointments_needing_reschedule(request):
    """
    Lista de citas que necesitan reprogramación.
    Para Call Center.
    """
    if request.user.role not in ['ADMIN', 'CALL_CENTER_ADMIN', 'CALL_CENTER']:
        return Response({"error": "No autorizado"}, status=403)
    
    appointments = Appointment.objects.filter(
        status='NEEDS_RESCHEDULE'
    ).order_by('-updated_at')
    
    # Incluir información de tarea asignada
    data = []
    for apt in appointments:
        apt_data = AppointmentSerializer(apt).data
        # Buscar si tiene una tarea de reprogramación asignada
        task = apt.reschedule_tasks.first()
        if task:
            apt_data['assigned_task'] = {
                'id': str(task.id),
                'assigned_to_id': str(task.assigned_to.id) if task.assigned_to else None,
                'assigned_to_name': f"{task.assigned_to.first_name} {task.assigned_to.last_name}".strip() if task.assigned_to else None,
                'status': task.status,
                'created_at': task.created_at.isoformat() if task.created_at else None
            }
        else:
            apt_data['assigned_task'] = None
        data.append(apt_data)
    
    return Response({
        'success': True,
        'appointments': data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reschedule_appointment(request, appointment_id):
    """
    Reprogramar una cita.
    """
    if request.user.role not in ['ADMIN', 'CALL_CENTER_ADMIN', 'CALL_CENTER']:
        return Response({"error": "No autorizado"}, status=403)
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({"error": "Cita no encontrada"}, status=404)
    
    new_date = request.data.get('scheduled_date')
    new_time = request.data.get('scheduled_time')
    new_inspector = request.data.get('inspector')
    
    if not new_date or not new_time:
        return Response({"error": "Fecha y hora son requeridos"}, status=400)
    
    # Actualizar la cita
    appointment.scheduled_date = new_date
    appointment.scheduled_time = new_time
    if new_inspector:
        try:
            inspector = User.objects.get(id=new_inspector, role='INSPECTOR')
            appointment.inspector = inspector
        except User.DoesNotExist:
            return Response({"error": "Inspector no encontrado"}, status=404)
    
    appointment.status = 'RESCHEDULED'
    appointment.notes = f"{appointment.notes or ''}\n[Reprogramada el {date.today()}]"
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    return Response({
        'success': True,
        'message': 'Cita reprogramada exitosamente',
        'appointment': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inspector_schedule(request, inspector_id=None):
    """
    Obtiene el cronograma/calendario de un inspector.
    Si no se especifica inspector_id, retorna el del inspector actual.
    Parámetros opcionales: month, year para filtrar por mes.
    """
    from datetime import datetime, timedelta
    from calendar import monthrange
    
    # Determinar qué inspector consultar
    if inspector_id:
        if request.user.role not in ['ADMIN', 'CALL_CENTER_ADMIN', 'CALL_CENTER', 'INSPECTOR']:
            return Response({"error": "No autorizado"}, status=403)
        try:
            inspector = User.objects.get(id=inspector_id, role='INSPECTOR')
        except User.DoesNotExist:
            return Response({"error": "Inspector no encontrado"}, status=404)
    else:
        # Solo inspectores pueden ver su propio cronograma sin ID
        if request.user.role != 'INSPECTOR':
            return Response({"error": "Debe especificar un inspector"}, status=400)
        inspector = request.user
    
    # Obtener mes y año (default: mes actual)
    today = date.today()
    month = int(request.query_params.get('month', today.month))
    year = int(request.query_params.get('year', today.year))
    
    # Calcular rango de fechas del mes
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    # Obtener citas del inspector en el rango
    appointments = Appointment.objects.filter(
        inspector=inspector,
        scheduled_date__gte=first_day,
        scheduled_date__lte=last_day
    ).exclude(
        status__in=['CANCELLED']
    ).order_by('scheduled_date', 'scheduled_time')
    
    # Organizar por día
    schedule_by_day = {}
    for apt in appointments:
        day_key = apt.scheduled_date.isoformat()
        if day_key not in schedule_by_day:
            schedule_by_day[day_key] = []
        
        schedule_by_day[day_key].append({
            'id': str(apt.id),
            'time': apt.scheduled_time.strftime('%H:%M'),
            'client_name': apt.client_name,
            'address': apt.address,
            'status': apt.status,
            'status_display': apt.get_status_display(),
        })
    
    # Crear lista de todos los días del mes con su info
    calendar_data = []
    current = first_day
    while current <= last_day:
        day_str = current.isoformat()
        day_appointments = schedule_by_day.get(day_str, [])
        
        calendar_data.append({
            'date': day_str,
            'day': current.day,
            'weekday': current.strftime('%A'),
            'weekday_short': current.strftime('%a'),
            'is_today': current == today,
            'is_past': current < today,
            'appointments_count': len(day_appointments),
            'appointments': day_appointments,
            'is_busy': len(day_appointments) >= 8,  # Más de 8 citas = día ocupado
        })
        current += timedelta(days=1)
    
    # Estadísticas del mes
    total_appointments = appointments.count()
    completed = appointments.filter(status='COMPLETED').count()
    pending = appointments.filter(status__in=['PENDING', 'CONFIRMED']).count()
    
    return Response({
        'success': True,
        'inspector': {
            'id': str(inspector.id),
            'name': f"{inspector.first_name} {inspector.last_name}".strip() or inspector.username,
        },
        'month': month,
        'year': year,
        'month_name': first_day.strftime('%B'),
        'calendar': calendar_data,
        'stats': {
            'total': total_appointments,
            'completed': completed,
            'pending': pending,
            'available_slots': (monthrange(year, month)[1] * 8) - total_appointments  # 8 slots por día
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_call_centers(request):
    """Lista de Call Centers para asignar tareas"""
    if request.user.role not in ['ADMIN', 'CALL_CENTER_ADMIN']:
        return Response({"error": "No autorizado"}, status=403)
    
    call_centers = User.objects.filter(
        role='CALL_CENTER',
        is_active=True
    ).order_by('first_name')
    
    data = [{
        'id': str(cc.id),
        'first_name': cc.first_name or cc.username,
        'last_name': cc.last_name or '',
        'full_name': f"{cc.first_name} {cc.last_name}".strip() or cc.username,
        'email': cc.email,
        'username': cc.username
    } for cc in call_centers]
    
    return Response({'success': True, 'call_centers': data})
