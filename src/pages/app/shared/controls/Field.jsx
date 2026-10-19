import { useId } from "react";

export default function Field({
  label,
  hint,
  options,
  emptyLabel = "Selecione…",
  type = "text",
  step = "any",
  value,
  onChange,
  ...props
}) {
  const id = useId();
  const common = {
    id,
    "aria-label": label,
    "aria-describedby": hint ? `${id}-hint` : undefined,
    ...props,
  };
  return (
    <label className="form-field" htmlFor={id}>
      <span>{label}</span>
      {options ? (
        <select
          {...common}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          {emptyLabel !== null && <option value="">{emptyLabel}</option>}
          {options.map(([key, name]) => (
            <option key={key} value={key}>
              {name}
            </option>
          ))}
        </select>
      ) : (
        <input
          {...common}
          type={type}
          value={type === "checkbox" ? undefined : value}
          checked={type === "checkbox" ? Boolean(value) : undefined}
          step={type === "number" ? step : undefined}
          onChange={(e) =>
            onChange(type === "checkbox" ? e.target.checked : e.target.value)
          }
        />
      )}
      {hint && <small id={`${id}-hint`}>{hint}</small>}
    </label>
  );
}
