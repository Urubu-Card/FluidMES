export default function Button({
  children,
  variant = "primary",
  icon,
  className = "",
  type = "button",
  ...props
}) {
  return (
    <button
      type={type}
      className={`mes-button ${variant === "primary" ? "" : variant} ${className}`.trim()}
      {...props}
    >
      {icon && <i aria-hidden="true" className={`bi ${icon}`} />}
      {children}
    </button>
  );
}
