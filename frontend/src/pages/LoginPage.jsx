import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { getErrorMessage } from "../utils/errorHandler";
import "../styles/LoginPage.css";

const API_URL = "http://localhost:8000/api";

function LoginPage({ setUser }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: ""
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await axios.post(`${API_URL}/auth/login/`, formData);

      if (response.data.success) {
        const userData = response.data.user;
        const token = response.data.token;

        // Save to localStorage
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", token);

        // Update parent state
        setUser(userData);

        // Redirect based on role
        const role = userData.role.toUpperCase();
        if (role === "ADMIN") {
          navigate("/admin");
        } else if (role === "CALL_CENTER") {
          navigate("/call-center");
        } else if (role === "INSPECTOR") {
          navigate("/inspector_panel");
        } else {
          navigate("/home");
        }
      }
    } catch (err) {
      setError(getErrorMessage(err, "Error al iniciar sesión. Verifica tus credenciales."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>Iniciar Sesión</h1>
          <p>Sistema de Gestión de Inspecciones de Gas</p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Correo Electrónico</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="tu@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="********"
              required
            />
          </div>

          <button type="submit" className="btn-login" disabled={loading}>
            {loading ? "Iniciando sesión..." : "Iniciar Sesión"}
          </button>
        </form>

        <div className="login-footer">
          <p>¿Olvidaste tu contraseña? Contacta al administrador</p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
