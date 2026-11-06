import { dateTime, number } from "../../shared/format";

const modeIcons = { 0: "bi-person-gear", 1: "bi-tablet", 2: "bi-pc-display" };

/* Selo do registro MODO: 0 local, 1 aparelho, 2 MES. Texto e ícone, não só cor. */
export function ModeBadge({ control }) {
  if (!control) return null;
  const known = control.modo != null;
  return (
    <span
      className={`mode-badge ${control.mes_liberado ? "is-mes" : "is-locked"}`}
      title={control.motivo || "MES no comando do tanque"}
    >
      <i
        aria-hidden="true"
        className={`bi ${control.mes_liberado ? modeIcons[2] : known ? modeIcons[control.modo] || "bi-lock" : "bi-question-circle"}`}
      />
      {known ? `Modo ${control.modo} · ${control.modo_label}` : "Modo não lido"}
    </span>
  );
}

export default function TankControl({ control }) {
  if (!control) return null;
  const target = control.niveis?.[2] || 0;
  const fill = target
    ? Math.min(100, ((control.nivel_atual || 0) / target) * 100)
    : 0;
  return (
    <section className="telemetry-panel tank-control">
      <div className="tank-control-head">
        <h3>Tanque {control.tanque} · controle pelo CLP</h3>
        <ModeBadge control={control} />
      </div>
      {control.motivo ? (
        <p className="form-error" role="status">
          <i aria-hidden="true" className="bi bi-lock-fill" /> MES bloqueado.{" "}
          {control.motivo} Os ciclos programados aguardam.
        </p>
      ) : (
        <p className="info-note" role="status">
          MES no comando: ao iniciar um ciclo, a receita é gravada e o
          START_CYCLE é acionado.
        </p>
      )}
      <div className="telemetry-values">
        <span>
          Ciclo
          <strong>{control.status_ciclo_label || "—"}</strong>
        </span>
        <span>
          Etapa
          <strong>{control.etapa ? `${control.etapa} de 3` : "—"}</strong>
        </span>
        <span>
          Nível atual
          <strong>
            {number(control.nivel_atual)}
            {target ? ` / ${number(target)}` : ""}
          </strong>
        </span>
        <span>
          Níveis 1 · 2 · 3
          <strong>{control.niveis?.join(" · ") || "—"}</strong>
        </span>
        <span>
          Tempos 1 · 2 · 3 (s)
          <strong>{control.tempos?.join(" · ") || "—"}</strong>
        </span>
      </div>
      <div className="mes-progress" aria-hidden="true">
        <span style={{ width: `${fill}%` }} />
      </div>
      <p className="muted">
        Última leitura: {control.lido_em ? dateTime(control.lido_em) : "aguardando"}
      </p>
    </section>
  );
}
