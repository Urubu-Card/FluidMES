# 1.3.0 — produção real por Modbus

- START_CYCLE acionado pelo MES no início de cada ciclo do pedido, após gravar NIVEL1..3 e TEMPO1..3.
- Registro MODO: 0 local, 1 aparelho, 2 MES. Fora do modo 2 o MES só lê; programação, partida e escrita manual ficam bloqueadas.
- Corrige pedidos pausados para sempre: CLPs sem tanque agora são lidos pelo processo de produção (antes exigiam Redis e o coletor).
- O pedido pausado mostra o motivo por planta; comando `diagnostico_modbus` para relatório completo.
- CLP com tanque cadastra sozinho as 22 tags da planilha; comando `aplicar_mapeamento` para CLPs antigos.
- `INICIAR.bat` e `SIMULADOR.bat` para Windows; valor de STATUS "em ciclo" configurável (`MODBUS_STATUS_EM_CICLO`).
- Cards de planta com modo, etapa e nível lidos do CLP; simulador com os três modos.

# 1.2.2 — demonstração gratuita

- Vercel Services para frontend/Django no mesmo domínio, com Neon Free.
- Relógio de simulação por requisição autenticada, transacional e isolado por empresa; sem worker contínuo.
- Migrações no build Production, rotas /admin e arquivos estáticos, guia gratuito.
- Preservados os fluxos locais, auth e landing.

# Changelog

## 1.2.1

- Pacote de publicação Vercel + API/worker persistente e PostgreSQL online.
- Configuração cloud de HTTPS, hosts, cookies, CSRF e estáticos com WhiteNoise.
- Painel Django Admin com formulário de senha adequado ao usuário por e-mail e registros operacionais consultáveis.
- Geração de rewrites API/admin/static e rotas SPA.
- Health check de banco e guia de criação do administrador.

## 1.2.0

- Planejamento de volume em tanques paralelos e ciclos sucessivos, com previsão e etapas.
- Capacidade útil e reset configuráveis nas plantas; preferência do funcionário usada como desempate.
- Receitas de dois/três ingredientes com dosagem sequencial, vazão por ingrediente e mistura fixa por ciclo.
- Histórico com versão da receita preservada; OEE por volume concluído em cada tanque.
- Pausas suspendem execução simulada e deslocam previsão na retomada.
- Componentes compartilhados Button, Field e FormModal; formulários específicos de receita/pedido.
- Botão flutuante somente +, com descrição acessível e hover; identificação da versão removida da sidebar.
- Diagnóstico somente leitura de CLP, última comunicação válida e indicação de dados antigos.
- Guias de planejamento, referências MES e explicação de CLPs/sensores.

## 1.1.4

- Acesso LAN pronto com detecção dos IPv4 locais e endereços exibidos no terminal.
- Configuração integral de ALLOWED_HOSTS e origens CSRF/CORS para os IPs identificados, sem wildcard.
- Frontend escuta em 0.0.0.0:5173; API permanece interna em 127.0.0.1:8000.
- Variável opcional FLUIDMES_LAN_IP para selecionar IP sem editar código.
- Notificações compatíveis com HTTP pelo IP, mesmo sem crypto.randomUUID.
- Auth original, permissões e scroll preservados.

## 1.1.3

- Removida a tela adicional Concluir cadastro da empresa e seus estilos.
- Auth original permanece visível ao abrir Acessar, mesmo com sessão salva.
- Contas antigas sem empresa retornam ao auth com mensagem no formulário existente, sem redirecionamento em ciclo.
- Cadastro de empresa e Preposto continua no formulário original do auth.
- Scroll da landing e permissões mantidos.

## 1.1.2

- Restauração da apresentação original do auth sem mudar o cadastro exclusivo de Preposto.
- Remoção da interceptação da roda do mouse e do bloqueio de rolagem na landing.
- Alinhamento suave à seção mais próxima após 240 ms sem rolagem, interrompível por nova interação.
- Suporte a teclado e toque, preservação de rolagem interna e leitura de seções longas.
- Preferência de movimento reduzido respeitada; navegação por âncoras preservada.
- Testes de geometria com `cd client && npm run test:scroll`.

## 1.1.1

- Cadastro público explicitamente restrito à criação de Preposto e sua empresa.
- Permissões do Preposto independentes dos flags administrativos do Django.
- Conclusão de cadastro para contas sem empresa, substituindo bloqueios genéricos.
- Comando local `definir_preposto` para corrigir contas existentes sem apagar dados.
- Remoção do atalho de depuração "Entrada Secreta" no auth.
- Regressão testada no navegador com criação de receita e card de planta.

## 1.1.0

- Retomada da paleta e tipografia da landing; cards de plantas e pedidos.
- Menus e rotas por cargo, com controles correspondentes na API.
- Fluxo de propostas/aprovações para plantas e receitas.
- Produção simulada de 10 segundos com fila persistente por planta e histórico.
- Listas e formulários em modais expansíveis; notificações suaves.
- Homes e gráficos por cargo, preferências persistentes e modos de sidebar.
- Administração técnica e feed de atualizações exclusivos do Preposto.
- Iniciador local, comando opcional de dados demonstrativos e guia de execução.
