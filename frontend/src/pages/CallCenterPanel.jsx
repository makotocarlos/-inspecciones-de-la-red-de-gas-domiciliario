import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/CallCenterPanel.css";
import { getErrorMessage } from "../utils/errorHandler";
import InspectorSchedule from "../components/InspectorSchedule";

const API_URL = "http://localhost:8000/api";

function CallCenterPanel() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("nueva-cita");
  const [appointments, setAppointments] = useState([]);
  const [inspectors, setInspectors] = useState([]);
  const [assignedTasks, setAssignedTasks] = useState([]);
  const [needsReschedule, setNeedsReschedule] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    client_name: "",
    client_email: "",
    client_phone: "",
    address_type: "CALLE",
    address_number: "",
    address_cross: "",
    address_detail: "",
    address_neighborhood: "",
    address_city: "Pasto, Nariño",
    client_dni: "",
    last_inspection_date: "",
    inspector_id: "",
    appointment_date: "",
    appointment_time: "",
    service_type: "INSPECCION_GAS",
    notes: ""
  });
  const [message, setMessage] = useState({ text: "", type: "" });
  
  // Para reprogramación
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [rescheduleData, setRescheduleData] = useState({
    new_date: "",
    new_time: "",
    inspector_id: "",
    notes: ""
  });
  
  // Para mostrar cronograma del inspector
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [selectedInspectorForSchedule, setSelectedInspectorForSchedule] = useState(null);
  const [scheduleContext, setScheduleContext] = useState({ date: null, time: null });

  // Función para ver cronograma del inspector
  const handleViewInspectorSchedule = (inspectorId, contextDate = null, contextTime = null) => {
    const inspector = inspectors.find(i => i.id === inspectorId);
    setSelectedInspectorForSchedule({
      id: inspectorId,
      name: inspector ? `${inspector.first_name} ${inspector.last_name}` : ''
    });
    // Establecer contexto de fecha/hora si viene del formulario
    setScheduleContext({
      date: contextDate || formData.appointment_date || null,
      time: contextTime || formData.appointment_time || null
    });
    setShowScheduleModal(true);
  };

  // Cuando se selecciona una fecha y hora del calendario
  const handleScheduleDateSelect = (date, time = null) => {
    if (showRescheduleModal) {
      setRescheduleData(prev => ({ 
        ...prev, 
        new_date: date,
        ...(time && { new_time: time })
      }));
    } else {
      setFormData(prev => ({ 
        ...prev, 
        appointment_date: date,
        ...(time && { appointment_time: time })
      }));
    }
    // Si se seleccionó hora, cerrar el modal
    if (time) {
      setShowScheduleModal(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      loadAppointments();
      loadInspectors();
      loadAssignedTasks();
      loadNeedsReschedule();
    } else {
      const timer = setTimeout(() => {
        const retryToken = localStorage.getItem("token");
        if (retryToken) {
          loadAppointments();
          loadInspectors();
          loadAssignedTasks();
          loadNeedsReschedule();
        } else {
          showMessage("Sesión no válida. Por favor inicia sesión nuevamente.", "error");
          setTimeout(() => navigate("/login"), 2000);
        }
      }, 500);
      return () => clearTimeout(timer);
    }
  }, []);

  const getToken = () => localStorage.getItem("token");

  const loadAppointments = async () => {
    const token = getToken();
    if (!token) return;
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/appointments/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAppointments(response.data.appointments || []);
    } catch (error) {
      console.error("Error cargando citas:", error);
      if (error.response?.status === 401) {
        showMessage("Sesión expirada", "error");
        setTimeout(() => navigate("/login"), 2000);
      }
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

  const loadAssignedTasks = async () => {
    try {
      const response = await axios.get(`${API_URL}/appointments/tasks/`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      // Filtrar solo tareas asignadas a este usuario
      const userStr = localStorage.getItem("user");
      const userId = userStr ? JSON.parse(userStr).id : null;
      const myTasks = (response.data.tasks || []).filter(t => 
        t.assigned_to === userId || t.assigned_to_name
      );
      setAssignedTasks(myTasks);
    } catch (error) {
      console.error("Error cargando tareas asignadas:", error);
    }
  };

  const loadNeedsReschedule = async () => {
    try {
      const response = await axios.get(`${API_URL}/appointments/needs-reschedule/`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setNeedsReschedule(response.data.appointments || []);
    } catch (error) {
      console.error("Error cargando citas para reprogramar:", error);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const buildFormattedAddress = () => {
    const tipo = formData.address_type === "CALLE" ? "Calle" : "Carrera";
    const numero = formData.address_number;
    const cruce = formData.address_cross;
    const detalle = formData.address_detail;
    const barrio = formData.address_neighborhood;
    const ciudad = formData.address_city;
    
    let address = `${tipo} ${numero}`;
    if (cruce) address += ` # ${cruce}`;
    if (detalle) address += `-${detalle}`;
    if (barrio) address += `, Barrio ${barrio}`;
    if (ciudad) address += `, ${ciudad}`;
    
    return address;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const formattedAddress = buildFormattedAddress();
      const appointmentData = {
        client_name: formData.client_name,
        client_email: formData.client_email,
        client_phone: formData.client_phone,
        client_dni: formData.client_dni,
        address: formattedAddress,
        last_inspection_date: formData.last_inspection_date || null,
        inspector: formData.inspector_id,
        scheduled_date: formData.appointment_date,
        scheduled_time: formData.appointment_time,
        notes: formData.notes
      };

      const response = await axios.post(
        `${API_URL}/appointments/`,
        appointmentData,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );

      if (response.data.success) {
        showMessage("Cita agendada exitosamente", "success");
        setFormData({
          client_name: "",
          client_email: "",
          client_phone: "",
          address_type: "CALLE",
          address_number: "",
          address_cross: "",
          address_detail: "",
          address_neighborhood: "",
          address_city: "Pasto, Nariño",
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
      showMessage(getErrorMessage(error, "Error al agendar cita"), "error");
    } finally {
      setLoading(false);
    }
  };

  // Crear cita desde tarea asignada
  const handleCreateFromTask = (task) => {
    // Pre-llenar formulario con datos de la tarea
    setFormData({
      ...formData,
      client_name: task.client_name || "",
      client_email: task.client_email || "",
      client_phone: task.client_phone || "",
      client_dni: "",
      address_type: "CALLE",
      address_number: "",
      address_cross: "",
      address_detail: "",
      address_neighborhood: "",
      address_city: "Pasto, Nariño",
      last_inspection_date: task.last_inspection_date || "",
      notes: `Tarea asignada por Call Center Admin. ${task.notes || ""}`
    });
    setShowForm(true);
    setActiveTab("nueva-cita");
  };

  // Actualizar estado de tarea
  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      await axios.patch(
        `${API_URL}/appointments/tasks/${taskId}/`,
        { status: newStatus },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      showMessage("Estado actualizado", "success");
      loadAssignedTasks();
    } catch (error) {
      showMessage(getErrorMessage(error, "Error al actualizar"), "error");
    }
  };

  // Incrementar intentos de llamada
  const incrementCallAttempts = async (taskId, currentAttempts) => {
    try {
      await axios.patch(
        `${API_URL}/appointments/tasks/${taskId}/`,
        { 
          call_attempts: currentAttempts + 1,
          last_call_date: new Date().toISOString().split('T')[0]
        },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      showMessage("Intento de llamada registrado", "success");
      loadAssignedTasks();
    } catch (error) {
      showMessage(getErrorMessage(error, "Error al registrar"), "error");
    }
  };

  // Reprogramación
  const openRescheduleModal = (appointment) => {
    setSelectedAppointment(appointment);
    setRescheduleData({
      new_date: "",
      new_time: "",
      inspector_id: appointment.inspector || "",
      notes: ""
    });
    setShowRescheduleModal(true);
  };

  const submitReschedule = async (e) => {
    e.preventDefault();
    if (!rescheduleData.new_date || !rescheduleData.new_time || !rescheduleData.inspector_id) {
      showMessage("Complete todos los campos obligatorios", "error");
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API_URL}/appointments/${selectedAppointment.id}/reschedule/`,
        {
          new_date: rescheduleData.new_date,
          new_time: rescheduleData.new_time,
          inspector_id: rescheduleData.inspector_id,
          notes: rescheduleData.notes
        },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      
      showMessage("Cita reprogramada exitosamente", "success");
      setShowRescheduleModal(false);
      loadNeedsReschedule();
      loadAppointments();
    } catch (error) {
      showMessage(getErrorMessage(error, "Error al reprogramar"), "error");
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAppointment = async (appointmentId) => {
    if (!window.confirm("¿Estás seguro de cancelar esta cita?")) return;
    try {
      await axios.patch(
        `${API_URL}/appointments/${appointmentId}/`,
        { status: "CANCELLED" },
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
      RESCHEDULED: { label: "Reagendada", className: "status-rescheduled" },
      NEEDS_RESCHEDULE: { label: "Requiere Reprogramar", className: "status-needs-reschedule" }
    };
    const statusInfo = statusMap[status] || { label: status, className: "" };
    return <span className={`status-badge ${statusInfo.className}`}>{statusInfo.label}</span>;
  };

  const getTaskStatusBadge = (status) => {
    const statusMap = {
      PENDING: { label: "Pendiente", className: "task-pending" },
      IN_PROGRESS: { label: "En Progreso", className: "task-in-progress" },
      COMPLETED: { label: "Completada", className: "task-completed" },
      APPOINTMENT_SCHEDULED: { label: "Cita Agendada", className: "task-scheduled" },
      CLIENT_REFUSED: { label: "Cliente Rechazó", className: "task-refused" },
      NO_ANSWER: { label: "Sin Respuesta", className: "task-no-answer" }
    };
    const info = statusMap[status] || { label: status, className: "" };
    return <span className={`task-status-badge ${info.className}`}>{info.label}</span>;
  };

  const getPriorityBadge = (priority) => {
    const priorityMap = {
      LOW: { label: "Baja", className: "priority-low" },
      MEDIUM: { label: "Media", className: "priority-medium" },
      HIGH: { label: "Alta", className: "priority-high" },
      URGENT: { label: "Urgente", className: "priority-urgent" }
    };
    const info = priorityMap[priority] || { label: priority, className: "" };
    return <span className={`priority-badge ${info.className}`}>{info.label}</span>;
  };

  const formatDate = (dateString) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleDateString("es-CO");
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

        {/* Tabs */}
        <div className="cc-tabs">
          <button
            className={`cc-tab ${activeTab === "nueva-cita" ? "active" : ""}`}
            onClick={() => setActiveTab("nueva-cita")}
          >
            📅 Nueva Cita
          </button>
          <button
            className={`cc-tab ${activeTab === "tareas" ? "active" : ""}`}
            onClick={() => setActiveTab("tareas")}
          >
            📋 Tareas Asignadas ({assignedTasks.length})
          </button>
          <button
            className={`cc-tab ${activeTab === "reprogramar" ? "active" : ""}`}
            onClick={() => setActiveTab("reprogramar")}
          >
            🔄 Reprogramar ({needsReschedule.length})
          </button>
        </div>

        <div className="panel-content">
          {/* Tab: Nueva Cita */}
          {activeTab === "nueva-cita" && (
            <>
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

                    <div className="form-group address-group">
                      <label>Dirección *</label>
                      <div className="address-structured">
                        <div className="address-row">
                          <select
                            name="address_type"
                            value={formData.address_type}
                            onChange={handleInputChange}
                            className="address-type-select"
                          >
                            <option value="CALLE">Calle</option>
                            <option value="CARRERA">Carrera</option>
                          </select>
                          <input
                            type="text"
                            name="address_number"
                            value={formData.address_number}
                            onChange={handleInputChange}
                            placeholder="Nº vía"
                            className="address-number"
                            required
                          />
                          <span className="address-separator">#</span>
                          <input
                            type="text"
                            name="address_cross"
                            value={formData.address_cross}
                            onChange={handleInputChange}
                            placeholder="Nº"
                            className="address-cross"
                            required
                          />
                          <span className="address-separator">-</span>
                          <input
                            type="text"
                            name="address_detail"
                            value={formData.address_detail}
                            onChange={handleInputChange}
                            placeholder="Nº"
                            className="address-detail"
                          />
                        </div>
                        <div className="address-row">
                          <input
                            type="text"
                            name="address_neighborhood"
                            value={formData.address_neighborhood}
                            onChange={handleInputChange}
                            placeholder="Barrio"
                            className="address-neighborhood"
                            required
                          />
                          <input
                            type="text"
                            name="address_city"
                            value={formData.address_city}
                            onChange={handleInputChange}
                            placeholder="Ciudad"
                            className="address-city"
                          />
                        </div>
                        <small className="address-preview">
                          <strong>Vista previa:</strong> {formData.address_type === "CALLE" ? "Calle" : "Carrera"} {formData.address_number || "___"} # {formData.address_cross || "___"}-{formData.address_detail || "___"}, Barrio {formData.address_neighborhood || "___"}, {formData.address_city || "___"}
                        </small>
                      </div>
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
                    </div>
                  </div>

                  <div className="form-section">
                    <h4>Datos de la Cita</h4>
                    
                    {/* Inspector y Tipo de Servicio primero */}
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

                    {/* Fecha y Hora después */}
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
                    
                    {/* Botón de verificar disponibilidad y seleccionar desde cronograma */}
                    {formData.inspector_id && (
                      <div className="availability-check-row">
                        <button
                          type="button"
                          className="btn-check-availability"
                          onClick={() => handleViewInspectorSchedule(formData.inspector_id, formData.appointment_date, formData.appointment_time)}
                        >
                          📅 {formData.appointment_date && formData.appointment_time 
                            ? 'Verificar Disponibilidad' 
                            : 'Seleccionar Fecha/Hora desde Cronograma'}
                        </button>
                        <span className="availability-hint">
                          {formData.appointment_date && formData.appointment_time 
                            ? 'Click para ver el cronograma del inspector'
                            : 'Selecciona inspector primero, luego elige fecha y hora desde el cronograma'}
                        </span>
                      </div>
                    )}

                    <div className="form-group">
                      <label>Notas Adicionales</label>
                      <textarea
                        name="notes"
                        value={formData.notes}
                        onChange={handleInputChange}
                        rows="3"
                        placeholder="Información adicional..."
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
                        </div>
                        {appointment.status === "PENDING" && (
                          <div className="appointment-actions">
                            <button
                              className="btn-cancel"
                              onClick={() => handleCancelAppointment(appointment.id)}
                            >
                              Cancelar
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}

          {/* Tab: Tareas Asignadas */}
          {activeTab === "tareas" && (
            <div className="tasks-section">
              <div className="section-header-cc">
                <h3>📋 Tareas Asignadas por Call Center Admin</h3>
                <button onClick={loadAssignedTasks} className="btn-refresh">
                  🔄 Actualizar
                </button>
              </div>

              {assignedTasks.length === 0 ? (
                <div className="empty-state-cc">
                  <p>📭 No tienes tareas asignadas</p>
                </div>
              ) : (
                <div className="tasks-grid-cc">
                  {assignedTasks.map((task) => (
                    <div key={task.id} className={`task-card-cc ${task.priority.toLowerCase()}`}>
                      <div className="task-header-cc">
                        <h4>{task.client_name}</h4>
                        <div className="task-badges">
                          {getPriorityBadge(task.priority)}
                          {getTaskStatusBadge(task.status)}
                        </div>
                      </div>
                      
                      <div className="task-details-cc">
                        <p>📧 {task.client_email || "-"}</p>
                        <p>📞 {task.client_phone || "-"}</p>
                        <p>📍 {task.client_address || "-"}</p>
                        <p>📅 Última inspección: {formatDate(task.last_inspection_date)}</p>
                        <p>⏰ Próxima: {formatDate(task.next_inspection_due)}</p>
                        <p>📞 Intentos: {task.call_attempts || 0}</p>
                        {task.notes && <p>💬 {task.notes}</p>}
                      </div>
                      
                      <div className="task-actions-cc">
                        {task.status === "PENDING" && (
                          <>
                            <button 
                              onClick={() => updateTaskStatus(task.id, "IN_PROGRESS")}
                              className="btn-start"
                            >
                              ▶️ Iniciar
                            </button>
                          </>
                        )}
                        
                        {task.status === "IN_PROGRESS" && (
                          <>
                            <button 
                              onClick={() => incrementCallAttempts(task.id, task.call_attempts || 0)}
                              className="btn-call"
                            >
                              📞 Registrar Llamada
                            </button>
                            <button 
                              onClick={() => handleCreateFromTask(task)}
                              className="btn-schedule"
                            >
                              📅 Agendar Cita
                            </button>
                            <button 
                              onClick={() => updateTaskStatus(task.id, "NO_ANSWER")}
                              className="btn-no-answer"
                            >
                              ❌ Sin Respuesta
                            </button>
                            <button 
                              onClick={() => updateTaskStatus(task.id, "CLIENT_REFUSED")}
                              className="btn-refused"
                            >
                              🚫 Rechazó
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Tab: Reprogramar */}
          {activeTab === "reprogramar" && (
            <div className="reschedule-section">
              <div className="section-header-cc">
                <h3>🔄 Citas que Requieren Reprogramación</h3>
                <button onClick={loadNeedsReschedule} className="btn-refresh">
                  🔄 Actualizar
                </button>
              </div>

              {needsReschedule.length === 0 ? (
                <div className="empty-state-cc">
                  <p>✅ No hay citas pendientes de reprogramar</p>
                </div>
              ) : (
                <div className="reschedule-grid">
                  {needsReschedule.map((apt) => (
                    <div key={apt.id} className="reschedule-card">
                      <div className="reschedule-header">
                        <h4>{apt.client_name}</h4>
                        {getStatusBadge(apt.status)}
                      </div>
                      
                      <div className="reschedule-details">
                        <p><strong>📅 Fecha original:</strong> {formatDate(apt.scheduled_date)}</p>
                        <p><strong>⏰ Hora:</strong> {formatTime(apt.scheduled_time)}</p>
                        <p><strong>📍 Dirección:</strong> {apt.address}</p>
                        <p><strong>📞 Teléfono:</strong> {apt.client_phone}</p>
                        <p><strong>👷 Inspector:</strong> {apt.inspector_name || "-"}</p>
                        {apt.notes && (
                          <p><strong>📝 Notas:</strong> {apt.notes}</p>
                        )}
                      </div>
                      
                      <div className="reschedule-actions">
                        <button 
                          onClick={() => openRescheduleModal(apt)}
                          className="btn-reschedule"
                        >
                          📅 Reprogramar Cita
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Modal de Reprogramación */}
      {showRescheduleModal && selectedAppointment && (
        <div className="modal-overlay-cc" onClick={() => setShowRescheduleModal(false)}>
          <div className="modal-content-cc" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-cc">
              <h2>Reprogramar Cita</h2>
              <button className="close-btn-cc" onClick={() => setShowRescheduleModal(false)}>×</button>
            </div>
            
            <div className="modal-body-cc">
              <div className="apt-info-box">
                <h3>{selectedAppointment.client_name}</h3>
                <p>📞 {selectedAppointment.client_phone}</p>
                <p>📍 {selectedAppointment.address}</p>
                <p>📅 Fecha original: {formatDate(selectedAppointment.scheduled_date)} - {formatTime(selectedAppointment.scheduled_time)}</p>
              </div>

              <form onSubmit={submitReschedule}>
                <div className="form-group">
                  <label>Nueva Fecha *</label>
                  <input
                    type="date"
                    value={rescheduleData.new_date}
                    onChange={(e) => setRescheduleData({...rescheduleData, new_date: e.target.value})}
                    min={new Date().toISOString().split("T")[0]}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Nueva Hora *</label>
                  <input
                    type="time"
                    value={rescheduleData.new_time}
                    onChange={(e) => setRescheduleData({...rescheduleData, new_time: e.target.value})}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Inspector *</label>
                  <div className="inspector-select-wrapper">
                    <select
                      value={rescheduleData.inspector_id}
                      onChange={(e) => setRescheduleData({...rescheduleData, inspector_id: e.target.value})}
                      required
                    >
                      <option value="">Seleccione un inspector</option>
                      {inspectors.map((inspector) => (
                        <option key={inspector.id} value={inspector.id}>
                          {inspector.first_name} {inspector.last_name}
                        </option>
                      ))}
                    </select>
                    {rescheduleData.inspector_id && (
                      <button
                        type="button"
                        className="btn-view-schedule"
                        onClick={() => handleViewInspectorSchedule(rescheduleData.inspector_id)}
                        title="Ver cronograma del inspector"
                      >
                        📅 Ver Cronograma
                      </button>
                    )}
                  </div>
                </div>

                <div className="form-group">
                  <label>Notas (opcional)</label>
                  <textarea
                    value={rescheduleData.notes}
                    onChange={(e) => setRescheduleData({...rescheduleData, notes: e.target.value})}
                    rows={3}
                    placeholder="Razón de reprogramación..."
                  />
                </div>

                <div className="modal-actions-cc">
                  <button 
                    type="button" 
                    className="btn-cancel-modal"
                    onClick={() => setShowRescheduleModal(false)}
                  >
                    Cancelar
                  </button>
                  <button 
                    type="submit" 
                    className="btn-submit-modal"
                    disabled={loading}
                  >
                    {loading ? "Reprogramando..." : "Confirmar Reprogramación"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Cronograma del Inspector */}
      {showScheduleModal && selectedInspectorForSchedule && (
        <InspectorSchedule
          inspectorId={selectedInspectorForSchedule.id}
          inspectorName={selectedInspectorForSchedule.name}
          onSelectDate={handleScheduleDateSelect}
          onClose={() => setShowScheduleModal(false)}
          initialDate={scheduleContext.date}
          initialTime={scheduleContext.time}
        />
      )}
    </div>
  );
}

export default CallCenterPanel;
