import { useState } from "react";
import Button from "../../shared/controls/Button";
import api from "../../../../services/api";
import { errorMessage } from "../../../../services/errors";
export default function ClpConnectionTest({ clp }) {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  async function test() {
    setBusy(true);
    try {
      setResult((await api.post(`/api/clps/${clp.idclp}/testar/`)).data);
    } catch (e) {
      setResult({ mensagem: errorMessage(e) });
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="telemetry-panel">
      <h3>Diagnóstico de comunicação</h3>
      <p className="muted">
        Verifica a conexão e, se houver um sensor cadastrado, lê seu registro.
        Este teste não aciona bombas ou válvulas.
      </p>
      <Button variant="secondary" icon="bi-plug" disabled={busy} onClick={test}>
        {busy ? "Testando…" : "Testar comunicação"}
      </Button>
      {result && (
        <p
          className={result.leitura_validada ? "info-note" : "form-error"}
          role="status"
        >
          {result.mensagem}
          {result.valor != null
            ? ` ${result.sensor}: ${result.valor} (valor bruto).`
            : ""}
        </p>
      )}
    </section>
  );
}
