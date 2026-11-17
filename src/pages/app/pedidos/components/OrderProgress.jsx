import { useEffect, useState } from "react";
export default function OrderProgress({ order }) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (order.estado !== "producao") return;
    const timer = setInterval(() => setNow(Date.now()), 500);
    return () => clearInterval(timer);
  }, [order.estado]);
  if (order.estado !== "producao") return null;
  const elapsed = Math.max(
    0,
    (now - new Date(order.iniciado_em).getTime()) / 1000,
  );
  const progress = Math.min(
    99,
    (elapsed / (order.duracao_simulada_seg || 10)) * 100,
  );
  return (
    <div className="order-progress">
      <div className="mes-progress">
        <span style={{ width: `${progress}%` }} />
      </div>
      <small>
        {elapsed < (order.duracao_simulada_seg || 10)
          ? `Produção em andamento · ${Math.max(0, Math.ceil((order.duracao_simulada_seg || 10) - elapsed))} s`
          : "Finalizando produção…"}
      </small>
    </div>
  );
}
