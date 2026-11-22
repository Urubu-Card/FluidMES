# FluidMES 1.2.0 — executar e acessar pela LAN

## Atualizar a instalação existente

1. Encerre o projeto com Ctrl+C.
2. Faça backup de `server/db.sqlite3`. Preserve o banco, sua pasta `.venv` e as configurações de ambiente locais.
3. Extraia os arquivos deste ZIP na pasta FluidMES, substituindo o código anterior, inclusive `server/config/settings/dev.py` e `run_local.py`.
4. No PowerShell, dentro da pasta FluidMES, execute:

```powershell
.\.venv\Scripts\python.exe run_local.py
```

O terminal mostra o endereço deste computador e um ou mais endereços **Na rede LAN**, por exemplo:

```text
Neste computador: http://127.0.0.1:5173
Na rede LAN: http://192.168.0.20:5173
```

No outro computador ou celular conectado à mesma rede, abra o endereço da LAN. O IP do exemplo deve ser substituído pelo endereço mostrado no seu terminal. Nenhuma edição de ALLOWED_HOSTS é necessária. Cadastro, login e operações usam a mesma porta 5173. O backend continua interno na porta 8000.

## Primeira instalação

Use Python 3.12 e Node.js 22 ou superior. Na pasta FluidMES:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r server\requirements.txt
.\.venv\Scripts\python.exe run_local.py
```

## Firewall e rede

Quando o Windows perguntar, permita o Node.js em redes privadas. Se o acesso continuar bloqueado, em uma rede local confiável verifique se a conexão está classificada como privada e permita entrada TCP na porta 5173. Não é necessário abrir a porta 8000.

O computador e o terminal precisam permanecer ligados. O dispositivo cliente deve usar uma rede que permita comunicação entre os equipamentos; redes de convidados e isolamento de clientes Wi-Fi podem bloquear esse acesso. Não é necessário encaminhar portas no roteador para uso na mesma LAN.

## Se houver VPN ou várias conexões

Confira o IPv4 da placa de Wi-Fi/Ethernet com `ipconfig`. Para escolher o endereço explicitamente apenas neste terminal:

```powershell
$env:FLUIDMES_LAN_IP = "192.168.0.20"
.\.venv\Scripts\python.exe run_local.py
```

Use seu IP real, sem `http://` nem porta. Se o endereço mudar, atualize essa variável e reinicie o iniciador. Para voltar à detecção automática:

```powershell
Remove-Item Env:FLUIDMES_LAN_IP -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe run_local.py
```

## O que foi corrigido

A configuração local agora define ALLOWED_HOSTS antes de usá-lo, evitando o NameError reportado. Os IPs locais são resolvidos no próprio computador, sem consultar serviços externos. O iniciador compartilha a mesma lista com o backend e prepara as origens CSRF/CORS necessárias ao login. As notificações têm alternativa quando crypto.randomUUID não está disponível pelo HTTP do IP.

O modo fornecido é de desenvolvimento para testes na rede local. O iniciador aplica as migrações incrementais da 1.2. Faça backup do banco antes de atualizar. O guia completo de contas, produção simulada e instalação está em GUIA_EXECUCAO.md.
