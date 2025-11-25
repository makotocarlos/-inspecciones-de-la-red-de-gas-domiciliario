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
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone', '')
        
        if not all([username, email, first_name, last_name]):
            return Response({"error": "Campos obligatorios: username, email, first_name, last_name"}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "El usuario ya existe"}, status=400)
        
        if User.objects.filter(email=email).exists():
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
                role='CALL_CENTER'
            )
            
            if phone:
                user.phone_number = phone
                user.save()
            
            serializer = UserSerializer(user)
            return Response({
                "success": True,
                "user": serializer.data,
                "temp_password": temp_password,
                "message": f"Call Center creado. Contraseña temporal: {temp_password}"
            })
        except Exception as e:
            return Response({"error": f"Error al crear call center: {str(e)}"}, status=500)


# ------------------ ADMIN: GESTIÓN DE INSPECTORES ------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_inspectors(request):
    """Admin can view and create inspector users"""
    if request.user.role != 'ADMIN':
        return Response({"error": "No autorizado"}, status=403)
    
    if request.method == 'GET':
        # List all inspectors
        inspectors = User.objects.filter(role='INSPECTOR').order_by('-date_joined')
        serializer = UserSerializer(inspectors, many=True)
        return Response({"success": True, "inspectors": serializer.data})
    
    elif request.method == 'POST':
        # Create new inspector
        data = request.data
        username = data.get('username')
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone', '')
        license_number = data.get('license_number', '')
        
        if not all([username, email, first_name, last_name]):
            return Response({"error": "Campos obligatorios: username, email, first_name, last_name"}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "El usuario ya existe"}, status=400)
        
        if User.objects.filter(email=email).exists():
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
                role='INSPECTOR',
                license_number=license_number
            )
            
            if phone:
                user.phone_number = phone
                user.save()
            
            serializer = UserSerializer(user)
            return Response({
                "success": True,
                "user": serializer.data,
                "temp_password": temp_password,
                "message": f"Inspector creado. Contraseña temporal: {temp_password}"
            })
        except Exception as e:
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
