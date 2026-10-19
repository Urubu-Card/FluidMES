import { useState } from "react";
import Modal from "./Modal";
import Button from "./controls/Button";
export function PageHeader({
  eyebrow = "SUA OPERAÇÃO EM MOVIMENTO",
  title,
  description,
  children,
}) {
  return (
    <header className="page-heading">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      <div className="heading-actions">{children}</div>
    </header>
  );
}
export function AddButton({ label, onClick }) {
  return (
    <button
      type="button"
      className="fab-add"
      aria-label={label}
      title={label}
      onClick={onClick}
    >
      <span aria-hidden="true">+</span>
    </button>
  );
}
export function Empty({
  title = "Nada por aqui ainda",
  description = "Os novos registros aparecerão aqui.",
  icon = "bi-inbox",
}) {
  return (
    <div className="empty-state">
      <i aria-hidden="true" className={`bi ${icon}`} />
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}
export function DataState({ loading, error, reload }) {
  return loading ? (
    <div className="loading-state" role="status">
      <span className="spinner-border spinner-border-sm" /> Carregando sua
      operação…
    </div>
  ) : error ? (
    <div className="empty-state" role="alert">
      <h3>Não foi possível carregar</h3>
      <p>{error}</p>
      <Button variant="secondary" onClick={reload}>
        Tentar novamente
      </Button>
    </div>
  ) : null;
}
export function StatusBadge({ label, tone = "secondary" }) {
  return (
    <span className={`status-badge tone-${tone}`}>
      <span />
      {label}
    </span>
  );
}
export function Confirm({
  title = "Excluir registro?",
  description,
  onClose,
  onConfirm,
}) {
  const [busy, setBusy] = useState(false);
  return (
    <Modal
      title={title}
      onClose={() => {
        if (!busy) onClose();
      }}
    >
      <p>{description || "Esta ação não pode ser desfeita."}</p>
      <div className="form-actions">
        <Button className="secondary" onClick={onClose} disabled={busy}>
          Cancelar
        </Button>
        <Button
          className="danger"
          disabled={busy}
          onClick={async () => {
            setBusy(true);
            try {
              await onConfirm();
            } finally {
              setBusy(false);
            }
          }}
        >
          {busy ? "Processando…" : "Confirmar"}
        </Button>
      </div>
    </Modal>
  );
}
export function Details({ items }) {
  return (
    <dl className="detail-grid">
      {items.map(([label, value]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd>{value ?? "—"}</dd>
        </div>
      ))}
    </dl>
  );
}
