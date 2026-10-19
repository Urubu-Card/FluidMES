export const plantFields = [
  { name: "nome", label: "Nome da planta", maxLength: 45 },
  { name: "localizacao", label: "Localização", maxLength: 45 },
  {
    name: "capacidade_l",
    label: "Capacidade útil do tanque (L)",
    type: "number",
    min: 0.01,
    max: 1000000,
    default: 50,
  },
  {
    name: "tempo_reset_seg",
    label: "Reset entre receitas diferentes (s)",
    type: "number",
    min: 0,
    max: 604800,
    default: 60,
    hint: "Repetir a mesma versão da receita não aplica reset.",
  },
];
export const recipeFields = [
  { name: "nome", label: "Nome da receita", maxLength: 45 },
  ...["ingrediente1", "ingrediente2", "ingrediente3"].map((name, i) => ({
    name,
    label: `Ingrediente ${i + 1} · quantidade por unidade`,
    type: "number",
    min: 0,
  })),
  ...["tempo1", "tempo2"].map((name, i) => ({
    name,
    label: `Etapa ${i + 1} · segundos por unidade`,
    type: "number",
    min: 0,
  })),
];
export const orderFields = [
  {
    name: "receita",
    label: "Receita",
    source: "/api/receitas/",
    key: "idreceita",
  },
  { name: "planta", label: "Planta", source: "/api/plantas/", key: "idplanta" },
  {
    name: "quantidade",
    label: "Quantidade a produzir (L)",
    type: "number",
    min: 0.01,
  },
  { name: "prazo", label: "Prazo", type: "date" },
  { name: "pedidocol", label: "Observação", required: false, maxLength: 45 },
];
export const employeeFields = [
  { name: "first_name", label: "Nome", maxLength: 150 },
  { name: "last_name", label: "Sobrenome", maxLength: 150 },
  { name: "email", label: "E-mail", type: "email" },
  { name: "cpf", label: "CPF", hint: "Com ou sem pontuação." },
  { name: "password", label: "Senha inicial / nova senha", type: "password" },
  {
    name: "role",
    label: "Cargo",
    default: 3,
    options: [
      [2, "Chefe"],
      [3, "Funcionário"],
    ],
  },
  { name: "is_active", label: "Conta ativa", type: "checkbox", default: true },
];
export const clpFields = [
  { name: "nome", label: "Nome do CLP" },
  { name: "ip", label: "Endereço IP" },
  {
    name: "porta",
    label: "Porta",
    default: "502",
    hint: "CLP real: 502. Simulador de bancada: 5020.",
  },
  { name: "ativo", label: "Ativo", type: "checkbox", default: true },
  {
    name: "escrita_habilitada",
    label: "Habilitar comandos Modbus neste CLP",
    type: "checkbox",
  },
  { name: "planta", label: "Planta", source: "/api/plantas/", key: "idplanta" },
  {
    name: "tanque",
    label: "Tanque de produção (planilha Modbus)",
    required: false,
    emptyLabel: "Nenhum · somente monitoramento",
    options: [
      ["TK1", "TK1 · registros 1–10, coil 1"],
      ["TK2", "TK2 · registros 11–20, coil 2"],
    ],
    hint: "Com um tanque definido e os comandos habilitados, o MES grava a receita e aciona START_CYCLE quando a planta está no modo 2.",
  },
];
export const sensorFields = [
  { name: "nome", label: "Nome do sensor" },
  { name: "clp", label: "CLP", source: "/api/clps/", key: "idclp" },
  {
    name: "tipo",
    label: "Tipo",
    options: [
      ["volume", "Volume"],
      ["temperatura", "Temperatura"],
      ["pressao", "Pressão"],
      ["vazao", "Vazão"],
      ["nivel", "Nível"],
      ["tempo", "Tempo"],
      ["processo", "Variável de processo"],
    ],
  },
  { name: "unidade", label: "Unidade de medida", dependsOn: "tipo" },
  {
    name: "tipo_registro",
    label: "Registro Modbus",
    options: [
      ["coil", "Coil"],
      ["holding_register", "Holding register"],
      ["input_status", "Input status"],
    ],
  },
  {
    name: "gravavel",
    label: "Permitir escrita neste sensor",
    type: "checkbox",
    hint: "Disponível para coil e holding register quando o CLP aceita comandos.",
  },
  ...["endereco", "minimo", "maximo"].map((name) => ({
    name,
    label: { endereco: "Endereço", minimo: "Mínimo", maximo: "Máximo" }[name],
    type: "number",
  })),
];
export const stopFields = [
  { name: "planta", label: "Planta", source: "/api/plantas/", key: "idplanta" },
  { name: "inicio", label: "Início", type: "datetime-local" },
  { name: "fim", label: "Fim", type: "datetime-local", required: false },
];
