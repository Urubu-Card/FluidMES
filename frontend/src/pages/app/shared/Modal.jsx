import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
export default function Modal({ title, children, onClose, footer }) {
  const [expanded, setExpanded] = useState(false);
  const panel = useRef(null);
  const id = useId();
  const closeRef = useRef(onClose);
  useEffect(() => {
    closeRef.current = onClose;
  }, [onClose]);
  useEffect(() => {
    const previous = document.activeElement;
    const dialog = panel.current;
    dialog.focus();
    const escape = (event) => {
      if (event.key === "Escape") closeRef.current();
      if (event.key === "Tab") {
        const nodes = [
          ...dialog.querySelectorAll(
            'button:not(:disabled),input:not(:disabled),select:not(:disabled),a[href],textarea:not(:disabled),[tabindex="0"]',
          ),
        ].filter((n) => n.offsetParent !== null);
        if (!nodes.length) {
          event.preventDefault();
          return;
        }
        const first = nodes[0],
          last = nodes.at(-1);
        if (
          event.shiftKey &&
          (document.activeElement === first ||
            document.activeElement === dialog)
        ) {
          event.preventDefault();
          last.focus();
        } else if (
          !event.shiftKey &&
          (document.activeElement === last || document.activeElement === dialog)
        ) {
          event.preventDefault();
          first.focus();
        }
      }
    };
    dialog.addEventListener("keydown", escape);
    const old = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      dialog.removeEventListener("keydown", escape);
      document.body.style.overflow = old;
      previous?.focus();
    };
  }, []);
  // Portal stays inside the themed workspace to inherit variables and contrast.
  return createPortal(
    <div
      className={`mes-modal-layer ${expanded ? "fullscreen-layer" : ""}`}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        ref={panel}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby={id}
        className={`mes-modal ${expanded ? "expanded" : ""}`}
      >
        <header>
          <div>
            <span className="eyebrow">FLUIDMES</span>
            <h2 id={id}>{title}</h2>
          </div>
          <div className="modal-tools">
            <button
              className="icon-button"
              aria-label={expanded ? "Restaurar tamanho" : "Expandir modal"}
              onClick={() => setExpanded(!expanded)}
            >
              <i
                aria-hidden="true"
                className={`bi ${expanded ? "bi-fullscreen-exit" : "bi-arrows-fullscreen"}`}
              />
            </button>
            <button
              className="icon-button"
              aria-label="Fechar modal"
              onClick={onClose}
            >
              <i aria-hidden="true" className="bi bi-x-lg" />
            </button>
          </div>
        </header>
        <div className="mes-modal-body">{children}</div>
        {footer && <footer>{footer}</footer>}
      </section>
    </div>,
    document.getElementById("mes-overlays"),
  );
}
