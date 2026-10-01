import { useState, useEffect } from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar/sideBar.jsx';
import api from '../../services/api.js';
import './style.css';

export default function App() {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(true);
    const [dadosUsuario, setDadosUsuario] = useState(null);

    useEffect(() => {
        async function carregarDadosUsuario() {
            try {
                const response = await api.get('/api/me/');
                setDadosUsuario(response.data);
                setIsLoading(false);
            } catch (error) {
                console.error('Erro ao buscar dados do usuário:', error);
                if (error.response && error.response.status === 401) {
                    navigate('/auth');
                }
                setIsLoading(false);
            }
        }
        carregarDadosUsuario();
    }, [navigate]);

    return (
        <div className='app-shell d-flex min-vh-100 vw-100' style={{ position: 'relative' }}>

            {/* TELA DE CARREGAMENTO COM TRANSIÇÃO */}
            <div
                className="d-flex justify-content-center align-items-center"
                style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '100vw',
                    height: '100vh',
                    backgroundColor: 'var(--azul-petroleo)', 
                    transition: 'opacity 0.4s ease-in-out, visibility 0.4s ease-in-out',
                    opacity: isLoading ? 1 : 0,
                    visibility: isLoading ? 'visible' : 'hidden',
                    zIndex: 9999 // Garante que fica por cima de tudo
                }}
            >
                <div
                    className="spinner-border text-primary"
                    style={{ width: '7rem', height: '7rem' }}
                    role="status"
                >
                    <span className="visually-hidden">Carregando...</span>
                </div>
            </div>

            {/* SIDEBAR */}
            <Sidebar dados={dadosUsuario} />

            {/* CONTENT */}
            <main className='app-main flex-grow-1 overflow-y-auto p-3 p-lg-4'>
                <Outlet />
            </main>
        </div>
    );
}
