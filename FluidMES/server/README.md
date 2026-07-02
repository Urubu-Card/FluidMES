# Todo API — Node.js + Express + Prisma

API REST de tarefas com autenticação JWT. Mesma lógica da API Django, agora em JS.

## Instalação

```bash
npm install
```

Criar e conectar o banco de dados:

```bash
npx prisma generate
npx prisma db push
```

Iniciar o servidor:

```bash
node server.js
```

Servidor rodando em **http://localhost:3000**

---

## Endpoints

### Auth

| Método | Rota                | Descrição                        |
|--------|---------------------|----------------------------------|
| POST   | /api/cadastro       | Cria um novo usuário             |
| POST   | /api/token          | Faz login, retorna access+refresh|
| POST   | /api/token/refresh  | Renova o access token            |

### Tasks (requer Authorization: Bearer <token>)

| Método | Rota            | Descrição              |
|--------|-----------------|------------------------|
| GET    | /api/tasks      | Lista suas tarefas     |
| POST   | /api/tasks      | Cria uma tarefa        |
| GET    | /api/tasks/:id  | Busca uma tarefa       |
| PATCH  | /api/tasks/:id  | Atualiza uma tarefa    |
| DELETE | /api/tasks/:id  | Deleta uma tarefa      |

---

## Exemplos de uso

### 1. Criar usuário
```json
POST /api/cadastro
{ "username": "pedro", "password": "123456" }
```

### 2. Login
```json
POST /api/token
{ "username": "pedro", "password": "123456" }
```
Retorna:
```json
{ "access": "eyJ...", "refresh": "eyJ..." }
```

### 3. Criar tarefa
```
POST /api/tasks
Authorization: Bearer <access token>
{ "titulo": "Minha tarefa", "concluida": false }
```

### 4. Marcar como concluída
```
PATCH /api/tasks/1
Authorization: Bearer <access token>
{ "concluida": true }
```

### 5. Renovar token expirado
```json
POST /api/token/refresh
{ "refresh": "eyJ..." }
```
