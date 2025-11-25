import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/InspectorPanel.css";
import { getErrorMessage } from "../utils/errorHandler";
import ONACInspectionForm from "../components/ONACInspectionForm";

const API_URL = "http://localhost:8000/api";

function InspectorPanel() {
  const navigate = useNavigate();
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
    loadMyAppointments();
  }, []);

  const getToken = () => localStorage.getItem("token");

  const loadMyAppointments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/appointments/`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setAppointments(response.data.appointments || []);
    } catch (error) {
      console.error("Error cargando citas:", error);
      showMessage(getErrorMessage(error, "Error al cargar citas asignadas"), "error");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setInspectionData({
      ...inspectionData,
      [name]: type === "checkbox" ? checked : value
    });
  };

  const handleStartInspection = async (appointment) => {
    // SOLUCIÓN SIMPLE: Mostrar formulario inmediatamente sin backend
    // El formulario guardará los datos cuando el inspector lo complete

    // Si ya tiene una inspección existente, usar ese ID
    if (appointment.inspection) {
      setSelectedAppointment({ ...appointment, inspection_id: appointment.inspection });
      setShowInspectionForm(true);
      return;
    }

    // Si no tiene inspección, crear una "temporal" solo en el frontend
    // Se creará en el backend cuando el inspector guarde el formulario
    setSelectedAppointment({
      ...appointment,
      inspection_id: null, // null significa que se creará al guardar
      tempInspectionData: {
        address: appointment.address || appointment.client_address,
        city: appointment.city || "Montería",
        neighborhood: appointment.neighborhood || "",
        gas_type: "NATURAL",
        user: appointment.user
      }
    });
    setShowInspectionForm(true);
    showMessage("Formulario ONAC listo para llenar", "success");
  };

  const handleInspectionComplete = () => {
    setShowInspectionForm(false);
    setSelectedAppointment(null);
    showMessage("Inspección completada exitosamente", "success");
    loadMyAppointments();
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

  const getStatusBadge = (status) => {
    const statusMap = {
      PENDING: { label: "Pendiente", className: "status-pending" },
      CONFIRMED: { label: "Confirmada", className: "status-confirmed" },
      IN_PROGRESS: { label: "En Progreso", className: "status-in-progress" },
      COMPLETED: { label: "Completada", className: "status-completed" },
      CANCELLED: { label: "Cancelada", className: "status-cancelled" },
      RESCHEDULED: { label: "Reagendada", className: "status-rescheduled" }
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
        <div className="appointments-section">
          <h3>Citas Asignadas</h3>
          {loading ? (
            <p>Cargando...</p>
          ) : appointments.length === 0 ? (
            <p className="no-data">No tienes citas asignadas</p>
          ) : (
            <div className="appointments-grid">
              {appointments.map((appointment) => (
                <div key={appointment.id} className="appointment-card">
                  <div className="appointment-header">
                    <h4>{appointment.client_name}</h4>
                    {getStatusBadge(appointment.status)}
                  </div>
                  <div className="appointment-details">
                    <p><strong>Fecha:</strong> {formatDate(appointment.scheduled_date)}</p>
                    <p><strong>Hora:</strong> {formatTime(appointment.scheduled_time)}</p>
                    <p><strong>Dirección:</strong> {appointment.address}</p>
                    <p><strong>Teléfono:</strong> {appointment.client_phone}</p>
                    <p><strong>DNI:</strong> {appointment.client_dni || "-"}</p>
                    {appointment.notes && (
                      <p><strong>Notas:</strong> {appointment.notes}</p>
                    )}
                  </div>
                  {(appointment.status === "PENDING" || appointment.status === "CONFIRMED") && (
                    <div className="appointment-actions">
                      <button
                        className="btn-primary"
                        onClick={() => handleStartInspection(appointment)}
                      >
                        Realizar Inspección
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="inspection-form-container">
          <ONACInspectionForm
            inspectionId={selectedAppointment?.inspection_id}
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
