import { StrictMode, lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";

import "./index.css";

const LandingPage = lazy(() => import("./pages/landing/landing.jsx"));
const Auth = lazy(() => import("./pages/auth/auth.jsx"));
const ForgotPassword = lazy(() => import("./pages/forgot/forgot.jsx"));
const App = lazy(() => import("./pages/app/app.jsx"));
const ResetPassword = lazy(() => import("./pages/forgot/reset.jsx"));

// PAGINAS INTERNAS
const Home = lazy(() => import("./pages/app/home/home.jsx"));
const Pedidos = lazy(() => import("./pages/app/pedidos/pedidos.jsx"));
const Rendimento = lazy(
  () => import("./pages/app/rendimentos/rendimentos.jsx"),
);
const Funcionarios = lazy(
  () => import("./pages/app/funcionarios/funcionarios.jsx"),
);
const Plantas = lazy(() => import("./pages/app/plantas/plantas.jsx"));
const Receitas = lazy(() => import("./pages/app/receitas/receitas.jsx"));
const Configuracoes = lazy(
  () => import("./pages/app/configuracoes/config.jsx"),
);
const Administracao = lazy(
  () => import("./pages/app/administracao/administracao.jsx"),
);
const Atualizacoes = lazy(
  () => import("./pages/app/atualizacoes/atualizacoes.jsx"),
);
const Profile = lazy(() => import("./pages/app/profile/profile.jsx"));

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <Suspense fallback={<p role="status">Carregando…</p>}>
        <Routes>
          {/* LANDING PAGE */}
          <Route path="/" element={<LandingPage />} />

          {/* LOGIN E CADASTRO */}
          <Route path="/auth" element={<Auth />} />
          {/* ESQUECI MINHA SENHA */}
          <Route path="/auth/forgot-password" element={<ForgotPassword />} />
          <Route path="/auth/reset-password" element={<ResetPassword />} />

          {/* PAINEL DO SISTEMA (Agrupado sob a rota /app) */}
          <Route path="/app" element={<App />}>
            {/* apenas '/app', direto para a Home */}
            <Route index element={<Navigate to="/app/home" replace />} />

            {/* SUB-ROTAS */}
            <Route path="home" element={<Home />} />
            <Route path="administracao" element={<Administracao />} />
            <Route path="atualizacoes" element={<Atualizacoes />} />
            <Route path="profile" element={<Profile />} />
            <Route path="pedidos" element={<Pedidos />} />
            <Route path="rendimento" element={<Rendimento />} />
            <Route path="funcionarios" element={<Funcionarios />} />
            <Route path="plantas" element={<Plantas />} />
            <Route path="receitas" element={<Receitas />} />
            <Route path="configuracoes" element={<Configuracoes />} />
          </Route>

          {/* Fallback de segurança: qualquer rota desconhecida vai para a Landing Page */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  </StrictMode>,
);
