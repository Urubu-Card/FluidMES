import { useEffect, useMemo, useState } from 'react';
import api from '../../../services/api';
import './style.css';
import BotaoModal from "../../components/ButtonAdd/button";
import TituloPagina from "../../components/Titulo/titulo";
import SearchBar from "../../components/SearchBar/searchbar";

// ================================
// CONSTANTES (espelham o model Pedido)
// ================================
const STATUS = {
    pendente:     { label: 'Pendente',     classe: 'status-pendente' },
    em_andamento: { label: 'Em Andamento', classe: 'status-andamento' },
    concluido:    { label: 'Concluído',    classe: 'status-concluido' },
    cancelado:    { label: 'Cancelado',    classe: 'status-cancelado' },
};

const APROVACAO = {
    aguardando: { label: 'Aguardando', classe: 'aprov-aguardando' },
    aprovado:   { label: 'Aprovado',   classe: 'aprov-aprovado' },
    reprovado:  { label: 'Reprovado',  classe: 'aprov-reprovado' },
};

// ================================
// HELPERS
// ================================

// A FK pode vir como objeto, como id ou em um campo "<fk>_nome".
// Ajuste aqui conforme o seu serializer.
function nomeRelacao(pedido, campo) {
    const valor = pedido[campo];
    if (valor && typeof valor === 'object') {
        return valor.nome ?? valor.nome_fantasia ?? valor.descricao ?? `#${valor.id ?? ''}`;
    }
    return pedido[`${campo}_nome`] ?? (valor != null ? `#${valor}` : '—');
}

// "2026-10-05" -> "05/10/2026" (sem passar por Date, evita bug de fuso)
function formatarData(data) {
    if (!data) return '—';
    const [ano, mes, dia] = data.split('T')[0].split('-');
    return `${dia}/${mes}/${ano}`;
}

function formatarQuantidade(qtd) {
    if (qtd == null) return '—';
    return Number(qtd).toLocaleString('pt-BR', { maximumFractionDigits: 2 });
}

function estaAtrasado(pedido) {
    if (!pedido.prazo) return false;
    if (!['pendente', 'em_andamento'].includes(pedido.status)) return false;
    const hoje = new Date().toISOString().split('T')[0];
    return pedido.prazo.split('T')[0] < hoje;
}

export default function Pedidos() {
    const [pedidos, setPedidos] = useState([]);
    const [busca, setBusca] = useState('');
    const [filtroStatus, setFiltroStatus] = useState('todos');
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');

    const [selecionados, setSelecionados] = useState([]);
    const [ordem, setOrdem] = useState({ campo: 'idpedido', direcao: 'desc' });

    // ================================
    // BUSCAR PEDIDOS DO BACKEND
    // ================================
    useEffect(() => {
        buscarPedidos();
    }, []);

    async function buscarPedidos() {
        try {
            setCarregando(true);
            setErro('');
            const response = await api.get('/api/pedidos/');
            setPedidos(response.data);
        } catch (error) {
            console.error(error);
            setErro('Erro ao carregar pedidos.');
        } finally {
            setCarregando(false);
        }
    }

    // ================================
    // PESQUISA + FILTRO + ORDENAÇÃO
    // ================================
    const pedidosFiltrados = useMemo(() => {
        const textoBusca = busca.toLowerCase();

        const filtrados = pedidos.filter((pedido) => {
            if (filtroStatus !== 'todos' && pedido.status !== filtroStatus) return false;

            return (
                pedido.idpedido?.toString().includes(textoBusca) ||
                nomeRelacao(pedido, 'receita').toLowerCase().includes(textoBusca) ||
                nomeRelacao(pedido, 'planta').toLowerCase().includes(textoBusca) ||
                nomeRelacao(pedido, 'usuario').toLowerCase().includes(textoBusca) ||
                pedido.pedidocol?.toLowerCase().includes(textoBusca) ||
                STATUS[pedido.status]?.label.toLowerCase().includes(textoBusca) ||
                APROVACAO[pedido.aprovacao]?.label.toLowerCase().includes(textoBusca)
            );
        });

        const { campo, direcao } = ordem;
        const fator = direcao === 'asc' ? 1 : -1;

        return [...filtrados].sort((a, b) => {
            const va = a[campo];
            const vb = b[campo];
            if (va == null) return 1;
            if (vb == null) return -1;
            if (typeof va === 'number') return (va - vb) * fator;
            return String(va).localeCompare(String(vb)) * fator;
        });
    }, [pedidos, busca, filtroStatus, ordem]);

    // ================================
    // TOTAIS
    // ================================
    const total = (status) => pedidos.filter((p) => p.status === status).length;
    const totalPedidos = pedidos.length;
    const totalPendentes = total('pendente');
    const totalEmAndamento = total('em_andamento');
    const totalConcluidos = total('concluido');
    const totalCancelados = total('cancelado');

    // ================================
    // ORDENAR
    // ================================
    function ordenarPor(campo) {
        setOrdem((atual) => ({
            campo,
            direcao: atual.campo === campo && atual.direcao === 'asc' ? 'desc' : 'asc',
        }));
    }

    function iconeOrdem(campo) {
        if (ordem.campo !== campo) return 'bi-chevron-expand';
        return ordem.direcao === 'asc' ? 'bi-chevron-up' : 'bi-chevron-down';
    }

    // ================================
    // SELECIONAR PEDIDO
    // ================================
    function selecionarPedido(id) {
        setSelecionados((atual) =>
            atual.includes(id) ? atual.filter((pedidoId) => pedidoId !== id) : [...atual, id]
        );
    }

    function selecionarTodos() {
        if (
            selecionados.length === pedidosFiltrados.length &&
            pedidosFiltrados.length > 0
        ) {
            setSelecionados([]);
        } else {
            setSelecionados(pedidosFiltrados.map((pedido) => pedido.idpedido));
        }
    }

    // ================================
    // APROVAÇÃO (aprovar / reprovar)
    // ================================
    async function atualizarAprovacao(id, aprovacao) {
        try {
            const response = await api.patch(`/api/pedidos/${id}/`, { aprovacao });
            setPedidos((atual) =>
                atual.map((p) =>
                    p.idpedido === id ? { ...p, ...response.data } : p
                )
            );
        } catch (error) {
            console.error(error);
            alert('Erro ao atualizar aprovação do pedido.');
        }
    }

    // ================================
    // EDITAR
    // ================================
    function editarPedido(pedido) {
        console.log('Editar:', pedido);
        // Futuramente: abrir modal de edição
    }

    // ================================
    // EXCLUIR
    // ================================
    async function excluirPedido(id) {
        const confirmar = window.confirm('Deseja realmente excluir este pedido?');
        if (!confirmar) return;

        try {
            await api.delete(`/api/pedidos/${id}/`);

            setPedidos((atual) => atual.filter((pedido) => pedido.idpedido !== id));
            setSelecionados((atual) => atual.filter((pedidoId) => pedidoId !== id));
        } catch (error) {
            console.error(error);
            alert('Erro ao excluir pedido.');
        }
    }

    return (
        <div className='pedidos-page app-page'>

            {/* ================= HEADER ================= */}
            <div className='pedidos-header'>
                <TituloPagina titulo="Pedidos:">
                    <div className='col-md-3'>
                        <SearchBar
                            value={busca}
                            onChange={setBusca}
                            placeholder="Buscar por ID, receita, planta..."
                        />
                    </div>
                </TituloPagina>
            </div>

            {/* ================= CARDS DE STATUS ================= */}
            <div className='status-cards'>
                <div className='status-card escuro'>
                    <div className='status-card-icon'>
                        <i className='bi bi-card-checklist'></i>
                    </div>
                    <div>
                        <h3>Total de pedidos</h3>
                        <p>{totalPedidos}</p>
                    </div>
                </div>
                <div className='status-card claro'>
                    <div className='status-card-icon'>
                        <i className='bi bi-hourglass-split'></i>
                    </div>
                    <div>
                        <h3>Pendentes</h3>
                        <p>{totalPendentes}</p>
                    </div>
                </div>
                <div className='status-card escuro'>
                    <div className='status-card-icon'>
                        <i className='bi bi-gear-wide-connected'></i>
                    </div>
                    <div>
                        <h3>Em andamento</h3>
                        <p>{totalEmAndamento}</p>
                    </div>
                </div>
                <div className='status-card claro'>
                    <div className='status-card-icon'>
                        <i className='bi bi-check2-circle'></i>
                    </div>
                    <div>
                        <h3>Concluídos</h3>
                        <p>{totalConcluidos}</p>
                    </div>
                </div>
                <div className='status-card escuro'>
                    <div className='status-card-icon'>
                        <i className='bi bi-x-circle'></i>
                    </div>
                    <div>
                        <h3>Cancelados</h3>
                        <p>{totalCancelados}</p>
                    </div>
                </div>
            </div>

            {/* ================= FILTRO DE STATUS ================= */}
            <div className='status-filtros'>
                <button
                    className={`filtro-chip ${filtroStatus === 'todos' ? 'ativo' : ''}`}
                    onClick={() => setFiltroStatus('todos')}
                >
                    Todos
                </button>
                {Object.entries(STATUS).map(([chave, { label }]) => (
                    <button
                        key={chave}
                        className={`filtro-chip ${filtroStatus === chave ? 'ativo' : ''}`}
                        onClick={() => setFiltroStatus(chave)}
                    >
                        {label}
                    </button>
                ))}
            </div>

            {/* ================= TABELA ================= */}
            <div className='pedidos-table'>
                {/* HEADER */}
                <div className='table-header'>
                    <div className='check-column'>
                        <input
                            type='checkbox'
                            checked={
                                pedidosFiltrados.length > 0 &&
                                selecionados.length === pedidosFiltrados.length
                            }
                            onChange={selecionarTodos}
                        />
                    </div>
                    <div className='ordem-column sortable' onClick={() => ordenarPor('idpedido')}>
                        Pedido <i className={`bi ${iconeOrdem('idpedido')}`}></i>
                    </div>
                    <div className='receita-column'>Receita</div>
                    <div className='planta-column'>Planta</div>
                    <div className='data-column sortable' onClick={() => ordenarPor('prazo')}>
                        Prazo <i className={`bi ${iconeOrdem('prazo')}`}></i>
                    </div>
                    <div className='quantidade-column sortable' onClick={() => ordenarPor('quantidade')}>
                        Quantidade <i className={`bi ${iconeOrdem('quantidade')}`}></i>
                    </div>
                    <div className='status-column sortable' onClick={() => ordenarPor('status')}>
                        Status <i className={`bi ${iconeOrdem('status')}`}></i>
                    </div>
                    <div className='aprovacao-column sortable' onClick={() => ordenarPor('aprovacao')}>
                        Aprovação <i className={`bi ${iconeOrdem('aprovacao')}`}></i>
                    </div>
                    <div className='editar-column'></div>
                </div>

                {/* LOADING */}
                {carregando && (
                    <div className='table-message'>
                        Carregando pedidos...
                    </div>
                )}

                {/* ERRO */}
                {erro && (
                    <div className='table-message error'>
                        {erro}
                    </div>
                )}

                {/* PEDIDOS */}
                {!carregando &&
                    pedidosFiltrados.map((pedido) => {
                        const status = STATUS[pedido.status];
                        const aprovacao = APROVACAO[pedido.aprovacao];
                        const atrasado = estaAtrasado(pedido);

                        return (
                            <div className='table-row' key={pedido.idpedido}>
                                {/* CHECKBOX */}
                                <div className='check-column'>
                                    <input
                                        type='checkbox'
                                        checked={selecionados.includes(pedido.idpedido)}
                                        onChange={() => selecionarPedido(pedido.idpedido)}
                                    />
                                </div>

                                {/* ID */}
                                <div className='ordem-column'>
                                    #{pedido.idpedido}
                                </div>

                                {/* RECEITA */}
                                <div className='receita-column pedido-receita'>
                                    <div className='pedido-avatar'>
                                        <i className='bi bi-droplet-half'></i>
                                    </div>
                                    <div className='pedido-receita-info'>
                                        <strong>{nomeRelacao(pedido, 'receita')}</strong>
                                        <p>
                                            {pedido.pedidocol || `Solicitante: ${nomeRelacao(pedido, 'usuario')}`}
                                        </p>
                                    </div>
                                </div>

                                {/* PLANTA */}
                                <div className='planta-column'>
                                    {nomeRelacao(pedido, 'planta')}
                                </div>

                                {/* PRAZO */}
                                <div className={`data-column ${atrasado ? 'prazo-atrasado' : ''}`}>
                                    {formatarData(pedido.prazo)}
                                    {atrasado && <small>Atrasado</small>}
                                </div>

                                {/* QUANTIDADE */}
                                <div className='quantidade-column'>
                                    {formatarQuantidade(pedido.quantidade)}
                                </div>

                                {/* STATUS */}
                                <div className='status-column'>
                                    <span className={`status ${status?.classe ?? 'status-offline'}`}>
                                        {status?.label ?? pedido.status}
                                    </span>
                                </div>

                                {/* APROVAÇÃO */}
                                <div className='aprovacao-column'>
                                    <span className={`status ${aprovacao?.classe ?? 'status-offline'}`}>
                                        {aprovacao?.label ?? pedido.aprovacao}
                                    </span>
                                </div>

                                {/* AÇÕES */}
                                <div className='editar-column'>
                                    {pedido.aprovacao === 'aguardando' && (
                                        <>
                                            <button
                                                className='action-button approve-button'
                                                title='Aprovar'
                                                onClick={() => atualizarAprovacao(pedido.idpedido, 'aprovado')}
                                            >
                                                <i className='bi bi-check-lg'></i>
                                            </button>
                                            <button
                                                className='action-button reject-button'
                                                title='Reprovar'
                                                onClick={() => atualizarAprovacao(pedido.idpedido, 'reprovado')}
                                            >
                                                <i className='bi bi-x-lg'></i>
                                            </button>
                                        </>
                                    )}
                                    <button
                                        className='action-button edit-button'
                                        title='Editar'
                                        onClick={() => editarPedido(pedido)}
                                    >
                                        <i className='bi bi-pencil-fill'></i>
                                    </button>
                                    <button
                                        className='action-button delete-button'
                                        title='Excluir'
                                        onClick={() => excluirPedido(pedido.idpedido)}
                                    >
                                        <i className='bi bi-trash-fill'></i>
                                    </button>
                                </div>
                            </div>
                        );
                    })
                }

                {/* VAZIO */}
                {!carregando && !erro && pedidosFiltrados.length === 0 && (
                    <div className='table-message'>
                        Nenhum pedido encontrado.
                    </div>
                )}
            </div>

            {/* ================= BOTÃO ADICIONAR ================= */}
            <BotaoModal target="modalAddPedido" label="Adicionar pedido" />
        </div>
    );
}