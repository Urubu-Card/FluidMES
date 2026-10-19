import Button from "./controls/Button.jsx";
import { useState } from "react";
import api from "../../../services/api";
import useData from "./useData";
import { useWorkspace } from "./context";
import {
  AddButton,
  Confirm,
  DataState,
  Details,
  Empty,
  PageHeader,
} from "./UI";
import Modal from "./Modal";
import EntityForm from "./EntityForm";
export default function EntityList({
  title,
  description,
  endpoint,
  idField,
  fields,
  renderRow,
  details,
  canCreate = true,
  canEdit = true,
  canDelete = true,
  createLabel = "Adicionar",
  requestMode = false,
  formComponent = EntityForm,
  renderDetailExtra,
  refreshInterval = 0,
  renderOverview,
}) {
  const FormComponent = formComponent;
  const { data, error, reload, loading, act } = useData([endpoint], refreshInterval);
  const { user } = useWorkspace();
  const [query, setQuery] = useState("");
  const [selection, setSelection] = useState(null);
  const [mode, setMode] = useState(null);
  const items = data?.[0] || [];
  const current = items.find((item) => item[idField] === selection?.[idField]) || selection;
  const rows = items.filter((item) =>
    JSON.stringify(item).toLowerCase().includes(query.toLowerCase()),
  );
  const allowed = canEdit && (user.role === 1 || user.role === 2);
  const close = () => {
    setSelection(null);
    setMode(null);
  };
  async function save(payload) {
    const response = await (mode === "edit"
      ? api.patch(`${endpoint}${selection[idField]}/`, payload)
      : api.post(endpoint, payload));
    await reload();
    return response;
  }
  return (
    <section className="mes-page">
      <PageHeader title={title} description={description}>
        <div className="search-input">
          <i aria-hidden="true" className="bi bi-search" />
          <input
            aria-label={`Buscar em ${title}`}
            placeholder="Buscar…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </PageHeader>
      <DataState loading={loading} error={error} reload={reload} />
      {data && renderOverview?.(rows)}
      {data && (
        <div className="entity-list">
          {rows.length ? (
            rows.map((item) => (
              <button
                className="entity-row"
                key={item[idField]}
                onClick={() => {
                  setSelection(item);
                  setMode("detail");
                }}
              >
                {renderRow(item)}
                <i
                  aria-hidden="true"
                  className="bi bi-chevron-right row-chevron"
                />
              </button>
            ))
          ) : (
            <Empty
              title="Nenhum registro encontrado"
              description="Use o botão + para começar ou ajuste sua busca."
            />
          )}
        </div>
      )}
      {canCreate && (
        <AddButton label={createLabel} onClick={() => setMode("new")} />
      )}
      {(mode === "new" || mode === "edit") && (
        <FormComponent
          title={
            mode === "edit" ? `Editar ${title.toLowerCase()}` : createLabel
          }
          fields={fields}
          initial={mode === "edit" ? selection : {}}
          onClose={close}
          onSubmit={save}
          submitLabel={requestMode ? "Enviar para aprovação" : "Salvar"}
        />
      )}
      {mode === "detail" && current && (
        <Modal
          title={
            current.nome || `${current.first_name} ${current.last_name}`
          }
          onClose={close}
          footer={
            allowed && (
              <>
                <Button className="secondary" onClick={() => { setSelection(current); setMode("edit"); }}>
                  <i aria-hidden="true" className="bi bi-pencil" />
                  Editar
                </Button>
                {canDelete && (
                  <Button
                    className="ghost danger-text"
                    onClick={() => setMode("delete")}
                  >
                    <i aria-hidden="true" className="bi bi-trash" />
                    Excluir
                  </Button>
                )}
              </>
            )
          }
        >
          <Details items={details(current)} />
          {renderDetailExtra?.(current, reload)}
          {requestMode && (
            <p className="info-note">
              Você pode consultar este registro. Novos cadastros são enviados
              para aprovação.
            </p>
          )}
        </Modal>
      )}
      {mode === "delete" && (
        <Confirm
          description={`Excluir ${selection.nome || selection.first_name}? Esta ação não pode ser desfeita.`}
          onClose={close}
          onConfirm={async () => {
            if (
              await act(
                () => api.delete(`${endpoint}${selection[idField]}/`),
                "Registro excluído.",
              )
            )
              close();
          }}
        />
      )}
    </section>
  );
}
