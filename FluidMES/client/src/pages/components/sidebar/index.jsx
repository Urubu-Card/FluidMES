import { useState, useEffect, useRef } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import './style.css';

export default function Sidebar() {
    const location = useLocation(); // Escuta as mudanças de rota
    const sidebarRef = useRef(null); // Referência para a sidebar
    const indicadorRef = useRef(null); // Referência para a barra verde

    const [dropdown, setDropdown] = useState(false);
    const [userExit, setUserExit] = useState(false);

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
                // Recupera o token salvo no localStorage para autenticar a chamada
                const token = localStorage.getItem('@api:token');

                // Mantida a URL completa para evitar erros de rota no Front-end
                const response = await fetch('http://localhost:3000/api/profile', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}` 
                    }
                });

                if (!response.ok) {
                    throw new Error('Não foi possível carregar os dados do perfil.');
                }

                const dados = await response.json();
                
                setUsuario({
                    nome: dados.nome || 'Usuário',
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

    useEffect(() => {
        if (!sidebarRef.current || !indicadorRef.current) return;

        const linkAtivo = sidebarRef.current.querySelector('aside a.active');

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

    useEffect(() => {
        if (userExit) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'auto';
        }

        return () => {
            document.body.style.overflow = 'auto';
        };
    }, [userExit]);

    const primeiroNome = usuario.nome ? usuario.nome.split(' ')[0] : 'Usuário';
    const segundoNome = usuario.nome ? usuario.nome.split(' ')[1] : 'Usuário';

    return (
        <>
            <aside ref={sidebarRef}>
                <div>
                    <NavLink to='/app/profile' className='profile'>
                        <div className='avatar-container'>
                            {usuario.fotoUrl ? (
                                <img src={usuario.fotoUrl} alt='Foto do usuário' className='avatar-img' />
                            ) : (
                                <span className='avatar-placeholder'>
                                    {usuario.nome ? usuario.nome.charAt(0).toUpperCase() : 'U'}
                                </span>
                            )}
                        </div>
                        <div>
                            <p className='cargo'>{usuario.cargo}</p>
                            <h2 className='name'>{primeiroNome} {segundoNome}</h2>
                        </div>
                    </NavLink>
                    <p className='welcome'>Bem Vindo, {primeiroNome}!</p>
                    <nav>
                        {/* HOME */}
                        <NavLink to='/app/home'>
                            <i className='bi bi-house'></i>
                            <p>Home</p>
                        </NavLink>

                        {/* PEDIDOS */}
                        <NavLink to='/app/pedidos'>
                            <i className='bi bi-file-earmark'></i>
                            <p>Pedidos</p>
                        </NavLink>

                        {/* RENDIMENTO */}
                        <NavLink to='/app/rendimento'>
                            <i className='bi bi-graph-up-arrow'></i>
                            <p>Rendimento</p>
                        </NavLink>

                        {/* FUNCIONÁRIOS */}
                        <NavLink to='/app/funcionarios'>
                            <i className='bi bi-person-vcard'></i>
                            <p>Funcionários</p>
                        </NavLink>

                        {/* PLANTAS */}
                        <NavLink to='/app/plantas'>
                            <i className='bi bi-cpu'></i>
                            <p>Plantas</p>
                        </NavLink>

                        {/* RECEITAS */}
                        <NavLink to='/app/receitas'>
                            <i className='bi bi-flask'></i>
                            <p>Receitas</p>
                        </NavLink>
                    </nav>
                </div>
                <nav>
                    {/* CONFIGURAÇÕES */}
                    <NavLink to='/app/configuracoes' className='config-btn'>
                        <i className='bi bi-gear'></i>
                        <p>Configurações</p>
                    </NavLink>

                    {/* SAIR */}
                    <button className='logout-btn' onClick={() => setUserExit(true)}>
                        <i className='bi bi-box-arrow-left'></i>
                        <p>Sair da conta</p>
                    </button>
                </nav>

                <div className='indicador-animado' ref={indicadorRef}></div>
            </aside>

            {userExit && (
                <div className='bg-modal'>
                    <div className='modal-content'>
                        <p>Tem certeza que deseja sair da conta?</p>
                        <button onClick={() => setUserExit(false)}>Cancelar</button>
                        <NavLink to='/auth' onClick={() => {
                            localStorage.removeItem('@api:token');
                            setUserExit(false);
                        }}>Sair</NavLink>
                    </div>
                </div>
            )}
        </>
    );
}
