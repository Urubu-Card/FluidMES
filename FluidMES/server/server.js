const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { PrismaClient } = require('@prisma/client');

const app = express();
const prisma = new PrismaClient();
const SECRET = process.env.JWT_SECRET || 'segredo_dev';

app.use(cors());
app.use(express.json());

/* ==============================================
            TOKEN (JWT & AUTENTICAÇÃO)
===============================================*/
function auth(req, res, next) {
  const header = req.headers.authorization;
  if (!header) return res.status(401).json({ erro: 'Token não fornecido.' });

  const token = header.split(' ')[1];
  try {
    // decodifica o token contendo: id, nome, nivel_acesso, empresa_id, tipo_usuario
    req.usuarioLogado = jwt.verify(token, SECRET);
    next();
  } catch {
    return res.status(401).json({ erro: 'Token inválido ou expirado.' });
  }
}

/* ==============================================
            AUTH & CADASTRO DE EMPRESA
===============================================*/

app.post('/api/cadastro', async (req, res) => {
  const { nomeEmpresa, cnpj, nome, email, username, password } = req.body;

  if (!nomeEmpresa || !cnpj || !nome || !email || !username || !password) {
    return res.status(400).json({ erro: 'Todos os campos são obrigatórios para o cadastro.' });
  }

  const cpfLimpo = username.replace(/\D/g, '');
  const cnpjLimpo = cnpj.replace(/\D/g, '');

  try {
    const cpfExisteEmpresa = await prisma.empresa.findUnique({ where: { cpf: cpfLimpo } });
    const cpfExisteFuncionario = await prisma.funcionario.findUnique({ where: { cpf: cpfLimpo } });
    if (cpfExisteEmpresa || cpfExisteFuncionario) {
      return res.status(400).json({ erro: 'Este CPF já está cadastrado no sistema.' });
    }

    const existeCnpj = await prisma.empresa.findUnique({ where: { cnpj: cnpjLimpo } });
    if (existeCnpj) return res.status(400).json({ erro: 'Este CNPJ já está cadastrado.' });

    const existeEmail = await prisma.empresa.findUnique({ where: { email } });
    if (existeEmail) return res.status(400).json({ erro: 'Este e-mail já está cadastrado.' });

    const hash = await bcrypt.hash(password, 10);

    const novaEmpresa = await prisma.empresa.create({
      data: {
        nome_empresa: nomeEmpresa,
        cnpj: cnpjLimpo,
        nome_representante: nome,
        email,
        cpf: cpfLimpo,
        senha: hash
      }
    });

    res.status(201).json({ id: novaEmpresa.id, nome_representante: novaEmpresa.nome_representante, nome_empresa: novaEmpresa.nome_empresa });

  } catch (error) {
    console.error("Erro no cadastro:", error);
    res.status(500).json({ erro: 'Erro interno ao salvar os dados no servidor.' });
  }
});

/* ==============================================
            LOGIN DO USUÁRIO (EMPRESA OU FUNCIONÁRIO)
===============================================*/
app.post('/api/token', async (req, res) => {
  const { username, password } = req.body;
  const cpfLimpo = username.replace(/\D/g, '');

  let conta = null;
  let tipoUsuario = '';

  // 1. Tenta buscar na tabela de empresas
  conta = await prisma.empresa.findUnique({ where: { cpf: cpfLimpo } });
  if (conta) {
    tipoUsuario = 'empresa';
  } else {
    // 2. Se não achar, busca na tabela de funcionários
    conta = await prisma.funcionario.findUnique({ where: { cpf: cpfLimpo } });
    if (conta) tipoUsuario = 'funcionario';
  }

  if (!conta) return res.status(401).json({ erro: 'CPF ou senha incorretos.' });

  const senhaValida = await bcrypt.compare(password, conta.senha);
  if (!senhaValida) return res.status(401).json({ erro: 'CPF ou senha incorretos.' });

  // Monta o payload do token identificando a filiação da empresa pai
  const payload = {
    id: conta.id,
    nome: conta.nome || conta.nome_representante,
    nivel_acesso: conta.nivel_acesso,
    empresa_id: tipoUsuario === 'empresa' ? conta.id : conta.empresa_id,
    tipo_usuario: tipoUsuario
  };

  const access = jwt.sign(payload, SECRET, { expiresIn: '1d' });
  const refresh = jwt.sign({ id: conta.id, cpf: conta.cpf, tipo_usuario: tipoUsuario }, SECRET, { expiresIn: '7d' });

  // Retorna nivel_acesso para o seu Front-end gerenciar os botões invisíveis
  res.json({ access, refresh, nivel_acesso: conta.nivel_acesso });
});

// ── Rota Exclusiva do Chefe: Cadastrar Funcionários ───────────────
app.post('/api/funcionarios', auth, async (req, res) => {
  // Apenas o representante ('admin') possui permissão para criar funcionários
  if (req.usuarioLogado.nivel_acesso !== 'admin') {
    return res.status(403).json({ erro: 'Acesso negado. Apenas o administrador pode cadastrar funcionários.' });
  }

  const { nome, cpf, email, senha, cargo, nivel_acesso } = req.body;

  if (!nome || !cpf || !email || !senha || !cargo || !nivel_acesso) {
    return res.status(400).json({ erro: 'Todos os campos do funcionário são obrigatórios.' });
  }

  if (!['comprador_master', 'comprador_junior'].includes(nivel_acesso)) {
    return res.status(400).json({ erro: 'Nível de acesso inválido para funcionário.' });
  }

  const cpfLimpo = cpf.replace(/\D/g, '');

  try {
    const cpfExisteEmpresa = await prisma.empresa.findUnique({ where: { cpf: cpfLimpo } });
    const cpfExisteFuncionario = await prisma.funcionario.findUnique({ where: { cpf: cpfLimpo } });
    if (cpfExisteEmpresa || cpfExisteFuncionario) {
      return res.status(400).json({ erro: 'Este CPF já está em uso.' });
    }

    const emailExiste = await prisma.funcionario.findUnique({ where: { email } });
    if (emailExiste) return res.status(400).json({ erro: 'Este e-mail já está em uso.' });

    const hashSenha = await bcrypt.hash(senha, 10);

    const novoFuncionario = await prisma.funcionario.create({
      data: {
        nome,
        cpf: cpfLimpo,
        email,
        senha: hashSenha,
        cargo,
        nivel_acesso,
        empresa_id: req.usuarioLogado.id // Vincula automaticamente à empresa do chefe logado
      }
    });

    res.status(201).json({ id: novoFuncionario.id, nome: novoFuncionario.nome, nivel_acesso: novoFuncionario.nivel_acesso });
  } catch (error) {
    console.error(error);
    res.status(500).json({ erro: 'Erro interno ao cadastrar funcionário.' });
  }
});

// ── Tasks (Gerenciamento de Pedidos por Empresa) ─────────────────

// Listar tarefas/pedidos da Empresa (Todos os funcionários daquela empresa visualizam)
app.get('/api/tasks', auth, async (req, res) => {
  const tasks = await prisma.task.findMany({
    where: {
      OR: [
        { empresa_criador_id: req.usuarioLogado.empresa_id },
        { funcionario_criador: { empresa_id: req.usuarioLogado.empresa_id } }
      ]
    },
    orderBy: { criada_em: 'desc' },
  });
  res.json(tasks);
});

// Criar Tarefa/Pedido
app.post('/api/tasks', auth, async (req, res) => {
  const { titulo, descricao } = req.body;
  if (!titulo) return res.status(400).json({ erro: 'O título é obrigatório.' });

  const dadosTarefa = {
    titulo,
    descricao: descricao || '',
    situacao: 'Pendente'
  };

  // Identifica dinamicamente quem está inserindo baseado no tipo definido no login
  if (req.usuarioLogado.tipo_usuario === 'empresa') {
    dadosTarefa.empresa_criador_id = req.usuarioLogado.id;
  } else {
    dadosTarefa.funcionario_criador_id = req.usuarioLogado.id;
  }

  const task = await prisma.task.create({ data: dadosTarefa });
  res.status(201).json(task);
});

// Aprovar ou Alterar Situação da Tarefa
app.patch('/api/tasks/:id', auth, async (req, res) => {
  const { situacao } = req.body;
  const taskId = Number(req.params.id);

  const task = await prisma.task.findUnique({ where: { id: taskId } });
  if (!task) return res.status(404).json({ erro: 'Tarefa não encontrada.' });

  const dadosAtualizacao = {};

  if (situacao) {
    // REGRA DE NEGÓCIO: Se a situação for mudada para "Concluido" ou qualquer aprovação, valida os cargos
    if (['Concluido', 'Em andamento'].includes(situacao)) {
      const podeAprovar = ['admin', 'comprador_master'].includes(req.usuarioLogado.nivel_acesso);
      if (!podeAprovar) {
        return res.status(403).json({ erro: 'Acesso negado. Seu nível de acesso não permite aprovar/dar andamento em tarefas.' });
      }

      // Grava quem foi o aprovador oficial da ação
      if (req.usuarioLogado.tipo_usuario === 'empresa') {
        dadosAtualizacao.aprovado_por_empresa_id = req.usuarioLogado.id;
      } else {
        dadosAtualizacao.aprovado_por_funcionario_id = req.usuarioLogado.id;
      }
    }
    dadosAtualizacao.situacao = situacao;
  }

  // Permite atualizar outros campos de texto da req.body enviados pelo front
  if (req.body.titulo) dadosAtualizacao.titulo = req.body.titulo;
  if (req.body.descricao) dadosAtualizacao.descricao = req.body.descricao;

  const updated = await prisma.task.update({
    where: { id: taskId },
    data: dadosAtualizacao,
  });

  res.json(updated);
});

// Deletar tarefa
app.delete('/api/tasks/:id', auth, async (req, res) => {
  if (req.usuarioLogado.nivel_acesso !== 'admin') {
    return res.status(403).json({ erro: 'Apenas o administrador da empresa pode remover registros.' });
  }

  try {
    await prisma.task.delete({ where: { id: Number(req.params.id) } });
    res.status(204).send();
  } catch {
    res.status(404).json({ erro: 'Tarefa não encontrada.' });
  }
});

// ── ROTA: Buscar Perfil do Usuário Logado ──────────────────────
app.get('/api/profile', auth, async (req, res) => {
  try {
    const { id, tipo_usuario } = req.usuarioLogado;

    if (tipo_usuario === 'empresa') {
      const empresa = await prisma.empresa.findUnique({
        where: { id: id },
        select: { nome_representante: true }
      });
      if (!empresa) return res.status(404).json({ erro: 'Perfil não encontrado.' });
      return res.json({
        nome: empresa.nome_representante,
        cargo: 'Diretor / Admin',
        fotoUrl: null
      });
    }

    if (tipo_usuario === 'funcionario') {
      const funcionario = await prisma.funcionario.findUnique({
        where: { id: id },
        select: { nome: true, cargo: true }
      });
      if (!funcionario) return res.status(404).json({ erro: 'Perfil não encontrado.' });
      return res.json({
        nome: funcionario.nome,
        cargo: funcionario.cargo,
        fotoUrl: null
      });
    }

    return res.status(400).json({ erro: 'Tipo de usuário inválido.' });
  } catch (error) {
    console.error('Erro ao buscar perfil:', error);
    res.status(500).json({ erro: 'Erro interno ao carregar perfil.' });
  }
});

// Abrir servidor
app.listen(3000, () => {
  console.clear();
  console.log(`

    |================================|
    | Servidor rodando na porta 3000 |
    |================================|
`);
});
