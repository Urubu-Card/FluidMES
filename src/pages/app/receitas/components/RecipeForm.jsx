import { useState } from "react";
import FormModal from "../../shared/FormModal";
import Field from "../../shared/controls/Field";
import { number } from "../../shared/format";
const blank = () => ({ nome: "", quantidade_l: "", vazao_l_min: 30 });

export default function RecipeForm({
  title,
  initial = {},
  onSubmit,
  onClose,
  submitLabel,
}) {
  const [name, setName] = useState(initial.nome || "");
  const [parts, setParts] = useState(() => {
    const saved = (initial.componentes || []).map((p) => ({ ...p }));
    while (saved.length < 2) saved.push(blank());
    return saved.slice(0, 3);
  });
  const [mix1, setMix1] = useState(initial.tempo1 ?? 60);
  const [mix2, setMix2] = useState(initial.tempo2 ?? 60);
  const update = (index, key, value) =>
    setParts((old) =>
      old.map((p, i) => (i === index ? { ...p, [key]: value } : p)),
    );
  const base = parts.reduce((sum, p) => sum + Number(p.quantidade_l || 0), 0);
  const ingredient = (part, index) => (
    <section className="recipe-ingredient" key={index}>
      <h3>
        {index === 2 ? "Após a primeira mistura" : `Dosagem ${index + 1}`}
      </h3>
      <Field
        label={`Nome do ingrediente ${index + 1}`}
        required
        maxLength={80}
        value={part.nome}
        onChange={(v) => update(index, "nome", v)}
      />
      <div className="form-columns">
        <Field
          label={`Quantidade do ingrediente ${index + 1} (L)`}
          type="number"
          required
          min={0.000001}
          max={1000000}
          value={part.quantidade_l}
          onChange={(v) => update(index, "quantidade_l", v)}
        />
        <Field
          label={`Vazão do ingrediente ${index + 1} (L/min)`}
          type="number"
          required
          min={0.000001}
          max={100000}
          value={part.vazao_l_min}
          onChange={(v) => update(index, "vazao_l_min", v)}
        />
      </div>
    </section>
  );
  return (
    <FormModal
      title={title}
      onClose={onClose}
      submitLabel={submitLabel}
      onSubmit={() =>
        onSubmit({
          nome: name,
          componentes: parts.map((p) => ({
            ...p,
            quantidade_l: Number(p.quantidade_l),
            vazao_l_min: Number(p.vazao_l_min),
          })),
          tempo1: Number(mix1),
          tempo2: parts.length === 3 ? Number(mix2) : 0,
        })
      }
    >
      <Field
        label="Nome da receita"
        value={name}
        onChange={setName}
        required
        maxLength={45}
      />
      <Field
        label="Quantidade de ingredientes"
        value={String(parts.length)}
        emptyLabel={null}
        options={[
          ["2", "2 ingredientes"],
          ["3", "3 ingredientes"],
        ]}
        onChange={(v) =>
          setParts((old) =>
            Number(v) === 3 ? [...old, blank()] : old.slice(0, 2),
          )
        }
      />
      <p className="info-note">
        Defina a composição de referência em litros. O sistema mantém essas
        proporções em cada ciclo. Vazão inicial de 30 L/min é um exemplo
        ajustável; informe a vazão medida no equipamento.
      </p>
      {ingredient(parts[0], 0)}
      {ingredient(parts[1], 1)}
      <Field
        label="Tempo da mistura 1 (s)"
        type="number"
        required
        min={0}
        max={86400}
        value={mix1}
        onChange={setMix1}
        hint="Duração fixa por ciclo, independentemente do volume do tanque."
      />
      {parts.length === 3 && (
        <>
          {ingredient(parts[2], 2)}
          <Field
            label="Tempo da mistura 2 (s)"
            type="number"
            required
            min={0}
            max={86400}
            value={mix2}
            onChange={setMix2}
            hint="O terceiro ingrediente é dosado antes desta mistura."
          />
        </>
      )}
      <p className="info-note">
        Composição de referência: <strong>{number(base)} L</strong>. O tempo
        total inclui dosagens e misturas; repetir a mesma versão da receita
        dispensa o reset no modelo de simulação.
      </p>
    </FormModal>
  );
}
