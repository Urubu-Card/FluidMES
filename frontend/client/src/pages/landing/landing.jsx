import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import RotatingText from '../components/RotatingText/RotatingText.jsx';
import FerroFluid from '../components/Ferrofluid/ferrofluid.jsx';
import CardNav from '../components/NavBar/navbar.jsx';
import logo from '/logo-01/android-chrome-192x192.png?url';
import './style.css';
import './additions.css';
import useSectionScroll from './hooks/useSectionScroll.js';
import useElementMotion from './hooks/useElementMotion.js';
import { SectionNavigation, HeroDetails, Pillars, Architecture, Impact, Academic, FAQFooter } from './LandingAdditions.jsx';

const items = [
    {
        label: "Conheça",
        bgColor: "#3E7DFF",
        textColor: "#fff",
        links: [
            { label: "Início", ariaLabel: "Ir para o início", href: "#inicio" },
            { label: "Solução", ariaLabel: "Conhecer a solução", href: "#solucao" },
            { label: "Funcionalidades", ariaLabel: "Explorar funcionalidades", href: "#tecnologia" },
        ],
    },
    {
        label: "Produção",
        bgColor: "#2E4E99",
        textColor: "#fff",
        links: [
            { label: "Rastreabilidade", ariaLabel: "Fluxo de produção", href: "#producao" },
            { label: "Indicadores e OEE", ariaLabel: "Eficiência da linha", href: "#resultados" },
        ],
    },
    {
        label: "Acesso",
        bgColor: "#2E4E99",
        textColor: "#fff",
        links: [
            { label: "Segurança", ariaLabel: "Perfis de acesso", href: "#equipe" },
            { label: "Dúvidas frequentes", ariaLabel: "Perguntas e respostas", href: "#contato" },
            { label: "Começar agora", ariaLabel: "Acessar cadastro", href: "/auth?modo=cadastro" },
        ],
    },
];

function Landing() {
    const navigate = useNavigate();
    const landingRef = useRef(null);
    const activeSection = useSectionScroll(landingRef);
    useElementMotion(landingRef);

    useEffect(() => {
        // esconde a Landing Page e joga o usuário para o Login/App
        const isPWA = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
        if (isPWA) {
            navigate('/login');
            return;
        }
        const handleBeforeInstallPrompt = (e) => {
            e.preventDefault();
            console.log('Instalação desativada na Landing Page.');
        };

        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
        };
    }, [navigate]);

    return (
        <div className="landing-page" ref={landingRef}>
            <SectionNavigation active={activeSection} />
            <CardNav
                logo={logo}
                logoAlt="FluidMES Logo"
                logoHref="#inicio"
                items={items}
                baseColor={"var(--cinza-escuro)"}
                menuColor={"var(--branco-azulado)"}
                buttonBgColor="var(--azul-ceu)"
                buttonTextColor="var(--branco-azulado)"
                ease="circ.out"
                theme="dark"
                onclick={() => {
                    const background = document.getElementsByClassName("landing-hero")[0];
                    if (background) background.style.filter = "blur(5px)";
                }}
            />

            <section className="landing-hero" id='inicio' tabIndex={-1}>
                <FerroFluid
                    className='background-fluid'
                    colors={["#2E4E99", "#3E7DFF", "#DBF3FF"]}
                    scale={1.6}
                    speed={.1}
                    turbulence={1}
                    fluidity={0.15}
                    rimWidth={0.2}
                    sharpness={2.5}
                    shimmer={1.5}
                    glow={2.8}
                    flowDirection="down"
                    opacity={.67}
                    mouseInteraction={false}
                />
                <div className='content'>
                    <h1>Fluid
                        <span>
                            <RotatingText
                                texts={[' é inovação', ' é controle', ' é gestão', 'MES']}
                                mainClassName="px-2 sm:px-2 md:px-3 text-black overflow-hidden py-0.5 sm:py-1 md:py-2 flex items-center justify-center rounded-lg"
                                style={{ backgroundColor: '#2E4E99' }}
                                staggerFrom="center"
                                initial={{ y: "100%" }}
                                animate={{ y: 0 }}
                                staggerDuration={0.02}
                                splitLevelClassName="overflow-hidden pb-0.5 sm:pb-1 md:pb-1"
                                transition={{ type: "spring", damping: 20, stiffness: 500 }}
                                rotationInterval={1500}
                                splitBy="lines"
                                auto
                                loop={false}
                            />
                        </span>
                    </h1>
                </div>
                <HeroDetails />
            </section>

            <section className="landing-content" id="solucao" tabIndex={-1}>
                <div className="container">
                    <Pillars />
                </div>
            </section>
            <Architecture />
            <section className="landing-testimonials" id="resultados" tabIndex={-1}>
                <div className="container">
                    <Impact />
                </div>
            </section>
            <Academic />
            <section className="landing-contact" id="contato" tabIndex={-1}>
                <div className="container">
                    <FAQFooter />
                </div>
            </section>
        </div>
    );
}

export default Landing;
