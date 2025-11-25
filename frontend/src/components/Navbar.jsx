import { Link, useLocation, useNavigate } from "react-router-dom";
import { normalizeRole } from "../utils/roleUtils";

function Navbar({ user, setUser }) {
  const location = useLocation();
  const navigate = useNavigate();
  const role = normalizeRole(user?.role);

  // Si estoy en login, register o paneles -> NO renderizar la barra
  const hiddenPaths = [
    "/login",
    "/register",
    "/admin",
    "/admin_dashboard",
    "/call-center",
    "/inspector_panel"
  ];

  if (hiddenPaths.includes(location.pathname)) {
    return null;
  }

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    navigate("/login", { replace: true });
  };

  return (
    <nav className="navbar">
      <div className="navbar-links">
        {/* Muestra según rol */}
        {role === "ADMIN" && (
          <>
            <Link to="/home">Inicio</Link>
            <Link to="/admin">Panel Admin</Link>
          </>
        )}
        {role === "CALL_CENTER" && (
          <>
            <Link to="/call-center">Panel Call Center</Link>
          </>
        )}
        {role === "INSPECTOR" && <Link to="/inspector_panel">Panel Inspector</Link>}
        {role === "USER" && <Link to="/home">Inicio</Link>}
      </div>

      <div className="navbar-actions">
        {user ? (
          <>
            <span>👋 Hola, <b>{user.username}</b></span>
            <button onClick={handleLogout} className="logout-btn">Salir</button>
          </>
        ) : null}
      </div>
    </nav>
  );
}

export default Navbar;
