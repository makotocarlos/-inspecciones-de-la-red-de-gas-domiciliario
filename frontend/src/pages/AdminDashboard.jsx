import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/AdminDashboard.css";

const API_URL = "http://localhost:8000/api";

function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalUsers: 0,
    callCenters: 0,
    inspectors: 0,
    appointments: 0,
    inspections: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const getToken = () => localStorage.getItem("token");

  const loadStats = async () => {
    setLoading(true);
    try {
      // Cargar estadísticas del sistema
      const [callCentersRes, inspectorsRes] = await Promise.all([
        axios.get(`${API_URL}/auth/admin/call-center/`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        }),
        axios.get(`${API_URL}/auth/admin/inspectors/`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        })
      ]);

      const callCenters = callCentersRes.data.call_centers || [];
      const inspectors = inspectorsRes.data.inspectors || [];

      setStats({
        totalUsers: callCenters.length + inspectors.length,
        callCenters: callCenters.length,
        inspectors: inspectors.length,
        appointments: 0, // Se actualizará cuando implementes el endpoint
        inspections: 0 // Se actualizará cuando implementes el endpoint
      });
    } catch (error) {
      console.error("Error cargando estadísticas:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-dashboard">
      <div className="dashboard-header">
        <h1>Dashboard Administrador</h1>
        <p>Resumen del Sistema de Inspecciones</p>
      </div>

      {loading ? (
        <div className="loading">Cargando estadísticas...</div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">👥</div>
              <div className="stat-content">
                <h3>{stats.totalUsers}</h3>
                <p>Usuarios Totales</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">📞</div>
              <div className="stat-content">
                <h3>{stats.callCenters}</h3>
                <p>Call Centers</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">🔧</div>
              <div className="stat-content">
                <h3>{stats.inspectors}</h3>
                <p>Inspectores</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">📅</div>
              <div className="stat-content">
                <h3>{stats.appointments}</h3>
                <p>Citas Agendadas</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">✅</div>
              <div className="stat-content">
                <h3>{stats.inspections}</h3>
                <p>Inspecciones Realizadas</p>
              </div>
            </div>
          </div>

          <div className="quick-actions-dashboard">
            <h2>Acciones Rápidas</h2>
            <div className="actions-grid">
              <button
                className="action-btn"
                onClick={() => navigate("/admin")}
              >
                <span className="action-icon">👥</span>
                <span className="action-text">Gestionar Usuarios</span>
              </button>

              <button
                className="action-btn"
                onClick={() => navigate("/call-center")}
              >
                <span className="action-icon">📞</span>
                <span className="action-text">Ver Citas</span>
              </button>

              <button
                className="action-btn"
                onClick={() => navigate("/admin")}
              >
                <span className="action-icon">➕</span>
                <span className="action-text">Crear Usuario</span>
              </button>
            </div>
          </div>

          <div className="recent-activity">
            <h2>Actividad Reciente</h2>
            <div className="activity-placeholder">
              <p>Las estadísticas de actividad se mostrarán aquí cuando implementes los endpoints de citas e inspecciones.</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default AdminDashboard;
