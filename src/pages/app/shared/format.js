export const number = (value) =>
  Number(value || 0).toLocaleString("pt-BR", { maximumFractionDigits: 2 });
export const dateTime = (value) =>
  value ? new Date(value).toLocaleString("pt-BR") : "—";
export const percent = (value) =>
  value == null
    ? "Sem medição"
    : `${(value * 100).toFixed(1).replace(".", ",")}%`;
export const duration = (value) => {
  const seconds = Math.max(0, Math.round((Number(value) || 0) * 100) / 100);
  const hours = Math.floor(seconds / 3600),
    minutes = Math.floor((seconds % 3600) / 60);
  const remainder =
    Math.round((seconds - hours * 3600 - minutes * 60) * 100) / 100;
  return [
    hours ? `${hours} h` : "",
    minutes ? `${minutes} min` : "",
    remainder || (!hours && !minutes) ? `${number(remainder)} s` : "",
  ]
    .filter(Boolean)
    .join(" ");
};
