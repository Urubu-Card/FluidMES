
import React, { useMemo } from "react";
import "./statusPedido.css";

/* ---------- Ícones simples em SVG (sem dependências externas) ---------- */

const IconBookmark = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M19 21 12 16 5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
  </svg>
);

const IconCalendar = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round" {...props}>
    <rect x="3" y="4" width="18" height="18" rx="2" />
    <path d="M16 2v4M8 2v4M3 10h18" />
  </svg>
);

const IconUser = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round" {...props}>
    <rect x="3" y="4" width="18" height="16" rx="2" />
    <circle cx="12" cy="10" r="2.5" />
    <path d="M7 17c1-2.5 3-3.5 5-3.5s4 1 5 3.5" />
  </svg>
);

const IconPhone = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.7a2 2 0 0 1-.5 2.1L8 9.7a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.5 2.7.6a2 2 0 0 1 1.7 2z" />
  </svg>
);

const IconPin = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z" />
    <circle cx="12" cy="10" r="3" />
  </svg>
);

/* ---------- Utilitário: gera a borda serrilhada (efeito de ticket) ---------- */

function useZigzagClipPath(teeth = 16, amplitude = 7) {
  return useMemo(() => {
    const step = 100 / teeth;
    const top = [];
    const bottom = [];
    for (let i = 0; i <= teeth; i++) {
      const x = (i * step).toFixed(3);
      const upDown = i % 2 === 0 ? 0 : amplitude;
      top.push(`${x}% ${upDown}px`);
    }
    for (let i = teeth; i >= 0; i--) {
      const x = (i * step).toFixed(3);
      const upDown = i % 2 === 0 ? 0 : amplitude;
      bottom.push(`${x}% calc(100% - ${upDown}px)`);
    }
    return `polygon(${top.join(",")}, ${bottom.join(",")})`;
  }, [teeth, amplitude]);
}

/* ---------- Componente principal ---------- */

export default function OrderCard({
  orderNumber = "95103",
  date = "29/05/2026",
  issuer = "Emissor do pedido",
  issuerPhone = "Telefone do Emissor",
  issuerAddress = "Endereço do Emissor",
  status = "Feito",
  requestedBy = "Bonie Fontes",
  approvedBy = "Jefferson Bastos",
  note = "Os líquidos devem ter a a qualidade independe do desempenho em disponibilidade",
  items = [
    { item: "Coca-Cola", qty: "9 Litros", completedAt: "09/06/2026", time: "10:59" },
  ],
  onClose,
}) {
  const clipPath = useZigzagClipPath(16, 7);

  return (
    <div className="oc-wrapper">
      <div className="oc-card" style={{ clipPath, WebkitClipPath: clipPath }}>
        {/* Cabeçalho */}
        <div className="oc-header">
          <div className="oc-header-item">
            <IconBookmark className="oc-icon" />
            <span className="oc-header-title">Pedido: #{orderNumber}</span>
          </div>
          <div className="oc-header-item">
            <IconCalendar className="oc-icon" />
            <span className="oc-header-title">{date}</span>
          </div>
        </div>

        <div className="oc-divider" />

        {/* Emissor */}
        <div className="oc-issuer-row">
          <div className="oc-issuer-info">
            <div className="oc-line">
              <IconUser className="oc-icon oc-icon-muted" />
              <span className="oc-pill">{issuer}</span>
            </div>
            <div className="oc-line">
              <IconPhone className="oc-icon oc-icon-muted" />
              <span className="oc-pill">{issuerPhone}</span>
            </div>
            <div className="oc-line">
              <IconPin className="oc-icon oc-icon-muted" />
              <span className="oc-pill">{issuerAddress}</span>
            </div>
          </div>
          <div className="oc-status-badge">{status}</div>
        </div>

        <div className="oc-divider" />

        {/* Pedido por / Aprovado por / Observação */}
        <div className="oc-columns">
          <div className="oc-col">
            <div className="oc-col-label">Pedido por :</div>
            <div className="oc-col-value">{requestedBy}</div>
          </div>
          <div className="oc-col">
            <div className="oc-col-label">Aprovado por :</div>
            <div className="oc-col-value">{approvedBy}</div>
          </div>
          <div className="oc-col oc-col-note">
            <div className="oc-col-label">Observação :</div>
            <div className="oc-col-value oc-note-text">{note}</div>
          </div>
        </div>

        <div className="oc-divider" />

        {/* Tabela de itens */}
        <div className="oc-table">
          <div className="oc-table-head">
            <span>ITEM</span>
            <span>QTD</span>
            <span>Data da Conclusão</span>
            <span>Hora</span>
          </div>
          {items.map((row, i) => (
            <div className="oc-table-row" key={i}>
              <span>{row.item}</span>
              <span>{row.qty}</span>
              <span>{row.completedAt}</span>
              <span>{row.time}</span>
            </div>
          ))}
        </div>

        <div className="oc-divider" />

        {/* Rodapé */}
        <div className="oc-footer">
          <button className="oc-close-btn" onClick={onClose}>
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}