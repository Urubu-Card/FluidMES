import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import './index.css'

import LandingPage from './pages/landing/landing.jsx'
import Auth from './pages/auth/auth.jsx'
import ForgotPassword from './pages/forgot/forgot.jsx'
import App from './pages/app/app.jsx'


// PAGINAS INTERNAS
import Home from './pages/app/home/home.jsx'
import Pedidos from './pages/app/pedidos/pedidos.jsx'
import Rendimento from './pages/app/rendimentos/rendimentos.jsx'
import Funcionarios from './pages/app/funcionarios/funcionarios.jsx'
import Plantas from './pages/app/plantas/plantas.jsx'
import Receitas from './pages/app/receitas/receitas.jsx'
import Configuracoes from './pages/app/configuracoes/config.jsx'
import Profile from './pages/app/profile/profile.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        {/* LANDING PAGE */}
        <Route path='/' element={<LandingPage />} />

        {/* LOGIN E CADASTRO */}
        <Route path='/auth' element={<Auth />} />
        {/* ESQUECI MINHA SENHA */}
        <Route path='/auth/forgot-password' element={<ForgotPassword />} />

        {/* PAINEL DO SISTEMA (Agrupado sob a rota /app) */}
        <Route path='/app' element={<App />}>
          {/* apenas '/app', direto para a Home */}
          <Route index element={<Navigate to='/app/home' replace />} />
          
          {/* SUB-ROTAS */}
          <Route path='home' element={<Home />} />
          <Route path='profile' element={<Profile />} />
          <Route path='pedidos' element={<Pedidos />} />
          <Route path='rendimento' element={<Rendimento />} />
          <Route path='funcionarios' element={<Funcionarios />} />
          <Route path='plantas' element={<Plantas />} />
          <Route path='receitas' element={<Receitas />} />
          <Route path='configuracoes' element={<Configuracoes />} />
        </Route>

        {/* Fallback de segurança: qualquer rota desconhecida vai para a Landing Page */}
        <Route path='*' element={<Navigate to='/' />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>
)
