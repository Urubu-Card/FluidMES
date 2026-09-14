import { useEffect, useState } from 'react';
import api from '../../../services/api';
import './style.css';

export default function Funcionarios() {

    const [funcionarios, setFuncionarios] = useState([]);
    const [busca, setBusca] = useState('');
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');

    // IDs dos funcionários selecionados
    const [selecionados, setSelecionados] = useState([]);

    // ================================
    // BUSCAR FUNCIONÁRIOS DO BACKEND
    // ================================

    useEffect(() => {
        buscarFuncionarios();
    }, []);

    async function buscarFuncionarios() {
        try {
            setCarregando(true);
            const response = await api.get('/api/funcionarios/');
            console.log(response.data);
            setFuncionarios(response.data);
        } catch (error) {
            console.error(error);
            setErro('Erro ao carregar funcionários.');
        } finally {
            setCarregando(false);
        }
    }

    // ================================
    // PESQUISA
    // ================================
    const funcionariosFiltrados = funcionarios.filter((funcionario) => {
        const textoBusca = busca.toLowerCase();
        return (
            funcionario.first_name?.toLowerCase().includes(textoBusca) ||
            funcionario.last_name?.toLowerCase().includes(textoBusca) ||
            funcionario.email?.toLowerCase().includes(textoBusca) ||
            funcionario.cargo?.toLowerCase().includes(textoBusca)
        );
    });

    // ================================
    // SELECIONAR FUNCIONÁRIO
    // ================================

    function selecionarFuncionario(id) {
        setSelecionados((atual) => {
            if (atual.includes(id)) {
                return atual.filter((funcionarioId) =>
                    funcionarioId !== id
                );
            }
            return [...atual, id];
        });
    }

    // ================================
    // SELECIONAR TODOS
    // ================================

    function selecionarTodos() {
        if (
            selecionados.length === funcionariosFiltrados.length &&
            funcionariosFiltrados.length > 0
        ) {
            setSelecionados([]);
        } else {
            setSelecionados(
                funcionariosFiltrados.map(
                    (funcionario) => funcionario.id
                )
            );
        }
    }

    // ================================
    // EDITAR
    // ================================

    function editarFuncionario(funcionario) {
        console.log('Editar:', funcionario);
        // Futuramente:
        // abrir modal de edição
    }

    // ================================
    // EXCLUIR
    // ================================
    async function excluirFuncionario(id) {
        const confirmar = window.confirm(
            'Deseja realmente excluir este funcionário?'
        );
        if (!confirmar) return;
        try {
            await api.delete(
                `/api/funcionarios/${id}/`
            );

            // Remove da tela sem precisar recarregar
            setFuncionarios((atual) =>
                atual.filter(
                    (funcionario) =>
                        funcionario.id !== id
                )
            );

            // Remove dos selecionados
            setSelecionados((atual) =>
                atual.filter(
                    (funcionarioId) =>
                        funcionarioId !== id
                )
            );

        } catch (error) {
            console.error(error);
            alert('Erro ao excluir funcionário.');
        }
    }

    // ================================
    // ADICIONAR FUNCIONÁRIO
    // ================================

    function adicionarFuncionario() {
        console.log('Adicionar funcionário');
        // Futuramente:
        // abrir modal
    }

    // ================================
    // STATUS
    // ================================

    function getStatusClass(status) {
        const statusLower = status?.toLowerCase();
        if (statusLower === 'online') {
            return 'status-online';
        }
        if (statusLower === 'ausente') {
            return 'status-ausente';
        }
        return 'status-offline';
    }
    return (
        <div className='funcionarios-page'>

            {/* ================= HEADER ================= */}
            <div className='funcionarios-header'>
                <h1>
                    Funcionários:
                </h1>
                <div className='search-container'>
                    <i className='bi bi-search'></i>
                    <input
                        type='text'
                        placeholder='Buscar Funcionário'
                        value={busca}
                        onChange={(e) =>
                            setBusca(e.target.value)
                        }
                    />
                    <button
                        className='filter-button'
                    >
                        <i className='bi bi-sliders'></i>
                    </button>
                </div>
            </div>

            {/* ================= TABELA ================= */}
            <div className='funcionarios-table'>
                {/* HEADER */}
                <div className='table-header'>
                    <div className='check-column'>
                        <input
                            type='checkbox'
                            checked={
                                funcionariosFiltrados.length > 0 &&
                                selecionados.length === funcionariosFiltrados.length
                            }
                            onChange={selecionarTodos}
                        />
                    </div>
                    <div className='nome-column'>
                        Nome
                    </div>
                    <div className='cargo-column'>
                        Cargo
                    </div>
                    <div className='contato-column'>
                        Contato
                    </div>
                    <div className='status-column'>
                        Status
                    </div>
                    <div className='editar-column'>
                        Editar
                    </div>
                </div>

                {/* ================= LOADING ================= */}
                {carregando && (
                    <div className='table-message'>
                        Carregando funcionários...
                    </div>
                )}

                {/* ================= ERRO ================= */}
                {erro && (
                    <div className='table-message error'>
                        {erro}
                    </div>
                )}

                {/* ================= FUNCIONÁRIOS ================= */}
                {!carregando &&
                    funcionariosFiltrados.map((funcionario) => (
                        <div
                            className='table-row'
                            key={funcionario.id}
                        >
                            {/* CHECKBOX */}
                            <div className='check-column'>
                                <input
                                    type='checkbox'
                                    checked={
                                        selecionados.includes(
                                            funcionario.id
                                        )
                                    }
                                    onChange={() =>
                                        selecionarFuncionario(
                                            funcionario.id
                                        )
                                    }
                                />
                            </div>
                            {/* NOME */}
                            <div className='nome-column funcionario-nome'>
                                {/* SETA */}
                                <i className='bi bi-chevron-down'></i>
                                {/* FOTO */}
                                <div className='funcionario-avatar'>
                                    {funcionario.foto ? (
                                        <img
                                            src={funcionario.foto}
                                            alt={funcionario.first_name}
                                        />
                                    ) : (
                                        <i className='bi bi-person-fill'></i>
                                    )}
                                </div>
                                {/* NOME */}
                                <span>
                                    {funcionario.first_name}{' '}
                                    {funcionario.last_name}
                                </span>
                            </div>

                            {/* CARGO */}
                            <div className='cargo-column'>
                                {funcionario.cargo || 'Funcionário'}
                            </div>

                            {/* EMAIL */}
                            <div className='contato-column'>
                                {funcionario.email}
                            </div>

                            {/* STATUS */}
                            <div className='status-column'>
                                <span
                                    className={`
                                        status
                                        ${getStatusClass(funcionario.status)}
                                    `}
                                >
                                    {funcionario.status || 'Offline'}
                                </span>
                            </div>

                            {/* AÇÕES */}
                            <div className='editar-column'>

                                {/* EDITAR */}
                                <button
                                    className='action-button edit-button'
                                    onClick={() =>
                                        editarFuncionario(
                                            funcionario
                                        )
                                    }
                                >
                                    <i className='bi bi-pencil-fill'></i>
                                </button>

                                {/* EXCLUIR */}
                                <button
                                    className='action-button delete-button'
                                    onClick={() =>
                                        excluirFuncionario(
                                            funcionario.id
                                        )
                                    }
                                >
                                    <i className='bi bi-trash-fill'></i>
                                </button>
                            </div>
                        </div>
                    ))
                }

                {/* ================= VAZIO ================= */}
                {!carregando &&
                    funcionariosFiltrados.length === 0 && (
                        <div className='table-message'>
                            Nenhum funcionário encontrado.
                        </div>
                    )
                }
            </div>

            {/* ================= BOTÃO ADICIONAR ================= */}
            <button
                className='add-funcionario'
                onClick={adicionarFuncionario}
            >
                <i className='bi bi-plus-lg'></i>
            </button>
        </div>
    );
}