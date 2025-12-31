import { useState, useEffect } from "react";
import axios from "axios";
import "../styles/InspectorSchedule.css";

const API_URL = "http://localhost:8000/api";

const MONTHS_ES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
];

const WEEKDAYS_ES = ["Dom", "Lun", "Mar", "Mie", "Jue", "Vie", "Sab"];
const WEEKDAYS_FULL = ["Domingo", "Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"];

function InspectorSchedule({ 
  inspectorId, 
  inspectorName, 
  onSelectDate, 
  onClose, 
  embedded = false,
  initialDate = null,  // Nueva prop para mostrar fecha inicial
  initialTime = null   // Nueva prop para mostrar hora inicial
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth() + 1);
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [calendarData, setCalendarData] = useState([]);
  const [stats, setStats] = useState({});
  const [selectedDay, setSelectedDay] = useState(null);
  const [viewMode, setViewMode] = useState("month"); // month, week, day
  
  // Estado para navegación de semana y día
  const [currentWeekStart, setCurrentWeekStart] = useState(null);
  const [currentDayIndex, setCurrentDayIndex] = useState(0);

  const getToken = () => localStorage.getItem("token");

  // Inicializar con fecha seleccionada si existe
  useEffect(() => {
    if (initialDate) {
      const date = new Date(initialDate);
      setCurrentMonth(date.getMonth() + 1);
      setCurrentYear(date.getFullYear());
    }
  }, [initialDate]);

  useEffect(() => {
    loadSchedule();
  }, [inspectorId, currentMonth, currentYear]);

  // Cuando se carga el calendario, seleccionar el día de la fecha inicial
  useEffect(() => {
    if (initialDate && calendarData.length > 0) {
      const dayToSelect = calendarData.find(d => d.date === initialDate);
      if (dayToSelect) {
        setSelectedDay(dayToSelect);
        // Establecer inicio de semana
        const dayIndex = calendarData.indexOf(dayToSelect);
        const weekStartIndex = dayIndex - new Date(initialDate).getDay();
        setCurrentWeekStart(Math.max(0, weekStartIndex));
        setCurrentDayIndex(dayIndex);
      }
    }
  }, [initialDate, calendarData]);

  const loadSchedule = async () => {
    if (!inspectorId) return;
    
    setLoading(true);
    setError("");
    try {
      const url = inspectorId === "self" 
        ? `${API_URL}/appointments/inspector-schedule/`
        : `${API_URL}/appointments/inspector-schedule/${inspectorId}/`;
      
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${getToken()}` },
        params: { month: currentMonth, year: currentYear }
      });
      
      setCalendarData(response.data.calendar || []);
      setStats(response.data.stats || {});
      
      // Si no hay día seleccionado, seleccionar hoy si está en el mes
      if (!selectedDay) {
        const today = response.data.calendar?.find(d => d.is_today);
        if (today) {
          setSelectedDay(today);
          const todayIndex = response.data.calendar.indexOf(today);
          const weekStartIndex = todayIndex - new Date(today.date).getDay();
          setCurrentWeekStart(Math.max(0, weekStartIndex));
          setCurrentDayIndex(todayIndex);
        }
      }
    } catch (err) {
      console.error("Error cargando cronograma:", err);
      setError("Error al cargar el cronograma");
    } finally {
      setLoading(false);
    }
  };

  // Navegación por MES
  const goToPrevMonth = () => {
    if (currentMonth === 1) {
      setCurrentMonth(12);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
    setSelectedDay(null);
  };

  const goToNextMonth = () => {
    if (currentMonth === 12) {
      setCurrentMonth(1);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
    setSelectedDay(null);
  };

  // Navegación por SEMANA
  const goToPrevWeek = () => {
    if (currentWeekStart === null || currentWeekStart <= 0) {
      // Ir al mes anterior
      goToPrevMonth();
      // El nuevo mes se cargará y establecerá la última semana
      setTimeout(() => {
        if (calendarData.length > 0) {
          setCurrentWeekStart(Math.max(0, calendarData.length - 7));
        }
      }, 500);
    } else {
      setCurrentWeekStart(Math.max(0, currentWeekStart - 7));
    }
  };

  const goToNextWeek = () => {
    const maxStart = calendarData.length - 7;
    if (currentWeekStart === null) {
      setCurrentWeekStart(7);
    } else if (currentWeekStart >= maxStart) {
      // Ir al mes siguiente
      goToNextMonth();
      setTimeout(() => {
        setCurrentWeekStart(0);
      }, 500);
    } else {
      setCurrentWeekStart(Math.min(maxStart, currentWeekStart + 7));
    }
  };

  // Navegación por DÍA
  const goToPrevDay = () => {
    if (currentDayIndex <= 0) {
      // Ir al mes anterior
      goToPrevMonth();
      setTimeout(() => {
        if (calendarData.length > 0) {
          setCurrentDayIndex(calendarData.length - 1);
          setSelectedDay(calendarData[calendarData.length - 1]);
        }
      }, 500);
    } else {
      const newIndex = currentDayIndex - 1;
      setCurrentDayIndex(newIndex);
      setSelectedDay(calendarData[newIndex]);
    }
  };

  const goToNextDay = () => {
    if (currentDayIndex >= calendarData.length - 1) {
      // Ir al mes siguiente
      goToNextMonth();
      setTimeout(() => {
        setCurrentDayIndex(0);
        if (calendarData.length > 0) {
          setSelectedDay(calendarData[0]);
        }
      }, 500);
    } else {
      const newIndex = currentDayIndex + 1;
      setCurrentDayIndex(newIndex);
      setSelectedDay(calendarData[newIndex]);
    }
  };

  const goToToday = () => {
    const today = new Date();
    setCurrentMonth(today.getMonth() + 1);
    setCurrentYear(today.getFullYear());
    setSelectedDay(null);
    setCurrentWeekStart(null);
  };

  const handleDayClick = (day) => {
    setSelectedDay(day);
    const dayIndex = calendarData.indexOf(day);
    setCurrentDayIndex(dayIndex);
    
    // Actualizar inicio de semana
    const weekStartIndex = dayIndex - new Date(day.date).getDay();
    setCurrentWeekStart(Math.max(0, weekStartIndex));
    
    // Si hay callback, notificar la fecha seleccionada (sin hora)
    if (onSelectDate && !day.is_past) {
      onSelectDate(day.date, null);
    }
  };

  // Nueva función para seleccionar hora desde el cronograma
  const handleHourClick = (day, hour) => {
    if (day.is_past) return; // No permitir seleccionar horas en días pasados
    
    const timeStr = `${hour.toString().padStart(2, '0')}:00`;
    setSelectedDay(day);
    
    // Notificar fecha y hora seleccionada
    if (onSelectDate) {
      onSelectDate(day.date, timeStr);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'PENDING': '#f59e0b',
      'CONFIRMED': '#3b82f6',
      'IN_PROGRESS': '#8b5cf6',
      'COMPLETED': '#10b981',
      'CANCELLED': '#ef4444',
      'RESCHEDULED': '#6366f1',
      'NEEDS_RESCHEDULE': '#f97316'
    };
    return colors[status] || '#6b7280';
  };

  // Calcular días vacíos al inicio del mes
  const firstDayOfMonth = new Date(currentYear, currentMonth - 1, 1).getDay();
  const emptyDays = Array(firstDayOfMonth).fill(null);

  // Vista semanal - obtener los días de la semana actual
  const getWeekDays = () => {
    if (calendarData.length === 0) return [];
    const startIndex = currentWeekStart !== null ? currentWeekStart : 0;
    return calendarData.slice(startIndex, startIndex + 7);
  };

  // Obtener el rango de fechas de la semana actual
  const getWeekRange = () => {
    const weekDays = getWeekDays();
    if (weekDays.length === 0) return "";
    const first = weekDays[0];
    const last = weekDays[weekDays.length - 1];
    return `${first?.day || ''} - ${last?.day || ''} ${MONTHS_ES[currentMonth - 1]}`;
  };

  // Funciones de navegación según el modo de vista
  const handlePrevNav = () => {
    if (viewMode === 'month') goToPrevMonth();
    else if (viewMode === 'week') goToPrevWeek();
    else if (viewMode === 'day') goToPrevDay();
  };

  const handleNextNav = () => {
    if (viewMode === 'month') goToNextMonth();
    else if (viewMode === 'week') goToNextWeek();
    else if (viewMode === 'day') goToNextDay();
  };

  // Obtener título según modo de vista
  const getNavTitle = () => {
    if (viewMode === 'month') {
      return `${MONTHS_ES[currentMonth - 1]} ${currentYear}`;
    } else if (viewMode === 'week') {
      return getWeekRange();
    } else if (viewMode === 'day' && selectedDay) {
      return `${WEEKDAYS_FULL[new Date(selectedDay.date).getDay()]} ${selectedDay.day} de ${MONTHS_ES[currentMonth - 1]}`;
    }
    return `${MONTHS_ES[currentMonth - 1]} ${currentYear}`;
  };

  const renderMonthView = () => (
    <div className="schedule-calendar-grid">
      {/* Encabezado de días */}
      {WEEKDAYS_ES.map((day, i) => (
        <div key={i} className="schedule-weekday-header">{day}</div>
      ))}
      
      {/* Días vacíos al inicio */}
      {emptyDays.map((_, i) => (
        <div key={`empty-${i}`} className="schedule-day schedule-day-empty"></div>
      ))}
      
      {/* Días del mes - TODOS los días visibles */}
      {calendarData.map((day) => (
        <div
          key={day.date}
          className={`schedule-day 
            ${day.is_today ? 'schedule-day-today' : ''} 
            ${day.is_past ? 'schedule-day-past' : ''} 
            ${day.is_busy ? 'schedule-day-busy' : ''} 
            ${day.appointments_count > 0 ? 'schedule-day-has-appointments' : ''}
            ${selectedDay?.date === day.date ? 'schedule-day-selected' : ''}
          `}
          onClick={() => handleDayClick(day)}
        >
          <span className="schedule-day-number">{day.day}</span>
          {day.appointments_count > 0 && (
            <span className="schedule-day-count">{day.appointments_count}</span>
          )}
          {day.is_busy && <span className="schedule-day-busy-badge">Lleno</span>}
        </div>
      ))}
    </div>
  );

  const renderWeekView = () => {
    const weekDays = getWeekDays();
    if (weekDays.length === 0) return <p>Cargando semana...</p>;
    
    return (
      <div className="schedule-week-view">
        <div className="schedule-week-header-row">
          <div className="schedule-time-header"></div>
          {weekDays.map((day) => (
            <div 
              key={day.date} 
              className={`schedule-week-day-header ${day.is_today ? 'is-today' : ''} ${day.is_past ? 'is-past' : ''} ${selectedDay?.date === day.date ? 'is-selected' : ''}`}
              onClick={() => handleDayClick(day)}
            >
              <span className="week-day-name">{WEEKDAYS_ES[new Date(day.date).getDay()]}</span>
              <span className="week-day-number">{day.day}</span>
              {day.appointments_count > 0 && (
                <span className="week-day-badge">{day.appointments_count}</span>
              )}
            </div>
          ))}
        </div>
        <div className="schedule-week-body">
          {/* Horas del día */}
          <div className="schedule-time-column">
            {Array.from({length: 12}, (_, i) => i + 6).map(hour => (
              <div key={hour} className="schedule-time-slot">
                {hour.toString().padStart(2, '0')}:00
              </div>
            ))}
          </div>
          {/* Columnas de días */}
          {weekDays.map((day) => (
            <div key={day.date} className={`schedule-day-column ${day.is_past ? 'is-past' : ''}`}>
              {Array.from({length: 12}, (_, i) => i + 6).map(hour => {
                const hourStr = hour.toString().padStart(2, '0');
                const appointment = day.appointments?.find(apt => 
                  apt.time.startsWith(hourStr)
                );
                // Marcar la hora inicial si coincide
                const isInitialTime = initialTime && day.date === initialDate && initialTime.startsWith(hourStr);
                const isClickable = !day.is_past && !appointment;
                
                return (
                  <div 
                    key={hour} 
                    className={`schedule-hour-slot ${appointment ? 'has-appointment' : ''} ${isInitialTime ? 'initial-time' : ''} ${isClickable ? 'clickable' : ''}`}
                    style={appointment ? {borderLeftColor: getStatusColor(appointment.status)} : {}}
                    onClick={() => isClickable && handleHourClick(day, hour)}
                    title={isClickable ? `Click para seleccionar ${hourStr}:00` : ''}
                  >
                    {appointment && (
                      <div className="schedule-appointment-mini">
                        <span className="apt-time">{appointment.time}</span>
                        <span className="apt-client">{appointment.client_name}</span>
                      </div>
                    )}
                    {isInitialTime && !appointment && (
                      <div className="schedule-initial-marker">
                        <span>🎯 {initialTime}</span>
                      </div>
                    )}
                    {isClickable && !isInitialTime && (
                      <span className="slot-hint">+</span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderDayView = () => {
    const dayToShow = selectedDay || (calendarData.length > 0 ? calendarData[currentDayIndex] : null);
    
    if (!dayToShow) return <p className="no-selection">Selecciona un día para ver los detalles</p>;
    
    return (
      <div className="schedule-day-view">
        <h3 className="day-view-title">
          📅 {dayToShow.day} de {MONTHS_ES[currentMonth - 1]} de {currentYear}
          {dayToShow.is_past && <span className="past-badge">Pasado</span>}
        </h3>
        
        {/* Mostrar hora inicial si está seleccionada */}
        {initialTime && dayToShow.date === initialDate && (
          <div className="initial-time-indicator">
            <span className="indicator-icon">🎯</span>
            <span>Hora seleccionada: <strong>{initialTime}</strong></span>
          </div>
        )}
        
        {dayToShow.appointments?.length === 0 ? (
          <div className="day-view-empty">
            <span className="empty-icon">✓</span>
            <p>Sin citas programadas</p>
            <span className="empty-hint">Día disponible para asignar inspecciones</span>
          </div>
        ) : (
          <div className="day-view-appointments">
            {dayToShow.appointments?.map((apt, idx) => (
              <div 
                key={apt.id || idx} 
                className="day-appointment-card"
                style={{borderLeftColor: getStatusColor(apt.status)}}
              >
                <div className="apt-card-header">
                  <span className="apt-card-time">🕐 {apt.time}</span>
                  <span 
                    className="apt-card-status"
                    style={{backgroundColor: getStatusColor(apt.status)}}
                  >
                    {apt.status_display}
                  </span>
                </div>
                <div className="apt-card-body">
                  <p className="apt-card-client">👤 {apt.client_name}</p>
                  <p className="apt-card-address">📍 {apt.address}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Renderizar vista de día completa (cuando viewMode === 'day')
  const renderFullDayView = () => {
    const dayToShow = selectedDay || (calendarData.length > 0 ? calendarData[currentDayIndex] : null);
    
    if (!dayToShow) return <p>Selecciona un día</p>;
    
    return (
      <div className="schedule-full-day-view">
        <div className="full-day-timeline">
          {Array.from({length: 14}, (_, i) => i + 6).map(hour => {
            const hourStr = hour.toString().padStart(2, '0');
            const appointment = dayToShow.appointments?.find(apt => 
              apt.time.startsWith(hourStr)
            );
            const isInitialTime = initialTime && dayToShow.date === initialDate && initialTime.startsWith(hourStr);
            const isClickable = !dayToShow.is_past && !appointment;
            
            return (
              <div 
                key={hour} 
                className={`full-day-hour ${appointment ? 'has-appointment' : ''} ${isInitialTime ? 'initial-time' : ''} ${isClickable ? 'clickable' : ''}`}
                onClick={() => isClickable && handleHourClick(dayToShow, hour)}
              >
                <div className="hour-label">{hourStr}:00</div>
                <div className="hour-content" style={appointment ? {borderLeftColor: getStatusColor(appointment.status)} : {}}>
                  {appointment ? (
                    <div className="full-day-appointment">
                      <span className="apt-time">{appointment.time}</span>
                      <span className="apt-client">{appointment.client_name}</span>
                      <span className="apt-address">{appointment.address}</span>
                      <span className="apt-status" style={{backgroundColor: getStatusColor(appointment.status)}}>
                        {appointment.status_display}
                      </span>
                    </div>
                  ) : isInitialTime ? (
                    <div className="initial-time-marker">
                      <span>🎯 Hora seleccionada: {initialTime}</span>
                    </div>
                  ) : (
                    <div className="hour-empty">
                      Disponible
                      {isClickable && <span className="select-hint"> - Click para seleccionar</span>}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const containerClass = embedded ? "schedule-container embedded" : "schedule-container modal";

  return (
    <div className={containerClass}>
      {!embedded && (
        <div className="schedule-modal-overlay" onClick={onClose}></div>
      )}
      
      <div className="schedule-content">
        {/* Header */}
        <div className="schedule-header">
          <div className="schedule-title">
            <h2>📆 Cronograma {inspectorName ? `de ${inspectorName}` : ''}</h2>
            {!embedded && onClose && (
              <button className="schedule-close-btn" onClick={onClose}>✕</button>
            )}
          </div>
          
          {/* Navegación - cambia según el modo de vista */}
          <div className="schedule-nav">
            <button className="nav-btn" onClick={handlePrevNav}>‹</button>
            <span className="schedule-month-year">
              {getNavTitle()}
            </span>
            <button className="nav-btn" onClick={handleNextNav}>›</button>
            <button className="nav-btn nav-today" onClick={goToToday}>Hoy</button>
          </div>
          
          {/* Cambio de vista */}
          <div className="schedule-view-toggle">
            <button 
              className={`view-btn ${viewMode === 'month' ? 'active' : ''}`}
              onClick={() => setViewMode('month')}
            >
              Mes
            </button>
            <button 
              className={`view-btn ${viewMode === 'week' ? 'active' : ''}`}
              onClick={() => setViewMode('week')}
            >
              Semana
            </button>
            <button 
              className={`view-btn ${viewMode === 'day' ? 'active' : ''}`}
              onClick={() => setViewMode('day')}
            >
              Día
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="schedule-stats">
          <div className="stat-item">
            <span className="stat-value">{stats.total || 0}</span>
            <span className="stat-label">Total</span>
          </div>
          <div className="stat-item stat-pending">
            <span className="stat-value">{stats.pending || 0}</span>
            <span className="stat-label">Pendientes</span>
          </div>
          <div className="stat-item stat-completed">
            <span className="stat-value">{stats.completed || 0}</span>
            <span className="stat-label">Completadas</span>
          </div>
          <div className="stat-item stat-available">
            <span className="stat-value">{Math.max(0, stats.available_slots || 0)}</span>
            <span className="stat-label">Disponibles</span>
          </div>
        </div>

        {/* Loading/Error */}
        {loading && (
          <div className="schedule-loading">
            <div className="schedule-spinner"></div>
            <span>Cargando cronograma...</span>
          </div>
        )}
        
        {error && <div className="schedule-error">{error}</div>}

        {/* Calendar Content */}
        {!loading && !error && (
          <div className="schedule-body">
            <div className="schedule-main">
              {viewMode === 'month' && renderMonthView()}
              {viewMode === 'week' && renderWeekView()}
              {viewMode === 'day' && renderFullDayView()}
            </div>
            
            {/* Panel lateral con detalles del día - solo para mes y semana */}
            {viewMode !== 'day' && (
              <div className="schedule-sidebar">
                {renderDayView()}
              </div>
            )}
          </div>
        )}

        {/* Leyenda */}
        <div className="schedule-legend">
          <div className="legend-item">
            <span className="legend-color" style={{backgroundColor: '#10b981'}}></span>
            <span>Completada</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{backgroundColor: '#f59e0b'}}></span>
            <span>Pendiente</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{backgroundColor: '#8b5cf6'}}></span>
            <span>En Progreso</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{backgroundColor: '#ef4444'}}></span>
            <span>Día Lleno</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default InspectorSchedule;
