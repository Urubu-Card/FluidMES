import { useId, useState } from "react";
const palette = ["#3e7dff", "#198754", "#ffc107", "#dc3545", "#6f42c1"];
export function DonutChart({ title, items }) {
  const [active, setActive] = useState(null);
  const total = items.reduce((sum, item) => sum + item.value, 0);
  return (
    <article className="chart-panel">
      <h2>{title}</h2>
      <div className="donut-layout">
        <svg
          viewBox="0 0 160 160"
          role="img"
          aria-label={`${title}: ${total} registros`}
        >
          <circle
            cx="80"
            cy="80"
            r="57"
            className="chart-track"
            strokeWidth="17"
            fill="none"
          />
          {items.map((item, index) => {
            const size = total ? (item.value / total) * 358.14 : 0;
            const at = total
              ? (items
                  .slice(0, index)
                  .reduce((sum, entry) => sum + entry.value, 0) /
                  total) *
                358.14
              : 0;
            return (
              <circle
                key={item.label}
                cx="80"
                cy="80"
                r="57"
                stroke={item.color || palette[index % palette.length]}
                strokeWidth={active === index ? 22 : 17}
                strokeDasharray={`${size} ${358.14 - size}`}
                strokeDashoffset={-at}
                transform="rotate(-90 80 80)"
                fill="none"
                tabIndex={0}
                onFocus={() => setActive(index)}
                onBlur={() => setActive(null)}
                onMouseEnter={() => setActive(index)}
                onMouseLeave={() => setActive(null)}
                aria-label={`${item.label}: ${item.value}`}
              >
                <title>
                  {item.label}: {item.value} (
                  {total ? Math.round((item.value / total) * 100) : 0}%)
                </title>
              </circle>
            );
          })}
          <text x="80" y="78" textAnchor="middle" className="chart-number">
            {active === null ? total : items[active].value}
          </text>
          <text x="80" y="99" textAnchor="middle" className="chart-caption">
            {active === null
              ? "pedidos"
              : `${total ? Math.round((items[active].value / total) * 100) : 0}% do total`}
          </text>
        </svg>
        <ul className="chart-legend">
          {items.map((item, index) => (
            <li key={item.label}>
              <button
                onMouseEnter={() => setActive(index)}
                onMouseLeave={() => setActive(null)}
                onFocus={() => setActive(index)}
                onBlur={() => setActive(null)}
              >
                <i
                  aria-hidden="true"
                  style={{ background: palette[index % palette.length] }}
                />
                {item.label}
                <strong>{item.value}</strong>
              </button>
            </li>
          ))}
        </ul>
      </div>
      {!total && (
        <p className="muted">Seu gráfico começa com o primeiro pedido.</p>
      )}
    </article>
  );
}
export function BarChart({ title, items, suffix = "" }) {
  const id = useId();
  const [active, setActive] = useState(null);
  const maximum = Math.max(1, ...items.map((item) => item.value));
  return (
    <article className="chart-panel">
      <h2 id={id}>{title}</h2>
      <div className="bar-chart" role="group" aria-labelledby={id}>
        {items.length ? (
          items.map((item, index) => (
            <button
              key={item.label}
              className="bar-row"
              onMouseEnter={() => setActive(index)}
              onMouseLeave={() => setActive(null)}
              onFocus={() => setActive(index)}
              onBlur={() => setActive(null)}
              aria-label={`${item.label}: ${item.value}${suffix}`}
            >
              <span className="bar-name">{item.label}</span>
              <span className="bar-track">
                <span
                  style={{
                    width: `${(item.value / maximum) * 100}%`,
                    background: item.color || palette[index % palette.length],
                  }}
                />
              </span>
              <strong>
                {item.value}
                {suffix}
              </strong>
              {active === index && (
                <span className="chart-tooltip" role="tooltip">
                  {item.label}: {item.value}
                  {suffix}
                </span>
              )}
            </button>
          ))
        ) : (
          <p className="muted">Ainda não há dados para comparar.</p>
        )}
      </div>
    </article>
  );
}
export function OeeRing({ value }) {
  return (
    <div
      className="oee-ring"
      style={{
        "--oee": `${value == null ? 0 : Math.max(0, Math.min(value * 100, 100))}%`,
      }}
      aria-label={
        value == null ? "OEE sem medição" : `OEE ${(value * 100).toFixed(1)}%`
      }
    >
      <div>
        <strong>
          {value == null
            ? "—"
            : `${(value * 100).toFixed(1).replace(".", ",")}%`}
        </strong>
        <small>OEE</small>
      </div>
    </div>
  );
}
