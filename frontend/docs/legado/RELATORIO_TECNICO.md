# FluidMES 1.1.4 — relatório da revisão

**Documento histórico da revisão até a 1.1.4. A arquitetura e a validação atuais estão em RELATORIO_1.2.md.**

## Objetivo e resultado

A 1.1 retoma o direcionamento visual definido pelo usuário: Inter/Exo 2, azul-petróleo/azul-céu da landing, cards para reduzir a necessidade de interpretar tabelas, listas resumidas para pessoas/receitas e detalhes em modais. O foco principal é uso em computadores, com adaptação a telas pequenas. A landing page preserva sua identidade visual e estrutura; a rolagem foi ajustada na versão 1.1.2.

O frontend foi implementado em componentes de página, listas, formulários, modais, gráficos SVG interativos e contexto de sessão/preferências. O modal gerencia foco, Tab, Escape e retorno do foco, e pode ocupar toda a tela. As notificações são discretas e não cobrem o botão +. Indicadores usam dados reais da conta; campos sem medição exibem ausência de medição.

## Ajustes da 1.1.4 — LAN

O iniciador detecta os IPv4 locais, compartilha a lista com o backend e exibe os endereços de acesso. A configuração de desenvolvimento define integralmente ALLOWED_HOSTS e adiciona apenas as origens dos IPs conhecidos a CSRF/CORS. A variável opcional FLUIDMES_LAN_IP permite escolher uma interface sem editar código. O Vite escuta em 0.0.0.0:5173 e mantém a API acessível internamente via proxy em 127.0.0.1:8000.

Notificações recebem IDs alternativos quando crypto.randomUUID não existe em HTTP pelo IP; esses IDs identificam apenas elementos de interface. Auth e landing foram comparados com a 1.1.3 e não mudaram. A configuração local corrigida elimina a referência a ALLOWED_HOSTS antes de sua definição. Nenhuma migração foi adicionada.

Validação 1.1.4: 52 testes Django, lint, build e quatro testes de geometria passaram. O teste HTTP real inicializou o launcher com SQLite isolado e verificou cadastro, login com cookies e criação de planta usando Host/Origin IPv4 da LAN, além de rejeição de CSRF ausente, origem e host desconhecidos. O ambiente exige um fixture temporário para a enumeração de interfaces do Node.js; detalhes em quality/http-lan-1.1.4.txt. Não houve novo teste em navegador, em Windows ou em outro equipamento físico nesta atualização. A validação do firewall da rede do usuário depende do computador onde o projeto será executado.

## Ajustes da 1.1.3

A tela extra de conclusão de empresa foi removida. O auth deixa de consultar a sessão para redirecionar automaticamente ao painel; Acessar abre o formulário original, inclusive com cookies de uma conta válida ou antiga sem empresa. O guard do painel retorna contas sem vínculo ao auth com mensagem no formulário existente. Não ocorre promoção ou associação automática a outra empresa.

A apresentação JSX e o CSS do auth foram comparados diretamente com o ZIP inicial; são idênticos. Os arquivos da landing e do scroll permanecem iguais à 1.1.2. Também foi corrigida a instanciação de django-environ na configuração local DATABASE_URL, detectada ao isolar o banco dos testes de navegador. Nenhuma migração foi adicionada.

Os 48 testes Django, lint, build e quatro testes de geometria passaram. A validação real em Chromium usou banco SQLite isolado e cobriu Acessar sem sessão, sessão válida, sessão antiga sem empresa, cadastro, login, ausência de ciclo e criação de planta pelo Preposto. Evidências em quality/*-1.1.3.txt.

## Ajustes da 1.1.2

O auth recupera a apresentação da 1.1, sem alterar a camada de API ou o cadastro exclusivo de Preposto. O backend é idêntico ao pacote 1.1.1.

A landing mantém a rolagem nativa com listeners passivos e um debounce de 240 ms. A seleção da seção mais próxima usa geometria em função pura, testada separadamente. A animação usa requestAnimationFrame, é cancelada ao receber nova interação e não impede a leitura do meio de seções longas. Teclas pressionadas e gestos de toque/arrasto adiam o alinhamento; movimento reduzido desativa o alinhamento automático.

Quatro testes de geometria, ESLint e build passaram. O navegador Chromium verificou roda do mouse, pausa, interrupção, teclado, rolagem interna, âncoras, movimento reduzido, toque e apresentação do auth, sem erros JavaScript. Evidências em quality/frontend-1.1.2.txt e quality/browser-1.1.2.txt.

## Regras e arquitetura

- **Permissões:** validação de rota/interface e backend. O Preposto acessa todas as áreas; o Chefe consulta Funcionários e não acessa Rendimentos; o Funcionário consulta plantas/receitas e enxerga somente seus pedidos. CLPs/sensores/paradas, atualizações e OEE detalhado são restritos ao Preposto.
- **Aprovações:** `Solicitacao` armazena propostas de planta/receita com dados validados. Aprovar cria o registro dentro de transação; rejeitar não cria. Repetir a decisão retorna erro, prevenindo duplicação.
- **Produção:** `workflow.py` controla aprovação, fila por planta e execução. O pedido registra início, aprovação, conclusão e duração. A fila usa lock da planta e ordem de aprovação; o comando `run_production` processa pedidos vencidos independentemente do navegador.
- **Auditoria:** `Atualizacao` guarda nome/cargo do autor como snapshot, ação, recurso, descrição e horário. A API é paginada, isolada por empresa e exclui o próprio autor. Eventos automáticos são registrados como Sistema.
- **Preferências:** `Preferencias` é vinculada por usuário e persiste tema e os dois modos de sidebar. As opções administrativas não estão misturadas às preferências pessoais.
- **Dados operacionais:** plantas usam consultas relacionadas antecipadas para cards; dados de produção continuam separados dos equipamentos físicos. OEE é recalculado após conclusão simulada e pelo processamento diário existente.
- **Execução local:** `run_local.py` aplica migrações e inicia API, simulador e Vite. O modo local utiliza channel layer em memória quando Redis não é configurado; coleta entre processos exige Redis explícito.

## Decisões adotadas

Chefe consulta Funcionários sem alterar pessoas. Pedidos concluídos e solicitações analisadas ficam no Histórico. Cada planta executa um pedido por vez. Pedidos do Chefe/Preposto já nascem aprovados; pedidos do Funcionário dependem de aprovação. O Preposto pode editar/excluir pedidos ainda aguardando aprovação. Estados em produção/finalizados são protegidos de alterações arbitrárias.

A simulação tem 10 segundos e considera toda a quantidade como boa. Trata-se de uma simulação funcional; o OEE depende da convenção de tempo ideal `tempo1 + tempo2` e do turno padrão de 480 minutos. Valores não representam desempenho de tanques físicos enquanto o adaptador real não for implementado.

## Migrações

Migrações incrementais adicionam preferências, auditoria, propostas e os timestamps de produção. Dados anteriores de empresas/usuários/plantas/receitas são preservados. Quando não existia data de criação do pedido, a migração preenche a nova coluna com seu próprio horário, sem recuperar uma data histórica desconhecida. Faça backup de bases existentes antes de atualizar.

## Validação

**48 testes Django passaram**, além de lint, build e smoke tests. Consulte `quality/` para a saída final.

A validação em Chromium percorreu os três cargos, desktop e celular, formulários preenchidos por teclado, criação em modal, expansão, tema claro/escuro e persistência após recarregar. Também executou proposta do Funcionário, aprovação do Chefe, conclusão automática de 10 segundos, histórico, consulta de funcionários pelo Chefe, acesso reservado por URL e feed de atualizações. Não houve erros JavaScript nessa sequência. Capturas foram usadas apenas na inspeção interna e não são parte da entrega.

## Limites

Docker/PostgreSQL/Redis externos, SMTP real e hardware físico não foram executados nesta revisão. O Compose foi validado como YAML; a validação funcional foi local com SQLite, ASGI, Chromium e simulador Modbus TCP na suíte. A 1.1 não publica site externo nem implementa controle/escrita de receitas em tanques.

Listagens operacionais ainda usam arrays completos; paginação e agregações específicas de dashboard são evolução recomendada para grande volume. O histórico de auditoria já é paginado. Simulação é separada do coletor de telemetria: desativá-la não liga automaticamente a produção a equipamentos reais. O launcher é de desenvolvimento; publicação exige serviços persistentes, HTTPS e variáveis de produção.


## Correção 1.1.1

O cadastro já atribuía o cargo 1 aos novos usuários. Esta correção torna esse contrato explícito (cargo recebido do cliente é somente leitura), centraliza a autorização do Preposto e trata contas sem empresa antes que entrem nas telas operacionais. Uma conta sem vínculo não pode ser autorizada por um simples bypass. A interface de conclusão adicionada na 1.1.1 foi removida na 1.1.3; o vínculo de contas antigas exige correção explícita pelo administrador local.

Não houve acesso ao banco do usuário para determinar a origem exata da conta mostrada na captura. Foram cobertos o cadastro novo, a ausência de flags administrativos Django, contas sem empresa e o ajuste explícito de cargos antigos. Nenhuma promoção de funcionários é feita automaticamente por inferência de data ou ordem de cadastro. O comando local `definir_preposto` exige o e-mail exato da conta a ajustar; não é exposto por uma rota pública.

O teste em Chromium desta correção percorreu cadastro e login pelo auth, confirmou os menus do Preposto, salvou a receita coca-cola, criou uma planta com card e concluiu o cadastro de uma conta sem empresa. A senha e os dados de contas existentes são preservados. Não há mudança de schema nesta versão.
