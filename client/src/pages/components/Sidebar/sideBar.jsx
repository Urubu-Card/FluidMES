import { useState, useEffect, useRef } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import './style.css';
import api from '../../../services/api.js';


export default function Sidebar({ dados }) {
    const cargos = { 3: 'Funcionário', 2: 'Chefe', 1: 'Preposto' };
    const location = useLocation();
    const sidebarRef = useRef(null);
    const indicadorRef = useRef(null);

    const [userExit, setUserExit] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const primeiroNome = dados?.first_name || 'Usuário';
    const segundoNome = dados?.last_name || '';
    const cargo = cargos[dados?.role] || 'Cargo Desconhecido';
    const fotoUrl = dados?.fotoUrl || null;

    useEffect(() => {
        if (!sidebarRef.current || !indicadorRef.current) return;


        setTimeout(() => {
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
        }, 0);
    }, [location.pathname]);

    useEffect(() => {
        document.body.style.overflow = (userExit || sidebarOpen) ? 'hidden' : 'auto';

        return () => {
            document.body.style.overflow = 'auto';
        };
    }, [userExit, sidebarOpen]);

    return (
        <>
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
                            {fotoUrl ? (
                                <img src={fotoUrl} alt='Foto do usuário' className='avatar-img' />
                            ) : (
                                <span className='fw-bold fs-5'>
                                    {primeiroNome ? primeiroNome.charAt(0).toUpperCase() : 'U'}
                                </span>
                            )}
                        </div>
                        <div className='text-truncate'>
                            <p className='cargo text-uppercase mb-0'>{cargo}</p>
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
                        {(dados?.role !== 3) && (
                            <>
                                {(dados?.role !== 2) && (
                                    <NavLink to='/app/rendimento' className='sidebar-link d-flex align-items-center gap-2 w-100 rounded-3'>
                                        <i className='bi bi-graph-up-arrow'></i>
                                        <p className='mb-0'>Rendimento</p>
                                    </NavLink>
                                )}
                                <NavLink to='/app/funcionarios' className='sidebar-link d-flex align-items-center gap-2 w-100 rounded-3'>
                                    <i className='bi bi-person-vcard'></i>
                                    <p className='mb-0'>Funcionários</p>
                                </NavLink>
                            </>
                        )}
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
                                        api.post("/api/logout/")
                                    }}
                                >
                                    Sair
                                </NavLink>
                            </div>
                        </div>
                    </div>
                </div >
            )}
        </>
    );
}