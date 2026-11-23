# FluidMES · Backend

API do MES FluidMES: Django 5.2 + Django REST Framework, WebSockets (Channels), coleta e comando Modbus TCP dos tanques TK1/TK2, planejamento de produção por ciclos e OEE.
O frontend é um projeto separado (`fluidmes-frontend`).

## Estrutura

```
config/            settings (base, dev, prod), urls, asgi/wsgi, celery, middleware JWT
apps/accounts/     contas, cargos, autenticação, recuperação de senha, auditoria
apps/plantas/      plantas, CLPs, sensores, leituras, telemetria em tempo real
apps/producao/     receitas, pedidos, planejamento, execução por CLP, paradas, OEE
services/          cliente Modbus, mapa de registradores e CLP simulado
docs/              mapeamento.xlsx (registradores dos tanques)
```

## Requisitos

Python 3.12. Redis é opcional no uso básico (sem `REDIS_URL` a telemetria usa camada de canais em memória).

## Executar localmente

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt      # ou requirements.lock, com as versões travadas
python manage.py migrate
python manage.py createsuperuser     # opcional, para o /admin/
```

Em dois terminais:

```bash
python -m uvicorn config.asgi:application --host 127.0.0.1 --port 8000   # API + WebSocket
python manage.py run_production                                          # executa os pedidos aprovados
```

O banco local é SQLite (`db.sqlite3`) e os e-mails (como o link de recuperação de senha) aparecem no terminal da API.
A configuração padrão é `config.settings.dev`, que aceita o frontend em `localhost:5173` e `localhost:8080`.

Para acessar de outro computador ou do celular na mesma rede, informe o IP da máquina e o frontend (porta 5173) será liberado em hosts, CORS e CSRF:

```bash
FLUIDMES_LAN_IP=192.168.0.10 python -m uvicorn config.asgi:application --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker compose up --build
```

Sobe Postgres, Redis, migração, API (`http://127.0.0.1:8000`), `run_production`, coletor (`read_plants`) e Celery worker/beat.
Se o frontend não estiver em `http://localhost:8080`, defina `FRONTEND_URL`.

## Comandos de gerenciamento

| Comando | Para que serve |
| --- | --- |
| `run_production` | executa continuamente os ciclos dos pedidos aprovados (simulação ou CLP real) |
| `read_plants [--interval N]` | coleta leituras dos CLPs/sensores |
| `aplicar_mapeamento` | cadastra as 22 tags de `mapeamento.xlsx` em todos os CLPs, sem duplicar |
| `diagnostico_modbus` | testa a conexão TCP e a leitura Modbus dos CLPs |
| `prune_readings` | remove leituras antigas |
| `calculate_oee` | calcula o OEE |
| `definir_preposto` | promove uma conta existente a Preposto |
| `seed_demo` | cria dados de demonstração |

## Modbus: TK1 e TK2

Cada tanque tem 10 holding registers e uma coil (detalhes em `docs/mapeamento.xlsx` e `services/modbus_map.py`):

| Tag | TK1 | TK2 | Uso pelo MES |
| --- | --- | --- | --- |
| ETAPA, NIVEL_ATUAL, STATUS | 400001, 400005, 400009 | 400011, 400015, 400019 | leitura |
| NIVEL1..3, TEMPO1..3 | 400002–4, 400006–8 | 400012–14, 400016–18 | escrita da receita antes da partida |
| MODO | 400010 | 400020 | somente leitura |
| START_CYCLE (coil) | 1 | 2 | acionada no início de cada ciclo |

**MODO**: 0 = local na planta, 1 = pelo aparelho, 2 = sistema MES. Nos modos 0 e 1 o MES só lê, os ciclos aguardam e a escrita manual de sensores responde `423`. O MES nunca escreve em MODO.

Para ativar na interface: Administração técnica → CLPs, cadastre IP e porta, marque *Habilitar comandos Modbus* e escolha o *Tanque de produção*. Cada planta usa um tanque.

Hipóteses adotadas (ajustáveis em `services/modbus_map.py` e `apps/producao/services/execucao_clp.py`): STATUS 0 parado, 1 em ciclo, 2 concluído; NIVELn é o nível acumulado ao fim da dosagem n; TEMPOn é a mistura em segundos depois dela; START_CYCLE vai a 1 na partida e volta a 0 ao fim do ciclo.

### Bancada sem CLP real

```bash
python services/server_temp.py --port 5020 --modo 0     # CLP simulado em modo local
python services/definir_modo.py TK1 2 --port 5020       # "chave" que entrega o tanque ao MES
```

## Produção

Use `DJANGO_SETTINGS_MODULE=config.settings.prod` com HTTPS, PostgreSQL, SMTP e Redis reais. As variáveis estão em `.env.example` (o arquivo não é carregado automaticamente; injete-as no serviço). As mais importantes:

| Variável | Descrição |
| --- | --- |
| `DJANGO_SECRET_KEY` | chave com pelo menos 50 caracteres |
| `DJANGO_ALLOWED_HOSTS` | domínios da API |
| `DATABASE_URL` | PostgreSQL |
| `CORS_ALLOWED_ORIGINS` | origens do frontend (também usadas no CSRF) |
| `FRONTEND_URL` | URL pública do frontend |
| `REDIS_URL`, `CELERY_BROKER_URL` | Redis |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL` | SMTP |
| `TRUST_PROXY_SSL_HEADER` | `true` atrás de proxy que envia `X-Forwarded-Proto` |

Processos persistentes necessários: API (uvicorn), `run_production` e, se usar telemetria entre processos, `read_plants`. Rode `python manage.py collectstatic --noinput` e `python manage.py migrate --noinput` a cada deploy.

## Testes

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test apps.accounts apps.plantas apps.producao
```

O workflow `.github/workflows/ci.yml` executa os mesmos passos.
