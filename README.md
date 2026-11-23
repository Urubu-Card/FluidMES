# FluidMES · Frontend

Interface web do **FluidMES**, um MES (Manufacturing Execution System) para plantas de processos industriais com tanques controlados por CLP via Modbus TCP. Feita em React 19 + Vite, conversa com a API Django do diretório [`../backend`](../backend/README.md).

Versão atual: ver [`VERSION`](VERSION).

## Sumário

- [O que a interface oferece](#o-que-a-interface-oferece)
- [Tecnologias](#tecnologias)
- [Como rodar](#como-rodar)
- [Design](#design)
  - [Paleta de cores](#paleta-de-cores)
  - [Tema claro e escuro](#tema-claro-e-escuro)
  - [Tipografia](#tipografia)
  - [Layout, ícones e movimento](#layout-ícones-e-movimento)
  - [Contraste e acessibilidade](#contraste-e-acessibilidade)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Como o frontend encontra a API](#como-o-frontend-encontra-a-api)
- [Docker](#docker)
- [Deploy na Vercel](#deploy-na-vercel)
- [Testes e qualidade](#testes-e-qualidade)

## O que a interface oferece

| Rota | Tela | Quem vê |
| --- | --- | --- |
| `/` | Landing page institucional | todos |
| `/auth`, `/auth/forgot-password`, `/auth/reset-password` | Login, cadastro e recuperação de senha | todos |
| `/app/home` | Home com indicadores e gráficos interativos | todos |
| `/app/pedidos` | Pedidos de produção, plano de ciclos, aprovação e acompanhamento | todos |
| `/app/plantas` | Cards das plantas, telemetria ao vivo e controle de tanque | todos |
| `/app/receitas` | Receitas com dois ou três ingredientes | todos |
| `/app/funcionarios` | Lista de funcionários | Preposto e Chefe |
| `/app/rendimento` | Rendimentos (OEE) | Preposto |
| `/app/administracao` | Administração técnica de CLPs e sensores | Preposto |
| `/app/atualizacoes` | Últimas atualizações do sistema | Preposto |
| `/app/configuracoes`, `/app/profile` | Preferências da conta e perfil | todos |

Os cargos são **Preposto**, **Chefe** e **Funcionário**. A barra lateral mostra só o que o cargo pode acessar, e as permissões são validadas de novo no backend.

## Tecnologias

| Área | Escolha |
| --- | --- |
| Base | React 19, React Router 7, Vite 6 |
| Estilo | Bootstrap 5.3 + CSS próprio com variáveis (`index.css`, `workspace.css`) |
| Ícones | Bootstrap Icons e React Icons |
| Animação | GSAP e Motion (landing e microinterações) |
| Efeito visual | OGL (WebGL) para o ferrofluido da landing |
| HTTP | Axios, com cookies, CSRF e renovação automática de sessão |
| Qualidade | ESLint 9 e testes com o runner nativo do Node |

## Como rodar

Requisitos: Node.js 22+.

```bash
npm ci
npm run dev        # http://localhost:5173
```

O Vite encaminha `/api` e `/ws` para o backend, por padrão em `http://127.0.0.1:8000`. Para outro destino, defina `VITE_DEV_API_TARGET` (modelo em [`.env.example`](.env.example)). Suba o backend antes, seguindo o [README do backend](../backend/README.md).

| Script | O que faz |
| --- | --- |
| `npm run dev` | servidor de desenvolvimento |
| `npm run build` | build de produção em `dist/` |
| `npm run preview` | serve o build localmente |
| `npm run lint` | ESLint |
| `npm run test:scroll` | testes do alinhamento de seções da landing |

## Design

A identidade vem da landing page: um azul-petróleo profundo, azul-céu como cor de ação e um branco levemente azulado para texto. O workspace (`/app`) reaproveita a mesma paleta e adiciona um tema claro.

### Paleta de cores

Cores-base, declaradas em `src/index.css`:

| Nome | Hex | Uso |
| --- | --- | --- |
| Azul-petróleo | `#101629` | fundo da página no tema escuro |
| Cinza-escuro | `#2D3645` | cards elevados, superfícies secundárias |
| Azul-céu | `#3E7DFF` | cor primária: botões, links, foco e destaques |
| Azul-céu escuro | `#2E4E99` | profundidade, cards de destaque, gradientes |
| Branco-azulado | `#DBF3FF` | texto sobre fundo escuro |
| Branco | `#FFFFFF` | cards no tema claro e texto sobre azul |

Cores de estado e de gráficos (`src/pages/app/home/style.css`):

| Significado | Hex |
| --- | --- |
| Positivo, em operação | `#05C585` (ícone `#198754`) |
| Atenção | `#FFC107` |
| Erro, parada | `#DC3545` |
| Série azul de gráfico | `#3B82F6` |

O ferrofluido da landing usa variáveis próprias (`--fm-background: #10151B`, `--fm-card`, `--fm-depth`, `--fm-accent`, `--fm-text`) derivadas da mesma paleta.

### Tema claro e escuro

O workspace usa variáveis CSS em `.mes-shell`, trocadas pelo atributo `data-theme`:

| Variável | Escuro | Claro |
| --- | --- | --- |
| `--page` (fundo) | `#101629` | `#F5F8FD` |
| `--surface` (card) | `#1C2438` | `#FFFFFF` |
| `--surface-raised` | `#2D3645` | `#EDF2FA` |
| `--surface-soft` | `#202B42` | `#F0F5FC` |
| `--text` | `#DBF3FF` | `#18273E` |
| `--muted` (texto secundário) | `#A5B4C9` | `#586B82` |
| `--border` | `rgba(219, 243, 255, .12)` | `rgba(32, 55, 90, .14)` |
| `--primary` | `#3E7DFF` | `#3E7DFF` |

Cada pessoa escolhe em **Configurações**, e a escolha fica salva na conta:

- **Tema:** usar o do dispositivo (padrão), escuro ou claro. No modo do dispositivo, a interface acompanha `prefers-color-scheme` e fica escura se o navegador não informar preferência.
- **Menu em computadores e TVs:** sempre aberto, só ícones ou abrir ao passar o mouse.
- **Menu em telas médias e pequenas:** puxador lateral, só ícones ou menu hambúrguer.

### Tipografia

Duas famílias do Google Fonts, carregadas em `src/index.css` com `display=swap` e eixo de peso variável (100 a 900):

| Família | Papel | Onde aparece |
| --- | --- | --- |
| **Exo 2** | títulos e destaques, com um caráter técnico e levemente futurista | `h1` a `h6`, `.display-*`, títulos de cards, números grandes e cabeçalhos do workspace |
| **Inter** | texto de interface e leitura | corpo, parágrafos, formulários, tabelas, botões e rótulos |

Botões, campos e selects herdam a fonte do contexto (`font: inherit`). A fonte base do Bootstrap é sobrescrita com `--bs-body-font-family: "Inter"`, então componentes do Bootstrap seguem o mesmo padrão.

### Layout, ícones e movimento

- A barra lateral tem 250 px de largura no modo aberto e 82 px no modo de ícones.
- Detalhes de pedidos, plantas e funcionários abrem em **modais expansíveis**, e formulários e listas compartilham os componentes de `pages/app/shared`.
- Ícones: Bootstrap Icons nos menus e nas ações, React Icons em componentes pontuais.
- A landing combina ferrofluido em WebGL (OGL), partículas, texto rotativo e navegação por seções com rolagem alinhada. O alinhamento escolhe a seção mais próxima e deixa seções longas legíveis no celular. Com movimento reduzido ativo no sistema, o alinhamento é desativado.
- Estados de carregamento, erro e sucesso aparecem como mensagens inline ou avisos temporários (toasts).

### Contraste e acessibilidade

Razões de contraste calculadas (WCAG) para os pares mais usados:

| Par | Razão |
| --- | --- |
| Texto `#DBF3FF` sobre `#101629` (escuro) | 15,6 : 1 |
| Texto secundário `#A5B4C9` sobre `#101629` | 8,5 : 1 |
| Texto secundário `#A5B4C9` sobre card `#1C2438` | 7,3 : 1 |
| Texto `#18273E` sobre `#F5F8FD` (claro) | 14,1 : 1 |
| Texto secundário `#586B82` sobre `#FFFFFF` | 5,5 : 1 |
| Azul-céu `#3E7DFF` sobre `#101629` | 4,8 : 1 |
| Branco sobre botão azul-céu `#3E7DFF` | 3,8 : 1 |
| Azul-céu `#3E7DFF` sobre branco | 3,8 : 1 |

Os textos principais passam do nível AAA. Os dois últimos pares ficam abaixo de 4,5 : 1, então servem para textos grandes, botões e elementos de interface (mínimo de 3 : 1), mas não para texto pequeno corrido. Em fundo claro, evite o azul-céu para parágrafos e prefira `--text`.

Outros cuidados já aplicados: estilo de foco visível por teclado (`:focus-visible`) em todo o workspace, `Esc` fecha o menu e os modais, cores de estado acompanhadas de texto ou ícone, e movimento reduzido respeitado na landing.

## Estrutura de pastas

```
frontend/
├─ public/                      logos, favicons e imagens estáticas
├─ scripts/configure-vercel.mjs gera o vercel.json com os rewrites para o backend
├─ src/
│  ├─ main.jsx                  rotas da aplicação
│  ├─ index.css                 paleta-base, fontes e estilos globais
│  ├─ services/                 api.js (Axios, CSRF, refresh) e errors.js
│  └─ pages/
│     ├─ landing/               página institucional e hooks de rolagem
│     ├─ auth/ forgot/          login, cadastro e recuperação de senha
│     ├─ components/            Sidebar, NavBar, Ferrofluid, Particles, RotatingText...
│     └─ app/                   workspace autenticado
│        ├─ app.jsx             sessão, preferências, tema e toasts
│        ├─ workspace.css       tokens do tema claro/escuro
│        ├─ shared/             modais, formulários, listas, gráficos e hooks
│        └─ home/ pedidos/ plantas/ receitas/ funcionarios/
│           rendimentos/ administracao/ atualizacoes/ configuracoes/ profile/
├─ tests/                       testes do alinhamento de seções
├─ Dockerfile, nginx.conf.template, compose.yaml
└─ docs/legado/, quality/       guias antigos e registros de verificação
```

## Como o frontend encontra a API

- **Padrão:** chamadas relativas (`/api/...`), resolvidas por proxy: Vite em desenvolvimento, nginx no Docker e rewrites na Vercel.
- **Alternativa:** `VITE_API_URL=https://api.exemplo.com` no build, para chamar outra origem direto. Nesse caso o backend precisa listar o domínio do frontend em `FRONTEND_URL` e `CORS_ALLOWED_ORIGINS`.
- **Sessão:** cookies com `withCredentials`, token CSRF enviado nas escritas e renovação automática da sessão em caso de `401`. Se a renovação falhar, a pessoa volta para `/auth`.

## Docker

```bash
API_UPSTREAM=http://host.docker.internal:8000 docker compose up --build
# http://127.0.0.1:8080
```

O nginx serve o build estático e encaminha `/api`, `/admin`, `/static` e `/ws` para `API_UPSTREAM`. Se o backend estiver em outro host, use a URL dele (por exemplo `https://api.exemplo.com`).

## Deploy na Vercel

Defina `FLUIDMES_BACKEND_URL` (origem HTTPS do backend, sem caminho). O script `scripts/configure-vercel.mjs` gera o `vercel.json` com os rewrites de `/api`, `/admin` e `/static` para o backend e o fallback da SPA.

Build Command sugerido:

```bash
node scripts/configure-vercel.mjs && npm run build
```

## Testes e qualidade

O CI roda `npm run lint`, `npm run build` e `npm run test:scroll` a cada push (workflow na raiz do repositório). Guias antigos do projeto unificado estão em `docs/legado/` e registros de verificação em `quality/`.
