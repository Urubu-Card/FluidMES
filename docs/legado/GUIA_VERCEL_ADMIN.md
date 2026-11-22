> Alternativa com servidor persistente. Para a configuração gratuita atual, use [GUIA_GRATUITO.md](GUIA_GRATUITO.md). Não aplique o Blueprint Render para o modo gratuito.

# FluidMES online — Vercel, API persistente e Django Admin

Este pacote prepara a publicação; nenhum serviço online foi criado e nenhum banco existente foi migrado automaticamente. São necessários o repositório GitHub e as contas dos provedores.

## Estrutura escolhida

- Vercel: frontend React/Vite e encaminhamento HTTP de /api, /admin e /static.
- Render ou servidor persistente equivalente: API Django e processo run_production separado.
- PostgreSQL online: dados persistentes, compartilhados pela API e pelo processo de produção.
- Django Admin: painel autenticado de registros em /admin/.

A API poderia ser adaptada à Vercel Functions, mas publicar o endpoint HTTP não inicia automaticamente o loop contínuo de produção do projeto. Esta configuração preserva esse comportamento usando um worker persistente. Vercel também tem opções atuais para outros tipos de processamento; nenhuma foi presumida como habilitada ou gratuita na sua conta.

Confira os planos/custos antes de criar API, worker e banco. O arquivo render.yaml é uma referência de infraestrutura, não uma promessa de plano gratuito. Para configuração manual, siga a ordem abaixo; ative o worker depois de aplicar as migrações da API.

## 1. Colocar o pacote no GitHub

Suba o conteúdo da pasta FluidMES para o repositório que será publicado, incluindo client, server, render.yaml e os guias. Preserve .gitignore. .env, credenciais, .venv, node_modules e bancos SQLite não entram no commit. O banco online será independente do arquivo local; importar dados locais exige uma migração de dados separada.

## 2. Reservar o endereço da interface na Vercel

Importe o repositório em New Project. Configure:

| Campo | Valor |
|---|---|
| Root Directory | client |
| Framework | Vite |
| Install Command | npm ci |
| Build Command | npm run build |
| Output Directory | dist |

Deixe VITE_API_URL sem definição. O vercel.json inicial trata as rotas da SPA. Esse primeiro deploy serve para conhecer a URL estável, por exemplo https://seu-projeto.vercel.app. O login só funcionará depois de conectar a API nos próximos passos.

## 3. Criar PostgreSQL

Crie um banco no provedor escolhido, como Render Postgres ou Neon. Copie a connection string para a variável DATABASE_URL dos serviços, preservando as opções de SSL fornecidas pelo provedor. Não coloque essa URL no frontend nem no repositório.

Para SQL/tabelas, use o editor SQL do provedor ou um cliente PostgreSQL com essa conexão. O Django Admin é uma interface de registros, não um console SQL completo.

## 4. Publicar a API

No Render, crie um Web Service ligado ao mesmo repositório:

| Campo | Valor |
|---|---|
| Runtime | Python |
| Root Directory | server |
| Build Command | pip install -r requirements.cloud.txt && python manage.py collectstatic --noinput |
| Pre-Deploy Command | python manage.py migrate --noinput |
| Start Command | python -m uvicorn config.asgi:application --host 0.0.0.0 --port $PORT |
| Health Check | /api/health/ |

Use um plano que permita esses comandos. As alternativas de shell e pre-deploy variam com o plano do provedor; confira antes de contratar. Se aplicar migrações manualmente, faça isso antes de iniciar a API e o worker.

Variáveis da API:

```text
PYTHON_VERSION=3.12.12
DJANGO_SETTINGS_MODULE=config.settings.cloud
DJANGO_SECRET_KEY=uma-chave-aleatoria-forte-de-mais-de-50-caracteres
DATABASE_URL=connection-string-do-postgresql
FRONTEND_URL=https://seu-projeto.vercel.app
DJANGO_ALLOWED_HOSTS=seu-projeto.vercel.app,seu-backend.onrender.com
```

O Render pode acrescentar automaticamente seu hostname pelo ambiente. Use o endereço real do serviço. Hosts não incluem protocolo ou caminho. FRONTEND_URL inclui https://.

Gere sua própria chave no computador:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Sem SMTP, o ambiente cloud de testes imprime e-mails de recuperação nos logs do servidor; não envia e-mails reais. Para entrega real, configure EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend e EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL e EMAIL_USE_TLS.

Verifique https://seu-backend.onrender.com/api/health/ e https://seu-backend.onrender.com/admin/login/. O health retorna 503 se o banco não responder.

## 5. Conectar a Vercel à API

No seu computador, com a URL HTTPS definitiva do backend:

```powershell
cd client
$env:FLUIDMES_BACKEND_URL = "https://seu-backend.onrender.com"
node scripts/configure-vercel.mjs
```

O script escreve client/vercel.json com os destinos corretos para API, admin, arquivos estáticos e SPA. A URL é pública e pode entrar no commit. Faça commit desse arquivo e envie ao GitHub; a Vercel publicará novamente. O script precisa rodar antes do commit; não basta definir essa variável no painel da Vercel.

As chamadas passam pelo mesmo domínio do frontend, evitando depender de cookies entre sites diferentes. Não configure VITE_API_URL apontando diretamente para outro domínio nesta receita. Não remova a proteção CSRF nem use ALLOWED_HOSTS=*.

A configuração foi validada localmente. O encaminhamento real de cookies/redirects ainda precisa do teste no seu deployment; os domínios finais não foram informados nesta conversa.

## 6. Manter a simulação funcionando

Depois da API e das migrações estarem prontas, crie um Background Worker no Render:

```text
Root Directory: server
Build Command: pip install -r requirements.cloud.txt
Start Command: python manage.py run_production
```

Use DJANGO_SETTINGS_MODULE, DJANGO_SECRET_KEY, DATABASE_URL, DJANGO_ALLOWED_HOSTS e FRONTEND_URL iguais aos da API. DATABASE_URL deve apontar exatamente para o mesmo banco. O worker pode exigir um plano cobrado separadamente. Se não houver worker ativo, os novos ciclos não avançam automaticamente como na execução local.

O render.yaml descreve os dois serviços como ponto de partida. Se usar Blueprint, revise os custos e confirme que as migrações da API terminaram antes de manter o worker em execução; reinicie o worker caso ele tenha iniciado antes do schema.

## 7. Criar o administrador do banco

No shell do serviço backend, na pasta que contém manage.py:

```sh
python manage.py createsuperuser
```

Informe e-mail, primeiro nome, CPF e senha. Não use uma senha de demonstração. Depois acesse:

```text
https://seu-projeto.vercel.app/admin/
```

Também pode entrar diretamente em https://seu-backend.onrender.com/admin/. Use as credenciais recém-criadas. O acesso Django Admin depende de is_staff e das permissões administrativas; o cadastro público de Preposto não concede essas permissões.

A conta de administração técnica é diferente do usuário normal da operação. Para testar o MES, cadastre sua empresa e o Preposto pelo auth original, ou vincule explicitamente uma conta à empresa correta. Não é necessário dar acesso ao Django Admin a todos os usuários do MES.

O painel lista empresas, usuários, preferências, equipamentos, leituras, receitas, pedidos, ciclos, solicitações e OEE. Contas têm formulário correto de senha, com hash. Os registros de produção são para consulta no admin: criar/alterar/aprovar produção deve passar pelo aplicativo para preservar as regras do planejador. Auditoria não pode ser criada/excluída por esse painel.

## Monitoramento e CLP

Esta receita configura HTTP e admin; não configura o transporte WebSocket através do proxy da Vercel. Os cards/pedidos simulados usam HTTP e continuam funcionando. O monitor ao vivo do detalhe da planta requer configurar separadamente um transporte compatível e a autenticação correspondente.

Um backend na nuvem não alcança automaticamente o IP privado do CLP da escola. A coleta física exige um agente local ou conectividade privada apropriada e o mapa de registros. Isso é separado do teste online da simulação; não exponha o serviço Modbus diretamente à internet.

## Teste final

- Frontend abre e rotas /auth e /app funcionam após recarregar.
- Cadastro, login, criação, aprovação e conclusão de um pedido funcionam.
- /admin/ exige conta administrativa e carrega CSS.
- Outra conta comum não acessa o admin.
- Dados continuam no PostgreSQL após novo deploy.
- Worker está ativo e usando o mesmo banco da API.

Fontes oficiais consultadas em 24/10/2026: [Vite na Vercel](https://vercel.com/docs/frameworks/frontend/vite), [rewrites](https://vercel.com/docs/routing/rewrites), [Django na Vercel](https://vercel.com/docs/frameworks/full-stack/django), [Django no Render](https://render.com/docs/deploy-django), [workers Render](https://render.com/docs/background-workers), [Django Admin](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/).
