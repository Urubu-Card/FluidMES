import { useState, useEffect, useRef } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import api from '../../../services/api.js';
import './style.css';

export default function Sidebar() {
    const location = useLocation(); // Escuta as mudanças de rota
    const sidebarRef = useRef(null); // Referência para a sidebar
    const indicadorRef = useRef(null); // Referência para a barra verde

    const [userExit, setUserExit] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false); // Controle do offcanvas (telas pequenas)

    // ESTADO INICIAL COM VALORES DE CARREGAMENTO
    const [usuario, setUsuario] = useState({
        nome: 'Carregando...',
        cargo: 'Carregando...',
        fotoUrl: null
    });

    // REQUISIÇÃO REAL PARA A SUA API
    useEffect(() => {
        async function carregarDadosUsuario() {
            try {
                const token = localStorage.getItem('@api:token');

                const response = await api.get('/api/me/', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.status !== 200) {
                    throw new Error('Não foi possível carregar os dados do perfil.');
                }

                const dados = await response.data;

                setUsuario({
                    primeiroNome: dados.first_name || 'Usuário',
                    segundoNome: dados.last_name || '',
                    cargo: dados.cargo || 'Não informado',
                    fotoUrl: dados.fotoUrl || null
                });

            } catch (error) {
                console.error('Erro ao buscar dados do usuário:', error);
                setUsuario({
                    nome: 'Erro ao carregar',
                    cargo: 'Verifique a conexão',
                    fotoUrl: null
                });
            }
        }

        carregarDadosUsuario();
    }, []);

    // Move o indicador animado para o link ativo
    useEffect(() => {
        if (!sidebarRef.current || !indicadorRef.current) return;

        const linkAtivo = sidebarRef.current.querySelector('a.active');

        if (linkAtivo) {
            const topo = linkAtivo.offsetTop;
            const altura = linkAtivo.offsetHeight;

            indicadorRef.current.style.top = `${topo}px`;
            indicadorRef.current.style.height = `${altura}px`;
            indicadorRef.current.style.opacity = '1';
        } else {
            indicadorRef.current.style.opacity = '0';
        }
    }, [location.pathname]);

    // Fecha o menu (mobile) automaticamente ao trocar de rota
    useEffect(() => {
        setSidebarOpen(false);
    }, [location.pathname]);

    // Trava o scroll do body quando o modal de saída ou o menu mobile estão abertos
    useEffect(() => {
        document.body.style.overflow = (userExit || sidebarOpen) ? 'hidden' : 'auto';

        return () => {
            document.body.style.overflow = 'auto';
        };
    }, [userExit, sidebarOpen]);

    const primeiroNome = usuario.primeiroNome || 'Usuário';
    const segundoNome = usuario.segundoNome || '';

    return (
        <>
            {/* ALÇA / SETA - visível apenas em telas pequenas (< lg) */}
            <button
                type='button'
                className={`sidebar-handle d-lg-none btn p-0 ${sidebarOpen ? 'is-open' : ''}`}
                onClick={() => setSidebarOpen(prev => !prev)}
                aria-expanded={sidebarOpen}
                aria-controls='mainSidebar'
                aria-label={sidebarOpen ? 'Fechar menu' : 'Abrir menu'}
            >
                <i className={`bi ${sidebarOpen ? 'bi-chevron-left' : 'bi-chevron-right'}`}></i>
            </button>

            {/* BACKDROP - apenas mobile, quando o menu está aberto */}
            {sidebarOpen && (
                <div
                    className='offcanvas-backdrop fade show d-lg-none'
                    onClick={() => setSidebarOpen(false)}
                ></div>
            )}

            <aside
                id='mainSidebar'
                ref={sidebarRef}
                className={`sidebar offcanvas-lg offcanvas-start d-flex flex-column justify-content-between align-items-center py-3 ${sidebarOpen ? 'show' : ''}`}
                tabIndex='-1'
            >
                <div className='w-100 d-flex flex-column align-items-center px-0'>
                    <NavLink to='/app/profile' className='profile d-flex align-items-center gap-2 p-2 rounded-3 mb-2'>
                        <div className='avatar-container flex-shrink-0 rounded-circle d-flex align-items-center justify-content-center overflow-hidden'>
                            {usuario.fotoUrl ? (
                                <img src={usuario.fotoUrl} alt='Foto do usuário' className='avatar-img' />
                            ) : (
                                <span className='fw-bold fs-5'>
                                    {usuario.primeiroNome ? usuario.primeiroNome.charAt(0).toUpperCase() : 'U'}
                                </span>
                            )}
                        </div>
                        <div className='text-truncate'>
                            <p className='cargo text-uppercase mb-0'>{usuario.cargo}</p>
                            <h2 className='name mb-0 text-truncate'>{primeiroNome} {segundoNome}</h2>
                        </div>
                    </NavLink>

                    <p className='welcome w-100 mb-4'>Bem Vindo, {primeiroNome}!</p>

                    <nav className='w-100 d-flex flex-column align-items-center gap-1'>
                        <NavLink to='/app/home' className='sidebar-link d-flex align-items-center gap-2 w-100 rounded-3'>
                            <i className='bi bi-house'></i>
                            <p className='mb-0'>Home</p>
                        </NavLink>

                        <NavLink to='/app/pedidos' className='sidebar-link d-flex align-items-center gap-2 w-100 rounded-3'>
                            <i className='bi bi-file-earmark'></i>
                            <p className='mb-0'>Pedidos</p>
                        </NavLink>

                        <NavLink to='/app/rendimento' className='sidebar-link d-flex align-items-center gap-2 w-100 rounded-3'>
                            <i className='bi bi-graph-up-arrow'></i>
                            <p className='mb-0'>Rendimento</p>
                        </NavLink>

                        <NavLink to='/app/funcionarios' className='sidebar-link d-flex align-items-center gap-2 w-100 rounded-3'>
                            <i className='bi bi-person-vcard'></i>
                            <p className='mb-0'>Funcionários</p>
                        </NavLink>

                        <NavLink to='/app/plantas' className='sidebar-link d-flex align-items-center gap-2 w-100 rounded-3'>
                            <i className='bi bi-cpu'></i>
                            <p className='mb-0'>Plantas</p>
                        </NavLink>

                        <NavLink to='/app/receitas' className='sidebar-link d-flex align-items-center gap-2 w-100 rounded-3'>
                            <i className='bi bi-flask'></i>
                            <p className='mb-0'>Receitas</p>
                        </NavLink>
                    </nav>
                </div>

                <nav className='w-100 d-flex flex-column align-items-center gap-1'>
                    <NavLink to='/app/configuracoes' className='sidebar-link config-btn d-flex align-items-center gap-2 w-100 rounded-3'>
                        <i className='bi bi-gear'></i>
                        <p className='mb-0'>Configurações</p>
                    </NavLink>

                    <button
                        type='button'
                        className='sidebar-link logout-btn d-flex align-items-center gap-2 w-100 rounded-3 border-0 bg-transparent'
                        onClick={() => setUserExit(true)}
                    >
                        <i className='bi bi-box-arrow-left'></i>
                        <p className='mb-0'>Sair da conta</p>
                    </button>
                </nav>

                <div className='indicador-animado' ref={indicadorRef}></div>
            </aside>

            {userExit && (
                <div className='modal fade show d-block' tabIndex='-1' role='dialog'>
                    <div className='modal-dialog modal-dialog-centered'>
                        <div className='modal-content sidebar-modal-content text-center p-4'>
                            <p className='mb-4'>Tem certeza que deseja sair da conta?</p>
                            <div className='d-flex justify-content-center gap-2'>
                                <button
                                    type='button'
                                    className='btn btn-cancel px-4'
                                    onClick={() => setUserExit(false)}
                                >
                                    Cancelar
                                </button>
                                <NavLink
                                    to='/auth'
                                    className='btn btn-danger px-4'
                                    onClick={() => {
                                        localStorage.removeItem('@api:token');
                                        localStorage.removeItem('@api:refresh');
                                        localStorage.removeItem('@api:user');
                                        setUserExit(false);
                                    }}
                                >
                                    Sair
                                </NavLink>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}