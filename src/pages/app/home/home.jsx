import { useState } from "react";
import { Link } from "react-router-dom";
import useData from "../shared/useData";
import { useWorkspace } from "../shared/context";
import { PageHeader, DataState } from "../shared/UI";
import { number } from "../shared/format";
import { BarChart, DonutChart } from "../shared/Charts";
export default function Home() {
  const { user } = useWorkspace();
  const { data, error, reload, loading } = useData(
    ["/api/pedidos/", "/api/solicitacoes/", "/api/plantas/"],
    2500,
  );
  const [period, setPeriod] = useState("todos");
  const [now] = useState(() => Date.now());
  const allOrders = data?.[0] || [];
  const allRequests = data?.[1] || [];
  const plants = data?.[2] || [];
  const inPeriod = (item) =>
    period === "todos" ||
    new Date(item.criado_em) >= new Date(now - Number(period) * 86400000);
  const orders = allOrders.filter(inPeriod);
  const requests = allRequests.filter(inPeriod);
  const approved =
    orders.filter((o) => o.aprovacao === "aprovado").length +
    requests.filter((s) => s.status === "aprovado").length;
  const refused =
    orders.filter((o) => o.aprovacao === "reprovado").length +
    requests.filter((s) => s.status === "reprovado").length;
  const pending =
    orders.filter((o) => o.aprovacao === "aguardando").length +
    requests.filter((s) => s.status === "aguardando").length;
  const recipes = Object.entries(
    orders.reduce(
      (result, item) => ({
        ...result,
        [item.receita_nome]: (result[item.receita_nome] || 0) + 1,
      }),
      {},
    ),
  )
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([label, value]) => ({ label, value }));
  const cards =
    user.role === 1
      ? [
          [
            "bi-cpu",
            "Plantas em produção",
            plants.filter((p) => p.painel?.status === "produzindo").length,
            "success",
          ],
          [
            "bi-droplet-half",
            "Quantidade produzida",
            number(
              orders
                .filter((o) => o.status === "concluido")
                .reduce((sum, o) => sum + o.quantidade, 0),
            ),
            "primary",
          ],
          ["bi-hourglass-split", "Aguardando decisão", pending, "warning"],
          [
            "bi-check2-circle",
            "Pedidos concluídos",
            orders.filter((o) => o.status === "concluido").length,
            "primary",
          ],
        ]
      : [
          [
            "bi-file-earmark",
            "Pedidos realizados",
            orders.length + requests.length,
            "primary",
          ],
          ["bi-check2-circle", "Aprovados", approved, "success"],
          ["bi-x-circle", "Recusados", refused, "danger"],
          ["bi-hourglass-split", "Aguardando aprovação", pending, "warning"],
        ];
  return (
    <section className="mes-page">
      <PageHeader
        eyebrow={`BEM-VINDO, ${user.first_name.toUpperCase()}`}
        title={
          user.role === 1
            ? "Visão geral"
            : user.role === 2
              ? "Sua operação, no ritmo certo"
              : "Seu trabalho flui aqui"
        }
        description={
          user.role === 1
            ? "Indicadores para decidir com clareza."
            : user.role === 2
              ? "O que precisa da sua atenção, sem perder o todo."
              : "Seus pedidos, suas receitas e seu progresso."
        }
      >
        <select
          aria-label="Período dos indicadores"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
        >
          <option value="todos">Todo o período</option>
          <option value="7">Últimos 7 dias</option>
          <option value="30">Últimos 30 dias</option>
        </select>
      </PageHeader>
      <DataState loading={loading} error={error} reload={reload} />
      {data && (
        <>
          <div className="metric-grid">
            {cards.map(([icon, label, value, tone]) => (
              <article className="metric-card" key={label}>
                <div className={`metric-symbol tone-${tone}`}>
                  <i aria-hidden="true" className={`bi ${icon}`} />
                </div>
                <span>{label}</span>
                <strong>{value}</strong>
              </article>
            ))}
          </div>
          <div className="dashboard-callout">
            <div>
              <span className="eyebrow">PRÓXIMO PASSO</span>
              <h2>
                {pending
                  ? `${pending} ${user.role === 3 ? "solicitações aguardando análise" : "pedidos precisam de uma decisão"}`
                  : "Tudo organizado para continuar"}
              </h2>
              <p>
                {user.role === 3
                  ? "Você acompanha o andamento de cada solicitação na tela de pedidos."
                  : "Organize as aprovações e acompanhe cada planta em tempo real."}
              </p>
            </div>
            <Link className="mes-button" to="/app/pedidos">
              {user.role === 3 ? "Ver meus pedidos" : "Acompanhar pedidos"}
              <i aria-hidden="true" className="bi bi-arrow-right" />
            </Link>
          </div>
          <div className="chart-grid">
            <DonutChart
              title={
                user.role === 3 ? "Minhas solicitações" : "Visão das aprovações"
              }
              items={[
                { label: "Aprovados", value: approved, color: "#198754" },
                { label: "Aguardando", value: pending, color: "#ffc107" },
                { label: "Recusados", value: refused, color: "#dc3545" },
              ]}
            />
            <BarChart
              title={
                user.role === 3
                  ? "As receitas que você mais pede"
                  : "Receitas mais solicitadas"
              }
              items={recipes}
            />
          </div>
          {user.role === 1 && (
            <BarChart
              title="Produção acumulada por planta"
              items={plants.map((p) => ({
                label: p.nome,
                value: p.painel?.quantidade_produzida || 0,
              }))}
            />
          )}
        </>
      )}
    </section>
  );
}
