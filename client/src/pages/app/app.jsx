import { useState, useEffect } from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar/sideBar.jsx';
import api from '../../services/api.js';
import './style.css'

export default function App() {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(true);
    const [dadosUsuario, setDadosUsuario] = useState(null); 

    useEffect(() => {
        async function carregarDadosUsuario() {
            try {

                const response = await api.get('/api/me/');
                console.log(response);


                setDadosUsuario(response.data);
                setIsLoading(false);

            } catch (error) {
                console.error('Erro ao buscar dados do usuário:', error);
                
                //Se estiver em test retirar o navigate
                if (error.response && error.response.status === 401) {
                    navigate('/auth');
                }
                setIsLoading(false); 
            }
        }
        carregarDadosUsuario();
    }, [navigate]);

    if (isLoading) {
        return <div className="spinner">Verificando permissão<span>.</span><span>.</span><span>.</span></div>; 
    }

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
            {/* SIDEBAR */}
            <Sidebar dados={dadosUsuario} />

            {/* CONTENT */}
            <main style={{ flex: 1, overflowY: 'auto', padding: '24px', backgroundColor: '#101629' }}>
                <Outlet />
            </main>
        </div>
    );
}