import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";

import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import LandingPage from "./pages/LandingPage";
import AboutPage from "./pages/AboutPage";
import HomePage from "./pages/HomePage";
import AdminDashboard from "./pages/AdminDashboard";
import AdminPanel from "./pages/AdminPanel";
import InspectorPanel from "./pages/InspectorPanel";
import CallCenterPanel from "./pages/CallCenterPanel";
import CallCenterAdminPanel from "./pages/CallCenterAdminPanel";
import Navbar from "./components/Navbar";
import { normalizeRole } from "./utils/roleUtils";

const getRoleLandingPath = (role) => {
  switch (normalizeRole(role)) {
    case "ADMIN":
      return "/home";
    case "CALL_CENTER_ADMIN":
      return "/call-center-admin";
    case "CALL_CENTER":
      return "/call-center";
    case "INSPECTOR":
      return "/inspector_panel";
    default:
      return "/home";
  }
};

// Protected Route Component
const fallbackNormalizeRole = (rawRole) => {
  const normalized = normalizeRole(rawRole);
  if (normalized) {
    return normalized;
  }

  const coarse = (rawRole || '').toString().trim().toUpperCase();
  if (coarse.includes('ADMIN')) return 'ADMIN';
  if (coarse.includes('CALL') || coarse.includes('TELE') || coarse.includes('OPERADOR')) return 'CALL_CENTER';
  if (coarse.includes('INSPECT')) return 'INSPECTOR';
  if (coarse.includes('USER') || coarse.includes('USUAR') || coarse.includes('CLIENT')) return 'USER';
  return coarse;
};

const ProtectedRoute = ({ user, allowedRoles, children }) => {
  const storedUser = user || JSON.parse(localStorage.getItem('user') || 'null');
  const role = fallbackNormalizeRole(storedUser?.role);

  if (!storedUser || !role) {
    return <Navigate to="/login" replace />;
  }

  const normalizedAllowed = allowedRoles?.map(fallbackNormalizeRole).filter(Boolean);

  if (normalizedAllowed && !normalizedAllowed.includes(role)) {
    console.warn('[ProtectedRoute] acceso denegado', { role, allowed: normalizedAllowed, rawRole: storedUser?.role });
    return <Navigate to={getRoleLandingPath(role)} replace />;
  }

  return children;
};

function App() {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    if (!savedUser) return null;
    const parsed = JSON.parse(savedUser);
    if (parsed?.role) {
      parsed.role = normalizeRole(parsed.role);
      localStorage.setItem('user', JSON.stringify(parsed));
    }
    return parsed;
  });

  useEffect(() => {
    const handleStorageChange = () => {
      const savedUser = localStorage.getItem('user');
      if (!savedUser) {
        setUser(null);
        return;
      }
      const parsed = JSON.parse(savedUser);
      if (parsed?.role) {
        parsed.role = normalizeRole(parsed.role);
        localStorage.setItem('user', JSON.stringify(parsed));
      }
      setUser(parsed);
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  return (
    <Router>
      <Navbar user={user} setUser={setUser} />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/login"
          element={
            user ? (
              <Navigate to={getRoleLandingPath(user.role)} replace />
            ) : (
              <LoginPage setUser={setUser} />
            )
          }
        />
        <Route path="/home" element={<HomePage user={user} />} />
        <Route path="/dashboard" element={<HomePage user={user} />} />

        {/* Admin Routes */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute user={user} allowedRoles={["ADMIN"]}>
              <AdminPanel />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin_dashboard"
          element={
            <ProtectedRoute user={user} allowedRoles={["ADMIN"]}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        
        {/* Call Center Admin Routes */}
        <Route
          path="/call-center-admin"
          element={
            <ProtectedRoute user={user} allowedRoles={["CALL_CENTER_ADMIN", "ADMIN"]}>
              <CallCenterAdminPanel />
            </ProtectedRoute>
          }
        />
        
        {/* Call Center Routes */}
        <Route
          path="/call-center"
          element={
            <ProtectedRoute user={user} allowedRoles={["CALL_CENTER", "ADMIN"]}>
              <CallCenterPanel />
            </ProtectedRoute>
          }
        />
        
        {/* Inspector Routes */}
        <Route
          path="/inspector_panel"
          element={
            <ProtectedRoute user={user} allowedRoles={["INSPECTOR"]}>
              <InspectorPanel />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;