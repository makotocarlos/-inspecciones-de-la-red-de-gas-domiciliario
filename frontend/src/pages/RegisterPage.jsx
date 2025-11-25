import { useNavigate } from "react-router-dom";
import "../styles/RegisterPage.css";

function RegisterPage() {
  const navigate = useNavigate();

  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-header">
          <h1>Registro Deshabilitado</h1>
        </div>

        <div className="register-content">
          <div className="info-icon">🔒</div>
          <p>El registro público está deshabilitado.</p>
          <p>Los usuarios son creados por los administradores del sistema.</p>

          <div className="info-section">
            <h3>Para obtener acceso:</h3>
            <ul>
              <li>Los administradores crean cuentas de <strong>Call Center</strong> e <strong>Inspectores</strong></li>
              <li>Los inspectores crean cuentas de <strong>Clientes</strong> durante las inspecciones</li>
            </ul>
          </div>

          <button
            className="btn-back-login"
            onClick={() => navigate("/login")}
          >
            Volver al Inicio de Sesión
          </button>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
