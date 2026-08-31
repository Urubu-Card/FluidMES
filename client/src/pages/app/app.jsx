import { useState, useEffect } from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import Sidebar from '../components/sidebar/sideBar.jsx';
import api from '../../services/api.js';

export default function App() {
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(true);
    const [dadosUsuario, setDadosUsuario] = useState(null); 

    useEffect(() => {
        async function carregarDadosUsuario() {
            try {
                const token = localStorage.getItem('@api:token');

                // 2. Removido o method: 'POST' de dentro do api.get
                const response = await api.get('/api/me/', {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });

                // 3. Atualiza o estado com os dados recebidos (sem await)
                setDadosUsuario(response.data);
                setIsLoading(false);

            } catch (error) {
                console.error('Erro ao buscar dados do usuário:', error);
                
                // 4. A checagem do 401 Unauthorized agora fica no catch
                if (error.response && error.response.status === 401) {
                    navigate('/auth');
                }
                
                // Opcional: tirar o loading mesmo se falhar
                setIsLoading(false); 
            }
        }

        carregarDadosUsuario();
    }, [navigate]);

    if (isLoading) {
        return <div className="spinner">Verificando permissão...</div>; 
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