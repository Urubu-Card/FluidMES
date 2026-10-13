import './style.css';

export default function SearchBar({
    value,
    onChange,
    onSubmit,
    placeholder = 'Buscar...',
    className = '',
}) {
    function handleSubmit(e) {
        e.preventDefault();
        onSubmit?.(value);
    }

    return (
        <form
            className={`search-glass ${className}`.trim()}
            onSubmit={handleSubmit}
            role="search"
        >
            <input
                type="search"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                aria-label={placeholder}
            />
            <button type="submit" aria-label="Buscar">
                <i className="bi bi-search" aria-hidden="true" />
            </button>
        </form>
    );
}
