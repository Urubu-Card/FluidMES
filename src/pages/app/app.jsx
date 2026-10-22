import { useCallback, useEffect, useState } from "react";
import { Link, Navigate, Outlet, useLocation } from "react-router-dom";
import Sidebar from "../components/Sidebar/sideBar";
import api from "../../services/api";
import { WorkspaceContext } from "./shared/context";
import { errorMessage } from "../../services/errors";
import "./workspace.css";
export default function App() {
  const [session, setSession] = useState(null);
  const [prefs, setPrefs] = useState({
    tema: "sistema",
    sidebar_desktop: "aberta",
    sidebar_mobile: "puxador",
  });
  const [error, setError] = useState("");
  const [toasts, setToasts] = useState([]);
  const [deviceDark, setDeviceDark] = useState(
    () =>
      !window.matchMedia ||
      window.matchMedia("(prefers-color-scheme: dark)").matches ||
      !window.matchMedia("(prefers-color-scheme: light)").matches,
  );
  const location = useLocation();
  useEffect(() => {
    let active = true;
    Promise.all([api.get("/api/me/"), api.get("/api/preferencias/")])
      .then(([user, preferences]) => {
        if (active) {
          setSession(user.data);
          setPrefs(preferences.data);
        }
      })
      .catch((e) => {
        if (active) setError(errorMessage(e));
      });
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    const query = window.matchMedia("(prefers-color-scheme: light)");
    const update = () => setDeviceDark(!query.matches);
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);
  const notify = useCallback((message, type = "success") => {
    const id =
      globalThis.crypto?.randomUUID?.() ??
      `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    setToasts((old) => [
      ...old.filter((item) => item.message !== message).slice(-1),
      { id, message, type },
    ]);
    setTimeout(
      () => setToasts((old) => old.filter((toast) => toast.id !== id)),
      4000,
    );
  }, []);
  const theme =
    prefs.tema === "sistema"
      ? deviceDark
        ? "dark"
        : "light"
      : prefs.tema === "claro"
        ? "light"
        : "dark";
  const path = location.pathname.split("/").at(-1);
  const blocked =
    session &&
    ((["rendimento", "administracao", "atualizacoes"].includes(path) &&
      session.role !== 1) ||
      (path === "funcionarios" && session.role === 3));
  if (!session)
    return (
      <main className="session-loading">
        <h1>FluidMES</h1>
        {error ? (
          <>
            <p role="alert">{error}</p>
            <button onClick={() => window.location.reload()}>
              Tentar novamente
            </button>
            <Link to="/auth">Ir para login</Link>
          </>
        ) : (
          <p role="status">Preparando seu espaço de trabalho…</p>
        )}
      </main>
    );
  if (!session.empresa)
    return (
      <Navigate
        to="/auth"
        replace
        state={{
          authError:
            "Esta conta não está vinculada a uma empresa. Entre com outra conta ou solicite ao responsável a correção do vínculo.",
        }}
      />
    );
  return (
    <WorkspaceContext.Provider
      value={{ user: session, prefs, setPrefs, notify }}
    >
      <div
        className="mes-shell"
        data-theme={theme}
        data-bs-theme={theme}
        data-desktop={prefs.sidebar_desktop}
        data-mobile={prefs.sidebar_mobile}
      >
        <Sidebar dados={session} />
        <main className="mes-main" id="main-content">
          {blocked ? (
            <section className="mes-page">
              <h1>Acesso reservado</h1>
              <p>Esta área não está disponível para o seu cargo.</p>
              <Link to="/app/home">Voltar à Home</Link>
            </section>
          ) : (
            <Outlet context={session} />
          )}
        </main>
        <div className="toast-stack" aria-live="polite">
          {toasts.map((toast) => (
            <div className={`mes-toast ${toast.type}`} key={toast.id}>
              <i
                aria-hidden="true"
                className={`bi ${toast.type === "error" ? "bi-exclamation-circle" : "bi-check-circle"}`}
              />
              <span>{toast.message}</span>
              <button
                aria-label="Dispensar mensagem"
                onClick={() =>
                  setToasts((old) => old.filter((item) => item.id !== toast.id))
                }
              >
                <i aria-hidden="true" className="bi bi-x" />
              </button>
            </div>
          ))}
        </div>
        <div id="mes-overlays" />
      </div>
    </WorkspaceContext.Provider>
  );
}
