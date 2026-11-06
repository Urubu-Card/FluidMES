import { useEffect, useState } from "react";
import { dateTime, number } from "../../shared/format";
export default function Telemetry({ plant }) {
  const [status, setStatus] = useState("Conectando ao monitor…");
  const [readings, setReadings] = useState({});
  useEffect(() => {
    const base = new URL(
      import.meta.env.VITE_API_URL || window.location.origin,
    );
    base.protocol = base.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(`${base.origin}/ws/plant/${plant.uuid}/`);
    socket.onopen = () =>
      setStatus("Monitor conectado. Aguardando leituras dos sensores.");
    socket.onmessage = (event) => {
      const item = JSON.parse(event.data);
      setReadings((old) => ({ ...old, [item.clp]: item }));
    };
    socket.onerror = () => setStatus("Monitor indisponível no momento.");
    socket.onclose = () => setStatus("Monitor desconectado.");
    return () => socket.close();
  }, [plant.uuid]);
  return (
    <section className="telemetry-panel">
      <h3>Monitor ao vivo</h3>
      <p className="muted">{status}</p>
      {Object.entries(readings).map(([id, item]) => (
        <div key={id}>
          <strong>{item.nome_clp || `CLP #${id}`}</strong>
          <p>{item.erro || dateTime(item.timestamp)}</p>
          <div className="telemetry-values">
            {Object.entries(item.leituras).map(([sensor, value]) => (
              <span key={sensor}>
                {item.sensores?.[sensor]?.nome || `Sensor #${sensor}`}
                <strong>
                  {number(value)} {item.sensores?.[sensor]?.unidade}
                </strong>
              </span>
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}
