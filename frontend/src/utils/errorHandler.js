/**
 * Extrae un mensaje de error legible desde un error de API
 * @param {Error} error - El objeto error capturado
 * @param {string} defaultMessage - Mensaje por defecto si no se puede extraer el error
 * @returns {string} - Mensaje de error legible (SIEMPRE retorna string)
 */
export const getErrorMessage = (error, defaultMessage = "Ha ocurrido un error") => {
  try {
    // Verificar si hay una respuesta del servidor
    if (error.response?.data) {
      const { data } = error.response;

      // Intentar obtener el mensaje de error
      if (data.error) {
        // Si error es string, devolverlo directamente
        if (typeof data.error === 'string') {
          return data.error;
        }
        // Si error es objeto, intentar extraer el mensaje
        if (typeof data.error === 'object' && data.error !== null) {
          if (data.error.message && typeof data.error.message === 'string') {
            return data.error.message;
          }
          // Si tiene detalles, intentar mostrarlos
          if (data.error.details) {
            if (typeof data.error.details === 'string') {
              return data.error.details;
            }
            // Convertir detalles a string de forma segura
            try {
              return JSON.stringify(data.error.details);
            } catch {
              return String(data.error.details);
            }
          }
          // Como último recurso, stringify el objeto de forma segura
          try {
            const errorStr = JSON.stringify(data.error);
            return errorStr !== '{}' ? errorStr : defaultMessage;
          } catch {
            return String(data.error);
          }
        }
      }

      // Intentar con 'message'
      if (data.message) {
        if (typeof data.message === 'string') {
          return data.message;
        }
        // Si message es objeto, convertir a string
        try {
          return JSON.stringify(data.message);
        } catch {
          return String(data.message);
        }
      }

      // Intentar con 'detail' (común en DRF)
      if (data.detail) {
        if (typeof data.detail === 'string') {
          return data.detail;
        }
        // Si detail es objeto, convertir a string
        try {
          return JSON.stringify(data.detail);
        } catch {
          return String(data.detail);
        }
      }

      // Si data en sí es un string
      if (typeof data === 'string') {
        return data;
      }
    }

    // Verificar el status del error
    if (error.response?.status) {
      const status = error.response.status;
      if (status === 500) {
        return 'Error interno del servidor. Por favor, contacta al administrador.';
      }
      if (status === 404) {
        return 'Recurso no encontrado. Verifica la URL.';
      }
      if (status === 403) {
        return 'No tienes permisos para realizar esta acción.';
      }
      if (status === 401) {
        return 'No autorizado. Por favor, inicia sesión nuevamente.';
      }
    }

    // Si hay un mensaje en el error mismo
    if (error.message && typeof error.message === 'string') {
      return error.message;
    }

    // Mensaje por defecto
    return defaultMessage;
  } catch (e) {
    // Si algo falla en el manejo del error, devolver el mensaje por defecto
    console.error('Error en getErrorMessage:', e);
    return defaultMessage;
  }
};

/**
 * Maneja errores de red
 * @param {Error} error - El objeto error
 * @returns {string} - Mensaje de error
 */
export const handleNetworkError = (error) => {
  if (error.code === 'ECONNABORTED') {
    return 'La solicitud ha tardado demasiado. Por favor, intenta de nuevo.';
  }

  if (error.code === 'ERR_NETWORK') {
    return 'No se puede conectar con el servidor. Verifica tu conexión.';
  }

  return getErrorMessage(error, 'Error de conexión con el servidor');
};
