import { useNavigate } from "react-router-dom";
import "../styles/LandingPage.css";

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      <div className="landing-hero">
        <div className="hero-content">
          <h1>Sistema de Gestión de Inspecciones de Gas</h1>
          <p>Plataforma integral para la gestión de inspecciones domiciliarias de gas</p>
          <div className="hero-buttons">
            <button className="btn-primary" onClick={() => navigate("/login")}>
              Iniciar Sesión
            </button>
            <button className="btn-secondary" onClick={() => navigate("/about")}>
              Más Información
            </button>
          </div>
        </div>
      </div>

      <div className="landing-features">
        <div className="container">
          <h2>Características del Sistema</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">👥</div>
              <h3>Gestión de Usuarios</h3>
              <p>Administra usuarios con diferentes roles: administradores, call center e inspectores</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📅</div>
              <h3>Agendamiento de Citas</h3>
              <p>Sistema completo para agendar y gestionar citas de inspección</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🔧</div>
              <h3>Inspecciones Detalladas</h3>
              <p>Formularios completos para registrar inspecciones técnicas de gas</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Reportes y Estadísticas</h3>
              <p>Dashboard con métricas y estadísticas del sistema</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>Seguridad</h3>
              <p>Autenticación segura con roles y permisos diferenciados</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Responsive</h3>
              <p>Diseño adaptable para escritorio, tablet y móvil</p>
            </div>
          </div>
        </div>
      </div>

      <div className="landing-roles">
        <div className="container">
          <h2>Roles del Sistema</h2>
          <div className="roles-grid">
            <div className="role-card admin-card">
              <h3>🏢 Administrador</h3>
              <ul>
                <li>Crear cuentas de Call Center</li>
                <li>Crear cuentas de Inspectores</li>
                <li>Gestionar usuarios del sistema</li>
                <li>Ver estadísticas generales</li>
              </ul>
            </div>

            <div className="role-card callcenter-card">
              <h3>📞 Call Center</h3>
              <ul>
                <li>Agendar citas de inspección</li>
                <li>Registrar datos de clientes</li>
                <li>Asignar inspectores</li>
                <li>Gestionar citas agendadas</li>
              </ul>
            </div>

            <div className="role-card inspector-card">
              <h3>🔧 Inspector</h3>
              <ul>
                <li>Ver citas asignadas</li>
                <li>Realizar inspecciones</li>
                <li>Completar formularios técnicos</li>
                <li>Emitir certificados</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="landing-footer">
        <div className="container">
          <p>&copy; 2025 Sistema de Inspecciones de Gas. Todos los derechos reservados.</p>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
