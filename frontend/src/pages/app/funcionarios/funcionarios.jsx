import EntityList from "../shared/EntityList";
import { employeeFields } from "../shared/resources";
import { useWorkspace } from "../shared/context";
const roles = { 1: "Preposto", 2: "Chefe", 3: "Funcionário" };
export default function Funcionarios() {
  const { user } = useWorkspace();
  return (
    <EntityList
      title="Funcionários"
      description={
        user.role === 1
          ? "Pessoas que fazem a sua operação fluir."
          : "Conheça as pessoas da sua equipe."
      }
      endpoint="/api/funcionarios/"
      idField="id"
      fields={employeeFields}
      createLabel="Adicionar funcionário"
      canCreate={user.role === 1}
      canEdit={user.role === 1}
      renderRow={(item) => (
        <>
          <div className="entity-avatar">{item.first_name.charAt(0)}</div>
          <div className="row-main">
            <strong>
              {item.first_name} {item.last_name}
            </strong>
            <span>{item.email}</span>
          </div>
          <div className="row-secondary">
            <strong>{roles[item.role]}</strong>
            <span>{item.is_active ? "Conta ativa" : "Conta desativada"}</span>
          </div>
        </>
      )}
      details={(item) => [
        ["Nome", `${item.first_name} ${item.last_name}`],
        ["E-mail", item.email],
        ["CPF", item.cpf],
        ["Cargo", roles[item.role]],
        ["Situação", item.is_active ? "Ativo" : "Desativado"],
      ]}
    />
  );
}
