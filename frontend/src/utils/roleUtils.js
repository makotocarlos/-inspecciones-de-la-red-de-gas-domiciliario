/**
 * Normaliza el rol de usuario para asegurar consistencia en toda la aplicación
 * @param {string} role - El rol del usuario
 * @returns {string} - El rol normalizado
 */
export const normalizeRole = (role) => {
  if (!role) return null;

  const roleStr = role.toString().trim().toUpperCase();

  // Mapeo de roles
  const roleMap = {
    'ADMIN': 'ADMIN',
    'ADMINISTRADOR': 'ADMIN',
    'ADMINISTRATOR': 'ADMIN',

    'CALL_CENTER': 'CALL_CENTER',
    'CALLCENTER': 'CALL_CENTER',
    'CALL CENTER': 'CALL_CENTER',
    'TELEOPERADOR': 'CALL_CENTER',
    'OPERADOR': 'CALL_CENTER',

    'INSPECTOR': 'INSPECTOR',
    'INSP': 'INSPECTOR',

    'USER': 'USER',
    'USUARIO': 'USER',
    'CLIENT': 'USER',
    'CLIENTE': 'USER'
  };

  return roleMap[roleStr] || roleStr;
};

/**
 * Verifica si un usuario tiene un rol específico
 * @param {object} user - El objeto usuario
 * @param {string} requiredRole - El rol requerido
 * @returns {boolean} - True si el usuario tiene el rol
 */
export const hasRole = (user, requiredRole) => {
  if (!user || !user.role) return false;
  return normalizeRole(user.role) === normalizeRole(requiredRole);
};

/**
 * Verifica si un usuario tiene alguno de los roles especificados
 * @param {object} user - El objeto usuario
 * @param {array} roles - Array de roles permitidos
 * @returns {boolean} - True si el usuario tiene alguno de los roles
 */
export const hasAnyRole = (user, roles) => {
  if (!user || !user.role || !Array.isArray(roles)) return false;
  const userRole = normalizeRole(user.role);
  return roles.some(role => normalizeRole(role) === userRole);
};
