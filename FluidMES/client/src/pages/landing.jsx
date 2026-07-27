import { Link } from 'react-router-dom'

function Landing() {
    return (
        <div className='container' style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center', height: '80vh' }}>
            <header style={{ marginBottom: '30px' }}>
                <h1 style={{ fontSize: '2.8rem', color: '#00adb5', margin: '0' }}>Gerenciador de Tarefas</h1>
                <p style={{ fontSize: '1.1rem', color: '#000000', marginTop: '10px' }}>
                    Organize sua rotina e gerencie seus focos diários em um ambiente moderno.
                </p>
            </header>

            <main style={{ marginBottom: '40px' }}>
                <div style={{ background: '#252930', padding: '25px', borderRadius: '8px', maxWidth: '450px', margin: '0 auto', border: '1px solid #333' }}>
                    <h3 style={{ color: '#000000', marginTop: '0' }}>Funcionalidades principais</h3>
                    <ul style={{ textAlign: 'left', marginTop: '15px', color: '#ccc', lineHeight: '1.8', listStyleType: 'none', padding: '0' }}>
                        <li>✅ Criação e exclusão de tarefas em tempo real</li>
                        <li>⏳ Controle de status (Pendentes e Concluídas)</li>
                        <li>🔒 Segurança ponta a ponta com autenticação JWT</li>
                    </ul>
                </div>
            </main>

            <div>
                <Link
                    to="/auth"
                    style={{
                        background: '#00adb5',
                        color: '#fff',
                        padding: '14px 40px',
                        borderRadius: '5px',
                        fontSize: '1.1rem',
                        textDecoration: 'none',
                        fontWeight: 'bold',
                        display: 'inline-block',
                        transition: 'background 0.2s'
                    }}
                >
                    Começar Agora <i className='bx bx-right-arrow-alt' style={{ verticalAlign: 'middle', marginLeft: '5px' }}></i>
                </Link>
            </div>
        </div>
    )
}

export default Landing
