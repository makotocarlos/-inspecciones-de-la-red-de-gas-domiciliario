import { useRef, useEffect } from "react";
import SignatureCanvas from "react-signature-canvas";
import "./DrawingCanvas.css";

/**
 * Componente reutilizable para dibujar diagramas y capturar firmas
 * Optimizado para uso en tablets
 */
function DrawingCanvas({
  onChange,
  value,
  width = 600,
  height = 400,
  label = "Dibujo",
  backgroundColor = "#ffffff",
  penColor = "#000000"
}) {
  const sigCanvas = useRef(null);

  useEffect(() => {
    if (value && sigCanvas.current) {
      // Cargar imagen existente si hay valor
      sigCanvas.current.fromDataURL(value);
    }
  }, [value]);

  const handleClear = () => {
    if (sigCanvas.current) {
      sigCanvas.current.clear();
      if (onChange) {
        onChange(null);
      }
    }
  };

  const handleEnd = () => {
    if (sigCanvas.current && onChange) {
      const dataURL = sigCanvas.current.toDataURL("image/png");
      onChange(dataURL);
    }
  };

  return (
    <div className="drawing-canvas-container">
      <label className="canvas-label">{label}</label>
      <div className="canvas-wrapper">
        <SignatureCanvas
          ref={sigCanvas}
          canvasProps={{
            width: width,
            height: height,
            className: "signature-canvas"
          }}
          backgroundColor={backgroundColor}
          penColor={penColor}
          onEnd={handleEnd}
        />
      </div>
      <button
        type="button"
        className="btn-clear-canvas"
        onClick={handleClear}
      >
        🗑️ Limpiar
      </button>
    </div>
  );
}

export default DrawingCanvas;
