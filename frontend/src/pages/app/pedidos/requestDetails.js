import { number, duration } from "../shared/format";
export function requestDetails(data) {
  const rows = [["Nome", data.nome]];
  if (data.componentes?.length) {
    for (const [i, part] of data.componentes.entries())
      rows.push([
        `Dosagem ${i + 1}: ${part.nome}`,
        `${number(part.quantidade_l)} L · ${number(part.vazao_l_min)} L/min`,
      ]);
    rows.push(["Mistura 1", duration(data.tempo1)]);
    if (data.componentes.length === 3)
      rows.push(["Mistura 2", duration(data.tempo2)]);
  } else {
    const labels = {
      localizacao: "Localização",
      capacidade_l: "Capacidade útil (L)",
      tempo_reset_seg: "Reset entre receitas (s)",
      ingrediente1: "Ingrediente 1",
      ingrediente2: "Ingrediente 2",
      ingrediente3: "Ingrediente 3",
      tempo1: "Mistura 1 (s)",
      tempo2: "Mistura 2 (s)",
    };
    for (const [key, label] of Object.entries(labels))
      if (data[key] != null) rows.push([label, String(data[key])]);
  }
  return rows;
}
