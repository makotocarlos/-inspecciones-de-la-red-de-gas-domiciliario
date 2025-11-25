import { useNavigate } from "react-router-dom";
import "../styles/AboutPage.css";

function AboutPage() {
  const navigate = useNavigate();

  return (
    <div className="about-page">
      <div className="about-header">
        <h1>Acerca del Sistema</h1>
        <p>Sistema de Gestión para Inspecciones de Gas Domiciliario</p>
      </div>

      <div className="about-content">
        <div className="container">
          <section className="about-section">
            <h2>¿Qué es este sistema?</h2>
            <p>
              Este es un sistema integral diseñado para gestionar el proceso completo de inspecciones
              de gas domiciliario, desde el agendamiento de citas hasta la emisión de certificados de inspección.
            </p>
            <p>
              El sistema facilita la coordinación entre administradores, call center, inspectores y clientes,
              asegurando un proceso eficiente y trazable.
            </p>
          </section>

          <section className="about-section">
            <h2>Funcionalidades Principales</h2>
            <div className="functionality-grid">
              <div className="functionality-item">
                <h3>👥 Gestión de Usuarios</h3>
                <p>Sistema robusto de autenticación con tres roles principales: Administrador, Call Center e Inspector.</p>
              </div>
              <div className="functionality-item">
                <h3>📅 Agendamiento</h3>
                <p>Programación eficiente de citas con asignación automática de inspectores disponibles.</p>
              </div>
              <div className="functionality-item">
                <h3>🔍 Inspecciones</h3>
                <p>Formularios técnicos completos para documentar cada inspección con todos los detalles necesarios.</p>
              </div>
              <div className="functionality-item">
                <h3>📊 Reportes</h3>
                <p>Generación de reportes y estadísticas para monitorear el desempeño del sistema.</p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>¿Cómo funciona?</h2>
            <div className="workflow">
              <div className="workflow-step">
                <div className="step-number">1</div>
                <h3>Administrador</h3>
                <p>Crea cuentas para el personal de Call Center e Inspectores</p>
              </div>
              <div className="workflow-arrow">→</div>
              <div className="workflow-step">
                <div className="step-number">2</div>
                <h3>Call Center</h3>
                <p>Agenda citas con los clientes y asigna inspectores</p>
              </div>
              <div className="workflow-arrow">→</div>
              <div className="workflow-step">
                <div className="step-number">3</div>
                <h3>Inspector</h3>
                <p>Realiza la inspección y completa el formulario técnico</p>
              </div>
              <div className="workflow-arrow">→</div>
              <div className="workflow-step">
                <div className="step-number">4</div>
                <h3>Certificado</h3>
                <p>Se emite el certificado de inspección al cliente</p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Tecnologías Utilizadas</h2>
            <div className="tech-grid">
              <div className="tech-item">
                <h4>Frontend</h4>
                <ul>
                  <li>React 18</li>
                  <li>React Router</li>
                  <li>Axios</li>
                  <li>CSS3</li>
                </ul>
              </div>
              <div className="tech-item">
                <h4>Backend</h4>
                <ul>
                  <li>Django</li>
                  <li>Django REST Framework</li>
                  <li>JWT Authentication</li>
                  <li>PostgreSQL</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="about-section about-cta">
            <h2>¿Listo para comenzar?</h2>
            <p>Inicia sesión para acceder al sistema</p>
            <button className="btn-cta" onClick={() => navigate("/login")}>
              Iniciar Sesión
            </button>
          </section>
        </div>
      </div>

      <div className="about-footer">
        <div className="container">
          <p>&copy; 2025 Sistema de Inspecciones de Gas</p>
        </div>
      </div>
    </div>
  );
}

export default AboutPage;
