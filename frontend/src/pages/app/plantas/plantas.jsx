import Button from "../shared/controls/Button.jsx";
import { useState } from "react";
import api from "../../../services/api";
import useData from "../shared/useData";
import { useWorkspace } from "../shared/context";
import { plantFields } from "../shared/resources";
import {
  PageHeader,
  AddButton,
  DataState,
  Empty,
  Details,
  Confirm,
} from "../shared/UI";
import { number, percent } from "../shared/format";
import { OeeRing } from "../shared/Charts";
import EntityForm from "../shared/EntityForm";
import Modal from "../shared/Modal";
import Telemetry from "./components/Telemetry";
import TankControl, { ModeBadge } from "./components/TankControl";
const states = {
  produzindo: ["Produzindo", "success", "bi-gear-wide-connected"],
  disponivel: ["Disponível", "primary", "bi-check-circle"],
  offline: ["Sem comunicação recente", "danger", "bi-wifi-off"],
  parada: ["Parada", "warning", "bi-pause-circle"],
  bloqueada: ["MES bloqueado", "secondary", "bi-lock-fill"],
};
export default function Plantas() {
  const { user } = useWorkspace();
  const { data, error, reload, act, loading } = useData(
    ["/api/plantas/"],
    2000,
  );
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(null);
  const [mode, setMode] = useState(null);
  const plants = data?.[0] || [];
  const selection = plants.find((item) => item.idplanta === selected);
  const close = () => {
    setMode(null);
    setSelected(null);
  };
  const total = plants.reduce(
    (sum, p) => sum + (p.painel?.quantidade_produzida || 0),
    0,
  );
  async function save(payload) {
    const response =
      mode === "edit"
        ? await api.patch(`/api/plantas/${selected}/`, payload)
        : await api.post("/api/plantas/", payload);
    await reload();
    return response;
  }
  return (
    <section className="mes-page">
      <PageHeader
        title="Plantas"
        description="Um olhar para saber como a operação está fluindo."
      >
        <div className="search-input">
          <i aria-hidden="true" className="bi bi-search" />
          <input
            aria-label="Buscar plantas"
            placeholder="Buscar planta…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </PageHeader>
      <div className="plant-summary">
        <div>
          <span>Volume produzido</span>
          <strong>
            {number(total)} <small>L</small>
          </strong>
        </div>
        <div>
          <span>Em produção</span>
          <strong>
            {plants.filter((p) => p.painel?.status === "produzindo").length}
            <small> / {plants.length} plantas</small>
          </strong>
        </div>
        <div>
          <i aria-hidden="true" className="bi bi-arrow-repeat" />
          <span>Visão atualizada automaticamente</span>
        </div>
      </div>
      <DataState loading={loading} error={error} reload={reload} />
      <div className="plant-grid">
        {plants
          .filter((p) =>
            `${p.nome} ${p.localizacao}`
              .toLowerCase()
              .includes(query.toLowerCase()),
          )
          .map((plant) => {
            const panel = plant.painel || {};
            const [label, tone, icon] =
              states[panel.status] || states.disponivel;
            const progress = panel.quantidade_planejada
              ? Math.min(
                  (panel.quantidade_produzida / panel.quantidade_planejada) *
                    100,
                  100,
                )
              : 0;
            return (
              <button
                className={`plant-card accent-${tone}`}
                key={plant.idplanta}
                onClick={() => {
                  setSelected(plant.idplanta);
                  setMode("detail");
                }}
              >
                <header className={`card-band bg-${tone}`}>
                  <span>
                    <i aria-hidden="true" className={`bi ${icon}`} />
                    {label}
                  </span>
                  <small>#{String(plant.idplanta).padStart(2, "0")}</small>
                </header>
                <div className="plant-card-content">
                  <div className="card-title-row">
                    <h2>{plant.nome}</h2>
                    <i aria-hidden="true" className="bi bi-arrow-up-right" />
                  </div>
                  <p className="muted">
                    <i aria-hidden="true" className="bi bi-geo-alt" />{" "}
                    {plant.localizacao}
                  </p>
                  {panel.controle && (
                    <p className="mode-row">
                      <ModeBadge control={panel.controle} />
                    </p>
                  )}
                  <div className="current-recipe">
                    <i aria-hidden="true" className="bi bi-droplet-half" />
                    <span>
                      {panel.receita ||
                        (panel.status === "bloqueada"
                          ? "Aguardando o modo 2 para o MES produzir"
                          : "Pronta para o próximo pedido")}
                    </span>
                  </div>
                  <div className="production-volume">
                    <span>
                      {number(panel.quantidade_produzida)} /{" "}
                      {number(panel.quantidade_planejada)}
                    </span>
                    <small>produzido / planejado</small>
                  </div>
                  <div className="mes-progress">
                    <span style={{ width: `${progress}%` }} />
                  </div>
                  <footer>
                    <OeeRing value={panel.oee} />
                    <div>
                      <span>Ciclos programados</span>
                      <strong>{panel.fila || 0}</strong>
                      <small>
                        {panel.oee_data
                          ? `OEE de ${panel.oee_data.split("-").reverse().join("/")}`
                          : "OEE aguardando medição"}
                      </small>
                    </div>
                  </footer>
                </div>
              </button>
            );
          })}
      </div>
      {data && !plants.length && (
        <Empty
          title="Sua primeira planta começa aqui"
          description="Cadastre uma planta para organizar a produção e acompanhar seus indicadores."
          icon="bi-cpu"
        />
      )}
      <AddButton
        label={user.role === 3 ? "Solicitar planta" : "Adicionar planta"}
        onClick={() => setMode("new")}
      />
      {(mode === "new" || mode === "edit") && (
        <EntityForm
          title={
            mode === "edit"
              ? "Editar planta"
              : user.role === 3
                ? "Solicitar nova planta"
                : "Adicionar planta"
          }
          fields={plantFields}
          initial={selection || {}}
          onSubmit={save}
          onClose={close}
          submitLabel={
            user.role === 3 ? "Enviar para aprovação" : "Salvar planta"
          }
        />
      )}
      {mode === "detail" && selection && (
        <Modal
          title={selection.nome}
          onClose={close}
          footer={
            user.role !== 3 && (
              <>
                <Button className="secondary" onClick={() => setMode("edit")}>
                  <i aria-hidden="true" className="bi bi-pencil" />
                  Editar
                </Button>
                <Button
                  className="ghost danger-text"
                  onClick={() => setMode("delete")}
                >
                  <i aria-hidden="true" className="bi bi-trash" />
                  Excluir
                </Button>
              </>
            )
          }
        >
          <Details
            items={[
              ["Localização", selection.localizacao],
              ["Capacidade útil", `${number(selection.capacidade_l)} L`],
              [
                "Reset entre receitas",
                `${number(selection.tempo_reset_seg)} s`,
              ],
              ["Status", states[selection.painel?.status]?.[0] || "Disponível"],
              ["Produzido", number(selection.painel?.quantidade_produzida)],
              ["OEE", percent(selection.painel?.oee)],
              ["Receita em produção", selection.painel?.receita],
              ["Ciclos programados", selection.painel?.fila || 0],
            ]}
          />
          <TankControl control={selection.painel?.controle} />
          <Telemetry plant={selection} />
        </Modal>
      )}
      {mode === "delete" && selection && (
        <Confirm
          description={`Excluir a planta ${selection.nome}? Plantas com pedidos não podem ser excluídas.`}
          onClose={close}
          onConfirm={async () => {
            if (
              await act(
                () => api.delete(`/api/plantas/${selected}/`),
                "Planta excluída.",
              )
            )
              close();
          }}
        />
      )}
    </section>
  );
}
