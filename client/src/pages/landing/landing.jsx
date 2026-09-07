import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import RotatingText from '../components/RotatingText/RotatingText.jsx';
import FerroFluid from '../components/Ferrofluid/ferrofluid.jsx';
import CardNav from '../components/NavBar/navbar.jsx';
import logo from '/logo-01/android-chrome-192x192.png?url';
import './style.css';

const items = [
    {
        label: "Sobre",
        bgColor: "#3E7DFF",
        textColor: "#fff",
        links: [
            { label: "Home", ariaLabel: "About Company", href: 'https://www.google.com/' },
            { label: "Sobre", ariaLabel: "About Company", href: 'https://www.google.com/' },
            { label: "Funcionalidades", ariaLabel: "About Company", href: 'https://www.google.com/' }
        ]
    },
    {
        label: "O Amanhã",
        bgColor: "#2E4E99",
        textColor: "#fff",
        links: [
            { label: "NAUTILUS", ariaLabel: "Featured Projects" },
        ]
    },
    {
        label: "Contato",
        bgColor: "#2E4E99",
        textColor: "#fff",
        links: [
            { label: "Email", ariaLabel: "Email us" },
            { label: "GitHub", ariaLabel: "Gitgub" },
            { label: "LinkedIn", ariaLabel: "LinkedIn" }
        ]
    }
];

function Landing() {
    const navigate = useNavigate();

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
        <div className="landing-page">
            <CardNav
                logo={logo}
                logoAlt="Company Logo"
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

            <section className="landing-hero">
              <FerroFluid
                className = 'background-fluid'
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
            </section>

            <section className="landing-content">
                <div className="container">
                    <h2>Our Services</h2>
                    <p>Discover how we can help you achieve your goals.</p>
                </div>
            </section>
            <section className="landing-testimonials">
                <div className="container">
                    <h2>What Our Clients Say</h2>
                    <p>Don't just take our word for it - hear from our satisfied customers.</p>
                </div>
            </section>
            <section className="landing-contact">
                <div className="container">
                    <h2>Get In Touch</h2>
                    <p>Have questions? We'd love to hear from you.</p>
                </div>
            </section>
        </div>
    );
}

export default Landing;
