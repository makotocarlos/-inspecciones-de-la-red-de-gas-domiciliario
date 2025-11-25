import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/CallCenterPanel.css";
import { getErrorMessage } from "../utils/errorHandler";

const API_URL = "http://localhost:8000/api";

function CallCenterPanel() {
  const navigate = useNavigate();
  const [appointments, setAppointments] = useState([]);
  const [inspectors, setInspectors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    client_name: "",
    client_email: "",
    client_phone: "",
    client_address: "",
    client_dni: "",
    last_inspection_date: "",
    inspector_id: "",
    appointment_date: "",
    appointment_time: "",
    service_type: "INSPECCION_GAS",
    notes: ""
  });
  const [message, setMessage] = useState({ text: "", type: "" });

  useEffect(() => {
    loadAppointments();
    loadInspectors();
  }, []);

  const getToken = () => localStorage.getItem("token");

  const loadAppointments = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/appointments/`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setAppointments(response.data.appointments || []);
    } catch (error) {
      console.error("Error cargando citas:", error);
      showMessage(getErrorMessage(error, "Error al cargar citas"), "error");
    } finally {
      setLoading(false);
    }
  };

  const loadInspectors = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/inspectors/`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setInspectors(response.data.inspectors || []);
    } catch (error) {
      console.error("Error cargando inspectores:", error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Transform data to match backend expected format
      const appointmentData = {
        client_name: formData.client_name,
        client_email: formData.client_email,
        client_phone: formData.client_phone,
        client_dni: formData.client_dni,
        address: formData.client_address,  // backend expects 'address'
        last_inspection_date: formData.last_inspection_date || null,  // última inspección
        inspector: formData.inspector_id,   // backend expects 'inspector'
        scheduled_date: formData.appointment_date,  // backend expects 'scheduled_date'
        scheduled_time: formData.appointment_time,  // backend expects 'scheduled_time'
        notes: formData.notes
      };

      console.log("Enviando datos:", appointmentData);

      const response = await axios.post(
        `${API_URL}/appointments/`,
        appointmentData,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );

      console.log("Respuesta del servidor:", response.data);

      if (response.data.success) {
        showMessage("Cita agendada exitosamente", "success");
        setFormData({
          client_name: "",
          client_email: "",
          client_phone: "",
          client_address: "",
          client_dni: "",
          last_inspection_date: "",
          inspector_id: "",
          appointment_date: "",
          appointment_time: "",
          service_type: "INSPECCION_GAS",
          notes: ""
        });
        setShowForm(false);
        loadAppointments();
      }
    } catch (error) {
      console.error("Error completo:", error);
      console.error("Response data:", error.response?.data);
      showMessage(
        getErrorMessage(error, "Error al agendar cita"),
        "error"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAppointment = async (appointmentId) => {
    if (!window.confirm("¿Estás seguro de cancelar esta cita?")) return;

    try {
      await axios.patch(
        `${API_URL}/appointments/${appointmentId}/`,
        { status: "CANCELADA" },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      showMessage("Cita cancelada exitosamente", "success");
      loadAppointments();
    } catch (error) {
      showMessage(getErrorMessage(error, "Error al cancelar cita"), "error");
    }
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
    <div className="callcenter-panel">
      {/* Navbar */}
      <nav className="callcenter-navbar">
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
          <h2 className="navbar-title">Panel Call Center</h2>
        </div>
        <div className="navbar-right">
          {/* Espacio para futuros elementos */}
        </div>
      </nav>

      {/* Content */}
      <div className="callcenter-content">
        <div className="callcenter-header">
          <h1>Panel Call Center</h1>
          <p>Gestión de Citas de Inspección</p>
        </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="panel-content">
        <div className="panel-actions">
          <button
            className="btn-primary"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? "Cancelar" : "Agendar Nueva Cita"}
          </button>
        </div>

        {showForm && (
          <form className="appointment-form" onSubmit={handleSubmit}>
            <h3>Nueva Cita de Inspección</h3>

            <div className="form-section">
              <h4>Datos del Cliente</h4>
              <div className="form-row">
                <div className="form-group">
                  <label>Nombre Completo *</label>
                  <input
                    type="text"
                    name="client_name"
                    value={formData.client_name}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Cédula *</label>
                  <input
                    type="text"
                    name="client_dni"
                    value={formData.client_dni}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="client_email"
                    value={formData.client_email}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>Teléfono *</label>
                  <input
                    type="tel"
                    name="client_phone"
                    value={formData.client_phone}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Dirección *</label>
                <input
                  type="text"
                  name="client_address"
                  value={formData.client_address}
                  onChange={handleInputChange}
                  placeholder="Ej: Calle 123 #45-67, Bogotá"
                  required
                />
              </div>

              <div className="form-group">
                <label>Fecha de Última Inspección (Opcional)</label>
                <input
                  type="date"
                  name="last_inspection_date"
                  value={formData.last_inspection_date}
                  onChange={handleInputChange}
                  max={new Date().toISOString().split("T")[0]}
                />
                <small style={{color: '#888', fontSize: '0.85em'}}>
                  Si el cliente ya tuvo una inspección anterior, ingrese la fecha aquí
                </small>
              </div>
            </div>

            <div className="form-section">
              <h4>Datos de la Cita</h4>
              <div className="form-row">
                <div className="form-group">
                  <label>Fecha *</label>
                  <input
                    type="date"
                    name="appointment_date"
                    value={formData.appointment_date}
                    onChange={handleInputChange}
                    min={new Date().toISOString().split("T")[0]}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Hora *</label>
                  <input
                    type="time"
                    name="appointment_time"
                    value={formData.appointment_time}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Inspector Asignado *</label>
                  <select
                    name="inspector_id"
                    value={formData.inspector_id}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Seleccione un inspector</option>
                    {inspectors.map((inspector) => (
                      <option key={inspector.id} value={inspector.id}>
                        {inspector.first_name} {inspector.last_name}
                        {inspector.license_number && ` - Lic: ${inspector.license_number}`}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Tipo de Servicio *</label>
                  <select
                    name="service_type"
                    value={formData.service_type}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="INSPECCION_GAS">Inspección de Gas</option>
                    <option value="MANTENIMIENTO">Mantenimiento</option>
                    <option value="REPARACION">Reparación</option>
                    <option value="INSTALACION">Instalación</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Notas Adicionales</label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  rows="3"
                  placeholder="Información adicional relevante..."
                />
              </div>
            </div>

            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? "Agendando..." : "Agendar Cita"}
            </button>
          </form>
        )}

        <div className="appointments-list">
          <h3>Citas Agendadas</h3>
          {loading ? (
            <p>Cargando...</p>
          ) : appointments.length === 0 ? (
            <p className="no-data">No hay citas agendadas</p>
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
                    <p><strong>Inspector:</strong> {appointment.inspector_name || "-"}</p>
                    {appointment.notes && (
                      <p><strong>Notas:</strong> {appointment.notes}</p>
                    )}
                  </div>
                  {appointment.status === "PENDING" && (
                    <div className="appointment-actions">
                      <button
                        className="btn-cancel"
                        onClick={() => handleCancelAppointment(appointment.id)}
                      >
                        Cancelar Cita
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      </div>
    </div>
  );
}

export default CallCenterPanel;
