import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/AdminPanel.css";
import { getErrorMessage } from "../utils/errorHandler";

const API_URL = "http://localhost:8000/api";

function CallCenterAdminPanel() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("alerts");
  const [clientsNeedingInspection, setClientsNeedingInspection] = useState([]);
  const [callCenters, setCallCenters] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [reschedules, setReschedules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });
  
  // Modal para asignar tarea
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [assignData, setAssignData] = useState({
    assigned_to: "",
    priority: "MEDIUM",
    notes: ""
  });

  // Modal para asignar reprogramación
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [selectedReschedule, setSelectedReschedule] = useState(null);
  const [rescheduleAssignData, setRescheduleAssignData] = useState({
    assigned_to: "",
    priority: "HIGH",
    notes: ""
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      loadClientsNeedingInspection();
      loadCallCenters();
      loadTasks();
      loadReschedules();
    } else {
      setTimeout(() => navigate("/login"), 500);
    }
  }, []);

  const getToken = () => localStorage.getItem("token");

  const loadClientsNeedingInspection = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/appointments/clients-needing-inspection/`,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      setClientsNeedingInspection(response.data.clients || []);
    } catch (error) {
      console.error("Error cargando clientes:", error);
      showMessage(getErrorMessage(error, "Error al cargar clientes"), "error");
    }
  };

  const loadCallCenters = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/appointments/call-centers/`,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      setCallCenters(response.data.call_centers || []);
    } catch (error) {
      console.error("Error cargando call centers:", error);
    }
  };

  const loadTasks = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/appointments/tasks/`,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      setTasks(response.data.tasks || []);
    } catch (error) {
      console.error("Error cargando tareas:", error);
    }
  };

  const loadReschedules = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/appointments/needs-reschedule/`,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      setReschedules(response.data.appointments || []);
    } catch (error) {
      console.error("Error cargando reprogramaciones:", error);
    }
  };

  const handleAssignTask = (client) => {
    setSelectedClient(client);
    setAssignData({
      assigned_to: "",
      priority: client.priority || "MEDIUM",
      notes: ""
    });
    setShowAssignModal(true);
  };

  const submitAssignment = async (e) => {
    e.preventDefault();
    if (!assignData.assigned_to) {
      showMessage("Selecciona un Call Center", "error");
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API_URL}/appointments/tasks/`,
        {
          client_id: selectedClient.id,
          client_name: selectedClient.full_name,
          client_email: selectedClient.email,
          client_phone: selectedClient.phone_number,
          client_address: selectedClient.address,
          last_inspection_date: selectedClient.last_inspection_date,
          next_inspection_due: selectedClient.next_inspection_due,
          assigned_to: assignData.assigned_to,
          priority: assignData.priority,
          notes: assignData.notes
        },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      
      showMessage("Tarea asignada exitosamente", "success");
      setShowAssignModal(false);
      loadTasks();
      loadClientsNeedingInspection();
    } catch (error) {
      showMessage(getErrorMessage(error, "Error al asignar tarea"), "error");
    } finally {
      setLoading(false);
    }
  };

  // Funciones para reprogramaciones
  const handleAssignReschedule = (appointment) => {
    setSelectedReschedule(appointment);
    setRescheduleAssignData({
      assigned_to: "",
      priority: "HIGH",
      notes: `Reprogramar cita del ${formatDate(appointment.scheduled_date)}. ${appointment.notes || ""}`
    });
    setShowRescheduleModal(true);
  };

  const submitRescheduleAssignment = async (e) => {
    e.preventDefault();
    if (!rescheduleAssignData.assigned_to) {
      showMessage("Selecciona un Call Center", "error");
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API_URL}/appointments/tasks/`,
        {
          client_name: selectedReschedule.client_name,
          client_email: selectedReschedule.client_email,
          client_phone: selectedReschedule.client_phone,
          client_address: selectedReschedule.address,
          source_appointment: selectedReschedule.id,
          task_type: "RESCHEDULE",
          assigned_to: rescheduleAssignData.assigned_to,
          priority: rescheduleAssignData.priority,
          notes: rescheduleAssignData.notes
        },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      
      showMessage("Tarea de reprogramación asignada exitosamente", "success");
      setShowRescheduleModal(false);
      loadTasks();
      loadReschedules();
    } catch (error) {
      showMessage(getErrorMessage(error, "Error al asignar reprogramación"), "error");
    } finally {
      setLoading(false);
    }
  };

  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      await axios.patch(
        `${API_URL}/appointments/tasks/${taskId}/`,
        { status: newStatus },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      showMessage("Estado actualizado", "success");
      loadTasks();
    } catch (error) {
      showMessage(getErrorMessage(error, "Error al actualizar"), "error");
    }
  };

  const deleteTask = async (taskId) => {
    if (!window.confirm("¿Eliminar esta tarea?")) return;
    
    try {
      await axios.delete(
        `${API_URL}/appointments/tasks/${taskId}/`,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      showMessage("Tarea eliminada", "success");
      loadTasks();
    } catch (error) {
      showMessage(getErrorMessage(error, "Error al eliminar"), "error");
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: "", type: "" }), 5000);
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

  const getStatusBadge = (status) => {
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

  const formatDate = (dateString) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleDateString("es-CO");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/login";
  };

  const getDaysUntilText = (days) => {
    if (days === null || days === undefined) return "-";
    if (days < 0) return <span className="overdue">Vencido hace {Math.abs(days)} días</span>;
    if (days === 0) return <span className="due-today">¡Hoy vence!</span>;
    if (days <= 30) return <span className="urgent">{days} días</span>;
    if (days <= 90) return <span className="soon">{days} días</span>;
    return <span className="ok">{days} días</span>;
  };

  return (
    <div className="admin-panel">
      {/* Navbar */}
      <nav className="admin-navbar">
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
          <h2 className="navbar-title">Call Center Admin</h2>
        </div>
        <div className="navbar-right"></div>
      </nav>

      {/* Content */}
      <div className="admin-content">
        <div className="admin-header">
          <h1>📋 Call Center Admin</h1>
          <p>Gestión de Inspecciones Periódicas</p>
        </div>

        {/* Mensaje */}
        {message.text && (
          <div className={`message ${message.type}`}>{message.text}</div>
        )}

        {/* Tabs */}
        <div className="tabs">
          <button
            className={activeTab === "alerts" ? "active" : ""}
            onClick={() => setActiveTab("alerts")}
          >
            🔔 Alertas de Inspección ({clientsNeedingInspection.length})
          </button>
          <button
            className={activeTab === "reschedules" ? "active" : ""}
            onClick={() => setActiveTab("reschedules")}
          >
            🔄 Reprogramaciones ({reschedules.length})
          </button>
          <button
            className={activeTab === "tasks" ? "active" : ""}
            onClick={() => setActiveTab("tasks")}
          >
            📝 Tareas Asignadas ({tasks.length})
          </button>
        </div>

        {/* Panel Content */}
        <div className="panel-content">
          {/* Tab: Alertas */}
          {activeTab === "alerts" && (
            <div className="alerts-section">
              <div className="section-header">
                <h3>Clientes que Necesitan Inspección</h3>
                <p className="info-text">
                  Las inspecciones de gas son obligatorias cada 5 años. 
                  Aquí se muestran los clientes próximos a vencer o ya vencidos.
                </p>
                <button 
                  onClick={loadClientsNeedingInspection} 
                  className="btn-primary refresh-btn"
                >
                  🔄 Actualizar
                </button>
              </div>

              {clientsNeedingInspection.length === 0 ? (
                <div className="empty-state">
                  <p>✅ No hay clientes con inspecciones próximas a vencer</p>
                </div>
              ) : (
                <div className="users-list">
                  <table>
                    <thead>
                      <tr>
                        <th>Cliente</th>
                        <th>Contacto</th>
                        <th>Última Inspección</th>
                        <th>Próxima Inspección</th>
                        <th>Días Restantes</th>
                        <th>Prioridad</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {clientsNeedingInspection.map((client) => (
                        <tr key={client.id} className={client.days_until_due < 0 ? "overdue-row" : ""}>
                          <td>
                            <strong>{client.full_name}</strong>
                            <br />
                            <small>{client.address || "-"}</small>
                          </td>
                          <td>
                            {client.email}<br />
                            {client.phone_number || "-"}
                          </td>
                          <td>{formatDate(client.last_inspection_date)}</td>
                          <td>{formatDate(client.next_inspection_due)}</td>
                          <td>{getDaysUntilText(client.days_until_due)}</td>
                          <td>{getPriorityBadge(client.priority)}</td>
                          <td>
                            <button
                              onClick={() => handleAssignTask(client)}
                              className="assign-btn"
                            >
                              📞 Asignar Llamada
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Tab: Reprogramaciones */}
          {activeTab === "reschedules" && (
            <div className="reschedules-section">
              <div className="section-header">
                <h3>Citas que Requieren Reprogramación</h3>
                <p className="info-text">
                  Estas citas fueron marcadas por el inspector para reprogramar.
                  Asigna a un Call Center para contactar al cliente.
                </p>
                <button 
                  onClick={loadReschedules} 
                  className="btn-primary refresh-btn"
                >
                  🔄 Actualizar
                </button>
              </div>

              {reschedules.length === 0 ? (
                <div className="empty-state">
                  <p>✅ No hay citas pendientes de reprogramar</p>
                </div>
              ) : (
                <div className="users-list">
                  <table>
                    <thead>
                      <tr>
                        <th>Cliente</th>
                        <th>Dirección</th>
                        <th>Fecha Original</th>
                        <th>Inspector</th>
                        <th>Motivo</th>
                        <th>Asignado a</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reschedules.map((apt) => (
                        <tr key={apt.id}>
                          <td>
                            <strong>{apt.client_name}</strong>
                            <br />
                            <small>{apt.client_phone}</small>
                          </td>
                          <td>{apt.address}</td>
                          <td>
                            {formatDate(apt.scheduled_date)}
                            <br />
                            <small>{apt.scheduled_time}</small>
                          </td>
                          <td>{apt.inspector_name || "-"}</td>
                          <td>
                            <span className="reschedule-reason">
                              {apt.notes || "Sin motivo especificado"}
                            </span>
                          </td>
                          <td>
                            {apt.assigned_task ? (
                              <span className="assigned-badge">
                                👤 {apt.assigned_task.assigned_to_name}
                                <br />
                                <small className={`task-status ${apt.assigned_task.status.toLowerCase()}`}>
                                  {apt.assigned_task.status === 'PENDING' && '⏳ Pendiente'}
                                  {apt.assigned_task.status === 'IN_PROGRESS' && '🔄 En Proceso'}
                                  {apt.assigned_task.status === 'COMPLETED' && '✅ Completado'}
                                  {apt.assigned_task.status === 'APPOINTMENT_SCHEDULED' && '📅 Cita Agendada'}
                                </small>
                              </span>
                            ) : (
                              <span className="not-assigned">Sin asignar</span>
                            )}
                          </td>
                          <td>
                            {apt.assigned_task ? (
                              <span className="already-assigned-info">
                                ✅ Ya asignado
                              </span>
                            ) : (
                              <button
                                onClick={() => handleAssignReschedule(apt)}
                                className="assign-btn reschedule-btn"
                              >
                                📞 Asignar Reprogramación
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Tab: Tareas */}
          {activeTab === "tasks" && (
            <div className="tasks-section">
              <div className="section-header">
                <h3>Tareas Asignadas a Call Center</h3>
                <button onClick={loadTasks} className="btn-primary refresh-btn">
                  🔄 Actualizar
                </button>
              </div>

              {tasks.length === 0 ? (
                <div className="empty-state">
                  <p>📭 No hay tareas asignadas</p>
                </div>
              ) : (
                <div className="tasks-grid">
                  {tasks.map((task) => (
                    <div key={task.id} className={`task-card ${task.status.toLowerCase()}`}>
                      <div className="task-header">
                        <h4>{task.client_name}</h4>
                        {getStatusBadge(task.status)}
                      </div>
                      
                      <div className="task-details">
                        <p><strong>📍</strong> {task.client_address || "-"}</p>
                        <p><strong>📧</strong> {task.client_email || "-"}</p>
                        <p><strong>📞</strong> {task.client_phone || "-"}</p>
                        <p><strong>📅 Última:</strong> {formatDate(task.last_inspection_date)}</p>
                        <p><strong>⏰ Próxima:</strong> {formatDate(task.next_inspection_due)}</p>
                        <p><strong>📊 Prioridad:</strong> {getPriorityBadge(task.priority)}</p>
                        <p><strong>👤 Asignado a:</strong> {task.assigned_to_name}</p>
                        <p><strong>📝 Intentos:</strong> {task.call_attempts || 0}</p>
                        {task.notes && (
                          <p><strong>💬 Notas:</strong> {task.notes}</p>
                        )}
                      </div>
                      
                      <div className="task-actions">
                        {task.status === "PENDING" && (
                          <button 
                            onClick={() => updateTaskStatus(task.id, "IN_PROGRESS")}
                            className="btn-progress"
                          >
                            Iniciar
                          </button>
                        )}
                        {task.status !== "COMPLETED" && task.status !== "APPOINTMENT_SCHEDULED" && (
                          <button 
                            onClick={() => deleteTask(task.id)}
                            className="btn-delete"
                          >
                            Eliminar
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Modal Asignar Tarea */}
      {showAssignModal && selectedClient && (
        <div className="modal-overlay" onClick={() => setShowAssignModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Asignar Tarea de Llamada</h2>
              <button 
                className="close-btn" 
                onClick={() => setShowAssignModal(false)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="client-info-box">
                <h3>{selectedClient.full_name}</h3>
                <p>📧 {selectedClient.email}</p>
                <p>📞 {selectedClient.phone_number || "Sin teléfono"}</p>
                <p>📍 {selectedClient.address || "Sin dirección"}</p>
                <p>📅 Última inspección: {formatDate(selectedClient.last_inspection_date)}</p>
                <p>⏰ Próxima: {formatDate(selectedClient.next_inspection_due)}</p>
              </div>

              <form onSubmit={submitAssignment}>
                <div className="form-group">
                  <label>Asignar a Call Center *</label>
                  <select
                    value={assignData.assigned_to}
                    onChange={(e) => setAssignData({...assignData, assigned_to: e.target.value})}
                    required
                  >
                    <option value="">-- Seleccionar --</option>
                    {callCenters.map((cc) => (
                      <option key={cc.id} value={cc.id}>
                        {cc.first_name} {cc.last_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Prioridad</label>
                  <select
                    value={assignData.priority}
                    onChange={(e) => setAssignData({...assignData, priority: e.target.value})}
                  >
                    <option value="LOW">Baja</option>
                    <option value="MEDIUM">Media</option>
                    <option value="HIGH">Alta</option>
                    <option value="URGENT">Urgente</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Notas (opcional)</label>
                  <textarea
                    value={assignData.notes}
                    onChange={(e) => setAssignData({...assignData, notes: e.target.value})}
                    placeholder="Instrucciones adicionales..."
                    rows={3}
                  />
                </div>

                <div className="modal-actions">
                  <button 
                    type="button" 
                    className="btn-cancel"
                    onClick={() => setShowAssignModal(false)}
                  >
                    Cancelar
                  </button>
                  <button 
                    type="submit" 
                    className="btn-submit"
                    disabled={loading}
                  >
                    {loading ? "Asignando..." : "Asignar Tarea"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modal Asignar Reprogramación */}
      {showRescheduleModal && selectedReschedule && (
        <div className="modal-overlay" onClick={() => setShowRescheduleModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Asignar Reprogramación</h2>
              <button 
                className="close-btn" 
                onClick={() => setShowRescheduleModal(false)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="client-info-box reschedule-info">
                <h3>🔄 {selectedReschedule.client_name}</h3>
                <p>📞 {selectedReschedule.client_phone || "Sin teléfono"}</p>
                <p>📍 {selectedReschedule.address}</p>
                <p>📅 Cita original: {formatDate(selectedReschedule.scheduled_date)} {selectedReschedule.scheduled_time}</p>
                <p>👤 Inspector: {selectedReschedule.inspector_name || "Sin asignar"}</p>
                {selectedReschedule.notes && (
                  <p className="reschedule-notes">💬 Motivo: {selectedReschedule.notes}</p>
                )}
              </div>

              <form onSubmit={submitRescheduleAssignment}>
                <div className="form-group">
                  <label>Asignar a Call Center *</label>
                  <select
                    value={rescheduleAssignData.assigned_to}
                    onChange={(e) => setRescheduleAssignData({...rescheduleAssignData, assigned_to: e.target.value})}
                    required
                  >
                    <option value="">-- Seleccionar --</option>
                    {callCenters.map((cc) => (
                      <option key={cc.id} value={cc.id}>
                        {cc.first_name} {cc.last_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Prioridad</label>
                  <select
                    value={rescheduleAssignData.priority}
                    onChange={(e) => setRescheduleAssignData({...rescheduleAssignData, priority: e.target.value})}
                  >
                    <option value="LOW">Baja</option>
                    <option value="MEDIUM">Media</option>
                    <option value="HIGH">Alta</option>
                    <option value="URGENT">Urgente</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Notas (opcional)</label>
                  <textarea
                    value={rescheduleAssignData.notes}
                    onChange={(e) => setRescheduleAssignData({...rescheduleAssignData, notes: e.target.value})}
                    placeholder="Instrucciones para la reprogramación..."
                    rows={3}
                  />
                </div>

                <div className="modal-actions">
                  <button 
                    type="button" 
                    className="btn-cancel"
                    onClick={() => setShowRescheduleModal(false)}
                  >
                    Cancelar
                  </button>
                  <button 
                    type="submit" 
                    className="btn-submit"
                    disabled={loading}
                  >
                    {loading ? "Asignando..." : "Asignar Reprogramación"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CallCenterAdminPanel;
