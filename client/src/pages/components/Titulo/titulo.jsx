import './style.css';

export default function TituloPagina({ titulo, children }) {
    return (
        <div className="titulo-pagina-header">
            <h1 className="titulo-pagina">{titulo}</h1>
            {children}
        </div>
    );
}