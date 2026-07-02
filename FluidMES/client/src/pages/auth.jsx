import { useState, useRef } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import { PatternFormat } from 'react-number-format';
import api from '../services/api.js';

export default function Auth() {
    const formRef = useRef(null);
    // true = Tela de Login | false = Tela de Cadastro
    const [isLogin, setIsLogin] = useState(true);
    const [erro, setErro] = useState('');
    const navigate = useNavigate();

    // Estados dos inputs compartilhados e específicos
    const [cpf, setCpf] = useState('');
    const [password, setPassword] = useState('');

    // Estados exclusivos do cadastro
    const [nomeEmpresa, setNomeEmpresa] = useState('');
    const [cnpj, setCnpj] = useState('');
    const [nome, setNome] = useState('');
    const [email, setEmail] = useState('');

    // Limpa os estados para esvaziar os inputs controlados da tela
    function limparCampos() {
        if (formRef.current) {
            formRef.current.reset();
        }
        setCpf('');
        setPassword('');
        setNomeEmpresa('');
        setCnpj('');
        setNome('');
        setEmail('');
        setErro('');
    }

    async function enviarSubmit(e) {
        e.preventDefault();
        setErro('');

        try {
            if (isLogin) {
                const response = await api.post('/api/token', {
                    username: cpf,
                    password
                });
                localStorage.setItem('@api:token', response.data.access);
                navigate('/app');
            } else {
                await api.post('/api/cadastro', {
                    nomeEmpresa,
                    cnpj,
                    nome,
                    email,
                    username: cpf,
                    password
                });

                alert('Cadastro realizado com sucesso! Faça seu login.');
                setIsLogin(true);
                limparCampos();
            }
        } catch (error) {
            setErro(error.response?.data?.erro || 'Erro ao processar a requisição.');
        }
    }

    return (
        <div className='auth-page'>
            <header>
                <NavLink to='/' className='logo'>
                    FluidMES
                </NavLink>
            </header>
            <form ref={formRef} onSubmit={enviarSubmit}>
                <h2>Bem-vindo a FluidMES</h2>
                <p>{isLogin ? 'Faça login para continuar' : 'Crie sua conta para começar'}</p>
                {erro && <p className='error-text'>{erro}</p>}

                {/* ─── MODO CADASTRO ─── */}
                {!isLogin && (
                    <div className='columns'>
                        {/* Coluna Empresarial */}
                        <div className='column'>
                            <p className='col-title'>Empresarial :</p>
                            <div className='user-pass'>
                                <input
                                    type='text'
                                    placeholder='Nome da Empresa'
                                    required
                                    value={nomeEmpresa}
                                    onChange={e => setNomeEmpresa(e.target.value)}
                                />
                                <i className='bi bi-briefcase'></i>
                            </div>
                            <div className='user-pass'>
                                <PatternFormat
                                    type='text'
                                    format='##.###.###/####-##'
                                    placeholder='CNPJ'
                                    required
                                    value={cnpj}
                                    onValueChange={(values) => setCnpj(values.value)}
                                />
                                <i className='bi bi-person-vcard'></i>
                            </div>
                        </div>

                        <div className='divider-v'></div>

                        {/* Coluna Pessoal */}
                        <div className='column'>
                            <p className='col-title'>Pessoal :</p>
                            <div className='user-pass'>
                                <PatternFormat
                                    type='text'
                                    format='###.###.###-##'
                                    placeholder='CPF'
                                    required
                                    value={cpf}
                                    onValueChange={(values) => setCpf(values.value)}
                                />
                                <i className='bi bi-person-vcard'></i>
                            </div>
                            <div className='user-pass'>
                                <input
                                    type='text'
                                    placeholder='Nome Completo'
                                    required
                                    value={nome}
                                    onChange={e => setNome(e.target.value)}
                                />
                                <i className='bi bi-person'></i>
                            </div>
                            <div className='user-pass'>
                                <input
                                    type='email'
                                    placeholder='E-mail'
                                    required
                                    value={email}
                                    onChange={e => setEmail(e.target.value)}
                                />
                                <i className='bi bi-envelope'></i>
                            </div>
                            <div className='user-pass'>
                                <input
                                    type='password'
                                    placeholder='Senha'
                                    required
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                />
                                <i className='bi bi-lock'></i>
                            </div>
                        </div>
                    </div>
                )}

                {/* ─── MODO LOGIN ─── */}
                {isLogin && (
                    <div className='column'>
                        <div className='user-pass'>
                            <PatternFormat
                                type='text'
                                format='###.###.###-##'
                                placeholder='CPF'
                                required
                                value={cpf}
                                onValueChange={(values) => setCpf(values.value)}
                            />
                            <i className='bi bi-person-vcard'></i>
                        </div>

                        <div>
                            <div className='user-pass'>
                                <input
                                    type='password'
                                    placeholder='Senha'
                                    required
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                />
                                <i className='bi bi-lock'></i>
                            </div>
                            <NavLink to='/auth/forgot-password' className='forgot'>
                                Esqueci a senha
                            </NavLink>
                        </div>
                    </div>
                )}

                <button type='submit' className='btn-submit'>
                    {isLogin ? 'Fazer Login' : 'Cadastrar Empresa'}
                </button>

                {/* ALTERNADOR DE TELAS */}
                <div className='toggle-container'>
                    {isLogin ? (
                        <p>
                            Não tem uma conta?{' '}
                            <span
                                className='toggle-link'
                                onClick={() => { setIsLogin(false); limparCampos(); }}
                            >
                                Cadastre-se aqui
                            </span>
                        </p>
                    ) : (
                        <p>
                            Já possui uma conta?{' '}
                            <span
                                className='toggle-link'
                                onClick={() => { setIsLogin(true); limparCampos(); }}
                            >
                                Faça o Login
                            </span>
                        </p>
                    )}
                </div>
            </form>
        </div>
    )
}