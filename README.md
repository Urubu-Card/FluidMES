# FluidMES · Frontend (React/Vite)

Interface do MES. Versão: ver `VERSION`. O backend (Django/DRF) está em um projeto separado (`fluidmes-backend`).

## Desenvolvimento

Node.js 22+.

```bash
npm ci
npm run dev        # http://localhost:5173
```

O Vite encaminha `/api` e `/ws` para o backend. Por padrão `http://127.0.0.1:8000`; para outro destino defina `VITE_DEV_API_TARGET` (veja `.env.example`).
Suba o backend antes (`INICIAR.bat` / `python run_local.py` no projeto `fluidmes-backend`).

Outros scripts: `npm run build`, `npm run lint`, `npm run test:scroll`.

## Como o frontend encontra a API

- Padrão: chamadas relativas (`/api/...`), resolvidas por proxy (Vite em dev, nginx no Docker, rewrites na Vercel).
- Alternativa: `VITE_API_URL=https://api.exemplo.com` no build, para chamar outra origem diretamente. Nesse caso o backend precisa listar o domínio do frontend em `FRONTEND_URL`/`CORS_ALLOWED_ORIGINS`.

## Docker

```bash
API_UPSTREAM=http://host.docker.internal:8000 docker compose up --build   # http://127.0.0.1:8080
```

Se o backend estiver em outro host, use a URL dele em `API_UPSTREAM` (ex.: `https://api.exemplo.com`).

## Deploy na Vercel

Defina `FLUIDMES_BACKEND_URL` (origem HTTPS do backend, sem caminho) e execute `node scripts/configure-vercel.mjs` antes do build; ele gera o `vercel.json` com os rewrites de `/api`, `/admin` e `/static` para o backend e o fallback da SPA. Sugestão de *Build Command*: `node scripts/configure-vercel.mjs && npm run build`.

Guias antigos em `docs/legado/` e logs de verificação em `quality/`.
