import { useEffect, useState } from "react";
import api from "../../../services/api";
import FormModal from "./FormModal";
import Field from "./controls/Field";
import { errorMessage } from "../../../services/errors";

export default function EntityForm({
  title,
  fields,
  initial = {},
  onClose,
  onSubmit,
  submitLabel = "Salvar",
}) {
  const [values, setValues] = useState(() =>
    Object.fromEntries(
      fields.map((field) => [
        field.name,
        (field.type === "datetime-local" && initial[field.name]
          ? new Date(
              new Date(initial[field.name]).getTime() -
                new Date(initial[field.name]).getTimezoneOffset() * 60000,
            )
              .toISOString()
              .slice(0, 16)
          : initial[field.name]) ??
          field.default ??
          (field.type === "checkbox" ? false : ""),
      ]),
    ),
  );
  const [choices, setChoices] = useState({});
  const [loading, setLoading] = useState(fields.some((f) => f.source));
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    Promise.all(
      fields
        .filter((f) => f.source)
        .map(async (field) => [field.name, (await api.get(field.source)).data]),
    )
      .then((result) => {
        if (active) setChoices(Object.fromEntries(result));
      })
      .catch((err) => {
        if (active) setError(errorMessage(err));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [fields]);
  const payload = () =>
    Object.fromEntries(
      fields
        .filter((f) => !(f.type === "password" && !values[f.name]))
        .map((field) => {
          let value = values[field.name];
          if (field.type === "number" || field.source)
            value = value === "" ? null : Number(value);
          if (field.type === "datetime-local")
            value = value ? new Date(value).toISOString() : null;
          return [field.name, value];
        }),
    );
  return (
    <FormModal
      title={title}
      onClose={onClose}
      submitLabel={submitLabel}
      disabled={loading || Boolean(error)}
      onSubmit={() => onSubmit(payload())}
    >
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      {fields.map((field) => {
        const options = field.optionsBy
          ? Object.entries(field.optionsBy[values[field.dependsOn]] || {})
          : field.options ||
            (field.source
              ? (choices[field.name] || []).map((item) => [item[field.key], item.nome])
              : null);
        const current = values[field.name];
        if (field.optionsBy && current && !options.some(([key]) => key === current)) {
          options.push([current, `${current} (unidade cadastrada)`]);
        }
        return (
          <Field
            key={field.name}
            label={field.label}
            type={field.type || "text"}
            value={values[field.name]}
            onChange={(value) =>
              setValues((old) => {
                const next = { ...old, [field.name]: value };
                for (const dependent of fields.filter((item) => item.dependsOn === field.name)) {
                  next[dependent.name] = "";
                }
                return next;
              })
            }
            options={options}
            emptyLabel={field.emptyLabel || "Selecione…"}
            min={field.min}
            max={field.max}
            maxLength={field.maxLength}
            hint={field.hint}
            disabled={loading || Boolean(field.dependsOn && !values[field.dependsOn])}
            required={
              field.type !== "checkbox" &&
              field.required !== false &&
              !(field.type === "password" && initial.id)
            }
            autoComplete={field.type === "password" ? "new-password" : undefined}
          />
        );
      })}
    </FormModal>
  );
}
