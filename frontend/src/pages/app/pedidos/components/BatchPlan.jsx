import { dateTime, number, duration } from "../../shared/format";
export default function BatchPlan({ plan, lots = [], compact = false }) {
  if (!plan?.previsao_conclusao)
    return (
      <p className="info-note">
        A previsão e a divisão entre tanques serão calculadas na aprovação.
      </p>
    );
  return (
    <section className="batch-plan" aria-label="Plano de produção">
      <div className="plan-summary">
        <div>
          <small>Conclusão estimada</small>
          <strong>{dateTime(plan.previsao_conclusao)}</strong>
        </div>
        <div>
          <small>Duração estimada</small>
          <strong>{duration(plan.duracao_total_seg)}</strong>
        </div>
        <div>
          <small>Distribuição</small>
          <strong>
            {plan.lotes_qtd} ciclos · {plan.plantas_qtd} tanques
          </strong>
        </div>
      </div>
      {!compact && (
        <>
          <p className="muted">
            {plan.criterio} A aprovação confirma a disponibilidade e pode
            atualizar esta estimativa.
          </p>
          <ol className="batch-list">
            {lots.map((lot, i) => (
              <li key={lot.id || `${lot.planta}-${i}`}>
                <details open={lots.length < 5}>
                  <summary>
                    <strong>
                      {lot.planta_nome} · {number(lot.quantidade)} L
                    </strong>
                    <span>
                      Ciclo {lot.sequencia || i + 1} ·{" "}
                      {lot.fase_atual || "Programado"}
                    </span>
                  </summary>
                  <p className="muted">
                    {dateTime(lot.inicio_previsto)} →{" "}
                    {dateTime(lot.fim_previsto)}
                  </p>
                  {lot.motivo && <p className="muted">{lot.motivo}</p>}
                  <ol className="batch-stages">
                    {lot.etapas?.map((step, j) => (
                      <li key={j}>
                        <span>
                          {step.nome}
                          {step.quantidade_l != null
                            ? ` · ${number(step.quantidade_l)} L`
                            : ""}
                        </span>
                        <strong>{duration(step.duracao_seg)}</strong>
                      </li>
                    ))}
                  </ol>
                </details>
              </li>
            ))}
          </ol>
        </>
      )}
    </section>
  );
}
