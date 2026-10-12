import { Link } from "react-router-dom";

const sectionLinks = [
    ["inicio", "Início"],
    ["solucao", "Solução"],
    ["tecnologia", "Funcionalidades"],
    ["producao", "Produção"],
    ["resultados", "Indicadores"],
    ["equipe", "Segurança"],
    ["contato", "FAQ"],
];

const Icon = ({ name }) => <i className={`bi bi-${name}`} aria-hidden="true" />;

export function SectionNavigation({ active }) {
    return (
        <nav className="fm-section-nav" aria-label="Seções da FluidMES">
            {sectionLinks.map(([id, label]) => (
                <a
                    key={id}
                    data-section-link
                    href={`#${id}`}
                    aria-label={label}
                    aria-current={active === id ? "location" : undefined}
                >
                    <span className="fm-dot" />
                    <span className="fm-nav-label">{label}</span>
                </a>
            ))}
        </nav>
    );
}

export function HeroDetails() {
    return (
        <div className="fm-hero-details fm-reveal">
            <p className="fm-eyebrow"></p>

            <h2>
                O controle da sua fábrica.
                <br />
                em{" "}
                <strong style={{ color: "var(--azul-ceu)" }}>cada gota</strong>.
            </h2>

            <p>
                Saiba o que acontece em cada planta, acompanhe suas máquinas em
                tempo real e tome decisões com dados de produção — não com
                suposições.
            </p>

            <div className="fm-actions">
                <Link to="/auth" className="fm-button">
                    Começar Agora
                </Link>

                <a href="#solucao" data-section-link className="fm-link">
                    Conhecer a solução
                </a>
            </div>

            <a
                className="fm-scroll-cue"
                href="#solucao"
                data-section-link
                aria-label="Rolar para a solução"
            >
                <span>SAIBA MAIS</span>

                <Icon name="mouse" />
            </a>
        </div>
    );
}

export function Pillars() {
    return (
        <div className="fm-additions fm-reveal">
            <p className="fm-eyebrow"></p>

            <h2>A fábrica não pode depender de achismos.</h2>

            <p className="fm-intro">
                Máquina parada, sensor fora do limite, produção abaixo do
                esperado: sem uma visão centralizada, problemas passam
                despercebidos. A FluidMES reúne as informações da operação para
                você acompanhar o que importa.
            </p>

            <div className="fm-grid fm-three">
                {[
                    [
                        "activity",

                        "Enxergue sua operação",

                        "Veja o status das máquinas, as leituras dos sensores e o andamento da produção em um só lugar.",
                    ],

                    [
                        "cash-coin",

                        "Gestão Decida com confiança",

                        "Consulte eficiência, histórico de paradas e produção realizada para entender melhor cada resultado.",
                    ],

                    [
                        "droplet-half",

                        "Controle de desperdício",

                        "Transforme registros de consumo em indicadores de perdas. Identifique desvios para aproveitar melhor cada insumo.",
                    ],
                ].map(([icon, title, text]) => (
                    <article className="fm-card" key={title}>
                        <div className="fm-card-top">
                            <Icon name={icon} />
                        </div>

                        <h3>{title}</h3>

                        <p>{text}</p>
                    </article>
                ))}
            </div>

            <DemoPanel />
        </div>
    );
}

function DemoPanel() {
    return (
        <div
            className="fm-demo"
            aria-label="Painel ilustrativo com dados simulados"
        >
            <div className="fm-demo-heading">
                <span>
                    <Icon name="speedometer2" /> Visão da produção
                </span>

                <small>DADOS SIMULADOS</small>
            </div>

            <div className="fm-demo-grid">
                <div className="fm-demo-kpis">
                    {[
                        ["Vazão", "24,8", "L/min"],

                        ["Nível", "72", "%"],

                        ["Pressão", "2,4", "bar"],
                    ].map(([label, value, unit]) => (
                        <div key={label}>
                            <span>{label}</span>

                            <strong>
                                {value} <small>{unit}</small>
                            </strong>
                        </div>
                    ))}
                </div>

                <div className="fm-chart">
                    <span>Vazão ao longo do ciclo</span>

                    <svg
                        viewBox="0 0 600 115"
                        role="img"
                        aria-label="Curva ilustrativa da vazão, sem representar medições reais"
                    >
                        <defs>
                            <linearGradient
                                id="fm-area"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="0%"
                                    stopColor="#3E7DFF"
                                    stopOpacity=".35"
                                />

                                <stop
                                    offset="100%"
                                    stopColor="#3E7DFF"
                                    stopOpacity="0"
                                />
                            </linearGradient>
                        </defs>

                        {[25, 55, 85].map((y) => (
                            <line
                                key={y}
                                x1="0"
                                x2="600"
                                y1={y}
                                y2={y}
                                stroke="#526276"
                                strokeDasharray="4 8"
                            />
                        ))}

                        <path
                            d="M0 90 L35 82 L70 91 L105 65 L140 70 L175 48 L210 60 L245 43 L280 55 L315 24 L350 40 L385 32 L420 46 L455 20 L490 34 L525 18 L560 27 L600 15 L600 115 L0 115Z"
                            fill="url(#fm-area)"
                        />

                        <polyline
                            points="0,90 35,82 70,91 105,65 140,70 175,48 210,60 245,43 280,55 315,24 350,40 385,32 420,46 455,20 490,34 525,18 560,27 600,15"
                            fill="none"
                            stroke="#3E7DFF"
                            strokeWidth="3"
                        />
                    </svg>

                    <div className="fm-chart-labels">
                        <span>Início</span>

                        <span>Etapa intermediária</span>

                        <span>Fim do ciclo</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Conteúdo orientado ao produto (cards e fluxo).
const capabilities = [
    {
        icon: "broadcast-pin",
        label: "ACOMPANHAMENTO",
        title: "Monitoramento em tempo real",
        text: "Acompanhe cada planta, a situação online/offline das máquinas, os sensores e o fluxo de produção.",
    },
    {
        icon: "exclamation-triangle",
        label: "PREVENÇÃO",
        title: "Alarmes configuráveis",
        text: "Receba alertas quando um sensor ultrapassar os limites definidos e registre o reconhecimento pelo operador.",
    },
    {
        icon: "boxes",
        label: "ORGANIZAÇÃO",
        title: "Gestão da produção",
        text: "Organize o processo de receita até lote, conectando pedidos e ordens de produção.",
    },
    {
        icon: "speedometer",
        label: "EFICIÊNCIA",
        title: "OEE automático",
        text: "Visualize a eficiência da linha por meio da disponibilidade, performance e qualidade.",
    },
    {
        icon: "pause-circle",
        label: "HISTÓRICO",
        title: "Registro de paradas",
        text: "Saiba quando a linha parou e por quanto tempo, com registros que ajudam a analisar a operação.",
    },
    {
        icon: "shield-lock",
        label: "SEGURANÇA",
        title: "Controle de permissões",
        text: "Defina o que cada perfil pode acessar e executar, inclusive nas funções que envolvem máquinas.",
    },
];

export function Capabilities() {
    return (
        <div className="fm-additions fm-reveal">
            <p className="fm-eyebrow"></p>
            <h2>
                O que você precisa para{" "}
                <span className="fm-accent-text">operar melhor.</span>
            </h2>
            <p className="fm-intro">
                Da leitura dos sensores à análise de eficiência, a FluidMES
                conecta os pontos da operação e transforma informações dispersas
                em uma visão clara.
            </p>
            <div className="fm-grid fm-three fm-feature-grid">
                {capabilities.map(({ icon, label, title, text }) => (
                    <article className="fm-card fm-feature-card" key={title}>
                        <div className="fm-card-top">
                            <Icon name={icon} />
                            <span>{label}</span>
                        </div>
                        <h3>{title}</h3>
                        <p>{text}</p>
                    </article>
                ))}
            </div>
        </div>
    );
}

const productionSteps = [
    {
        number: "01",
        icon: "file-earmark-text",
        title: "Receita",
        text: "Defina a base do que será produzido.",
    },
    {
        number: "02",
        icon: "cart-check",
        title: "Pedido",
        text: "Registre a demanda de produção.",
    },
    {
        number: "03",
        icon: "clipboard-check",
        title: "Ordem",
        text: "Organize e encaminhe a execução.",
    },
    {
        number: "04",
        icon: "box-seam",
        title: "Lote",
        text: "Rastreie o que foi produzido, quando e como.",
    },
];

export function ProductionFlow() {
    return (
        <div className="fm-additions fm-reveal">
            <div className="fm-split fm-process-split">
                <div>
                    <h2>
                        Do planejamento ao lote.{" "}
                        <span className="fm-accent-text">
                            Tudo tem um caminho.
                        </span>
                    </h2>
                    <p className="fm-intro">
                        Não basta saber quanto saiu da linha. É importante
                        entender de onde veio cada produção. A FluidMES conecta
                        as etapas em um fluxo rastreável, do cadastro da receita
                        ao lote final.
                    </p>
                    <ul className="fm-checklist">
                        <li>
                            <Icon name="check-circle" /> Relacione receitas,
                            pedidos e ordens de produção.
                        </li>
                        <li>
                            <Icon name="check-circle" /> Acompanhe a execução de
                            cada lote.
                        </li>
                        <li>
                            <Icon name="check-circle" /> Consulte o histórico
                            para compreender o que foi produzido.
                        </li>
                    </ul>
                    <a
                        href="#resultados"
                        data-section-link
                        className="fm-inline-cta"
                    >
                        Veja como analisar seus resultados{" "}
                        <Icon name="arrow-right" />
                    </a>
                </div>
                <div
                    className="fm-architecture fm-process-panel"
                    aria-label="Etapas do fluxo de gestão da produção"
                >
                   
                    <div className="fm-process-steps">
                        {productionSteps.map(
                            ({ number, icon, title, text }, index) => (
                                <div className="fm-process-step" key={number}>
                                    <div className="fm-process-number">
                                        {number}
                                    </div>
                                    <div className="fm-process-icon">
                                        <Icon name={icon} />
                                    </div>
                                    <div className="fm-process-description">
                                        <h3>{title}</h3>
                                        <p>{text}</p>
                                    </div>
                                    {index !== productionSteps.length - 1 && (
                                        <span
                                            className="fm-process-line"
                                            aria-hidden="true"
                                        />
                                    )}
                                </div>
                            ),
                        )}
                    </div>
                    
                </div>
            </div>
        </div>
    );
}

export function Performance() {
    return (
        <div className="fm-additions fm-reveal">
          <h2>
                Saiba como sua linha{" "}
                <span className="fm-accent-text">realmente performa.</span>
            </h2>
            <p className="fm-intro">
                A FluidMES calcula o OEE automaticamente e apresenta os
                indicadores no dashboard. Junto aos registros de paradas, você
                consegue enxergar a operação além do volume produzido.
            </p>
            <div className="fm-split fm-performance-split">
                <div className="fm-architecture fm-oee-panel">
                    <div className="fm-oee-header">
                        <span>
                            <Icon name="speedometer2" /> Eficiência da linha
                        </span>
                        
                    </div>
                    <div className="fm-oee-overview">
                        <div
                            className="fm-oee-ring"
                            role="img"
                            aria-label="OEE simulado de 82 por cento"
                        >
                            <div>
                                <strong>82%</strong>
                                <small>OEE</small>
                            </div>
                        </div>
                        <div className="fm-oee-breakdown">
                            {[
                                ["Disponibilidade", "90%"],
                                ["Performance", "94%"],
                                ["Qualidade", "97%"],
                            ].map(([name, value]) => (
                                <div className="fm-oee-bar" key={name}>
                                    <div>
                                        <span>{name}</span>
                                        <strong>{value}</strong>
                                    </div>
                                    <div className="fm-oee-track">
                                        <span style={{ width: value }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                    
                </div>
                <div className="fm-performance-list">
                    <article className="fm-metric">
                        <span className="fm-metric-symbol">
                            <Icon name="speedometer2" />
                        </span>
                        <h3>OEE: eficiência em perspectiva</h3>
                        <p>
                            Reúne disponibilidade, performance e qualidade em um
                            indicador para acompanhar a eficiência da linha.
                        </p>
                    </article>
                    <article className="fm-metric">
                        <span className="fm-metric-symbol">
                            <Icon name="clock-history" />
                        </span>
                        <h3>Paradas registradas</h3>
                        <p>
                            Consulte quando a produção foi interrompida e o
                            tempo que a linha permaneceu parada.
                        </p>
                    </article>
                    <article className="fm-metric">
                        <span className="fm-metric-symbol">
                            <Icon name="bar-chart-line" />
                        </span>
                        <h3>Informação para decidir</h3>
                        <p>
                            Visualize os indicadores no dashboard e identifique
                            pontos que merecem investigação.
                        </p>
                    </article>
                </div>
            </div>
        </div>
    );
}

const roles = [
    {
        icon: "person-gear",
        name: "Preposto",
        subtitle: "Visão de gestão",
        detail: "É o proprietário com acesso à visão geral da operação e ao dashboard completo.",
    },
    {
        icon: "person-check",
        name: "Operador / Chefe",
        subtitle: "Aprovação da produção",
        detail: "Atua na aprovação das ordens de produção, de acordo com as permissões do perfil.",
    },
    {
        icon: "person",
        name: "Visualizador / Funcionário",
        subtitle: "Solicitações",
        detail: "Pode criar solicitações dentro do fluxo de produção, respeitando seu nível de acesso.",
    },
];

export function AccessControl() {
    return (
        <div className="fm-additions fm-reveal">
            <h2>
                Controle para a operação.{" "}
                <span className="fm-accent-text">Segurança para todos.</span>
            </h2>
            <p className="fm-intro">
                Um MES interage com equipamentos reais. Por isso, a
                FluidMES diferencia as permissões de cada pessoa e protege o
                acesso às ações da operação.
            </p>
            <div className="fm-grid fm-three fm-roles">
                {roles.map(({ icon, name, subtitle, detail }) => (
                    <article className="fm-card fm-role-card" key={name}>
                        <div className="fm-role-icon">
                            <Icon name={icon} />
                        </div>
                        <h3>{name}</h3>
                        <span className="fm-role">{subtitle}</span>
                        <p>{detail}</p>
                    </article>
                ))}
            </div>
            
        </div>
    );
}

// Adaptadores: o landing.jsx ORIGINAL continua importando
// Architecture, Impact e Academic, sem nenhuma mudança nas importações.
// O React Fragment cria duas seções irmãs; useSectionScroll reconhece ambas.
export function Architecture() {
    return (
        <>
            <section className="fm-new-section" id="tecnologia" tabIndex={-1}>
                <div className="container">
                    <Capabilities />
                </div>
            </section>
            <section className="fm-new-section" id="producao" tabIndex={-1}>
                <div className="container">
                    <ProductionFlow />
                </div>
            </section>
        </>
    );
}


export function Impact() {
    return <Performance />;
}

export function Academic() {
    return (
        <section className="fm-new-section" id="equipe" tabIndex={-1}>
            <div className="container">
                <AccessControl />
            </div>
        </section>
    );
}

const questions = [
    [
        "Para que serve a FluidMES?",
        "Para acompanhar e gerenciar a produção de indústrias de fluidos. O sistema reúne informações das máquinas, sensores, alarmes, ordens, lotes e indicadores em uma visão centralizada.",
    ],
    [
        "É possível ver o que acontece na fábrica em tempo real?",
        "Sim. A proposta da FluidMES é exibir o status das máquinas, leituras dos sensores e o fluxo de produção no painel de cada planta.",
    ],
    [
        "Como funcionam os alarmes?",
        "O sistema sinaliza quando uma leitura ultrapassa os limites definidos para um sensor. Esses limites podem ser configurados, e o operador pode reconhecer o alarme.",
    ],
    [
        "Como a FluidMES acompanha a eficiência da linha?",
        "Por meio do OEE, calculado automaticamente com base em disponibilidade, performance e qualidade. O painel também apresenta o histórico de paradas.",
    ],
    [
        "Como a produção é organizada?",
        "A gestão conecta receita, pedido, ordem e lote, permitindo acompanhar o que foi produzido, quando e como. Atualmente, cada planta possui uma linha de produção.",
    ],
    [
        "Todos os usuários têm o mesmo acesso?",
        "Não. A FluidMES trabalha com perfis: Preposto, Operador/Chefe e Visualizador/Funcionário. Cada um conta com permissões relacionadas à sua função.",
    ],
];

export function FAQFooter() {
    return (
        <div className="fm-additions fm-reveal">
            
            <h2>
                Tudo mais claro.{" "}
                <span className="fm-accent-text">Do início ao fim.</span>
            </h2>
            <p className="fm-intro">
                Conheça melhor como a FluidMES ajuda a transformar os dados do
                chão de fábrica em acompanhamento e controle da produção.
            </p>
            <div className="fm-faq">
                {questions.map(([question, answer]) => (
                    <details key={question}>
                        <summary>
                            {question}
                            <Icon name="plus-lg" />
                        </summary>
                        <p>{answer}</p>
                    </details>
                ))}
            </div>
            <div className="fm-final">
                <div>
                    <p className="fm-eyebrow">SUA PRODUÇÃO, EM SUAS MÃOS</p>
                    <h3>
                        Mais visibilidade. Mais controle.
                        <br />
                        <span className="fm-accent-text">Em cada gota.</span>
                    </h3>
                    <p>Descubra uma nova forma de acompanhar sua operação.</p>
                </div>
                <div className="fm-actions">
                    <Link to="/auth" className="fm-button">
                        Começar agora <Icon name="arrow-up-right" />
                    </Link>
                    <Link to="/login" className="fm-button fm-ghost">
                        Já tenho acesso <Icon name="box-arrow-in-right" />
                    </Link>
                </div>
            </div>
            <footer className="fm-footer">
                <span>
                    © {new Date().getFullYear()} FluidMES · Controle
                    inteligente da produção
                </span>
                
                <a href="#inicio" data-section-link>
                    Voltar ao início <Icon name="arrow-up" />
                </a>
            </footer>
        </div>
    );
}
