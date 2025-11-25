import { useState, useEffect } from "react";
import axios from "axios";
import "./ONACInspectionForm.css";
import DrawingCanvas from "./DrawingCanvas";

const API_URL = "http://localhost:8000/api";

/**
 * Formulario de inspección ONAC multi-paso
 * 9 pasos para completar el formulario oficial ONAC
 * Optimizado para tablets
 */
function ONACInspectionForm({ inspectionId, onComplete, onCancel }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });

  // Estado del formulario completo
  const [formData, setFormData] = useState({
    // PASO 1: Identificación de la Instalación
    account_number: "",
    meter_number: "",
    last_revision_date: "",
    expiration_date: "",

    // PASO 2: Organismo de Inspección
    inspection_org_name: "RUIS - Redes Urbanas Inspecciones S.A.S.",
    inspection_org_nit: "901 563 111-9",
    inspection_org_address: "",
    inspection_org_email: "",
    inspection_start_time: "",
    inspection_end_time: "",
    pressure_type: "BAJA",

    // PASO 3: Tipo de Inspección
    service_start_date: "",
    inspection_type_periodic: false,
    inspection_type_modification: false,
    inspection_type_user_request: false,
    inspection_type_follow_up: false,
    user_request_date: "",

    // PASO 4: Información de Recinto
    rooms_data: [],

    // PASO 5: Artefactos
    appliances_data: [],

    // PASO 6: Edificación e Instalación
    has_internal_void: false,
    has_property_certificate: false,
    property_aspect: "",
    leak_test_method: "",
    leak_test_pressure: "",
    leak_test_meter: false,
    leak_test_appliances: false,

    // PASO 7: Checklist de Inspección (Items 270-332)
    checklist_items: {},

    // PASO 8: Defectos y Equipos
    critical_defects: [],
    non_critical_defects: [],
    co_detector_serial: "",
    co_detector_brand: "",
    co_detector_model: "",
    manometer_serial: "",
    manometer_brand: "",
    manometer_model: "",
    has_calibration_pattern: false,
    calibration_serial: "",
    seal_number: "",

    // PASO 9: Resultado y Firmas
    has_no_defects: false,
    has_non_critical_defect: false,
    has_critical_defect: false,
    installation_continues_service: true,
    meter_reading: "",
    supply_situation: "",
    inspector_affirms_safe: true,
    client_signature: null,
    inspector_signature: null,
    client_phone: "",
    client_email_form: "",
    inspector_name: "",
    inspector_competence_id: "",
    inspector_specialty: "",
    observations: "",

    // Control
    form_completed_percentage: 0,
    current_step: 1
  });

  const getToken = () => localStorage.getItem("token");

  useEffect(() => {
    loadInspectionData();
  }, [inspectionId]);

  const loadInspectionData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_URL}/inspections/inspections/${inspectionId}/onac_form/`,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );

      if (response.data.success) {
        const data = response.data.data;
        setFormData(prev => ({ ...prev, ...data }));
        setCurrentStep(data.current_step || 1);
      }
    } catch (error) {
      console.error("Error cargando datos:", error);
      showMessage("Error al cargar los datos de la inspección", "error");
    } finally {
      setLoading(false);
    }
  };

  const saveProgress = async (stepData = {}) => {
    setSaving(true);
    try {
      const dataToSave = {
        ...stepData,
        current_step: currentStep,
        form_completed_percentage: Math.round((currentStep / 9) * 100)
      };

      const response = await axios.patch(
        `${API_URL}/inspections/inspections/${inspectionId}/onac_form/`,
        dataToSave,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );

      if (response.data.success) {
        showMessage("Progreso guardado", "success");
        return true;
      }
    } catch (error) {
      console.error("Error guardando:", error);
      showMessage("Error al guardar el progreso", "error");
      return false;
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = async () => {
    const stepData = getStepData(currentStep);
    const saved = await saveProgress(stepData);

    if (saved && currentStep < 9) {
      setCurrentStep(prev => prev + 1);
      window.scrollTo(0, 0);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
      window.scrollTo(0, 0);
    }
  };

  const handleComplete = async () => {
    const stepData = getStepData(currentStep);
    stepData.form_completed_percentage = 100;
    stepData.status = "COMPLETED";

    const saved = await saveProgress(stepData);
    if (saved) {
      showMessage("Inspección completada exitosamente", "success");
      setTimeout(() => {
        if (onComplete) onComplete();
      }, 1500);
    }
  };

  const getStepData = (step) => {
    switch (step) {
      case 1:
        return {
          account_number: formData.account_number,
          meter_number: formData.meter_number,
          last_revision_date: formData.last_revision_date,
          expiration_date: formData.expiration_date
        };
      case 2:
        return {
          inspection_org_name: formData.inspection_org_name,
          inspection_org_nit: formData.inspection_org_nit,
          inspection_org_address: formData.inspection_org_address,
          inspection_org_email: formData.inspection_org_email,
          inspection_start_time: formData.inspection_start_time,
          inspection_end_time: formData.inspection_end_time,
          pressure_type: formData.pressure_type
        };
      case 3:
        return {
          service_start_date: formData.service_start_date,
          inspection_type_periodic: formData.inspection_type_periodic,
          inspection_type_modification: formData.inspection_type_modification,
          inspection_type_user_request: formData.inspection_type_user_request,
          inspection_type_follow_up: formData.inspection_type_follow_up,
          user_request_date: formData.user_request_date
        };
      case 4:
        return { rooms_data: formData.rooms_data };
      case 5:
        return { appliances_data: formData.appliances_data };
      case 6:
        return {
          has_internal_void: formData.has_internal_void,
          has_property_certificate: formData.has_property_certificate,
          property_aspect: formData.property_aspect,
          leak_test_method: formData.leak_test_method,
          leak_test_pressure: formData.leak_test_pressure,
          leak_test_meter: formData.leak_test_meter,
          leak_test_appliances: formData.leak_test_appliances
        };
      case 7:
        return { checklist_items: formData.checklist_items };
      case 8:
        return {
          critical_defects: formData.critical_defects,
          non_critical_defects: formData.non_critical_defects,
          co_detector_serial: formData.co_detector_serial,
          co_detector_brand: formData.co_detector_brand,
          co_detector_model: formData.co_detector_model,
          manometer_serial: formData.manometer_serial,
          manometer_brand: formData.manometer_brand,
          manometer_model: formData.manometer_model,
          has_calibration_pattern: formData.has_calibration_pattern,
          calibration_serial: formData.calibration_serial,
          seal_number: formData.seal_number
        };
      case 9:
        return {
          has_no_defects: formData.has_no_defects,
          has_non_critical_defect: formData.has_non_critical_defect,
          has_critical_defect: formData.has_critical_defect,
          installation_continues_service: formData.installation_continues_service,
          meter_reading: formData.meter_reading,
          supply_situation: formData.supply_situation,
          inspector_affirms_safe: formData.inspector_affirms_safe,
          client_signature: formData.client_signature,
          inspector_signature: formData.inspector_signature,
          client_phone: formData.client_phone,
          client_email_form: formData.client_email_form,
          inspector_name: formData.inspector_name,
          inspector_competence_id: formData.inspector_competence_id,
          inspector_specialty: formData.inspector_specialty,
          observations: formData.observations
        };
      default:
        return {};
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: "", type: "" }), 4000);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <Step1 formData={formData} onChange={handleInputChange} />;
      case 2:
        return <Step2 formData={formData} onChange={handleInputChange} />;
      case 3:
        return <Step3 formData={formData} onChange={handleInputChange} />;
      case 4:
        return <Step4 formData={formData} onChange={handleInputChange} />;
      case 5:
        return <Step5 formData={formData} onChange={handleInputChange} />;
      case 6:
        return <Step6 formData={formData} onChange={handleInputChange} />;
      case 7:
        return <Step7 formData={formData} onChange={handleInputChange} />;
      case 8:
        return <Step8 formData={formData} onChange={handleInputChange} />;
      case 9:
        return <Step9 formData={formData} onChange={handleInputChange} />;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="onac-form-loading">
        <div className="spinner"></div>
        <p>Cargando formulario...</p>
      </div>
    );
  }

  return (
    <div className="onac-form-container">
      {/* Header */}
      <div className="onac-form-header">
        <h2>Formulario de Inspección ONAC</h2>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${(currentStep / 9) * 100}%` }}
          />
        </div>
        <p className="step-indicator">Paso {currentStep} de 9</p>
      </div>

      {/* Message */}
      {message.text && (
        <div className={`form-message ${message.type}`}>
          {message.text}
        </div>
      )}

      {/* Step Content */}
      <div className="onac-form-content">
        {renderStepContent()}
      </div>

      {/* Navigation */}
      <div className="onac-form-navigation">
        <button
          type="button"
          className="btn-secondary"
          onClick={onCancel}
          disabled={saving}
        >
          Cancelar
        </button>

        <div className="nav-right">
          {currentStep > 1 && (
            <button
              type="button"
              className="btn-secondary"
              onClick={handlePrevious}
              disabled={saving}
            >
              ← Anterior
            </button>
          )}

          {currentStep < 9 ? (
            <button
              type="button"
              className="btn-primary"
              onClick={handleNext}
              disabled={saving}
            >
              {saving ? "Guardando..." : "Siguiente →"}
            </button>
          ) : (
            <button
              type="button"
              className="btn-complete"
              onClick={handleComplete}
              disabled={saving}
            >
              {saving ? "Guardando..." : "Completar Inspección"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ==================== PASO 1: Identificación de la Instalación ====================
function Step1({ formData, onChange }) {
  return (
    <div className="form-step">
      <h3>1. Identificación de la Instalación</h3>

      <div className="form-group">
        <label>Número de Cuenta *</label>
        <input
          type="text"
          value={formData.account_number}
          onChange={(e) => onChange("account_number", e.target.value)}
          placeholder="Ej: 12345678"
          required
        />
      </div>

      <div className="form-group">
        <label>Número de Medidor *</label>
        <input
          type="text"
          value={formData.meter_number}
          onChange={(e) => onChange("meter_number", e.target.value)}
          placeholder="Ej: MED-987654"
          required
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Fecha de Última Revisión</label>
          <input
            type="date"
            value={formData.last_revision_date}
            onChange={(e) => onChange("last_revision_date", e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Fecha de Vencimiento</label>
          <input
            type="date"
            value={formData.expiration_date}
            onChange={(e) => onChange("expiration_date", e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}

// ==================== PASO 2: Organismo de Inspección ====================
function Step2({ formData, onChange }) {
  return (
    <div className="form-step">
      <h3>2. Organismo de Inspección</h3>

      <div className="form-group">
        <label>Razón Social</label>
        <input
          type="text"
          value={formData.inspection_org_name}
          onChange={(e) => onChange("inspection_org_name", e.target.value)}
          readOnly
        />
      </div>

      <div className="form-group">
        <label>NIT</label>
        <input
          type="text"
          value={formData.inspection_org_nit}
          onChange={(e) => onChange("inspection_org_nit", e.target.value)}
          readOnly
        />
      </div>

      <div className="form-group">
        <label>Dirección</label>
        <input
          type="text"
          value={formData.inspection_org_address}
          onChange={(e) => onChange("inspection_org_address", e.target.value)}
          placeholder="Dirección del organismo"
        />
      </div>

      <div className="form-group">
        <label>Email</label>
        <input
          type="email"
          value={formData.inspection_org_email}
          onChange={(e) => onChange("inspection_org_email", e.target.value)}
          placeholder="contacto@ruis.com"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Hora de Inicio *</label>
          <input
            type="time"
            value={formData.inspection_start_time}
            onChange={(e) => onChange("inspection_start_time", e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label>Hora Final *</label>
          <input
            type="time"
            value={formData.inspection_end_time}
            onChange={(e) => onChange("inspection_end_time", e.target.value)}
            required
          />
        </div>
      </div>

      <div className="form-group">
        <label>Tipo de Presión *</label>
        <select
          value={formData.pressure_type}
          onChange={(e) => onChange("pressure_type", e.target.value)}
          required
        >
          <option value="BAJA">Baja</option>
          <option value="MEDIA">Media</option>
          <option value="ALTA">Alta</option>
        </select>
      </div>
    </div>
  );
}

// ==================== PASO 3: Tipo de Inspección ====================
function Step3({ formData, onChange }) {
  return (
    <div className="form-step">
      <h3>3. Tipo de Inspección</h3>

      <div className="form-group">
        <label>Fecha de Puesta en Servicio</label>
        <input
          type="date"
          value={formData.service_start_date}
          onChange={(e) => onChange("service_start_date", e.target.value)}
        />
      </div>

      <div className="checkbox-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.inspection_type_periodic}
            onChange={(e) => onChange("inspection_type_periodic", e.target.checked)}
          />
          <span>Revisión Periódica (10 años)</span>
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.inspection_type_modification}
            onChange={(e) => onChange("inspection_type_modification", e.target.checked)}
          />
          <span>Modificación y Reforma</span>
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.inspection_type_user_request}
            onChange={(e) => onChange("inspection_type_user_request", e.target.checked)}
          />
          <span>Solicitud del Usuario</span>
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.inspection_type_follow_up}
            onChange={(e) => onChange("inspection_type_follow_up", e.target.checked)}
          />
          <span>Seguimiento</span>
        </label>
      </div>

      {formData.inspection_type_user_request && (
        <div className="form-group">
          <label>Fecha de Solicitud del Usuario</label>
          <input
            type="date"
            value={formData.user_request_date}
            onChange={(e) => onChange("user_request_date", e.target.value)}
          />
        </div>
      )}
    </div>
  );
}

// ==================== PASO 4: Información de Recinto ====================
function Step4({ formData, onChange }) {
  const addRoom = () => {
    const newRoom = {
      id: Date.now(),
      type: "COCINA",
      measurements: { length: "", width: "", height: "" },
      volume: 0,
      total_power: "",
      complies_standard: false,
      upper_ventilation_area: "",
      lower_ventilation_area: "",
      sketch: null
    };
    onChange("rooms_data", [...formData.rooms_data, newRoom]);
  };

  const updateRoom = (roomId, field, value) => {
    const updatedRooms = formData.rooms_data.map(room => {
      if (room.id === roomId) {
        const updated = { ...room, [field]: value };

        // Auto-calculate volume if measurements change
        if (field === "measurements") {
          const { length, width, height } = value;
          if (length && width && height) {
            updated.volume = (parseFloat(length) * parseFloat(width) * parseFloat(height)).toFixed(2);
          }
        }

        return updated;
      }
      return room;
    });
    onChange("rooms_data", updatedRooms);
  };

  const deleteRoom = (roomId) => {
    onChange("rooms_data", formData.rooms_data.filter(r => r.id !== roomId));
  };

  return (
    <div className="form-step">
      <h3>4. Información de Recinto</h3>

      <button type="button" className="btn-add" onClick={addRoom}>
        + Agregar Recinto
      </button>

      {formData.rooms_data.length === 0 && (
        <p className="no-data">No hay recintos agregados. Haz clic en "Agregar Recinto".</p>
      )}

      {formData.rooms_data.map((room, index) => (
        <div key={room.id} className="room-card">
          <div className="card-header">
            <h4>Recinto #{index + 1}</h4>
            <button
              type="button"
              className="btn-delete-small"
              onClick={() => deleteRoom(room.id)}
            >
              ✕
            </button>
          </div>

          <div className="form-group">
            <label>Tipo de Recinto *</label>
            <select
              value={room.type}
              onChange={(e) => updateRoom(room.id, "type", e.target.value)}
              required
            >
              <option value="COCINA">Cocina</option>
              <option value="CALENTADOR">Calentador</option>
              <option value="SALA">Sala</option>
              <option value="HABITACION">Habitación</option>
              <option value="OTRO">Otro</option>
            </select>
          </div>

          <div className="measurements-grid">
            <div className="form-group">
              <label>Largo (m) *</label>
              <input
                type="number"
                step="0.01"
                value={room.measurements.length}
                onChange={(e) => updateRoom(room.id, "measurements", {
                  ...room.measurements,
                  length: e.target.value
                })}
                required
              />
            </div>
            <div className="form-group">
              <label>Ancho (m) *</label>
              <input
                type="number"
                step="0.01"
                value={room.measurements.width}
                onChange={(e) => updateRoom(room.id, "measurements", {
                  ...room.measurements,
                  width: e.target.value
                })}
                required
              />
            </div>
            <div className="form-group">
              <label>Alto (m) *</label>
              <input
                type="number"
                step="0.01"
                value={room.measurements.height}
                onChange={(e) => updateRoom(room.id, "measurements", {
                  ...room.measurements,
                  height: e.target.value
                })}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Volumen (m³)</label>
            <input
              type="text"
              value={room.volume}
              readOnly
              className="readonly-field"
            />
            <small>Se calcula automáticamente: Largo × Ancho × Alto</small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Potencia Total (BTU)</label>
              <input
                type="number"
                step="0.1"
                value={room.total_power}
                onChange={(e) => updateRoom(room.id, "total_power", e.target.value)}
              />
            </div>
            <div className="form-group checkbox-inline">
              <label>
                <input
                  type="checkbox"
                  checked={room.complies_standard}
                  onChange={(e) => updateRoom(room.id, "complies_standard", e.target.checked)}
                />
                <span>Cumple con Norma</span>
              </label>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Área Ventilación Superior (m²)</label>
              <input
                type="number"
                step="0.01"
                value={room.upper_ventilation_area}
                onChange={(e) => updateRoom(room.id, "upper_ventilation_area", e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Área Ventilación Inferior (m²)</label>
              <input
                type="number"
                step="0.01"
                value={room.lower_ventilation_area}
                onChange={(e) => updateRoom(room.id, "lower_ventilation_area", e.target.value)}
              />
            </div>
          </div>

          <DrawingCanvas
            label="Dibujo del Recinto"
            value={room.sketch}
            onChange={(dataURL) => updateRoom(room.id, "sketch", dataURL)}
            width={600}
            height={400}
          />
        </div>
      ))}
    </div>
  );
}

// ==================== PASO 5: Artefactos ====================
function Step5({ formData, onChange }) {
  const addAppliance = () => {
    const newAppliance = {
      id: Date.now(),
      room_id: formData.rooms_data[0]?.id || null,
      name: "",
      type: "COCINA",
      power_btu: "",
      normalized_coupling: false,
      ventilation_type: "NATURAL",
      dimensions: { trans: "", dism: "", long: "" },
      material: "CIR"
    };
    onChange("appliances_data", [...formData.appliances_data, newAppliance]);
  };

  const updateAppliance = (applianceId, field, value) => {
    const updated = formData.appliances_data.map(app =>
      app.id === applianceId ? { ...app, [field]: value } : app
    );
    onChange("appliances_data", updated);
  };

  const deleteAppliance = (applianceId) => {
    onChange("appliances_data", formData.appliances_data.filter(a => a.id !== applianceId));
  };

  return (
    <div className="form-step">
      <h3>5. Identificación de Artefactos</h3>

      <button type="button" className="btn-add" onClick={addAppliance}>
        + Agregar Artefacto
      </button>

      {formData.appliances_data.length === 0 && (
        <p className="no-data">No hay artefactos agregados.</p>
      )}

      {formData.appliances_data.map((appliance, index) => (
        <div key={appliance.id} className="appliance-card">
          <div className="card-header">
            <h4>Artefacto #{index + 1}</h4>
            <button
              type="button"
              className="btn-delete-small"
              onClick={() => deleteAppliance(appliance.id)}
            >
              ✕
            </button>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Recinto</label>
              <select
                value={appliance.room_id || ""}
                onChange={(e) => updateAppliance(appliance.id, "room_id", parseInt(e.target.value))}
              >
                <option value="">Seleccionar recinto</option>
                {formData.rooms_data.map(room => (
                  <option key={room.id} value={room.id}>
                    {room.type}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Nombre del Artefacto *</label>
              <input
                type="text"
                value={appliance.name}
                onChange={(e) => updateAppliance(appliance.id, "name", e.target.value)}
                placeholder="Ej: Estufa 4 puestos"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Tipo *</label>
              <select
                value={appliance.type}
                onChange={(e) => updateAppliance(appliance.id, "type", e.target.value)}
                required
              >
                <option value="COCINA">Cocina</option>
                <option value="CALENTADOR">Calentador</option>
                <option value="HORNO">Horno</option>
                <option value="SECADORA">Secadora</option>
                <option value="OTRO">Otro</option>
              </select>
            </div>

            <div className="form-group">
              <label>Potencia (BTU) *</label>
              <input
                type="number"
                step="0.1"
                value={appliance.power_btu}
                onChange={(e) => updateAppliance(appliance.id, "power_btu", e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group checkbox-inline">
              <label>
                <input
                  type="checkbox"
                  checked={appliance.normalized_coupling}
                  onChange={(e) => updateAppliance(appliance.id, "normalized_coupling", e.target.checked)}
                />
                <span>Acoplamiento Normalizado</span>
              </label>
            </div>

            <div className="form-group">
              <label>Tipo de Ventilación</label>
              <select
                value={appliance.ventilation_type}
                onChange={(e) => updateAppliance(appliance.id, "ventilation_type", e.target.value)}
              >
                <option value="NATURAL">Natural</option>
                <option value="FORZADA">Forzada</option>
                <option value="NINGUNA">Ninguna</option>
              </select>
            </div>
          </div>

          <div className="measurements-grid">
            <div className="form-group">
              <label>Trans. (m)</label>
              <input
                type="number"
                step="0.01"
                value={appliance.dimensions.trans}
                onChange={(e) => updateAppliance(appliance.id, "dimensions", {
                  ...appliance.dimensions,
                  trans: e.target.value
                })}
              />
            </div>
            <div className="form-group">
              <label>Dism. (m)</label>
              <input
                type="number"
                step="0.01"
                value={appliance.dimensions.dism}
                onChange={(e) => updateAppliance(appliance.id, "dimensions", {
                  ...appliance.dimensions,
                  dism: e.target.value
                })}
              />
            </div>
            <div className="form-group">
              <label>Long. (m)</label>
              <input
                type="number"
                step="0.01"
                value={appliance.dimensions.long}
                onChange={(e) => updateAppliance(appliance.id, "dimensions", {
                  ...appliance.dimensions,
                  long: e.target.value
                })}
              />
            </div>
          </div>

          <div className="form-group">
            <label>Material de Tubería</label>
            <select
              value={appliance.material}
              onChange={(e) => updateAppliance(appliance.id, "material", e.target.value)}
            >
              <option value="CF">CF - Cobre Flexible</option>
              <option value="CIR">CIR - Cobre Rígido</option>
              <option value="CSST">CSST - Acero Corrugado</option>
              <option value="PE">PE - Polietileno</option>
              <option value="OTRO">Otro</option>
            </select>
          </div>
        </div>
      ))}
    </div>
  );
}

// ==================== PASO 6: Edificación e Instalación ====================
function Step6({ formData, onChange }) {
  return (
    <div className="form-step">
      <h3>6. Edificación e Instalación</h3>

      <div className="section-title">Edificación</div>

      <div className="checkbox-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.has_internal_void}
            onChange={(e) => onChange("has_internal_void", e.target.checked)}
          />
          <span>Cuenta con Vacío Interno</span>
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.has_property_certificate}
            onChange={(e) => onChange("has_property_certificate", e.target.checked)}
          />
          <span>Certificado de Tradición y Libertad</span>
        </label>
      </div>

      <div className="form-group">
        <label>Aspecto del Inmueble</label>
        <input
          type="text"
          value={formData.property_aspect}
          onChange={(e) => onChange("property_aspect", e.target.value)}
          placeholder="Descripción general del estado del inmueble"
        />
      </div>

      <div className="section-title">Prueba de Hermeticidad</div>

      <div className="form-row">
        <div className="form-group">
          <label>Método de Prueba *</label>
          <select
            value={formData.leak_test_method}
            onChange={(e) => onChange("leak_test_method", e.target.value)}
            required
          >
            <option value="">Seleccionar método</option>
            <option value="DETECTOR">Detector Electrónico</option>
            <option value="ESPUMA">Espuma / Agua Jabonosa</option>
          </select>
        </div>

        <div className="form-group">
          <label>Presión de Prueba (mbar) *</label>
          <input
            type="number"
            step="0.01"
            value={formData.leak_test_pressure}
            onChange={(e) => onChange("leak_test_pressure", e.target.value)}
            placeholder="Ej: 150"
            required
          />
        </div>
      </div>

      <div className="checkbox-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.leak_test_meter}
            onChange={(e) => onChange("leak_test_meter", e.target.checked)}
          />
          <span>Prueba en Medidor</span>
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.leak_test_appliances}
            onChange={(e) => onChange("leak_test_appliances", e.target.checked)}
          />
          <span>Prueba en Artefactos</span>
        </label>
      </div>
    </div>
  );
}

// ==================== PASO 7: Checklist de Inspección ====================
function Step7({ formData, onChange }) {
  // Items del checklist ONAC (270-332)
  const checklistCategories = {
    "Acometida y Medidor": [
      { id: "270", text: "Ubicación adecuada del medidor" },
      { id: "271", text: "Medidor en buen estado" },
      { id: "272", text: "Válvula de corte accesible" },
      { id: "273", text: "Sin fugas en acometida" },
    ],
    "Tuberías": [
      { id: "280", text: "Material apropiado y certificado" },
      { id: "281", text: "Diámetro adecuado" },
      { id: "282", text: "Soportes correctos" },
      { id: "283", text: "Sin daños visibles" },
      { id: "284", text: "Conexiones herméticas" },
      { id: "285", text: "Distancias de seguridad" },
    ],
    "Ventilación": [
      { id: "290", text: "Ventilación superior adecuada" },
      { id: "291", text: "Ventilación inferior adecuada" },
      { id: "292", text: "Áreas libres de obstrucción" },
      { id: "293", text: "Rejillas en buen estado" },
    ],
    "Artefactos": [
      { id: "300", text: "Artefactos certificados" },
      { id: "301", text: "Instalación correcta" },
      { id: "302", text: "Llamas de combustión adecuadas" },
      { id: "303", text: "Sistema de evacuación" },
      { id: "304", text: "Funcionamiento correcto" },
    ],
    "Seguridad": [
      { id: "310", text: "Válvulas de paso operativas" },
      { id: "311", text: "Señalización presente" },
      { id: "312", text: "Extractor de gases (si aplica)" },
      { id: "313", text: "Detectores de gas (si aplica)" },
    ],
    "Instalación General": [
      { id: "320", text: "Cumple con normas vigentes" },
      { id: "321", text: "Sin instalaciones clandestinas" },
      { id: "322", text: "Documentación técnica completa" },
      { id: "323", text: "Instalación sin alteraciones" },
    ]
  };

  const toggleChecklistItem = (itemId) => {
    const current = formData.checklist_items[itemId] || false;
    onChange("checklist_items", {
      ...formData.checklist_items,
      [itemId]: !current
    });
  };

  return (
    <div className="form-step">
      <h3>7. Checklist de Inspección</h3>
      <p className="step-description">
        Marque los ítems que cumplen con la norma ONAC
      </p>

      {Object.entries(checklistCategories).map(([category, items]) => (
        <div key={category} className="checklist-category">
          <h4 className="category-title">{category}</h4>
          <div className="checklist-items">
            {items.map(item => (
              <label key={item.id} className="checklist-item">
                <input
                  type="checkbox"
                  checked={formData.checklist_items[item.id] || false}
                  onChange={() => toggleChecklistItem(item.id)}
                />
                <span className="item-id">{item.id}</span>
                <span className="item-text">{item.text}</span>
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ==================== PASO 8: Defectos y Equipos ====================
function Step8({ formData, onChange }) {
  const defectsList = {
    critical: [
      { id: "270", text: "Fuga de gas en acometida" },
      { id: "271", text: "Fuga de gas en tubería interna" },
      { id: "272", text: "Tubería sin soporte" },
      { id: "273", text: "Material no certificado" },
      { id: "275", text: "Ventilación insuficiente" },
      { id: "280", text: "Artefacto sin evacuación de gases" },
      { id: "285", text: "Instalación clandestina" },
    ],
    non_critical: [
      { id: "310", text: "Pintura deteriorada" },
      { id: "311", text: "Señalización incompleta" },
      { id: "312", text: "Válvula de difícil acceso" },
      { id: "318", text: "Documentación incompleta" },
      { id: "320", text: "Rejilla de ventilación sucia" },
    ]
  };

  const toggleDefect = (type, defectId) => {
    const field = type === "critical" ? "critical_defects" : "non_critical_defects";
    const current = formData[field];

    if (current.includes(defectId)) {
      onChange(field, current.filter(id => id !== defectId));
    } else {
      onChange(field, [...current, defectId]);
    }
  };

  return (
    <div className="form-step">
      <h3>8. Defectos y Equipos de Medición</h3>

      <div className="section-title">Defectos Encontrados</div>

      <div className="defects-section">
        <h4 className="defect-type critical">Defectos Críticos</h4>
        <div className="defect-list">
          {defectsList.critical.map(defect => (
            <label key={defect.id} className="defect-item critical">
              <input
                type="checkbox"
                checked={formData.critical_defects.includes(defect.id)}
                onChange={() => toggleDefect("critical", defect.id)}
              />
              <span className="defect-id">{defect.id}</span>
              <span className="defect-text">{defect.text}</span>
            </label>
          ))}
        </div>

        <h4 className="defect-type non-critical">Defectos No Críticos</h4>
        <div className="defect-list">
          {defectsList.non_critical.map(defect => (
            <label key={defect.id} className="defect-item non-critical">
              <input
                type="checkbox"
                checked={formData.non_critical_defects.includes(defect.id)}
                onChange={() => toggleDefect("non_critical", defect.id)}
              />
              <span className="defect-id">{defect.id}</span>
              <span className="defect-text">{defect.text}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="section-title">Equipos de Medición Utilizados</div>

      <div className="equipment-section">
        <h4>Detector de CO</h4>
        <div className="form-row">
          <div className="form-group">
            <label>Marca</label>
            <input
              type="text"
              value={formData.co_detector_brand}
              onChange={(e) => onChange("co_detector_brand", e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Modelo</label>
            <input
              type="text"
              value={formData.co_detector_model}
              onChange={(e) => onChange("co_detector_model", e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Serie</label>
            <input
              type="text"
              value={formData.co_detector_serial}
              onChange={(e) => onChange("co_detector_serial", e.target.value)}
            />
          </div>
        </div>

        <h4>Manómetro</h4>
        <div className="form-row">
          <div className="form-group">
            <label>Marca</label>
            <input
              type="text"
              value={formData.manometer_brand}
              onChange={(e) => onChange("manometer_brand", e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Modelo</label>
            <input
              type="text"
              value={formData.manometer_model}
              onChange={(e) => onChange("manometer_model", e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Serie</label>
            <input
              type="text"
              value={formData.manometer_serial}
              onChange={(e) => onChange("manometer_serial", e.target.value)}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group checkbox-inline">
            <label>
              <input
                type="checkbox"
                checked={formData.has_calibration_pattern}
                onChange={(e) => onChange("has_calibration_pattern", e.target.checked)}
              />
              <span>Patrón de Rx</span>
            </label>
          </div>
          <div className="form-group">
            <label>Serie Patrón</label>
            <input
              type="text"
              value={formData.calibration_serial}
              onChange={(e) => onChange("calibration_serial", e.target.value)}
              disabled={!formData.has_calibration_pattern}
            />
          </div>
          <div className="form-group">
            <label>Número de Sello</label>
            <input
              type="text"
              value={formData.seal_number}
              onChange={(e) => onChange("seal_number", e.target.value)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// ==================== PASO 9: Resultado y Firmas ====================
function Step9({ formData, onChange }) {
  return (
    <div className="form-step">
      <h3>9. Resultado y Firmas</h3>

      <div className="section-title">Resultado de la Inspección</div>

      <div className="result-options">
        <label className={`result-card ${formData.has_no_defects ? 'selected success' : ''}`}>
          <input
            type="radio"
            name="inspection_result"
            checked={formData.has_no_defects}
            onChange={() => {
              onChange("has_no_defects", true);
              onChange("has_non_critical_defect", false);
              onChange("has_critical_defect", false);
            }}
          />
          <div className="result-content">
            <span className="result-icon">✓</span>
            <span className="result-text">Sin Defectos</span>
          </div>
        </label>

        <label className={`result-card ${formData.has_non_critical_defect ? 'selected warning' : ''}`}>
          <input
            type="radio"
            name="inspection_result"
            checked={formData.has_non_critical_defect}
            onChange={() => {
              onChange("has_no_defects", false);
              onChange("has_non_critical_defect", true);
              onChange("has_critical_defect", false);
            }}
          />
          <div className="result-content">
            <span className="result-icon">⚠</span>
            <span className="result-text">Defecto No Crítico</span>
          </div>
        </label>

        <label className={`result-card ${formData.has_critical_defect ? 'selected danger' : ''}`}>
          <input
            type="radio"
            name="inspection_result"
            checked={formData.has_critical_defect}
            onChange={() => {
              onChange("has_no_defects", false);
              onChange("has_non_critical_defect", false);
              onChange("has_critical_defect", true);
            }}
          />
          <div className="result-content">
            <span className="result-icon">✕</span>
            <span className="result-text">Defecto Crítico</span>
          </div>
        </label>
      </div>

      <div className="form-row">
        <div className="form-group checkbox-inline">
          <label>
            <input
              type="checkbox"
              checked={formData.installation_continues_service}
              onChange={(e) => onChange("installation_continues_service", e.target.checked)}
            />
            <span>Instalación Continúa en Servicio</span>
          </label>
        </div>

        <div className="form-group">
          <label>Lectura Medidor (m³)</label>
          <input
            type="number"
            step="0.01"
            value={formData.meter_reading}
            onChange={(e) => onChange("meter_reading", e.target.value)}
          />
        </div>
      </div>

      <div className="form-group">
        <label>Situación de Suministro</label>
        <input
          type="text"
          value={formData.supply_situation}
          onChange={(e) => onChange("supply_situation", e.target.value)}
          placeholder="Descripción de la situación del suministro"
        />
      </div>

      <div className="form-group checkbox-inline">
        <label>
          <input
            type="checkbox"
            checked={formData.inspector_affirms_safe}
            onChange={(e) => onChange("inspector_affirms_safe", e.target.checked)}
          />
          <span>El inspector afirma que las condiciones son seguras</span>
        </label>
      </div>

      <div className="section-title">Datos del Inspector</div>

      <div className="form-row">
        <div className="form-group">
          <label>Nombre Completo del Inspector *</label>
          <input
            type="text"
            value={formData.inspector_name}
            onChange={(e) => onChange("inspector_name", e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Cédula de Competencia Laboral *</label>
          <input
            type="text"
            value={formData.inspector_competence_id}
            onChange={(e) => onChange("inspector_competence_id", e.target.value)}
            required
          />
        </div>
      </div>

      <div className="form-group">
        <label>Especialidad</label>
        <input
          type="text"
          value={formData.inspector_specialty}
          onChange={(e) => onChange("inspector_specialty", e.target.value)}
          placeholder="Ej: Inspector de Instalaciones de Gas"
        />
      </div>

      <div className="section-title">Datos del Cliente</div>

      <div className="form-row">
        <div className="form-group">
          <label>Teléfono del Cliente</label>
          <input
            type="tel"
            value={formData.client_phone}
            onChange={(e) => onChange("client_phone", e.target.value)}
          />
        </div>
        <div className="form-group">
          <label>Email del Cliente</label>
          <input
            type="email"
            value={formData.client_email_form}
            onChange={(e) => onChange("client_email_form", e.target.value)}
          />
        </div>
      </div>

      <div className="section-title">Firmas Digitales</div>

      <div className="signatures-container">
        <DrawingCanvas
          label="Firma del Cliente"
          value={formData.client_signature}
          onChange={(dataURL) => onChange("client_signature", dataURL)}
          width={500}
          height={200}
          backgroundColor="#ffffff"
          penColor="#000000"
        />

        <DrawingCanvas
          label="Firma del Inspector"
          value={formData.inspector_signature}
          onChange={(dataURL) => onChange("inspector_signature", dataURL)}
          width={500}
          height={200}
          backgroundColor="#ffffff"
          penColor="#000000"
        />
      </div>

      <div className="section-title">Observaciones Generales</div>

      <div className="form-group">
        <label>Observaciones</label>
        <textarea
          value={formData.observations}
          onChange={(e) => onChange("observations", e.target.value)}
          placeholder="Ingrese cualquier observación adicional sobre la inspección"
          rows={5}
        />
      </div>
    </div>
  );
}

export default ONACInspectionForm;
