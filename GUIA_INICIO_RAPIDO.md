# Guía de Inicio Rápido - Sistema de Inspecciones de Gas

## ¿Qué se ha implementado?

Se ha creado un **frontend básico** completo con tres roles de usuario:

### 1. **ADMINISTRADOR**
✅ Puede crear cuentas de Call Center
✅ Puede crear cuentas de Inspectores
✅ Ve y gestiona todos los usuarios del sistema

### 2. **CALL CENTER**
✅ Puede agendar citas de inspección
✅ Registra datos del cliente (nombre, DNI, teléfono, dirección)
✅ Asigna inspectores a las citas
✅ Ve y cancela citas

### 3. **INSPECTOR**
✅ Ve sus citas asignadas
✅ Tiene un formulario completo para llenar datos de inspección
✅ Registra datos técnicos (medidor, presión, fugas, estado de instalaciones)
✅ Emite resultados de inspección

---

## Pasos para Probar el Sistema

### Paso 1: Iniciar el Backend

```bash
cd backend
python manage.py runserver
```

El backend correrá en: `http://localhost:8000`

### Paso 2: Crear Usuario Administrador

Si no tienes un usuario administrador, créalo:

```bash
cd backend
python create_admin.py
```

O usa el comando Django:

```bash
python manage.py createsuperuser
```

### Paso 3: Iniciar el Frontend

```bash
cd frontend
npm install  # Solo la primera vez
npm start
```

El frontend correrá en: `http://localhost:3000`

### Paso 4: Probar el Flujo Completo

#### 1. Iniciar sesión como Administrador
- Ve a: `http://localhost:3000/login`
- Ingresa credenciales del admin que creaste
- Serás redirigido a: `/admin`

#### 2. Crear usuarios Call Center e Inspector
- En el panel admin, verás dos pestañas: **Call Center** y **Inspectores**
- Haz clic en "Crear Call Center" y llena el formulario
- El sistema te mostrará la **contraseña temporal** generada
- Haz lo mismo para crear un Inspector

#### 3. Cerrar sesión y probar Call Center
- Cierra sesión (botón "Salir")
- Inicia sesión con las credenciales del Call Center
- Serás redirigido a: `/call-center`
- Haz clic en "Agendar Nueva Cita"
- Llena el formulario:
  - Datos del cliente (nombre, DNI, teléfono, dirección)
  - Fecha y hora de la cita
  - Selecciona el inspector que creaste
  - Tipo de servicio
  - Notas adicionales (opcional)
- Guarda la cita

#### 4. Cerrar sesión y probar Inspector
- Cierra sesión
- Inicia sesión con las credenciales del Inspector
- Serás redirigido a: `/inspector_panel`
- Verás la cita que el Call Center agendó
- Haz clic en "Realizar Inspección"
- Llena el formulario completo con:
  - Datos del cliente (pre-llenados)
  - Datos de la inspección (tipo, medidor, presión)
  - Estado de instalaciones (tuberías, conexiones, válvulas)
  - Observaciones y recomendaciones
  - Resultado (Aprobado/Rechazado)
- Guarda la inspección

---

## Archivos Creados

### Frontend (React)
```
frontend/src/pages/
  ├── LoginPage.jsx          # Página de inicio de sesión
  ├── AdminPanel.jsx         # Panel del administrador
  ├── CallCenterPanel.jsx    # Panel del call center
  └── InspectorPanel.jsx     # Panel del inspector

frontend/src/styles/
  ├── LoginPage.css
  ├── AdminPanel.css
  ├── CallCenterPanel.css
  └── InspectorPanel.css

frontend/src/components/
  └── Navbar.jsx             # Actualizado con enlaces para Call Center
```

### Documentación
```
FRONTEND_README.md         # Documentación completa del frontend
GUIA_INICIO_RAPIDO.md     # Esta guía
```

---

## Endpoints del Backend que Debes Implementar

El frontend está listo, pero necesitas completar estos endpoints en el backend:

### ✅ Ya implementados:
- `POST /api/users/login/` - Login
- `GET /api/users/call-center/` - Listar call centers
- `POST /api/users/call-center/` - Crear call center
- `GET /api/users/inspectors/` - Listar inspectores
- `POST /api/users/inspectors/` - Crear inspector
- `DELETE /api/users/manage/:id/` - Desactivar usuario

### ❌ Pendientes (necesarios para el frontend):
- `GET /api/appointments/` - Listar todas las citas
- `POST /api/appointments/` - Crear cita
- `PATCH /api/appointments/:id/` - Actualizar cita (cancelar)
- `GET /api/appointments/my-appointments/` - Listar citas del inspector logueado
- `POST /api/inspections/` - Crear inspección

---

## Estructura de Datos Esperada

### Para crear una cita (Call Center):
```json
{
  "client_name": "Juan Pérez",
  "client_email": "juan@example.com",
  "client_phone": "+573001234567",
  "client_address": "Calle 123 #45-67, Bogotá",
  "client_dni": "1234567890",
  "inspector_id": "uuid-del-inspector",
  "appointment_date": "2025-11-30",
  "appointment_time": "14:00",
  "service_type": "INSPECCION_GAS",
  "notes": "Cliente prefiere horario de la tarde"
}
```

### Para crear una inspección (Inspector):
```json
{
  "appointment_id": "uuid-de-la-cita",
  "client_name": "Juan Pérez",
  "client_dni": "1234567890",
  "client_phone": "+573001234567",
  "client_email": "juan@example.com",
  "client_address": "Calle 123 #45-67",
  "inspection_type": "RESIDENCIAL",
  "gas_meter_number": "MTR-123456",
  "meter_reading": "1234.56",
  "pressure_test": "25 PSI",
  "leak_detected": false,
  "leak_location": "",
  "pipes_condition": "BUENO",
  "connections_condition": "BUENO",
  "valve_condition": "BUENO",
  "regulator_condition": "BUENO",
  "recommendations": "Revisar válvula principal anualmente",
  "observations": "Instalación en buen estado",
  "requires_repair": false,
  "next_inspection_date": "2026-11-30",
  "inspection_result": "APROBADO",
  "certificate_issued": true
}
```

---

## Colores por Rol

Para identificar rápidamente cada panel:

- **Administrador**: Morado/Púrpura (#667eea → #764ba2)
- **Call Center**: Verde/Turquesa (#11998e → #38ef7d)
- **Inspector**: Rosa/Rojo (#f093fb → #f5576c)

---

## Próximos Pasos Recomendados

1. **Implementar los endpoints pendientes en el backend**
2. **Crear modelos de Django** para:
   - `Appointment` (Citas)
   - `Inspection` (Inspecciones)
3. **Agregar funcionalidades**:
   - Notificaciones por email cuando se agenda una cita
   - Generación de certificados PDF
   - Dashboard con estadísticas
   - Historial de inspecciones por cliente

---

## Soporte

Si encuentras algún error o necesitas ayuda:

1. Verifica que el backend esté corriendo en el puerto 8000
2. Revisa la consola del navegador (F12) para errores de JavaScript
3. Revisa la terminal del backend para errores de Django
4. Asegúrate de que las migraciones de la base de datos estén aplicadas

---

## Tecnologías Utilizadas

### Frontend:
- React 18
- React Router DOM
- Axios
- CSS3

### Backend:
- Django + Django REST Framework
- PostgreSQL / SQLite
- JWT Authentication

---

¡Todo listo para empezar a usar el sistema! 🚀
