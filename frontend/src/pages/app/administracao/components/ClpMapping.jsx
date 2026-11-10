import { useState } from "react";
import Button from "../../shared/controls/Button";
import api from "../../../../services/api";
import { errorMessage } from "../../../../services/errors";

export default function ClpMapping({ clp }) {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function applyMapping() {
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const { data } = await api.post(
        `/api/clps/${clp.idclp}/aplicar_mapeamento/`,
      );
      setResult(data);
    } catch (e) {
      setError(e.response?.data?.detail || errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="telemetry-panel">
      <h3>Mapa Modbus · TK1 e TK2</h3>
      <p className="muted">
        Cadastra 22 tags da planilha para este CLP. Os endereços no cadastro
        começam em zero. A operação grava somente o cadastro no FluidMES. O
        registro MODO é somente leitura: 0 operação local, 1 aparelho, 2 MES.
      </p>
      <Button
        variant="secondary"
        icon="bi-diagram-3"
        disabled={busy}
        onClick={applyMapping}
      >
        {busy ? "Aplicando…" : "Aplicar mapa da planilha"}
      </Button>
      {result && (
        <p className="info-note" role="status">
          {result.cadastradas} novas · {result.existentes} já cadastradas.
          Consulte as tags na aba Sensores.
        </p>
      )}
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
