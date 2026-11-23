# FluidMES

MES (Manufacturing Execution System) para plantas com tanques TK1/TK2 controlados por CLP via Modbus TCP.

| Pasta | Conteúdo | Como rodar |
| --- | --- | --- |
| [`backend/`](backend) | API Django/DRF, WebSockets, coleta Modbus, produção e OEE | veja `backend/README.md` |
| [`frontend/`](frontend) | Interface React/Vite | veja `frontend/README.md` |

## Início rápido

```bash
# terminal 1: API
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && python manage.py migrate
python -m uvicorn config.asgi:application --host 127.0.0.1 --port 8000

# terminal 2: execução dos pedidos
cd backend && source .venv/bin/activate && python manage.py run_production

# terminal 3: interface (http://localhost:5173)
cd frontend && npm ci && npm run dev
```

No Windows, ative o ambiente com `.venv\Scripts\activate`.

O CI está em `.github/workflows/ci.yml` e roda os testes do backend e o lint/build/testes do frontend.
