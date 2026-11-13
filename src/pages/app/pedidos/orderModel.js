export const types = {
  producao: ["Produção de líquido", "primary", "bi-droplet-half"],
  planta: ["Cadastro de planta", "warning", "bi-cpu"],
  receita: ["Cadastro de receita", "purple", "bi-flask"],
};
export function normalized(orders, requests) {
  return [
    ...orders.map((p) => ({
      ...p,
      key: `p${p.idpedido}`,
      id: p.idpedido,
      tipo: "producao",
      nome: p.receita_nome,
      autor_nome: p.usuario_nome,
      autor_cargo: p.usuario_cargo,
      estado:
        p.aprovacao === "reprovado"
          ? "reprovado"
          : p.status === "cancelado"
            ? "cancelado"
            : p.status === "em_andamento"
              ? "producao"
              : p.status === "concluido"
                ? "concluido"
                : p.aprovacao === "aprovado"
                  ? "fila"
                  : "aguardando",
      endpoint: "pedidos",
    })),
    ...requests.map((s) => ({
      ...s,
      key: `s${s.id}`,
      nome: s.dados.nome,
      estado: s.status === "aguardando" ? "aguardando" : s.status,
      endpoint: "solicitacoes",
    })),
  ].sort((a, b) => new Date(b.criado_em) - new Date(a.criado_em));
}
export const status = {
  aguardando: ["Aguardando aprovação", "warning"],
  fila: ["Produção programada", "primary"],
  producao: ["Em produção", "success"],
  concluido: ["Concluído", "success"],
  aprovado: ["Cadastro aprovado", "success"],
  reprovado: ["Recusado", "danger"],
  cancelado: ["Cancelado", "secondary"],
};
