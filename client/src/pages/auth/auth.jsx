import { useState, useRef } from 'react';
import { useNavigate, NavLink } from 'react-router-dom';
import { PatternFormat } from 'react-number-format';
import Particles from '../components/Particles/particles.jsx';
import api from '../../services/api.js';
import axios from 'axios';
import './style.css';

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
    const [primeiroNome, setPrimeiroNome] = useState('');
    const [ultimoNome, setUltimoNome] = useState('');
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
        setPrimeiroNome('');
        setUltimoNome('');
        setEmail('');
        setErro('');
    }

    async function enviarSubmit(e) {
        e.preventDefault();
        setErro('');

        try {
            if (isLogin) {
                const response = await api.post('/api/login/', {
                    usuario: cpf, email,
                    password
                });
                /*
                localStorage.setItem('@api:token', response.data.acess);
                localStorage.setItem('@api:refresh', response.data.refresh);
                */
                navigate('/app');
            } else {
                await api.post('/api/cadastro/', {
                    first_name: primeiroNome,
                    last_name: ultimoNome,
                    email,
                    cpf,
                    password,
                    nomeEmpresa,
                    cnpj,
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
        <div className='auth-page container-fluid p-0'>
            <div className={`${isLogin ? 'login-active' : 'login-inactive'}`}>
                {<Particles 
                    quantity={35}
                    color="#3E7DFF"
                    speed={5.5}
                    lineDistance={200}
                />}
            </div>

            <div className='content w-100'>
                <header className='d-flex align-items-center px-3 px-md-4'>
                    <NavLink to="/">
                        FluidMES
                    </NavLink>
                </header>
                
                <form ref={formRef} onSubmit={enviarSubmit} className={`w-100 mx-auto ${isLogin ? 'auth-login' : 'auth-register'}`}>
                    <h2>{isLogin ? 'Entrar':'Cadastrar-se'}</h2>
                    <p className='subtitle'>{isLogin ? 'Faça login para acessar sua conta' : 'Crie sua conta para começar'}</p>
                    {erro && <p className='error-text'>{erro}</p>}

                    {/* ─── MODO CADASTRO ─── */}
                    {!isLogin && (
                        <div className='row g-4'>
                            {/* Coluna Empresarial */}
                            <div className='coline col-12 col-md-6'>
                                <p className='col-title'>Empresarial :</p>
                                <div className='user-pass'>
                                    <input
                                        type='text'
                                        placeholder='Nome da Empresa'
                                        required
                                        className=''
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

                            

                            {/* Coluna Pessoal */}
                            <div className=' col-12 col-md-6'>
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
                                        placeholder='Primeiro Nome'
                                        required
                                        value={primeiroNome}
                                        onChange={e => setPrimeiroNome(e.target.value)}
                                    />
                                    <i className='bi bi-person'></i>
                                </div>
                                <div className='user-pass'>
                                    <input
                                        type='text'
                                        placeholder='Último Nome'
                                        required
                                        value={ultimoNome}
                                        onChange={e => setUltimoNome(e.target.value)}
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
                    
                        <div className='row g-4'>
                            <div>
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
                                <NavLink to='/app' className='secret'>
                                    Entrada Secreta
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
        </div>
    );
}
