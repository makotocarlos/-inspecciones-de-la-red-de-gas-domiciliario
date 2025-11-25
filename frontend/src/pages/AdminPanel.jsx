import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/AdminPanel.css";
import { getErrorMessage } from "../utils/errorHandler";

const API_URL = "http://localhost:8000/api";

function AdminPanel() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("callcenter");
  const [callCenters, setCallCenters] = useState([]);
  const [inspectors, setInspectors] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    phone: "",
    license_number: ""
  });
  const [message, setMessage] = useState({ text: "", type: "" });
  const [tempPassword, setTempPassword] = useState(null);
  const [showPasswordModal, setShowPasswordModal] = useState(false);

  useEffect(() => {
    loadUsers();
  }, [activeTab]);

  const getToken = () => localStorage.getItem("token");

  const loadUsers = async () => {
    setLoading(true);
    try {
      let response;
      if (activeTab === "clients") {
        response = await axios.get(`${API_URL}/auth/admin/clients/`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        });
        setClients(response.data.clients || []);
      } else {
        const endpoint = activeTab === "callcenter" ? "call-center" : "inspectors";
        response = await axios.get(`${API_URL}/auth/admin/${endpoint}/`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        });

        if (activeTab === "callcenter") {
          setCallCenters(response.data.call_centers || []);
        } else {
          setInspectors(response.data.inspectors || []);
        }
      }
    } catch (error) {
      console.error("Error cargando usuarios:", error);
      showMessage("Error al cargar usuarios", "error");
    } finally {
      setLoading(false);
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
      const endpoint = activeTab === "callcenter" ? "call-center" : "inspectors";
      const response = await axios.post(
        `${API_URL}/auth/admin/${endpoint}/`,
        formData,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );

      if (response.data.success) {
        // Show password modal
        setTempPassword({
          username: formData.username,
          password: response.data.temp_password
        });
        setShowPasswordModal(true);

        setFormData({
          username: "",
          email: "",
          first_name: "",
          last_name: "",
          phone: "",
          license_number: ""
        });
        setShowForm(false);
        loadUsers();
      }
    } catch (error) {
      showMessage(
        getErrorMessage(error, "Error al crear usuario"),
        "error"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (userId) => {
    if (!window.confirm("¿Estás seguro de desactivar este usuario?")) return;

    try {
      await axios.delete(`${API_URL}/auth/admin/users/${userId}/`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      showMessage("Usuario desactivado exitosamente", "success");
      loadUsers();
    } catch (error) {
      showMessage("Error al desactivar usuario", "error");
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: "", type: "" }), 5000);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/login";
  };

  const users = activeTab === "callcenter" ? callCenters : activeTab === "inspectors" ? inspectors : clients;

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
          <h2 className="navbar-title">Panel de Administrador</h2>
        </div>
        <div className="navbar-right">
          {/* Espacio para futuros elementos */}
        </div>
      </nav>

      {/* Content */}
      <div className="admin-content">
        <div className="admin-header">
          <h1>Panel de Administrador</h1>
          <p>Gestiona usuarios del sistema</p>
        </div>

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="tabs">
        <button
          className={activeTab === "callcenter" ? "active" : ""}
          onClick={() => {
            setActiveTab("callcenter");
            setShowForm(false);
          }}
        >
          Call Center
        </button>
        <button
          className={activeTab === "inspectors" ? "active" : ""}
          onClick={() => {
            setActiveTab("inspectors");
            setShowForm(false);
          }}
        >
          Inspectores
        </button>
        <button
          className={activeTab === "clients" ? "active" : ""}
          onClick={() => {
            setActiveTab("clients");
            setShowForm(false);
          }}
        >
          Clientes
        </button>
      </div>

      <div className="panel-content">
        {activeTab !== "clients" && (
          <div className="panel-actions">
            <button
              className="btn-primary"
              onClick={() => setShowForm(!showForm)}
            >
              {showForm ? "Cancelar" : `Crear ${activeTab === "callcenter" ? "Call Center" : "Inspector"}`}
            </button>
          </div>
        )}

        {showForm && (
          <form className="user-form" onSubmit={handleSubmit}>
            <h3>Crear nuevo {activeTab === "callcenter" ? "Call Center" : "Inspector"}</h3>

            <div className="form-row">
              <div className="form-group">
                <label>Usuario *</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Nombre *</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Apellido *</label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Teléfono</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                />
              </div>
              {activeTab === "inspectors" && (
                <div className="form-group">
                  <label>Número de Licencia</label>
                  <input
                    type="text"
                    name="license_number"
                    value={formData.license_number}
                    onChange={handleInputChange}
                  />
                </div>
              )}
            </div>

            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? "Creando..." : "Crear Usuario"}
            </button>
          </form>
        )}

        <div className="users-list">
          <h3>
            {activeTab === "callcenter" ? "Call Centers" :
             activeTab === "inspectors" ? "Inspectores" : "Clientes Registrados"}
          </h3>
          {loading ? (
            <p>Cargando...</p>
          ) : users.length === 0 ? (
            <p className="no-data">No hay usuarios registrados</p>
          ) : (
            <table>
              <thead>
                <tr>
                  {activeTab !== "clients" && <th>Usuario</th>}
                  <th>Nombre</th>
                  {activeTab !== "clients" && <th>Email</th>}
                  {activeTab === "clients" && <th>DNI</th>}
                  {activeTab === "clients" && <th>Email</th>}
                  <th>Teléfono</th>
                  {activeTab === "clients" && <th>Dirección</th>}
                  {activeTab === "clients" && <th>Última Inspección</th>}
                  {activeTab === "inspectors" && <th>Licencia</th>}
                  {activeTab !== "clients" && <th>Estado</th>}
                  {activeTab !== "clients" && <th>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    {activeTab !== "clients" && <td>{user.username}</td>}
                    <td>{activeTab === "clients" ? user.full_name : `${user.first_name} ${user.last_name}`}</td>
                    {activeTab === "clients" && <td>{user.dni || "-"}</td>}
                    <td>{user.email}</td>
                    <td>{user.phone_number || "-"}</td>
                    {activeTab === "clients" && <td>{user.address || "-"}</td>}
                    {activeTab === "clients" && (
                      <td>
                        {user.last_inspection_date ?
                          new Date(user.last_inspection_date).toLocaleDateString('es-CO') :
                          "Sin inspecciones"}
                      </td>
                    )}
                    {activeTab === "inspectors" && <td>{user.license_number || "-"}</td>}
                    {activeTab !== "clients" && (
                      <>
                        <td>
                          <span className={`status ${user.is_active ? "active" : "inactive"}`}>
                            {user.is_active ? "Activo" : "Inactivo"}
                          </span>
                        </td>
                        <td>
                          <button
                            className="btn-delete"
                            onClick={() => handleDelete(user.id)}
                            disabled={!user.is_active}
                          >
                            Desactivar
                          </button>
                        </td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Password Modal */}
      {showPasswordModal && tempPassword && (
        <div className="modal-overlay" onClick={() => setShowPasswordModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>✅ Usuario Creado Exitosamente</h2>
            </div>
            <div className="modal-body">
              <p className="modal-info">
                El usuario ha sido creado. Comparte esta información con el usuario:
              </p>
              <div className="password-box">
                <div className="password-field">
                  <label>Usuario:</label>
                  <div className="password-value">{tempPassword.username}</div>
                </div>
                <div className="password-field">
                  <label>Contraseña Temporal:</label>
                  <div className="password-value password-highlight">{tempPassword.password}</div>
                </div>
              </div>
              <p className="modal-warning">
                ⚠️ <strong>Importante:</strong> Guarda esta contraseña ahora.
                El usuario deberá cambiarla en su primer inicio de sesión.
              </p>
              <button
                className="btn-copy"
                onClick={() => {
                  navigator.clipboard.writeText(`Usuario: ${tempPassword.username}\nContraseña: ${tempPassword.password}`);
                  showMessage("Credenciales copiadas al portapapeles", "success");
                }}
              >
                📋 Copiar Credenciales
              </button>
            </div>
            <div className="modal-footer">
              <button className="btn-close" onClick={() => setShowPasswordModal(false)}>
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}

export default AdminPanel;
