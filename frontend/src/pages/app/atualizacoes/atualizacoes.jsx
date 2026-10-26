import Button from "../shared/controls/Button.jsx";
import { useState } from "react";
import useData from "../shared/useData";
import { PageHeader, DataState, Empty } from "../shared/UI";
import { dateTime } from "../shared/format";
export default function Atualizacoes() {
  const [offset, setOffset] = useState(0);
  const { data, error, reload, loading } = useData(
    [`/api/atualizacoes/?limit=30&offset=${offset}`],
    5000,
  );
  const page = data?.[0];
  return (
    <section className="mes-page">
      <PageHeader
        title="Últimas atualizações"
        description="O que mudou na sua empresa, com autoria e contexto. Suas próprias ações não aparecem aqui."
      />
      <DataState loading={loading} error={error} reload={reload} />
      {page && (
        <>
          <div className="activity-list">
            {page.results.map((item) => (
              <article className="activity-item" key={item.id}>
                <div
                  className={`activity-icon ${item.acao === "excluiu" ? "danger-text" : ""}`}
                >
                  <i
                    aria-hidden="true"
                    className={`bi ${item.acao === "excluiu" ? "bi-trash" : item.acao === "editou" ? "bi-pencil" : item.acao === "recusou" ? "bi-x-circle" : "bi-check2-circle"}`}
                  />
                </div>
                <div>
                  <p>
                    <strong>{item.autor_nome}</strong> {item.acao}{" "}
                    <strong>{item.recurso}</strong>
                  </p>
                  <p className="muted">{item.descricao}</p>
                  <small>
                    {item.autor_cargo} · {dateTime(item.criado_em)}
                  </small>
                </div>
              </article>
            ))}
          </div>
          {!page.results.length && (
            <Empty
              title="Nenhuma atualização por enquanto"
              description="As ações de outras pessoas da equipe aparecerão aqui."
            />
          )}
          <div className="pagination-controls">
            <Button
              className="secondary"
              disabled={!page.previous}
              onClick={() => setOffset(Math.max(0, offset - 30))}
            >
              Anterior
            </Button>
            <span>{page.count} atualizações</span>
            <Button
              className="secondary"
              disabled={!page.next}
              onClick={() => setOffset(offset + 30)}
            >
              Próxima
            </Button>
          </div>
        </>
      )}
    </section>
  );
}
