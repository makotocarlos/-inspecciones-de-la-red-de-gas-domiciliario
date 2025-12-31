# users/views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login, logout, get_user_model
from .serializers import UserSerializer
from django.views import View
from django.http import JsonResponse
from .decorators import role_required
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import generate_temp_password


User = get_user_model()

# ------------------ LOGIN ------------------
@api_view(["POST"])
@permission_classes([AllowAny])  # Allow anonymous access
def login_view(request):
    # Accept both username and email for login
    email = request.data.get("email")
    password = request.data.get("password")
    
    # Try to find user by email first
    user = None
    if email:
        try:
            user_obj = User.objects.get(email=email)
            # Check password directly instead of using authenticate()
            if user_obj.check_password(password) and user_obj.is_active:
                user = user_obj
        except User.DoesNotExist:
            pass
    
    if not user:
        return Response({"success": False, "error": "Credenciales inválidas"}, status=400)

    login(request, user)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    redirect_to = "home"
    if user.role == "ADMIN":
        redirect_to = "admin_dashboard"
    elif user.role == "INSPECTOR":
        redirect_to = "inspector_panel"

    serializer = UserSerializer(user)
    return Response({
        "success": True, 
        "user": serializer.data, 
        "redirect": redirect_to, 
        "token": access_token,
        "access": access_token,
        "refresh": str(refresh)
    })

# ------------------ LOGOUT ------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])  # Requires authentication
def logout_view(request):
    logout(request)
    return Response({"success": True, "message": "Sesión cerrada"})

# ------------------ REGISTRO NORMAL (DESHABILITADO - Solo inspectores crean usuarios) ------------------
@api_view(["POST"])
@permission_classes([AllowAny])  # Temporarily disabled public registration
def register_view(request):
    return Response({
        "success": False,
        "error": "El registro público está deshabilitado. Los usuarios son registrados por inspectores durante las inspecciones."
    }, status=403)

# ------------------ DASHBOARDS ------------------
@method_decorator(role_required(allowed_roles=['admin']), name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        return JsonResponse({"message": "Bienvenido Admin"})

@method_decorator(role_required(allowed_roles=['inspector']), name='dispatch')
class InspectorPanelView(View):
    def get(self, request):
        return JsonResponse({"message": "Bienvenido Inspector"})

# ------------------ REGISTRO POR INSPECTOR ------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_client(request):
    # Solo inspectores pueden crear clientes
    if request.user.role != "inspector":
        return Response({"error": "No autorizado"}, status=403)

    data = request.data.copy()
    data['role'] = 'user'  # cliente será role "user"

    # Validar campos obligatorios
    required_fields = ['username', 'email', 'first_name', 'last_name', 'identification_number', 'birth_date']
    missing_fields = [f for f in required_fields if not data.get(f)]
    if missing_fields:
        return Response({"error": f"Faltan campos obligatorios: {', '.join(missing_fields)}"}, status=400)

    # Validar usuario y correo duplicados
    if User.objects.filter(username=data['username']).exists():
        return Response({"error": "El nombre de usuario ya existe"}, status=400)
    if User.objects.filter(email=data['email']).exists():
        return Response({"error": "El correo ya está registrado"}, status=400)

    # Crear contraseña temporal
    temp_password = get_random_string(8)
    data['password'] = temp_password

    # Serializar
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        try:
            # Enviar correo
            send_mail(
                'Completa tu registro',
                f'Hola {user.first_name},\n\nTu cuenta ha sido creada por un inspector. '
                f'Usa esta contraseña temporal: {temp_password} y cambia tu contraseña al iniciar sesión.',
                'noreply@empresa.com',
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print("Error enviando correo:", e)
            return Response({"error": "Usuario creado, pero no se pudo enviar correo"}, status=500)

        return Response({"success": True, "user": serializer.data})

    else:
        # Devolver errores exactos de validación
        return Response({"error": serializer.errors}, status=400)


# ------------------ ADMIN: GESTIÓN DE CALL CENTER ------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_call_center(request):
    """Admin can view and create call center users"""
    if request.user.role != 'ADMIN':
        return Response({"error": "No autorizado"}, status=403)
    
    if request.method == 'GET':
        # List all call center users
        call_centers = User.objects.filter(role='CALL_CENTER').order_by('-date_joined')
        serializer = UserSerializer(call_centers, many=True)
        return Response({"success": True, "call_centers": serializer.data})
    
    elif request.method == 'POST':
        # Create new call center user
        data = request.data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '')
        
        if not all([username, email, first_name, last_name]):
            return Response({"error": "Campos obligatorios: username, email, first_name, last_name"}, status=400)
        
        # Check for existing username or email (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            return Response({"error": "El nombre de usuario ya existe"}, status=400)
        
        if User.objects.filter(email__iexact=email).exists():
            return Response({"error": "El correo ya está registrado"}, status=400)
        
        # Generate temporary password
        temp_password = generate_temp_password()
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                role='CALL_CENTER',
                is_active=True
            )
            
            if phone:
                user.phone_number = phone
                user.save()
            
            serializer = UserSerializer(user)
            return Response({
                "success": True,
                "user": serializer.data,
                "temp_password": temp_password,
                "message": f"Call Center creado exitosamente. Contraseña temporal: {temp_password}"
            })
        except Exception as e:
            import traceback
            print(f"Error creando call center: {str(e)}")
            print(traceback.format_exc())
            return Response({"error": f"Error al crear call center: {str(e)}"}, status=500)


# ------------------ ADMIN: GESTIÓN DE CALL CENTER ADMIN ------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_call_center_admin(request):
    """Admin can view and create call center admin users"""
    if request.user.role != 'ADMIN':
        return Response({"error": "No autorizado"}, status=403)
    
    if request.method == 'GET':
        # List all call center admin users
        cc_admins = User.objects.filter(role='CALL_CENTER_ADMIN').order_by('-date_joined')
        serializer = UserSerializer(cc_admins, many=True)
        return Response({"success": True, "call_center_admins": serializer.data})
    
    elif request.method == 'POST':
        # Create new call center admin user
        data = request.data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '')
        
        if not all([username, email, first_name, last_name]):
            return Response({"error": "Campos obligatorios: username, email, first_name, last_name"}, status=400)
        
        # Check for existing username or email (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            return Response({"error": "El nombre de usuario ya existe"}, status=400)
        
        if User.objects.filter(email__iexact=email).exists():
            return Response({"error": "El correo ya está registrado"}, status=400)
        
        # Generate temporary password
        temp_password = generate_temp_password()
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                role='CALL_CENTER_ADMIN',
                is_active=True
            )
            
            if phone:
                user.phone_number = phone
                user.save()
            
            serializer = UserSerializer(user)
            return Response({
                "success": True,
                "user": serializer.data,
                "temp_password": temp_password,
                "message": f"Call Center Admin creado exitosamente. Contraseña temporal: {temp_password}"
            })
        except Exception as e:
            import traceback
            print(f"Error creando call center admin: {str(e)}")
            print(traceback.format_exc())
            return Response({"error": f"Error al crear call center admin: {str(e)}"}, status=500)


# ------------------ ADMIN: GESTIÓN DE INSPECTORES ------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_inspectors(request):
    """Admin and Call Center can view inspector users, only Admin can create"""
    # Allow ADMIN and CALL_CENTER to GET inspectors
    # Only ADMIN can POST (create) inspectors
    if request.method == 'GET':
        if request.user.role not in ['ADMIN', 'CALL_CENTER']:
            return Response({"error": "No autorizado"}, status=403)
        # List all active inspectors
        inspectors = User.objects.filter(role='INSPECTOR', is_active=True).order_by('-date_joined')
        serializer = UserSerializer(inspectors, many=True)
        return Response({"success": True, "inspectors": serializer.data})
    
    elif request.method == 'POST':
        # Only ADMIN can create inspectors
        if request.user.role != 'ADMIN':
            return Response({"error": "Solo administradores pueden crear inspectores"}, status=403)
        
        # Create new inspector
        data = request.data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '')
        license_number = data.get('license_number', '').strip()
        
        if not all([username, email, first_name, last_name]):
            return Response({"error": "Campos obligatorios: username, email, first_name, last_name"}, status=400)
        
        # Check for existing username or email (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            return Response({"error": "El nombre de usuario ya existe"}, status=400)
        
        if User.objects.filter(email__iexact=email).exists():
            return Response({"error": "El correo ya está registrado"}, status=400)
        
        # Check for existing license number (if provided)
        if license_number and User.objects.filter(license_number=license_number).exists():
            return Response({"error": f"El número de licencia '{license_number}' ya está registrado"}, status=400)
        
        # Generate temporary password
        temp_password = generate_temp_password()
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                role='INSPECTOR',
                license_number=license_number if license_number else None,
                is_active=True
            )
            
            if phone:
                user.phone_number = phone
                user.save()
            
            serializer = UserSerializer(user)
            return Response({
                "success": True,
                "user": serializer.data,
                "temp_password": temp_password,
                "message": f"Inspector creado exitosamente. Contraseña temporal: {temp_password}"
            })
        except Exception as e:
            import traceback
            print(f"Error creando inspector: {str(e)}")
            print(traceback.format_exc())
            return Response({"error": f"Error al crear inspector: {str(e)}"}, status=500)


# ------------------ ADMIN: EDITAR/ELIMINAR USUARIOS ------------------
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_user(request, user_id):
    """Admin can edit or delete users (call center, inspectors)"""
    if request.user.role != 'ADMIN':
        return Response({"error": "No autorizado"}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)
    
    if request.method == 'PUT':
        # Update user
        data = request.data
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.is_active = data.get('is_active', user.is_active)
        
        if data.get('phone'):
            user.phone_number = data.get('phone')
        
        user.save()
        serializer = UserSerializer(user)
        return Response({"success": True, "user": serializer.data})
    
    elif request.method == 'DELETE':
        # Soft delete - just deactivate
        user.is_active = False
        user.save()
        return Response({"success": True, "message": "Usuario desactivado"})


# ------------------ CAMBIAR CONTRASEÑA ------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Allow users to change their own password"""
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return Response({
            "success": False,
            "error": "Se requieren old_password y new_password"
        }, status=400)
    
    # Verify old password
    if not user.check_password(old_password):
        return Response({
            "success": False,
            "error": "La contraseña actual es incorrecta"
        }, status=400)
    
    # Validate new password length
    if len(new_password) < 8:
        return Response({
            "success": False,
            "error": "La nueva contraseña debe tener al menos 8 caracteres"
        }, status=400)
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    return Response({
        "success": True,
        "message": "Contraseña actualizada exitosamente"
    })


# ------------------ ADMIN: RESETEAR CONTRASEÑA ------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_user_password(request, user_id):
    """Admin can reset a user's password"""
    if request.user.role != 'ADMIN':
        return Response({"error": "No autorizado"}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)
    
    # Generate new temporary password
    new_password = generate_temp_password()
    user.set_password(new_password)
    user.save()
    
    return Response({
        "success": True,
        "temp_password": new_password,
        "message": f"Contraseña reseteada. Nueva contraseña temporal: {new_password}"
    })


# ------------------ LISTA DE INSPECTORES PARA CALL CENTER ------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_inspectors(request):
    """Call Center and Admin can view list of inspectors"""
    if request.user.role not in ['ADMIN', 'CALL_CENTER']:
        return Response({"error": "No autorizado"}, status=403)

    # List all active inspectors
    inspectors = User.objects.filter(role='INSPECTOR', is_active=True).order_by('first_name', 'last_name')
    serializer = UserSerializer(inspectors, many=True)
    return Response({"success": True, "inspectors": serializer.data})


# ------------------ LISTA DE CLIENTES PARA ADMIN ------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_clients(request):
    """Admin can view list of all clients (USER role)"""
    if request.user.role != 'ADMIN':
        return Response({"error": "No autorizado"}, status=403)

    # List all clients (users with role USER)
    clients = User.objects.filter(role='USER', is_active=True).order_by('-created_at')

    # Prepare client data with last inspection info
    clients_data = []
    for client in clients:
        clients_data.append({
            'id': str(client.id),
            'full_name': client.get_full_name(),
            'email': client.email,
            'dni': client.dni,
            'phone_number': str(client.phone_number) if client.phone_number else '',
            'address': client.address,
            'city': client.city,
            'last_inspection_date': client.last_inspection_date.isoformat() if client.last_inspection_date else None,
            'created_at': client.created_at.isoformat(),
        })

    return Response({"success": True, "clients": clients_data})


# ------------------ HISTORIAL DE INSPECTOR PARA ADMIN ------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inspector_history(request, inspector_id):
    """Admin can view history and statistics for an inspector"""
    if request.user.role != 'ADMIN':
        return Response({"error": "No autorizado"}, status=403)
    
    try:
        inspector = User.objects.get(id=inspector_id, role='INSPECTOR')
    except User.DoesNotExist:
        return Response({"error": "Inspector no encontrado"}, status=404)
    
    from appointments.models import Appointment
    from django.db.models import Avg, Count, Q
    from datetime import timedelta
    
    # Obtener todas las citas completadas del inspector
    appointments = Appointment.objects.filter(
        inspector=inspector,
        status='COMPLETED'
    ).order_by('-scheduled_date', '-scheduled_time')
    
    # Estadísticas de puntualidad
    completed_with_start = appointments.filter(actual_start_time__isnull=False)
    
    total_completed = appointments.count()
    total_with_tracking = completed_with_start.count()
    
    # Calcular puntualidad
    on_time_count = 0
    early_count = 0
    late_count = 0
    total_delay_minutes = 0
    
    history_list = []
    
    for apt in appointments:
        history_item = {
            'id': str(apt.id),
            'client_name': apt.client_name,
            'address': apt.address,
            'scheduled_date': apt.scheduled_date.isoformat(),
            'scheduled_time': apt.scheduled_time.strftime('%H:%M'),
            'actual_start_time': apt.actual_start_time.isoformat() if apt.actual_start_time else None,
            'actual_end_time': apt.actual_end_time.isoformat() if apt.actual_end_time else None,
            'punctuality_minutes': apt.punctuality_minutes,
            'punctuality_status': apt.punctuality_status,
            'duration_minutes': apt.duration_minutes,
        }
        history_list.append(history_item)
        
        # Contar estadísticas
        if apt.punctuality_status == 'ON_TIME':
            on_time_count += 1
        elif apt.punctuality_status == 'EARLY':
            early_count += 1
        elif apt.punctuality_status == 'LATE':
            late_count += 1
            if apt.punctuality_minutes:
                total_delay_minutes += apt.punctuality_minutes
    
    # Calcular porcentajes y promedios
    punctuality_rate = round((on_time_count + early_count) / total_with_tracking * 100, 1) if total_with_tracking > 0 else 0
    avg_delay = round(total_delay_minutes / late_count, 1) if late_count > 0 else 0
    
    # Duración promedio
    durations = [apt.duration_minutes for apt in appointments if apt.duration_minutes]
    avg_duration = round(sum(durations) / len(durations), 1) if durations else 0
    
    # Información del inspector
    inspector_data = {
        'id': str(inspector.id),
        'full_name': f"{inspector.first_name} {inspector.last_name}",
        'email': inspector.email,
        'license_number': inspector.license_number,
        'phone_number': str(inspector.phone_number) if inspector.phone_number else '',
        'date_joined': inspector.date_joined.isoformat(),
    }
    
    # Estadísticas
    statistics = {
        'total_completed': total_completed,
        'total_with_tracking': total_with_tracking,
        'on_time_count': on_time_count,
        'early_count': early_count,
        'late_count': late_count,
        'punctuality_rate': punctuality_rate,
        'avg_delay_minutes': avg_delay,
        'avg_duration_minutes': avg_duration,
    }
    
    return Response({
        "success": True,
        "inspector": inspector_data,
        "statistics": statistics,
        "history": history_list
    })
