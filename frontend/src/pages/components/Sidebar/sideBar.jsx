import Button from "../../app/shared/controls/Button.jsx";
import { useEffect, useRef, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import api from "../../../services/api";
import { useWorkspace } from "../../app/shared/context";
import Modal from "../../app/shared/Modal";
export default function Sidebar({ dados }) {
  const [open, setOpen] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const [busy, setBusy] = useState(false);
  const pointer = useRef(null);
  const aside = useRef(null);
  const { prefs, notify } = useWorkspace();
  const location = useLocation();
  const navigate = useNavigate();
  const roles = { 1: "Preposto", 2: "Chefe", 3: "Funcionário" };
  const links = [
    ["home", "bi-house", "Home"],
    ["pedidos", "bi-file-earmark", "Pedidos"],
    ...(dados.role === 1
      ? [["rendimento", "bi-graph-up-arrow", "Rendimentos"]]
      : []),
    ...(dados.role !== 3
      ? [["funcionarios", "bi-person-vcard", "Funcionários"]]
      : []),
    ["plantas", "bi-cpu", "Plantas"],
    ["receitas", "bi-flask", "Receitas"],
    ...(dados.role === 1
      ? [["administracao", "bi-sliders2", "Administração técnica"]]
      : []),
  ];
  useEffect(() => {
    if (!open) return;
    const close = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", close);
    return () => document.removeEventListener("keydown", close);
  }, [open]);
  const link = ([path, icon, label]) => (
    <NavLink
      key={path}
      to={`/app/${path}`}
      title={label}
      onClick={() => setOpen(false)}
      className="mes-nav-link"
    >
      <i aria-hidden="true" className={`bi ${icon}`} />
      <span>{label}</span>
    </NavLink>
  );
  async function logout() {
    setBusy(true);
    try {
      await api.post("/api/logout/");
      navigate("/auth");
    } catch {
      notify("Não foi possível sair. Tente novamente.", "error");
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <a className="skip-link" href="#main-content">
        Pular para conteúdo
      </a>
      {prefs.sidebar_mobile !== "icones" && (
        <button
          className={`menu-trigger ${prefs.sidebar_mobile === "hamburguer" ? "hamburger" : "pull-handle"} ${open ? "open" : ""}`}
          aria-label={open ? "Fechar menu" : "Abrir menu"}
          aria-expanded={open}
          aria-controls="workspace-sidebar"
          onClick={() => setOpen(!open)}
          onPointerDown={(e) => {
            pointer.current = e.clientX;
            e.currentTarget.setPointerCapture(e.pointerId);
          }}
          onPointerUp={(e) => {
            if (pointer.current !== null && e.clientX - pointer.current > 35)
              setOpen(true);
            pointer.current = null;
          }}
        >
          <i
            aria-hidden="true"
            className={`bi ${prefs.sidebar_mobile === "hamburguer" ? "bi-list" : open ? "bi-chevron-left" : "bi-chevron-right"}`}
          />
        </button>
      )}
      {open && (
        <button
          className="sidebar-backdrop"
          aria-label="Fechar menu"
          onClick={() => setOpen(false)}
        />
      )}
      <aside
        ref={aside}
        id="workspace-sidebar"
        className={`mes-sidebar ${open ? "open" : ""}`}
        aria-label="Menu principal"
        onPointerDown={(e) => {
          pointer.current = e.clientX;
        }}
        onPointerUp={(e) => {
          if (pointer.current !== null && e.clientX - pointer.current < -50)
            setOpen(false);
          pointer.current = null;
        }}
      >
        <NavLink
          to="/app/profile"
          className="sidebar-profile"
          title={`${dados.first_name} · ${roles[dados.role]}`}
          onClick={() => setOpen(false)}
        >
          <div className="user-avatar">
            {dados.fotoUrl ? (
              <img src={dados.fotoUrl} alt="" />
            ) : (
              dados.first_name?.charAt(0) || "U"
            )}
          </div>
          <div className="profile-copy">
            <small>{roles[dados.role]}</small>
            <strong>
              {dados.first_name} {dados.last_name}
            </strong>
          </div>
        </NavLink>
        <p className="sidebar-welcome">Bem-vindo, {dados.first_name}!</p>
        <nav className="sidebar-primary" key={location.pathname}>
          {links.map(link)}
        </nav>
        <nav className="sidebar-bottom">
          {dados.role === 1 &&
            link(["atualizacoes", "bi-clock-history", "Últimas atualizações"])}
          {link(["configuracoes", "bi-gear", "Configurações"])}
          <button
            className="mes-nav-link logout-link"
            title="Sair da conta"
            onClick={() => setLeaving(true)}
          >
            <i aria-hidden="true" className="bi bi-box-arrow-left" />
            <span>Sair da conta</span>
          </button>
        </nav>
      </aside>
      {leaving && (
        <Modal
          title="Sair da conta?"
          onClose={() => {
            if (!busy) setLeaving(false);
          }}
        >
          <p>Você poderá continuar sua operação ao entrar novamente.</p>
          <div className="form-actions">
            <Button
              className="secondary"
              disabled={busy}
              onClick={() => setLeaving(false)}
            >
              Continuar aqui
            </Button>
            <Button className="danger" disabled={busy} onClick={logout}>
              {busy ? "Saindo…" : "Sair"}
            </Button>
          </div>
        </Modal>
      )}
    </>
  );
}
