import { useEffect, useState } from 'react';
import api from '../../../services/api';
import './style.css';

export default function Funcionarios() {
    const [funcionarios, setFuncionarios] = useState([]);
    const [busca, setBusca] = useState('');
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');

    const [selecionados, setSelecionados] = useState([]);

    const cargos = { 3: 'Funcionário', 2: 'Chefe', 1: 'Preposto' };


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
                return atual.filter((funcionarioId) => funcionarioId !== id);
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
                funcionariosFiltrados.map((funcionario) => funcionario.id)
            );
        }
    }

    // ================================
    // EDITAR
    // ================================
    function editarFuncionario(funcionario) {
        console.log('Editar:', funcionario);
        // Futuramente: abrir modal de edição
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
            await api.delete(`/api/funcionarios/${id}/`);

            setFuncionarios((atual) =>
                atual.filter((funcionario) => funcionario.id !== id)
            );

            setSelecionados((atual) =>
                atual.filter((funcionarioId) => funcionarioId !== id)
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
        // Futuramente: abrir modal
    }

    // ================================
    // STATUS
    // ================================
    function getStatusClass(status) {
        const statusLower = status?.toLowerCase();
        if (statusLower === 'ativo') return 'status-online';
        if (statusLower === 'inativo') return 'status-ausente';
        return 'status-offline';
    }

    return (
        <div className='funcionarios-page'>

            {/* ================= HEADER ================= */}
            <div className='funcionarios-header'>
                <h1>Funcionários:</h1>
                <div className='col-md-4'>
                    <form onSubmit={(e) => e.preventDefault()}>
                        <div className='input-group app-search-group'>
                            <select className='form-select' defaultValue="">
                                <option value="">Filtrar por</option>
                                <option value="ativo">Ativo</option>
                                <option value="inativo">Inativo</option>
                            </select>
                            <input 
                                type='text' 
                                className='form-control' 
                                placeholder='Achar funcionário...' 
                                value={busca}
                                onChange={(e) => setBusca(e.target.value)}
                            />
                            <button className='btn btn-primary' type='submit'>
                                <i className='bi bi-search me-2' aria-hidden='true'></i>Buscar
                            </button>
                        </div>
                    </form>
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
                    <div className='nome-column'>Nome</div>
                    <div className='cargo-column'>Cargo</div>
                    <div className='contato-column'>Contato</div>
                    <div className='status-column'>Status</div>
                    <div className='editar-column'>Editar</div>
                </div>

                {/* LOADING */}
                {carregando && (
                    <div className='table-message'>
                        Carregando funcionários...
                    </div>
                )}

                {/* ERRO */}
                {erro && (
                    <div className='table-message error'>
                        {erro}
                    </div>
                )}

                {/* FUNCIONÁRIOS */}
                {!carregando &&
                    funcionariosFiltrados.map((funcionario) => (
                        <div className='table-row' key={funcionario.id}>
                            {/* CHECKBOX */}
                            <div className='check-column'>
                                <input
                                    type='checkbox'
                                    checked={selecionados.includes(funcionario.id)}
                                    onChange={() => selecionarFuncionario(funcionario.id)}
                                />
                            </div>
                            
                            {/* NOME */}
                            <div className='nome-column funcionario-nome'>
                                <i className='bi bi-chevron-down'></i>
                                <div className='funcionario-avatar'>
                                    {funcionario.foto ? (
                                        <img src={funcionario.foto} alt={funcionario.first_name} />
                                    ) : (
                                        <i className='bi bi-person-fill'></i>
                                    )}
                                </div>
                                <span>
                                    {funcionario.first_name} {funcionario.last_name}
                                </span>
                            </div>

                            {/* CARGO (Corrigido o acento na variável) */}
                            <div className='cargo-column'>
                                {cargos[funcionario.role]}
                            </div>

                            {/* EMAIL */}
                            <div className='contato-column'>
                                {funcionario.email}
                            </div>

                            {/* STATUS */}
                            <div className='status-column'>
                                <span className={`status ${getStatusClass(funcionario.is_active ? 'Ativo' : 'Inativo')}`}>
                                    {funcionario.is_active ? 'Ativo' : 'Inativo'}
                                </span>
                            </div>

                            {/* AÇÕES */}
                            <div className='editar-column'>
                                <button
                                    className='action-button edit-button'
                                    onClick={() => editarFuncionario(funcionario)}
                                >
                                    <i className='bi bi-pencil-fill'></i>
                                </button>
                                <button
                                    className='action-button delete-button'
                                    onClick={() => excluirFuncionario(funcionario.id)}
                                >
                                    <i className='bi bi-trash-fill'></i>
                                </button>
                            </div>
                        </div>
                    ))
                }

                {/* VAZIO */}
                {!carregando && funcionariosFiltrados.length === 0 && (
                    <div className='table-message'>
                        Nenhum funcionário encontrado.
                    </div>
                )}
            </div>

            {/* ================= BOTÃO ADICIONAR ================= */}
            <button className='add-funcionario' onClick={adicionarFuncionario}>
                <i className='bi bi-plus-lg'></i>
            </button>
        </div>
    );
}
