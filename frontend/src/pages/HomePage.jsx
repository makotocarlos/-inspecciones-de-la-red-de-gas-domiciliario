import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/HomePage.css";

function HomePage({ user }) {
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      const role = user.role?.toUpperCase();
      // Redirigir según el rol
      if (role === "ADMIN") {
        navigate("/admin");
      } else if (role === "CALL_CENTER") {
        navigate("/call-center");
      } else if (role === "INSPECTOR") {
        navigate("/inspector_panel");
      }
    }
  }, [user, navigate]);

  return (
    <div className="home-page">
      <div className="home-container">
        <div className="home-header">
          <h1>Sistema de Gestión de Inspecciones de Gas</h1>
          <p>Bienvenido al sistema de inspecciones domiciliarias de gas</p>
        </div>

        <div className="home-content">
          {user ? (
            <div className="welcome-section">
              <h2>Hola, {user.first_name || user.username}!</h2>
              <p>Rol: <strong>{user.role}</strong></p>

              <div className="quick-actions">
                <h3>Accesos Rápidos</h3>
                {user.role === "ADMIN" && (
                  <button onClick={() => navigate("/admin")} className="btn-action">
                    Ir al Panel de Administración
                  </button>
                )}
                {user.role === "CALL_CENTER" && (
                  <button onClick={() => navigate("/call-center")} className="btn-action">
                    Ir al Panel Call Center
                  </button>
                )}
                {user.role === "INSPECTOR" && (
                  <button onClick={() => navigate("/inspector_panel")} className="btn-action">
                    Ir al Panel Inspector
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="guest-section">
              <h2>Bienvenido</h2>
              <p>Por favor inicia sesión para acceder al sistema</p>
              <button onClick={() => navigate("/login")} className="btn-login">
                Iniciar Sesión
              </button>
            </div>
          )}
        </div>

        <div className="home-info">
          <div className="info-card">
            <h3>🏢 Administrador</h3>
            <p>Gestiona usuarios del sistema, crea cuentas de Call Center e Inspectores</p>
          </div>
          <div className="info-card">
            <h3>📞 Call Center</h3>
            <p>Agenda citas de inspección y gestiona la información de los clientes</p>
          </div>
          <div className="info-card">
            <h3>🔧 Inspector</h3>
            <p>Realiza inspecciones y completa formularios técnicos detallados</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
