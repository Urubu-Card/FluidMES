import { SensorControl, SensorOverview, SensorRowStatus } from "./components/SensorPanel";
import SensorForm from "./components/SensorForm";
import ClpMapping from "./components/ClpMapping";
import ClpConnectionTest from "./components/ClpConnectionTest";
import { dateTime } from "../shared/format";
import { useState } from "react";
import EntityList from "../shared/EntityList";
import { clpFields, sensorFields, stopFields } from "../shared/resources";
export default function Administracao() {
  const [tab, setTab] = useState("clps");
  const configs = {
    clps: ["CLPs", "idclp", clpFields],
    sensores: ["Sensores", "idsensor", sensorFields],
    paradas: ["Paradas", "idparada", stopFields],
  };
  const [title, id, fields] = configs[tab];
  const sensores = tab === "sensores";
  return (
    <div>
      <div className="admin-tabs segmented">
        {Object.entries(configs).map(([key, [label]]) => (
          <button
            key={key}
            className={tab === key ? "active" : ""}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>
      <EntityList
        key={tab}
        title={`Administração · ${title}`}
        description="Configuração técnica da operação. Acesso exclusivo do Preposto."
        endpoint={`/api/${tab}/`}
        idField={id}
        fields={fields}
        formComponent={sensores ? SensorForm : undefined}
        refreshInterval={sensores ? 3000 : 0}
        renderOverview={sensores ? (items) => <SensorOverview sensors={items} /> : undefined}
        createLabel={`Adicionar ${title === "Paradas" ? "parada" : title === "Sensores" ? "sensor" : "CLP"}`}
        renderRow={(item) => (
          <>
            <div className="entity-avatar">
              <i
                aria-hidden="true"
                className={`bi ${tab === "clps" ? "bi-hdd-network" : tab === "sensores" ? "bi-broadcast" : "bi-pause-circle"}`}
              />
            </div>
            <div className="row-main">
              <strong>{item.nome || `Parada #${item.idparada}`}</strong>
              <span>
                {tab === "clps"
                  ? `${item.ip}:${item.porta}`
                  : tab === "sensores"
                    ? `${item.clp_nome} · ${item.tipo_label} · ${item.unidade_label}`
                    : new Date(item.inicio).toLocaleString("pt-BR")}
              </span>
            </div>
            {sensores && <SensorRowStatus sensor={item} />}
          </>
        )}
        renderDetailExtra={
          tab === "clps"
            ? (item) => (
                <>
                  <ClpMapping clp={item} />
                  <ClpConnectionTest clp={item} />
                </>
              )
            : sensores
              ? (item, reload) => <SensorControl sensor={item} reload={reload} />
              : undefined
        }
        details={(item) => [
          ...(tab === "clps"
            ? [
                ["Comunicação", item.status || "Não testada"],
                ["Última leitura válida", dateTime(item.ultima_comunicacao)],
                [
                  "Modo da planta",
                  item.controle
                    ? item.controle.modo != null
                      ? `${item.controle.modo} · ${item.controle.modo_label}${item.controle.mes_liberado ? "" : " (MES bloqueado)"}`
                      : "Ainda não lido"
                    : "Sem tanque de produção",
                ],
              ]
            : []),
          ...fields
            .filter((f) => f.type !== "password")
            .map((f) => {
              const labels = {
                unidade: item.unidade_label,
                tipo: item.tipo_label,
                tipo_registro: item.registro_label,
                clp: item.clp_nome,
              };
              const value = labels[f.name] ?? item[f.name];
              return [f.label, f.type === "checkbox" ? (value ? "Sim" : "Não") : String(value ?? "—")];
            }),
        ]}
      />
    </div>
  );
}
