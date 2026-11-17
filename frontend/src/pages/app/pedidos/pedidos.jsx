import { types, normalized, status } from "./orderModel";
import OrderProgress from "./components/OrderProgress";
import { requestDetails } from "./requestDetails";
import Button from "../shared/controls/Button.jsx";
import { useState } from "react";
import api from "../../../services/api";
import useData from "../shared/useData";
import { useWorkspace } from "../shared/context";
import {
  AddButton,
  DataState,
  Details,
  Empty,
  PageHeader,
  StatusBadge,
  Confirm,
} from "../shared/UI";
import { dateTime, number } from "../shared/format";
import Modal from "../shared/Modal";
import ProductionOrderForm from "./components/ProductionOrderForm";
import OrderExecution from "./components/OrderExecution";
export default function Pedidos() {
  const { user } = useWorkspace();
  const { data, error, reload, loading, act } = useData(
    ["/api/pedidos/", "/api/solicitacoes/"],
    1500,
  );
  const [tab, setTab] = useState("ativos");
  const [kind, setKind] = useState("todos");
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(null);
  const [create, setCreate] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [busy, setBusy] = useState(null);
  const all = normalized(data?.[0] || [], data?.[1] || []);
  const current = all.find((item) => item.key === selected);
  const active = (item) =>
    ["aguardando", "fila", "producao"].includes(item.estado);
  const filtered = all.filter(
    (item) =>
      (tab === "ativos" ? active(item) : !active(item)) &&
      (kind === "todos" || item.tipo === kind) &&
      `${item.nome} ${item.autor_nome} ${item.id}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  async function decide(item, approved) {
    setBusy(item.key);
    try {
      await act(
        () =>
          api.post(
            `/api/${item.endpoint}/${item.id}/${approved ? "aprovar" : "recusar"}/`,
          ),
        approved ? "Pedido aprovado." : "Pedido recusado.",
      );
    } finally {
      setBusy(null);
    }
  }
  function actions(item) {
    return user.role !== 3 && item.estado === "aguardando" ? (
      <div className="order-actions">
        <Button
          className="secondary"
          disabled={busy === item.key}
          onClick={(e) => {
            e.stopPropagation();
            decide(item, false);
          }}
        >
          <i aria-hidden="true" className="bi bi-x-lg" />
          Recusar
        </Button>
        <Button
          disabled={busy === item.key}
          onClick={(e) => {
            e.stopPropagation();
            decide(item, true);
          }}
        >
          <i aria-hidden="true" className="bi bi-check-lg" />
          Aprovar
        </Button>
      </div>
    ) : null;
  }
  return (
    <section className="mes-page">
      <PageHeader
        title={user.role === 3 ? "Meus pedidos" : "Pedidos"}
        description={
          user.role === 3
            ? "Acompanhe suas solicitações, da ideia à conclusão."
            : "Aprovações claras. Produção em movimento."
        }
      >
        <div className="search-input">
          <i aria-hidden="true" className="bi bi-search" />
          <input
            aria-label="Buscar pedidos"
            placeholder="Buscar pedido…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </PageHeader>
      <div className="overview-strip">
        <div>
          <strong>{all.filter((i) => i.estado === "aguardando").length}</strong>
          <span>Aguardando aprovação</span>
        </div>
        <div>
          <strong>{all.filter((i) => i.estado === "producao").length}</strong>
          <span>Em produção</span>
        </div>
        <div>
          <strong>
            {
              all.filter((i) => ["concluido", "aprovado"].includes(i.estado))
                .length
            }
          </strong>
          <span>Concluídos / aprovados</span>
        </div>
      </div>
      <div className="filter-toolbar">
        <div className="segmented">
          <button
            className={tab === "ativos" ? "active" : ""}
            onClick={() => setTab("ativos")}
          >
            Ativos <small>{all.filter(active).length}</small>
          </button>
          <button
            className={tab === "historico" ? "active" : ""}
            onClick={() => setTab("historico")}
          >
            Histórico
          </button>
        </div>
        <select
          aria-label="Filtrar tipo de pedido"
          value={kind}
          onChange={(e) => setKind(e.target.value)}
        >
          <option value="todos">Todos os tipos</option>
          {Object.entries(types).map(([key, [label]]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>
      </div>
      <DataState loading={loading} error={error} reload={reload} />
      <div className="order-grid">
        {filtered.map((item) => {
          const [typeLabel, typeTone, icon] = types[item.tipo];
          const [label, tone] = status[item.estado] || status.cancelado;
          return (
            <article key={item.key} className="order-card">
              <button
                className="order-card-open"
                onClick={() => setSelected(item.key)}
                aria-label={`Ver pedido ${item.id}: ${item.nome}`}
              >
                <header
                  className={`card-band bg-${user.role === 3 ? tone : typeTone}`}
                >
                  <span>
                    <i aria-hidden="true" className={`bi ${icon}`} />
                    {user.role === 3 ? label : typeLabel}
                  </span>
                  <small>#{item.id}</small>
                </header>
                <div className="order-card-content">
                  <div className="card-title-row">
                    <h2>{item.nome}</h2>
                    <i aria-hidden="true" className="bi bi-arrow-up-right" />
                  </div>
                  <StatusBadge label={label} tone={tone} />
                  <p className="muted order-author">
                    <i aria-hidden="true" className="bi bi-person" />{" "}
                    {item.autor_nome} · {item.autor_cargo}
                  </p>
                  {item.tipo === "producao" ? (
                    <div className="order-meta">
                      <div>
                        <small>Quantidade (L)</small>
                        <strong>{number(item.quantidade)}</strong>
                      </div>
                      <div>
                        <small>Tanques</small>
                        <strong>
                          {item.plano?.plantas?.join(", ") || item.planta_nome}
                        </strong>
                      </div>
                      <div>
                        <small>Prazo</small>
                        <strong>
                          {item.prazo?.split("-").reverse().join("/")}
                        </strong>
                      </div>
                    </div>
                  ) : (
                    <p className="muted">
                      {item.tipo === "planta"
                        ? item.dados.localizacao
                        : "Nova composição para a operação."}
                    </p>
                  )}
                  {item.plano?.previsao_conclusao && (
                    <p className="order-estimate">
                      <small>
                        {item.em_pausa
                          ? "Previsão pausada"
                          : "Conclusão estimada"}
                      </small>
                      <strong>
                        {item.em_pausa
                          ? "Aguardando liberação"
                          : dateTime(item.plano.previsao_conclusao)}
                      </strong>
                      <span>
                        {item.plano.lotes_qtd} ciclos · {item.plano.plantas_qtd}{" "}
                        tanques
                      </span>
                    </p>
                  )}
                  {!item.plano?.previsao_conclusao && (
                    <OrderProgress order={item} />
                  )}
                  <p className="order-date">{dateTime(item.criado_em)}</p>
                </div>
              </button>
              {actions(item)}
            </article>
          );
        })}
      </div>
      {data && !filtered.length && (
        <Empty
          title={
            tab === "ativos"
              ? "Tudo em dia por aqui"
              : "Seu histórico começa aqui"
          }
          description={
            tab === "ativos"
              ? "Novos pedidos aparecerão neste espaço."
              : "Pedidos concluídos e solicitações analisadas ficam disponíveis neste filtro."
          }
        />
      )}
      <AddButton
        label="Novo pedido de produção"
        onClick={() => setCreate(true)}
      />
      {create && (
        <ProductionOrderForm
          title="Novo pedido de produção"
          submitLabel={
            user.role === 3 ? "Enviar para aprovação" : "Confirmar programação"
          }
          onClose={() => setCreate(false)}
          onSubmit={async (payload) => {
            const response = await api.post("/api/pedidos/", payload);
            await reload();
            return response;
          }}
        />
      )}
      {current && (
        <Modal
          title={`Pedido #${current.id} · ${current.nome}`}
          onClose={() => setSelected(null)}
          footer={
            <>
              {actions(current)}
              {user.role === 1 &&
                current.tipo === "producao" &&
                current.estado === "aguardando" && (
                  <>
                    <Button
                      className="secondary"
                      onClick={() => {
                        setEditing(current);
                        setSelected(null);
                      }}
                    >
                      Editar
                    </Button>
                    <Button
                      className="ghost danger-text"
                      onClick={() => {
                        setDeleting(current);
                        setSelected(null);
                      }}
                    >
                      Excluir
                    </Button>
                  </>
                )}
            </>
          }
        >
          <StatusBadge
            label={status[current.estado]?.[0] || current.estado}
            tone={status[current.estado]?.[1]}
          />
          <Details
            items={[
              ["Tipo", types[current.tipo][0]],
              ["Solicitante", current.autor_nome],
              ["Cargo", current.autor_cargo],
              ["Criado em", dateTime(current.criado_em)],
              ...(current.tipo === "producao"
                ? [
                    [
                      "Planta de preferência",
                      current.planta_preferida_nome || "Seleção automática",
                    ],
                    [
                      "Tanques programados",
                      current.plano?.plantas?.join(", ") || current.planta_nome,
                    ],
                    ["Quantidade", `${number(current.quantidade)} L`],
                    ["Observação", current.pedidocol],
                    ["Início", dateTime(current.iniciado_em)],
                    ["Conclusão", dateTime(current.concluido_em)],
                  ]
                : requestDetails(current.dados)),
            ]}
          />
          {current.tipo === "producao" && <OrderExecution id={current.id} />}
          {!current.plano?.previsao_conclusao && (
            <OrderProgress order={current} />
          )}
        </Modal>
      )}
      {editing && (
        <ProductionOrderForm
          title={`Editar pedido #${editing.id}`}
          initial={editing}
          onClose={() => setEditing(null)}
          onSubmit={async (payload) => {
            const response = await api.patch(
              `/api/pedidos/${editing.id}/`,
              payload,
            );
            await reload();
            return response;
          }}
        />
      )}
      {deleting && (
        <Confirm
          description={`Excluir o pedido #${deleting.id}?`}
          onClose={() => setDeleting(null)}
          onConfirm={async () => {
            if (
              await act(
                () => api.delete(`/api/pedidos/${deleting.id}/`),
                "Pedido excluído.",
              )
            )
              setDeleting(null);
          }}
        />
      )}
    </section>
  );
}
