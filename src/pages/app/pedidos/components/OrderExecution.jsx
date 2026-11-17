import useData from "../../shared/useData";
import { DataState } from "../../shared/UI";
import BatchPlan from "./BatchPlan";

export default function OrderExecution({ id }) {
  const { data, error, loading, reload } = useData(
    [`/api/pedidos/${id}/`],
    1500,
  );
  const order = data?.[0];
  return (
    <>
      <DataState loading={loading} error={error} reload={reload} />
      {order && (
        <>
          {order.em_pausa && (
            <div className="form-error" role="status">
              <p>
                Produção pausada. A previsão será atualizada na retomada.
              </p>
              {order.motivo_pausa?.map((item) => (
                <p key={item.planta}>
                  <strong>{item.planta}:</strong> {item.motivo}.
                </p>
              ))}
            </div>
          )}
          {order.aviso_previsao && (
            <p className="form-error">{order.aviso_previsao}</p>
          )}
          <p className="info-note">
            Receita: {order.receita_snapshot?.nome || order.receita_nome} ·
            versão {order.receita_snapshot?.versao || "anterior"}.{" "}
            {order.execucao_clp?.length
              ? "Execução real: em cada ciclo o MES grava a receita no CLP e aciona o START_CYCLE."
              : order.simulado
                ? "Execução simulada com as durações da receita."
                : "Simulação desligada; este plano não envia comandos ao equipamento."}
          </p>
          {order.execucao_clp
            ?.filter((item) => item.motivo)
            .map((item) => (
              <p className="form-error" role="status" key={item.clp}>
                <i aria-hidden="true" className="bi bi-lock-fill" />{" "}
                {item.planta}: MES bloqueado. {item.motivo}
              </p>
            ))}
          <BatchPlan plan={order.plano} lots={order.lotes} />
        </>
      )}
    </>
  );
}
