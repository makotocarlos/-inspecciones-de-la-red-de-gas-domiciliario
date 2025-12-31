import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/InspectorPanel.css";
import { getErrorMessage } from "../utils/errorHandler";
import ONACInspectionForm from "../components/ONACInspectionForm";
import InspectorSchedule from "../components/InspectorSchedule";

const API_URL = "http://localhost:8000/api";

function InspectorPanel() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("pendientes"); // pendientes, historial, cronograma
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showInspectionForm, setShowInspectionForm] = useState(false);
  const [inspectionData, setInspectionData] = useState({
    // Datos del cliente
    client_name: "",
    client_dni: "",
    client_phone: "",
    client_email: "",
    client_address: "",

    // Datos de la inspección
    inspection_type: "RESIDENCIAL",
    gas_meter_number: "",
    meter_reading: "",
    pressure_test: "",
    leak_detected: false,
    leak_location: "",

    // Estado de instalaciones
    pipes_condition: "BUENO",
    connections_condition: "BUENO",
    valve_condition: "BUENO",
    regulator_condition: "BUENO",

    // Recomendaciones y observaciones
    recommendations: "",
    observations: "",
    requires_repair: false,
    next_inspection_date: "",

    // Resultados
    inspection_result: "APROBADO",
    certificate_issued: false
  });
  const [message, setMessage] = useState({ text: "", type: "" });

  useEffect(() => {
    // Wait for token to be available before loading
    const token = localStorage.getItem("token");
    if (token) {
      loadMyAppointments();
    } else {
      // Retry after a short delay if token not found
      const timer = setTimeout(() => {
        const retryToken = localStorage.getItem("token");
        if (retryToken) {
          loadMyAppointments();
        } else {
          showMessage("Sesión no válida. Por favor inicia sesión nuevamente.", "error");
          setTimeout(() => navigate("/login"), 2000);
        }
      }, 500);
      return () => clearTimeout(timer);
    }
  }, []);

  const getToken = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.warn("[InspectorPanel] Token no encontrado en localStorage");
    }
    return token;
  };

  const loadMyAppointments = async () => {
    const token = getToken();
    if (!token) {
      showMessage("Token no válido. Redirigiendo al login...", "error");
      setTimeout(() => navigate("/login"), 1500);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/appointments/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAppointments(response.data.appointments || []);
    } catch (error) {
      console.error("Error cargando citas:", error);
      if (error.response?.status === 401) {
        showMessage("Sesión expirada. Por favor inicia sesión nuevamente.", "error");
        setTimeout(() => {
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          navigate("/login");
        }, 2000);
      } else {
        showMessage(getErrorMessage(error, "Error al cargar citas asignadas"), "error");
      }
    } finally {
      setLoading(false);
    }
  };

  // Filtrar citas por estado
  const pendingAppointments = appointments.filter(apt => 
    ['PENDING', 'CONFIRMED', 'IN_PROGRESS', 'RESCHEDULED'].includes(apt.status)
  );
  
  const completedAppointments = appointments.filter(apt => 
    ['COMPLETED', 'CANCELLED', 'NEEDS_RESCHEDULE'].includes(apt.status)
  );

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setInspectionData({
      ...inspectionData,
      [name]: type === "checkbox" ? checked : value
    });
  };

  const handleStartInspection = async (appointment) => {
    // Si ya tiene una inspección existente, cargar esa inspección
    if (appointment.inspection) {
      setSelectedAppointment({ ...appointment, inspection_id: appointment.inspection });
      setShowInspectionForm(true);
      showMessage("Cargando inspección existente...", "info");
      return;
    }

    // Si no tiene inspección, crear una nueva en el backend primero
    setLoading(true);
    try {
      const token = getToken();
      
      // Capturar hora actual del dispositivo
      const actualStartTime = new Date().toISOString();
      
      const inspectionPayload = {
        appointment: appointment.id,
        address: appointment.address || appointment.client_address,
        city: appointment.city || "Pasto, Nariño",
        neighborhood: appointment.neighborhood || "",
        gas_type: "NATURAL",
        inspection_type: "PERIODIC",
        status: "IN_PROGRESS"
      };

      const response = await axios.post(
        `${API_URL}/inspections/`,
        inspectionPayload,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success || response.data.id) {
        const inspectionId = response.data.inspection?.id || response.data.id;
        
        // Actualizar la cita con el ID de inspección, estado y HORA REAL DE INICIO
        await axios.patch(
          `${API_URL}/appointments/${appointment.id}/`,
          { 
            inspection: inspectionId,
            status: "IN_PROGRESS",
            actual_start_time: actualStartTime  // ← Hora real de inicio
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        setSelectedAppointment({
          ...appointment,
          inspection_id: inspectionId,
          inspection: inspectionId,
          actual_start_time: actualStartTime
        });
        setShowInspectionForm(true);
        
        // Mostrar comparación de hora
        const startedAt = new Date(actualStartTime).toLocaleTimeString('es-CO');
        showMessage(`Inspección iniciada a las ${startedAt}. Hora programada: ${appointment.scheduled_time}`, "success");
      }
    } catch (error) {
      console.error("Error creando inspección:", error);
      showMessage("Error al crear la inspección: " + (error.response?.data?.error || error.message), "error");
    } finally {
      setLoading(false);
    }
  };

  const handleInspectionComplete = async () => {
    // Actualizar el estado de la cita a COMPLETED
    if (selectedAppointment?.id) {
      try {
        const token = getToken();
        await axios.patch(
          `${API_URL}/appointments/${selectedAppointment.id}/`,
          { status: "COMPLETED" },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (error) {
        console.error("Error actualizando estado de cita:", error);
      }
    }
    
    setShowInspectionForm(false);
    setSelectedAppointment(null);
    showMessage("Inspección completada exitosamente", "success");
    loadMyAppointments(); // Recargar para ver estados actualizados
  };

  const handleInspectionCancel = () => {
    setShowInspectionForm(false);
    setSelectedAppointment(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...inspectionData,
        appointment_id: selectedAppointment?.id
      };

      const response = await axios.post(
        `${API_URL}/inspections/`,
        payload,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );

      if (response.data.success) {
        showMessage("Inspección registrada exitosamente", "success");
        setShowInspectionForm(false);
        setSelectedAppointment(null);
        resetForm();
        loadMyAppointments();
      }
    } catch (error) {
      showMessage(
        getErrorMessage(error, "Error al registrar inspección"),
        "error"
      );
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setInspectionData({
      client_name: "",
      client_dni: "",
      client_phone: "",
      client_email: "",
      client_address: "",
      inspection_type: "RESIDENCIAL",
      gas_meter_number: "",
      meter_reading: "",
      pressure_test: "",
      leak_detected: false,
      leak_location: "",
      pipes_condition: "BUENO",
      connections_condition: "BUENO",
      valve_condition: "BUENO",
      regulator_condition: "BUENO",
      recommendations: "",
      observations: "",
      requires_repair: false,
      next_inspection_date: "",
      inspection_result: "APROBADO",
      certificate_issued: false
    });
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: "", type: "" }), 5000);
  };

  const getStatusBadge = (status, inspectionStatus = null) => {
    // Si la inspección está completada, mostrar ese estado
    if (inspectionStatus === 'COMPLETED' || status === 'COMPLETED') {
      return <span className="status-badge status-completed">Completada</span>;
    }
    
    const statusMap = {
      PENDING: { label: "Pendiente", className: "status-pending" },
      CONFIRMED: { label: "Confirmada", className: "status-confirmed" },
      IN_PROGRESS: { label: "En Progreso", className: "status-in-progress" },
      COMPLETED: { label: "Completada", className: "status-completed" },
      CANCELLED: { label: "Cancelada", className: "status-cancelled" },
      RESCHEDULED: { label: "Reagendada", className: "status-rescheduled" },
      NEEDS_RESCHEDULE: { label: "Reprogramada", className: "status-needs-reschedule" }
    };
    const statusInfo = statusMap[status] || { label: status, className: "" };
    return <span className={`status-badge ${statusInfo.className}`}>{statusInfo.label}</span>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleDateString("es-CO");
  };

  const formatTime = (timeString) => {
    if (!timeString) return "-";
    return timeString.substring(0, 5);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/login";
  };

  const renderAppointmentCard = (appointment, isHistory = false) => (
    <div key={appointment.id} className={`appointment-card ${isHistory ? 'history-card' : ''}`}>
      <div className="appointment-header">
        <h4>{appointment.client_name}</h4>
        {getStatusBadge(appointment.status, appointment.inspection_status)}
      </div>
      <div className="appointment-details">
        <p><strong>Fecha:</strong> {formatDate(appointment.scheduled_date)}</p>
        <p><strong>Hora:</strong> {formatTime(appointment.scheduled_time)}</p>
        <div className="address-display">
          <strong>📍 Dirección:</strong>
          <span className="address-text">{appointment.address}</span>
        </div>
        <p><strong>Teléfono:</strong> <a href={`tel:${appointment.client_phone}`}>{appointment.client_phone}</a></p>
        <p><strong>DNI:</strong> {appointment.client_dni || "-"}</p>
        {appointment.inspection_completed_percentage > 0 && appointment.inspection_completed_percentage < 100 && (
          <p><strong>Progreso:</strong> {appointment.inspection_completed_percentage}%</p>
        )}
        {appointment.notes && (
          <p><strong>Notas:</strong> {appointment.notes}</p>
        )}
      </div>
      <div className="appointment-actions">
        {(appointment.status === "COMPLETED" || appointment.inspection_status === "COMPLETED") && appointment.inspection ? (
          <button
            className="btn-secondary"
            onClick={() => {
              setSelectedAppointment({ ...appointment, inspection_id: appointment.inspection });
              setShowInspectionForm(true);
            }}
          >
            Ver Detalles
          </button>
        ) : (appointment.status === "PENDING" || appointment.status === "CONFIRMED" || appointment.status === "IN_PROGRESS") && (
          <button
            className="btn-primary"
            onClick={() => handleStartInspection(appointment)}
            disabled={loading}
          >
            {appointment.inspection ? "Continuar Inspección" : "Realizar Inspección"}
          </button>
        )}
      </div>
    </div>
  );

  return (
    <div className="inspector-panel">
      {/* Navbar */}
      <nav className="inspector-navbar">
        <div className="navbar-left">
          <button className="btn-logout" onClick={handleLogout}>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            Salir
          </button>
        </div>
        <div className="navbar-center">
          <h2 className="navbar-title">Panel Inspector</h2>
        </div>
        <div className="navbar-right">
          {/* Espacio para futuros elementos */}
        </div>
      </nav>

      {/* Content */}
      <div className="inspector-content">
        <div className="inspector-header">
          <h1>Panel Inspector</h1>
          <p>Mis Citas e Inspecciones</p>
        </div>

        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        {!showInspectionForm ? (
          <>
            {/* Tabs de navegación */}
            <div className="inspector-tabs">
              <button
                className={`inspector-tab ${activeTab === 'pendientes' ? 'active' : ''}`}
                onClick={() => setActiveTab('pendientes')}
              >
                <span className="tab-icon">📋</span>
                Pendientes
                {pendingAppointments.length > 0 && (
                  <span className="tab-badge">{pendingAppointments.length}</span>
                )}
              </button>
              <button
                className={`inspector-tab ${activeTab === 'historial' ? 'active' : ''}`}
                onClick={() => setActiveTab('historial')}
              >
                <span className="tab-icon">📜</span>
                Historial
                {completedAppointments.length > 0 && (
                  <span className="tab-badge history">{completedAppointments.length}</span>
                )}
              </button>
              <button
                className={`inspector-tab ${activeTab === 'cronograma' ? 'active' : ''}`}
                onClick={() => setActiveTab('cronograma')}
              >
                <span className="tab-icon">📆</span>
                Mi Cronograma
              </button>
            </div>

            {/* Contenido según pestaña activa */}
            {activeTab === 'pendientes' && (
              <div className="appointments-section">
                <div className="section-header">
                  <h3>Citas Pendientes</h3>
                  <button className="btn-refresh" onClick={loadMyAppointments} disabled={loading}>
                    🔄 Actualizar
                  </button>
                </div>
                {loading ? (
                  <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Cargando citas...</p>
                  </div>
                ) : pendingAppointments.length === 0 ? (
                  <div className="no-data-container">
                    <span className="no-data-icon">✅</span>
                    <p className="no-data">No tienes citas pendientes</p>
                    <span className="no-data-hint">¡Buen trabajo! Todas las citas están al día</span>
                  </div>
                ) : (
                  <div className="appointments-grid">
                    {pendingAppointments.map((appointment) => renderAppointmentCard(appointment))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'historial' && (
              <div className="appointments-section history-section">
                <div className="section-header">
                  <h3>Historial de Inspecciones</h3>
                  <span className="history-count">{completedAppointments.length} registros</span>
                </div>
                {loading ? (
                  <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Cargando historial...</p>
                  </div>
                ) : completedAppointments.length === 0 ? (
                  <div className="no-data-container">
                    <span className="no-data-icon">📭</span>
                    <p className="no-data">No hay inspecciones completadas</p>
                    <span className="no-data-hint">Las inspecciones completadas aparecerán aquí</span>
                  </div>
                ) : (
                  <div className="appointments-grid history-grid">
                    {completedAppointments.map((appointment) => renderAppointmentCard(appointment, true))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'cronograma' && (
              <div className="schedule-section">
                <InspectorSchedule
                  inspectorId="self"
                  embedded={true}
                />
              </div>
            )}
          </>
        ) : (
          <div className="inspection-form-container">
            <ONACInspectionForm
              inspectionId={selectedAppointment?.inspection_id}
              appointmentId={selectedAppointment?.id}
              onComplete={handleInspectionComplete}
              onCancel={handleInspectionCancel}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default InspectorPanel;
