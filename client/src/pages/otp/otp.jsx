import { useState, useRef } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import Particles from '../components/Particles/particles.jsx';
import api from '../../services/api.js';
import './style.css';

export default function OTP() {
    const navigate = useNavigate();
    const location = useLocation();

    const inputRefs = useRef([]);

    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [erro, setErro] = useState('');
    const [sucesso, setSucesso] = useState('');
    const [loading, setLoading] = useState(false);

    // E-mail enviado pela tela anterior
    const email = location.state?.email || '';

    function handleChange(value, index) {
        if (!/^\d*$/.test(value)) return;

        const novoOtp = [...otp];
        novoOtp[index] = value.slice(-1);

        setOtp(novoOtp);
        setErro('');
        setSucesso('');

        // Avança automaticamente para o próximo campo
        if (value && index < otp.length - 1) {
            inputRefs.current[index + 1]?.focus();
        }
    }

    function handleKeyDown(e, index) {
        if (
            e.key === 'Backspace' &&
            !otp[index] &&
            index > 0
        ) {
            inputRefs.current[index - 1]?.focus();
        }
    }

    function handlePaste(e) {
        e.preventDefault();

        const codigo = e.clipboardData
            .getData('text')
            .replace(/\D/g, '')
            .slice(0, 6);

        if (!codigo) return;

        const novoOtp = ['', '', '', '', '', ''];

        codigo.split('').forEach((numero, index) => {
            novoOtp[index] = numero;
        });

        setOtp(novoOtp);

        const proximoCampo = Math.min(codigo.length, 5);

        inputRefs.current[proximoCampo]?.focus();
    }

    async function enviarCodigo(e) {
        e.preventDefault();

        const codigo = otp.join('');

        if (codigo.length !== 6) {
            setErro('Digite o código completo de 6 dígitos.');
            return;
        }

        setErro('');
        setSucesso('');
        setLoading(true);

        try {
            await api.post('/api/verify-otp/', {
                email,
                otp: codigo
            });

            setSucesso('Código verificado com sucesso!');

            setTimeout(() => {
                navigate('/auth/reset-password', {
                    state: {
                        email,
                        otp: codigo
                    }
                });
            }, 800);

        } catch (error) {
            setErro(
                error.response?.data?.erro ||
                'Código inválido ou expirado.'
            );
        } finally {
            setLoading(false);
        }
    }

    async function reenviarCodigo() {
        setErro('');
        setSucesso('');

        try {
            await api.post('/api/forgot-password/', {
                email
            });

            setSucesso('Um novo código foi enviado para seu e-mail.');

            setOtp(['', '', '', '', '', '']);

            inputRefs.current[0]?.focus();

        } catch (error) {
            setErro(
                error.response?.data?.erro ||
                'Não foi possível reenviar o código.'
            );
        }
    }

    return (
        <div className="auth-page otp-page container-fluid p-0">

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
                    onSubmit={enviarCodigo}
                    className="otp-form w-100 mx-auto"
                >

                    <div className="otp-icon">
                        <i className="bi bi-shield-lock"></i>
                    </div>

                    <h2>Verificação</h2>

                    <p className="subtitle">
                        Digite o código de 6 dígitos enviado para
                        {email && (
                            <strong> {email}</strong>
                        )}
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

                    <div
                        className="otp-inputs"
                        onPaste={handlePaste}
                    >
                        {otp.map((numero, index) => (
                            <input
                                key={index}
                                ref={(element) => {
                                    inputRefs.current[index] = element;
                                }}
                                type="text"
                                inputMode="numeric"
                                maxLength="1"
                                value={numero}
                                onChange={(e) =>
                                    handleChange(
                                        e.target.value,
                                        index
                                    )
                                }
                                onKeyDown={(e) =>
                                    handleKeyDown(e, index)
                                }
                                autoComplete={
                                    index === 0
                                        ? 'one-time-code'
                                        : 'off'
                                }
                                aria-label={`Dígito ${index + 1}`}
                            />
                        ))}
                    </div>

                    <button
                        type="submit"
                        className="btn-submit"
                        disabled={loading}
                    >
                        {loading
                            ? 'Verificando...'
                            : 'Verificar código'}
                    </button>

                    <div className="resend-code">
                        <span>
                            Não recebeu o código?
                        </span>

                        <button
                            type="button"
                            onClick={reenviarCodigo}
                        >
                            Reenviar código
                        </button>
                    </div>

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
