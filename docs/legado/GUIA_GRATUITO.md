# FluidMES gratuito — Vercel Hobby + Neon Free

A partir da versão 1.2.2, a configuração principal usa Vercel Services (beta, disponível no Hobby) para publicar React e Django juntos. O banco fica no Neon Free. Não é necessário contratar Render, worker, Redis, domínio ou plano Pro. A configuração anterior do Render continua disponível apenas como alternativa e não deve ser aplicada para este guia.

## O que já está preparado

- Repositório: https://github.com/Pedr003/FluidMES
- Projeto Vercel: https://vercel.com/pedrootavioramoslima-9280/fluidmes-pedr003
- Root Directory: raiz do repositório (deixe vazio), **não client**.
- vercel.json na raiz: frontend em client, backend em server; /api, /admin e /static vão para Django.
- DJANGO_SETTINGS_MODULE=config.settings.vercel, chave secreta aleatória e hosts configurados para Production no projeto criado.
- Previews desabilitados neste projeto de demonstração. Nenhuma credencial de banco deve ser configurada globalmente para branches não revisadas.

O projeto ainda precisa do banco e do primeiro deploy. A existência do projeto Vercel não significa que já existe um site funcionando.

## 1. Criar o banco gratuito

No projeto Vercel, abra **Storage → Create Database → Neon**. Selecione explicitamente **Free / US$ 0**. Não habilite upgrade, trial pago ou cobrança por excedentes. Se o Marketplace não disponibilizar Free sem cobrança, use https://console.neon.tech e crie um projeto no plano Free diretamente.

Conecte o banco somente ao ambiente **Production** deste projeto. A integração pode criar DATABASE_URL ou POSTGRES_URL. Em Settings → Environment Variables, confirme que **DATABASE_URL** existe em Production com a connection string PostgreSQL fornecida pelo Neon, incluindo os parâmetros SSL. Prefira a conexão pooled para a API; para migrações, use uma conexão direta se o provedor exigir. Não cole a conexão no chat, no código ou no frontend. Não defina VITE_API_URL nem VITE_DATABASE_URL.

No Neon Free consultado em 24/10/2026, não é necessário cartão e não há prazo de expiração do plano. Há cotas de armazenamento, processamento e transferência; confira os limites exibidos ao criar, pois os provedores podem alterá-los. O banco pode adormecer quando ocioso e a primeira consulta demorar mais.

## 2. Fazer o primeiro deploy

Depois de conectar o banco, abra **Settings → Git → Connect Git Repository** e conecte **Pedr003/FluidMES**, branch **main**, a este projeto Vercel. Preserve Root Directory na raiz, Framework Preset Other e os comandos do vercel.json. Não crie outro projeto com raiz client. Se a interface não permitir conectar o repositório ao projeto já criado, informe isso para finalizar pela integração.

Ao publicar, o build do backend instala requirements.cloud.txt, executa migrações apenas no ambiente Production e coleta os arquivos estáticos. Como este é um banco de demonstração novo e isolado, as migrações são automáticas. Faça backup antes de usar esse processo com dados importantes.

Confirme a URL de produção mostrada no deploy. O nome pretendido é https://fluidmes-pedr003.vercel.app; ele só deve ser considerado ativo após um deploy Ready. Se a Vercel atribuir outro domínio, atualize FRONTEND_URL e DJANGO_ALLOWED_HOSTS para o endereço real e publique novamente. Os domínios exatos fornecidos pelo ambiente Vercel também são aceitos; não use wildcard.

Verifique:

- /api/health/: status ok e conexão com o PostgreSQL.
- /auth: autenticação original; cadastro público continua criando apenas empresa e Preposto.
- /admin/: tela de login do Django Admin, com CSS carregado.
- Crie planta, receita e pedido; aguarde o tempo previsto e confirme conclusão.

## 3. Criar sua conta do Django Admin

O Preposto do cadastro público não recebe is_staff ou is_superuser. Crie o administrador técnico pelo terminal do seu computador, usando o banco Neon online. Não existe uma rota pública para promover usuários.

No PowerShell, com Python 3.12, na pasta do projeto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r server/requirements.cloud.txt
# Copie a connection string no painel Neon. Ela é um segredo.
$env:DATABASE_URL = Read-Host "Connection string do Neon"
.\.venv\Scripts\python.exe server/manage.py migrate --noinput --settings=config.settings.dev
.\.venv\Scripts\python.exe server/manage.py createsuperuser --settings=config.settings.dev
Remove-Item Env:DATABASE_URL
```

O Read-Host evita registrar a connection string no histórico do PowerShell; digite somente no seu computador. Use o endereço direto do banco para esses comandos se necessário. Informe e-mail, primeiro nome, CPF e uma senha própria. O comando faz alterações no banco online, não no SQLite local. Depois entre em **https://DOMINIO-DO-DEPLOY/admin/**.

Para consultas SQL e tabelas diretamente, use o SQL Editor do Neon. O Django Admin oferece administração de registros; registros de produção permanecem somente leitura para preservar as regras do planejador.

## Como funciona a produção sem worker

A simulação gratuita calcula o estado pelo relógio do servidor e pelos horários dos ciclos já salvos no banco. Antes de atualizar os cards, a aplicação chama POST /api/simulacao/sincronizar/ autenticado, restrito à empresa do usuário. Antes de alterar pedidos, plantas ou paradas, o backend também reconcilia o estado anterior. Consultas GET não alteram a produção.

Com a aplicação aberta, o polling existente atualiza os dados. Com o site fechado, não existe um processo executando continuamente: na próxima consulta, os ciclos vencidos são concluídos com seus horários previstos. A operação é transacional e repetível sem duplicar as conclusões. Isso atende à demonstração; não é controle industrial em tempo real, não envia comandos a CLPs e não coleta sensores continuamente. O modo local anterior com run_production continua disponível.

Não mantenha um segundo worker no mesmo demo: ele é desnecessário. Não use serviços de ping para contornar cotas ou manter recursos acordados.

## Limites do ambiente gratuito

Vercel Hobby é para uso pessoal e não comercial. Ao atingir cotas, a aplicação pode ser suspensa ou ter o uso limitado; não habilite upgrade automático. Não há promessa de hospedagem ilimitada ou disponibilidade industrial.

O envio real de e-mails não foi configurado. A recuperação de senha usa o backend console até ser conectado um provedor de e-mail; não considere os logs como entrega ao usuário.

Telemetria ao vivo e conectividade com a rede local dos CLPs exigem uma configuração separada. O deploy HTTP permite testar cadastros, permissões, cards, planejamento e simulação.

Referências oficiais:

- https://vercel.com/docs/services
- https://vercel.com/docs/services/pricing
- https://vercel.com/docs/frameworks/full-stack/django
- https://vercel.com/docs/plans/hobby
- https://neon.com/pricing
