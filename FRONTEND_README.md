# Frontend - Sistema de Gestión de Inspecciones de Gas

## Descripción
Frontend desarrollado en React para gestionar inspecciones de gas domiciliario con autenticación basada en roles.

## Estructura de Usuarios y Roles

### 1. **Administrador (ADMIN)**
- **Acceso**: `/admin`
- **Funcionalidades**:
  - Crear cuentas de Call Center
  - Crear cuentas de Inspectores
  - Ver lista de Call Centers e Inspectores
  - Desactivar usuarios
  - Gestión completa del sistema

### 2. **Call Center (CALL_CENTER)**
- **Acceso**: `/call-center`
- **Funcionalidades**:
  - Agendar citas de inspección
  - Ver lista de citas agendadas
  - Cancelar citas
  - Asignar inspectores a las citas
  - Registrar datos del cliente (nombre, DNI, dirección, teléfono)

### 3. **Inspector (INSPECTOR)**
- **Acceso**: `/inspector_panel`
- **Funcionalidades**:
  - Ver citas asignadas
  - Realizar inspecciones
  - Llenar formulario completo de inspección con:
    - Datos del cliente
    - Tipo de inspección (Residencial/Comercial/Industrial)
    - Lectura de medidor
    - Prueba de presión
    - Detección de fugas
    - Estado de instalaciones (tuberías, conexiones, válvulas, regulador)
    - Recomendaciones y observaciones
    - Resultado de inspección (Aprobado/Aprobado con observaciones/Rechazado)
    - Emisión de certificado

## Archivos Creados

### Componentes (Pages)
- `frontend/src/pages/LoginPage.jsx` - Página de inicio de sesión
- `frontend/src/pages/AdminPanel.jsx` - Panel del administrador
- `frontend/src/pages/CallCenterPanel.jsx` - Panel del call center
- `frontend/src/pages/InspectorPanel.jsx` - Panel del inspector

### Estilos (CSS)
- `frontend/src/styles/LoginPage.css` - Estilos del login
- `frontend/src/styles/AdminPanel.css` - Estilos del panel admin
- `frontend/src/styles/CallCenterPanel.css` - Estilos del panel call center
- `frontend/src/styles/InspectorPanel.css` - Estilos del panel inspector

## Instalación y Ejecución

### 1. Instalar Dependencias
```bash
cd frontend
npm install
```

### 2. Configurar Variables de Entorno
El frontend se conecta al backend en `http://localhost:8000/api`

### 3. Ejecutar el Frontend
```bash
npm start
```

La aplicación se abrirá en `http://localhost:3000`

## Flujo de Uso

### Para Administrador:
1. Iniciar sesión con credenciales de administrador
2. Acceder al panel de administración
3. Crear usuarios de Call Center e Inspector
4. Se genera una contraseña temporal que debe compartir con el usuario

### Para Call Center:
1. Iniciar sesión con credenciales proporcionadas
2. Acceder al panel de call center
3. Hacer clic en "Agendar Nueva Cita"
4. Llenar formulario con:
   - Datos del cliente (nombre, DNI, teléfono, dirección)
   - Fecha y hora de la cita
   - Seleccionar inspector disponible
   - Tipo de servicio
   - Notas adicionales
5. Ver lista de citas agendadas
6. Opción de cancelar citas pendientes

### Para Inspector:
1. Iniciar sesión con credenciales proporcionadas
2. Ver lista de citas asignadas
3. Seleccionar una cita y hacer clic en "Realizar Inspección"
4. Llenar el formulario completo de inspección:
   - Verificar/editar datos del cliente
   - Registrar datos técnicos (medidor, presión, fugas)
   - Evaluar estado de instalaciones
   - Agregar recomendaciones
   - Establecer resultado de la inspección
   - Indicar si se emite certificado
5. Guardar la inspección

## Endpoints del Backend Utilizados

### Autenticación
- `POST /api/users/login/` - Iniciar sesión

### Administrador
- `GET /api/users/call-center/` - Listar call centers
- `POST /api/users/call-center/` - Crear call center
- `GET /api/users/inspectors/` - Listar inspectores
- `POST /api/users/inspectors/` - Crear inspector
- `DELETE /api/users/manage/:id/` - Desactivar usuario

### Call Center
- `GET /api/appointments/` - Listar citas
- `POST /api/appointments/` - Crear cita
- `PATCH /api/appointments/:id/` - Actualizar cita (cancelar)
- `GET /api/users/inspectors/` - Listar inspectores disponibles

### Inspector
- `GET /api/appointments/my-appointments/` - Listar mis citas
- `POST /api/inspections/` - Crear inspección

## Características Implementadas

### Seguridad
- Rutas protegidas por rol
- Autenticación con JWT tokens
- Redirección automática según rol de usuario
- Validación de permisos en frontend y backend

### Interfaz de Usuario
- Diseño responsive (móvil y escritorio)
- Gradientes coloridos por tipo de usuario
- Mensajes de éxito/error
- Estados de carga
- Validación de formularios
- Tarjetas visuales para citas

### Funcionalidad
- Gestión completa de usuarios (CRUD)
- Sistema de citas con estados (Pendiente/Confirmada/Completada/Cancelada)
- Formulario extenso de inspección con múltiples secciones
- Generación de contraseñas temporales
- Asignación de inspectores a citas

## Próximos Pasos Recomendados

1. **Backend**: Crear los endpoints faltantes para:
   - `/api/appointments/` (CRUD de citas)
   - `/api/appointments/my-appointments/` (citas del inspector)
   - `/api/inspections/` (CRUD de inspecciones)

2. **Funcionalidades adicionales**:
   - Recuperación de contraseña
   - Cambio de contraseña
   - Notificaciones por email
   - Generación de reportes PDF
   - Dashboard con estadísticas
   - Historial de inspecciones por cliente
   - Calendario de citas

3. **Mejoras**:
   - Paginación de listas
   - Filtros y búsqueda
   - Exportar datos a Excel
   - Subir fotos en inspecciones
   - Firma digital del inspector

## Tecnologías Utilizadas

- React 18
- React Router DOM (navegación)
- Axios (peticiones HTTP)
- CSS3 (estilos)
- LocalStorage (almacenamiento de sesión)

## Credenciales de Prueba

Para probar el sistema, necesitas crear primero un usuario administrador en el backend:

```bash
cd backend
python create_admin.py
```

Luego usa esas credenciales para:
1. Iniciar sesión como Admin
2. Crear usuarios de Call Center e Inspector
3. Usar esos usuarios para probar sus respectivos paneles
