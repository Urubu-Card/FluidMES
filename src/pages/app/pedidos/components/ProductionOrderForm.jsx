import { useEffect, useState } from "react";
import api from "../../../../services/api";
import FormModal from "../../shared/FormModal";
import Field from "../../shared/controls/Field";
import Button from "../../shared/controls/Button";
import BatchPlan from "./BatchPlan";
import { errorMessage } from "../../../../services/errors";

export default function ProductionOrderForm({
  title,
  initial = {},
  onSubmit,
  onClose,
  submitLabel = "Salvar pedido",
}) {
  const [values, setValues] = useState({
    receita: initial.receita || "",
    planta: initial.planta_preferida || "",
    quantidade: initial.quantidade || "",
    prazo: initial.prazo || "",
    pedidocol: initial.pedidocol || "",
  });
  const [choices, setChoices] = useState(null);
  const [error, setError] = useState("");
  const [plan, setPlan] = useState(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let active = true;
    Promise.all([api.get("/api/receitas/"), api.get("/api/plantas/")])
      .then(([recipes, plants]) => {
        if (active) setChoices({ recipes: recipes.data, plants: plants.data });
      })
      .catch((e) => {
        if (active) setError(errorMessage(e));
      });
    return () => {
      active = false;
    };
  }, []);
  const update = (key) => (value) => {
    setValues((old) => ({ ...old, [key]: value }));
    setPlan(null);
    setError("");
  };
  const payload = () => ({
    ...values,
    receita: Number(values.receita),
    planta: values.planta ? Number(values.planta) : null,
    quantidade: Number(values.quantidade),
  });
  async function preview() {
    setBusy(true);
    setError("");
    try {
      setPlan((await api.post("/api/pedidos/prever/", payload())).data);
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <FormModal
      title={title}
      onClose={onClose}
      submitLabel={submitLabel}
      disabled={!choices || busy}
      onSubmit={() => onSubmit(payload())}
    >
      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}
      <Field
        label="Receita"
        value={values.receita}
        onChange={update("receita")}
        required
        options={(choices?.recipes || []).map((r) => [r.idreceita, r.nome])}
      />
      <Field
        label="Planta de preferência"
        value={values.planta}
        onChange={update("planta")}
        emptyLabel="Seleção automática"
        options={(choices?.plants || []).map((p) => [
          p.idplanta,
          `${p.nome} · ${p.capacidade_l} L`,
        ])}
        hint="Preferência usada em caso de empate. O pedido pode ser dividido para terminar antes."
      />
      <Field
        label="Quantidade a produzir (L)"
        type="number"
        required
        min={0.01}
        max={1000000}
        value={values.quantidade}
        onChange={update("quantidade")}
      />
      <Field
        label="Prazo"
        type="date"
        required
        value={values.prazo}
        onChange={update("prazo")}
      />
      <Field
        label="Observação"
        maxLength={45}
        value={values.pedidocol}
        onChange={update("pedidocol")}
      />
      <Button
        variant="secondary"
        disabled={
          busy || !values.receita || !values.quantidade || !values.prazo
        }
        onClick={preview}
        icon="bi-diagram-3"
      >
        {busy ? "Calculando…" : "Calcular melhor distribuição"}
      </Button>
      {plan && <BatchPlan plan={plan} lots={plan.lotes} />}
    </FormModal>
  );
}
