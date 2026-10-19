import { useState } from "react";
import Modal from "./Modal";
import Button from "./controls/Button";
import { useWorkspace } from "./context";
import { errorMessage } from "../../../services/errors";

export default function FormModal({
  title,
  onClose,
  onSubmit,
  children,
  submitLabel = "Salvar",
  disabled = false,
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const { notify } = useWorkspace();
  const close = () => {
    if (!busy) onClose();
  };
  async function submit(event) {
    event.preventDefault();
    if (busy || disabled) return;
    setBusy(true);
    setError("");
    try {
      const response = await onSubmit();
      notify(
        response?.data?.detail ||
          (response?.status === 202
            ? "Solicitação enviada para aprovação."
            : "Salvo com sucesso."),
      );
      onClose();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <Modal title={title} onClose={close}>
      <form className="entity-form" onSubmit={submit}>
        {error && (
          <p role="alert" className="form-error">
            {error}
          </p>
        )}
        <fieldset className="form-fields" disabled={busy}>
          {children}
        </fieldset>
        <div className="form-actions">
          <Button variant="secondary" onClick={close} disabled={busy}>
            Cancelar
          </Button>
          <Button type="submit" disabled={busy || disabled}>
            {busy ? "Salvando…" : submitLabel}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
