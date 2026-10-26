import { useState } from "react";
import api from "../../../services/api";
import { useWorkspace } from "../shared/context";
import { PageHeader } from "../shared/UI";
import { errorMessage } from "../../../services/errors";
export default function Configuracoes() {
  const { prefs, setPrefs, notify } = useWorkspace();
  const [busy, setBusy] = useState(false);
  async function change(key, value) {
    setBusy(true);
    try {
      const result = await api.patch("/api/preferencias/", { [key]: value });
      setPrefs(result.data);
      notify("Preferência salva.");
    } catch (error) {
      notify(errorMessage(error), "error");
    } finally {
      setBusy(false);
    }
  }
  const choices = (key, options) => (
    <div className="preference-options">
      {options.map(([value, icon, title, text]) => (
        <button
          key={value}
          className={`preference-option ${prefs[key] === value ? "selected" : ""}`}
          disabled={busy}
          onClick={() => change(key, value)}
          aria-pressed={prefs[key] === value}
        >
          <i aria-hidden="true" className={`bi ${icon}`} />
          <strong>{title}</strong>
          <span>{text}</span>
          {prefs[key] === value && (
            <i
              aria-hidden="true"
              className="bi bi-check-circle-fill selected-check"
            />
          )}
        </button>
      ))}
    </div>
  );
  return (
    <section className="mes-page">
      <PageHeader
        title="Configurações"
        description="Um espaço de trabalho que combina com você."
      />
      <section className="preference-section">
        <h2>Aparência</h2>
        <p>Escolha como você prefere visualizar o FluidMES.</p>
        {choices("tema", [
          [
            "sistema",
            "bi-display",
            "Usar tema do dispositivo",
            "Acompanha a preferência do seu computador.",
          ],
          [
            "escuro",
            "bi-moon-stars",
            "Escuro",
            "Conforto e contraste para a operação.",
          ],
          [
            "claro",
            "bi-sun",
            "Claro",
            "Uma interface clara para o seu ambiente.",
          ],
        ])}
      </section>
      <section className="preference-section">
        <h2>Menu em computadores e TVs</h2>
        <p>Escolha entre acesso completo e mais espaço para o conteúdo.</p>
        {choices("sidebar_desktop", [
          [
            "aberta",
            "bi-layout-sidebar",
            "Sempre aberto",
            "Ícones e nomes sempre à vista.",
          ],
          [
            "icones",
            "bi-layout-sidebar-inset",
            "Apenas ícones",
            "Passe o mouse para ver o nome.",
          ],
          [
            "hover",
            "bi-arrow-bar-right",
            "Expandir ao passar o mouse",
            "O menu abre quando você precisa.",
          ],
        ])}
      </section>
      <section className="preference-section">
        <h2>Menu em telas médias e pequenas</h2>
        <p>Estas preferências entram em ação abaixo de 992 px.</p>
        {choices("sidebar_mobile", [
          [
            "puxador",
            "bi-chevron-bar-right",
            "Puxador lateral",
            "Clique ou arraste a seta na lateral esquerda.",
          ],
          [
            "icones",
            "bi-layout-sidebar",
            "Apenas ícones",
            "Acesso compacto na lateral.",
          ],
          [
            "hamburguer",
            "bi-list",
            "Menu hambúrguer",
            "Botão no canto superior direito.",
          ],
        ])}
      </section>
    </section>
  );
}
