import { useState, useRef } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import Particles from '../components/Particles/particles.jsx';
import api from '../../services/api.js';
import './style.css';

export default function ForgotPassword() {
    const formRef = useRef(null);
    const navigate = useNavigate();

    const [email, setEmail] = useState('');
    const [erro, setErro] = useState('');
    const [sucesso, setSucesso] = useState('');

    async function enviarSubmit(e) {
        e.preventDefault();

        setErro('');
        setSucesso('');

        try {
            await api.post('/api/forgot-password/', {
                email
            });

            setSucesso(
                'Se o e-mail estiver cadastrado, você receberá as instruções para redefinir sua senha.'
            );

            setEmail('');
            formRef.current?.reset();

        } catch (error) {
            setErro(
                error.response?.data?.erro ||
                'Erro ao solicitar a recuperação da senha.'
            );
        }
    }

    return (
        <div className="auth-page forgot-page container-fluid p-0">

            <div className="login-active">
                <Particles
                    quantity={65}
                    color="#3E7DFF"
                    speed={2.5}
                    lineDistance={200}
                />
            </div>

            <div className="content w-100">
                <header className="d-flex align-items-center px-3 px-md-4">
                    <NavLink to="/">
                        FluidMES
                    </NavLink>
                </header>

                <form
                    ref={formRef}
                    onSubmit={enviarSubmit}
                    className="forgot-form w-100 mx-auto"
                >

                    <h2>Esqueci a senha</h2>
                    <p className="subtitle">
                        Informe seu e-mail para recuperar o acesso à sua conta
                    </p>

                    {erro && (
                        <p className="error-text">
                            {erro}
                        </p>
                    )}

                    {sucesso && (
                        <p className="success-text">
                            {sucesso}
                        </p>
                    )}

                    <div className="user-pass">
                        <input
                            type="email"
                            placeholder="E-mail"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                        <i className="bi bi-envelope"></i>
                    </div>
                    <button type="submit" className="btn-submit">
                        Enviar instruções
                    </button>
                    <div className="back-login">
                        <NavLink to="/auth">
                            <i className="bi bi-arrow-left"></i>
                            Voltar para o login
                        </NavLink>
                    </div>
                </form>
            </div>
        </div>
    );
}