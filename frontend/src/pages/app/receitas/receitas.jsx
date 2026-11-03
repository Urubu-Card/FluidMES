import EntityList from "../shared/EntityList";
import { useWorkspace } from "../shared/context";
import { number, duration } from "../shared/format";
import RecipeForm from "./components/RecipeForm";

export default function Receitas() {
  const { user } = useWorkspace();
  return (
    <EntityList
      title="Receitas"
      description="Composição e etapas claras para cada ciclo."
      endpoint="/api/receitas/"
      idField="idreceita"
      fields={[]}
      formComponent={RecipeForm}
      createLabel={user.role === 3 ? "Solicitar receita" : "Adicionar receita"}
      requestMode={user.role === 3}
      renderRow={(item) => (
        <>
          <div className="entity-avatar recipe-avatar">
            <i aria-hidden="true" className="bi bi-flask" />
          </div>
          <div className="row-main">
            <strong>{item.nome}</strong>
            <span>{item.componentes?.map((p) => p.nome).join(" · ")}</span>
          </div>
          <div className="row-secondary">
            <strong>{number(item.volume_base_l)} L</strong>
            <span>composição de referência</span>
          </div>
          <div className="row-secondary">
            <strong>{duration(item.tempo1 + item.tempo2)}</strong>
            <span>mistura por ciclo · v{item.versao}</span>
          </div>
        </>
      )}
      details={(item) => [
        ["Nome", item.nome],
        ["Versão da receita", item.versao],
        ["Composição de referência", `${number(item.volume_base_l)} L`],
        ...(item.componentes || []).map((p, i) => [
          `Dosagem ${i + 1}: ${p.nome}`,
          `${number(p.quantidade_l)} L · ${number(p.vazao_l_min)} L/min`,
        ]),
        ["Mistura após a dosagem 2", duration(item.tempo1)],
        ...(item.componentes?.length === 3
          ? [["Mistura após a dosagem 3", duration(item.tempo2)]]
          : []),
      ]}
    />
  );
}
