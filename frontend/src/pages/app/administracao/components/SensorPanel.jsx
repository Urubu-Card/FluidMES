import { useState } from "react";
import api from "../../../../services/api";
import { errorMessage } from "../../../../services/errors";
import Button from "../../shared/controls/Button";
import Field from "../../shared/controls/Field";
import { StatusBadge } from "../../shared/UI";
import { dateTime, number } from "../../shared/format";
import "./sensorPanel.css";

const estados = {
  online: ["Online", "success"],
  fora_limite: ["Fora dos limites", "warning"],
  offline: ["Sem comunicação", "danger"],
  desativado: ["Desativado", "secondary"],
  desatualizado: ["Leitura antiga", "warning"],
  sem_leitura: ["Sem leitura", "secondary"],
};

function valorLido(sensor) {
  if (sensor.valor_atual == null) return "—";
  if (sensor.tipo_registro !== "holding_register") {
    return sensor.valor_atual ? "Ligado · 1" : "Desligado · 0";
  }
  const unidade = sensor.unidade_label === "sem unidade" ? "" : sensor.unidade_label;
  return [number(sensor.valor_atual), unidade].filter(Boolean).join(" ");
}

export function SensorRowStatus({ sensor }) {
  const [label, tone] = estados[sensor.estado] || estados.sem_leitura;
  return (
    <span className="sensor-row-status">
      <strong>{valorLido(sensor)}</strong>
      <StatusBadge label={label} tone={tone} />
    </span>
  );
}

export function SensorOverview({ sensors }) {
  const online = sensors.filter((sensor) => sensor.estado === "online").length;
  const alerts = sensors.filter((sensor) => sensor.estado === "fora_limite").length;
  return (
    <section className="sensor-overview" aria-label="Painel de sensores">
      <div>
        <h2>Painel de sensores</h2>
        <p className="muted">
          Abra um sensor para ler o CLP ou enviar um comando.
        </p>
      </div>
      <div className="sensor-indicators">
        <StatusBadge label={`${online} online`} tone="success" />
        <StatusBadge label={`${alerts} fora dos limites`} tone="warning" />
        <StatusBadge label={`${sensors.length - online - alerts} indisponíveis`} />
      </div>
    </section>
  );
}

export function SensorControl({ sensor, reload }) {
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null);
  const coil = sensor.tipo_registro === "coil";
  const pulse = coil && sensor.nome.endsWith(".START_CYCLE");

  async function execute(action, payload = {}) {
    setBusy(true);
    setMessage(null);
    try {
      const { data } = await api.post(
        `/api/sensores/${sensor.idsensor}/${action}/`,
        payload,
      );
      setMessage({ text: data.detail });
      await reload();
    } catch (error) {
      const detail = error.response?.data?.detail;
      setMessage({ text: detail || errorMessage(error), failed: true });
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="sensor-control" aria-label="Leitura e comandos Modbus">
      <div className="sensor-overview">
        <div>
          <h3>Leitura e comandos Modbus</h3>
          <p className="muted">{sensor.clp_endereco}</p>
        </div>
        <SensorRowStatus sensor={sensor} />
      </div>
      <p className="muted">
        Última leitura: {sensor.lido_em ? dateTime(sensor.lido_em) : "Aguardando leitura"}
      </p>
      <div className="form-actions sensor-buttons">
        <Button variant="secondary" icon="bi-arrow-repeat" disabled={busy || !sensor.clp_ativo}
          onClick={() => execute("ler")}>
          Ler agora
        </Button>
        {sensor.pode_escrever && coil && (
          <>
            <Button icon="bi-play-fill" disabled={busy}
              onClick={() => execute("escrever", { valor: true })}>
              {pulse ? "Disparar partida" : "Ligar coil"}
            </Button>
            <Button variant="secondary" disabled={busy}
              onClick={() => execute("escrever", { valor: false })}>
              Desligar coil
            </Button>
          </>
        )}
      </div>
      {sensor.pode_escrever && !coil && (
        <form
          className="sensor-write-form"
          onSubmit={(event) => {
            event.preventDefault();
            execute("escrever", { valor: Number(value) });
          }}
        >
          <Field
            label="Valor inteiro do registro"
            type="number"
            min={Math.max(0, sensor.minimo)}
            max={Math.min(65535, sensor.maximo)}
            step={1}
            required
            disabled={busy}
            value={value}
            onChange={setValue}
          />
          <Button type="submit" icon="bi-send" disabled={busy || value === ""}>
            Enviar valor
          </Button>
        </form>
      )}
      {!sensor.pode_escrever && (
        <p className="muted">Escrita indisponível para este sensor ou CLP.</p>
      )}
      {sensor.pode_escrever && pulse && (
        <p className="muted">A partida é um pulso e só é aceita com a planta no modo 2 (MES). Em produção, o MES a aciona sozinho ao iniciar cada ciclo do pedido.</p>
      )}
      {message && (
        <p className={message.failed ? "form-error" : "info-note"} role="status">
          {message.text}
        </p>
      )}
    </section>
  );
}
