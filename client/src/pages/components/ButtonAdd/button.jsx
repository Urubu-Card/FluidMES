import './style.css';


export default function BotaoModal({
  target,
  label = "Abrir",
  icon = "bi-plus-lg",
  className = "",
}) {
  return (
    <button
      className={`botao-modal btn btn-primary ${className}`}
      type="button"
      aria-label={label}
      data-bs-toggle="modal"
      data-bs-target={`#${target}`}
    >
      <i className={`bi ${icon}`} aria-hidden="true" />
    </button>
  );
}