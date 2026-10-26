import useData from "../shared/useData";
import { PageHeader, DataState, Empty } from "../shared/UI";
import { percent } from "../shared/format";
import { BarChart } from "../shared/Charts";
export default function Rendimentos() {
  const { data, error, reload, loading } = useData(["/api/rendimentos/"], 5000);
  const rows = data?.[0] || [];
  return (
    <section className="mes-page">
      <PageHeader
        title="Rendimentos"
        description="Disponibilidade, performance e qualidade para orientar suas decisões."
      />
      <DataState loading={loading} error={error} reload={reload} />
      {data &&
        (rows.length ? (
          <>
            <BarChart
              title="OEE por registro diário"
              items={rows.slice(0, 8).map((item) => ({
                label: `${item.planta_nome} · ${item.data.split("-").reverse().join("/")}`,
                value: Number((item.oee * 100).toFixed(1)),
              }))}
              suffix="%"
            />
            <div className="oee-record-grid">
              {rows.map((item) => (
                <article className="chart-panel" key={item.idoeeregistro}>
                  <h2>{item.planta_nome}</h2>
                  <p className="muted">
                    {item.data.split("-").reverse().join("/")}
                  </p>
                  <dl className="detail-grid">
                    {["disponibilidade", "performance", "qualidade", "oee"].map(
                      (key) => (
                        <div key={key}>
                          <dt>
                            {key === "oee"
                              ? "OEE"
                              : key.charAt(0).toUpperCase() + key.slice(1)}
                          </dt>
                          <dd>{percent(item[key])}</dd>
                        </div>
                      ),
                    )}
                  </dl>
                </article>
              ))}
            </div>
          </>
        ) : (
          <Empty
            title="Os primeiros indicadores estão a caminho"
            description="Os registros de OEE serão exibidos após a primeira produção concluída ou o cálculo diário."
            icon="bi-graph-up-arrow"
          />
        ))}
    </section>
  );
}
