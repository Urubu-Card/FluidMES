import { useEffect, useState } from 'react';
import api from '../../../services/api';
import './style.css';

export default function Pedidos({ dados }) {
    const [pedidos, setPedidos] = useState([]);
    const [busca, setBusca] = useState('');
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');

    const [selecionados, setSelecionados] = useState([]);

    // ================================
    // BUSCAR PEDIDOS DO BACKEND
    // ================================
    useEffect(() => {
        buscarPedidos();
    }, []);

    async function buscarPedidos() {
        try {
            setCarregando(true);
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
    // PESQUISA
    // ================================
    const pedidosFiltrados = pedidos.filter((pedido) => {
        const textoBusca = busca.toLowerCase();
        return (
            pedido.id?.toString().toLowerCase().includes(textoBusca) ||
            pedido.receita?.toLowerCase().includes(textoBusca) ||
            pedido.status?.toLowerCase().includes(textoBusca)
        );
    });

    // ================================
    // TOTAIS
    // ================================
    const totalPedidos = pedidos.length;
    const totalRealizados = pedidos.filter(
        (p) => p.status?.toLowerCase() === 'feito'
    ).length;
    const totalCancelados = pedidos.filter(
        (p) => p.status?.toLowerCase() === 'cancelado'
    ).length;

    // ================================
    // SELECIONAR PEDIDO
    // ================================
    function selecionarPedido(id) {
        setSelecionados((atual) => {
            if (atual.includes(id)) {
                return atual.filter((pedidoId) => pedidoId !== id);
            }
            return [...atual, id];
        });
    }

    // ================================
    // SELECIONAR TODOS
    // ================================
    function selecionarTodos() {
        if (
            selecionados.length === pedidosFiltrados.length &&
            pedidosFiltrados.length > 0
        ) {
            setSelecionados([]);
        } else {
            setSelecionados(pedidosFiltrados.map((pedido) => pedido.id));
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
        const confirmar = window.confirm(
            'Deseja realmente excluir este pedido?'
        );
        if (!confirmar) return;

        try {
            await api.delete(`/api/pedidos/${id}/`);

            setPedidos((atual) =>
                atual.filter((pedido) => pedido.id !== id)
            );

            setSelecionados((atual) =>
                atual.filter((pedidoId) => pedidoId !== id)
            );
        } catch (error) {
            console.error(error);
            alert('Erro ao excluir pedido.');
        }
    }

    // ================================
    // ADICIONAR PEDIDO
    // ================================
    function adicionarPedido() {
        console.log('Adicionar pedido');
        // Futuramente: abrir modal
    }

    // ================================
    // STATUS
    // ================================
    function getStatusClass(status) {
        const statusLower = status?.toLowerCase();
        if (statusLower === 'feito') return 'status-feito';
        if (statusLower === 'cancelado') return 'status-cancelado';
        if (statusLower === 'fazendo') return 'status-fazendo';
        if (statusLower === 'na fila') return 'status-nafila';
        return 'status-offline';
    }

    return (
        <div className='pedidos-page'>

            {/* ================= HEADER ================= */}
            <div className='pedidos-header'>
                <h1>Pedidos:</h1>
                <div className='col-md-6'>
                    <form onSubmit={(e) => e.preventDefault()}>
                        <div className='input-group mb-3'>
                            <span className='search-icon'>
                                <i className='bi bi-search'></i>
                            </span>
                            <input
                                type='text'
                                className='form-control'
                                placeholder='Buscar Pedido'
                                value={busca}
                                onChange={(e) => setBusca(e.target.value)}
                            />
                            <button className='filter-button' type='button'>
                                <i className='bi bi-sliders'></i>
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            {/* ================= CARDS DE STATUS ================= */}
            <div className='status-cards'>
                <div className='status-card escuro'>
                    <div className='status-card-icon'>
                        <i className='bi bi-card-checklist'></i>
                    </div>
                    <div>
                        <h3>Total Pedidos</h3>
                        <p>{totalPedidos}</p>
                    </div>
                </div>
                <div className='status-card claro'>
                    <div className='status-card-icon'>
                        <i className='bi bi-check2-circle'></i>
                    </div>
                    <div>
                        <h3>Total Realizados</h3>
                        <p>{totalRealizados}</p>
                    </div>
                </div>
                <div className='status-card escuro'>
                    <div className='status-card-icon'>
                        <i className='bi bi-x-circle'></i>
                    </div>
                    <div>
                        <h3>Total Cancelados</h3>
                        <p>{totalCancelados}</p>
                    </div>
                </div>
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
                    <div className='ordem-column'>Ordem de ID <i className='bi bi-chevron-down'></i></div>
                    <div className='receita-column'>Receita</div>
                    <div className='data-column'>Data <i className='bi bi-chevron-down'></i></div>
                    <div className='quantidade-column'>Quantidade <i className='bi bi-chevron-down'></i></div>
                    <div className='status-column'>Status <i className='bi bi-chevron-down'></i></div>
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
                    pedidosFiltrados.map((pedido) => (
                        <div className='table-row' key={pedido.id}>
                            {/* CHECKBOX */}
                            <div className='check-column'>
                                <input
                                    type='checkbox'
                                    checked={selecionados.includes(pedido.id)}
                                    onChange={() => selecionarPedido(pedido.id)}
                                />
                            </div>

                            {/* ORDEM ID */}
                            <div className='ordem-column'>
                                #{pedido.id}
                            </div>

                            {/* RECEITA */}
                            <div className='receita-column pedido-receita'>
                                <div className='pedido-avatar'>
                                    {pedido.imagem ? (
                                        <img src={pedido.imagem} alt={pedido.receita} />
                                    ) : (
                                        <i className='bi bi-cup-straw'></i>
                                    )}
                                </div>
                                <div className='pedido-receita-info'>
                                    <strong>{pedido.receita}</strong>
                                    <p>{pedido.descricao || 'Planta para produção de refrigerante'}</p>
                                </div>
                            </div>

                            {/* DATA */}
                            <div className='data-column'>
                                {pedido.data}
                            </div>

                            {/* QUANTIDADE */}
                            <div className='quantidade-column'>
                                {pedido.quantidade}
                            </div>

                            {/* STATUS */}
                            <div className='status-column'>
                                <span className={`status ${getStatusClass(pedido.status)}`}>
                                    {pedido.status}
                                </span>
                            </div>

                            {/* AÇÕES */}
                            <div className='editar-column'>
                                <button
                                    className='action-button edit-button'
                                    onClick={() => editarPedido(pedido)}
                                >
                                    <i className='bi bi-pencil-fill'></i>
                                </button>
                                <button
                                    className='action-button delete-button'
                                    onClick={() => excluirPedido(pedido.id)}
                                >
                                    <i className='bi bi-trash-fill'></i>
                                </button>
                            </div>
                        </div>
                    ))
                }

                {/* VAZIO */}
                {!carregando && pedidosFiltrados.length === 0 && (
                    <div className='table-message'>
                        Nenhum pedido encontrado.
                    </div>
                )}
            </div>

            {/* ================= BOTÃO ADICIONAR ================= */}
            <button className='add-pedido' onClick={adicionarPedido}>
                <i className='bi bi-plus-lg'></i>
            </button>
        </div>
    );
}