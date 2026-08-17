import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import RotatingText from '../components/RotatingText/RotatingText';
import Ferrofluid from '../components/Ferrofluid/Ferrofluid';
import CardNav from '../components/NavBar/navbar';
import logo from '../../../public/logo/android-chrome-192x192.png';
import { gsap } from 'gsap';
import './landing.css';

const items = [
    {
        label: "Sobre",
        bgColor: "#3E7DFF",
        textColor: "#fff",
        links: [
            { label: "Home", ariaLabel: "About Company", href: 'https://google.com' },
            { label: "Sobre", ariaLabel: "About Company", href: 'https://google.com' },
            { label: "Funcionalidades", ariaLabel: "About Company", href: 'https://google.com' }
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
    const [isHamburgerOpen, setIsHamburgerOpen] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);

    // Referências vinculadas ao HTML abaixo para o GSAP funcionar
    const line1Ref = useRef(null);
    const line2Ref = useRef(null);
    const tlRef = useRef(null);

    const menuColor = "#DBF3FF";

    useEffect(() => {
        const tl = gsap.timeline({ paused: true });

        // Executa a animação transformando as linhas no "X"
        tl.to(line1Ref.current, { y: 6, rotate: 45, duration: 0.25, ease: "power2.inOut" }, 0)
          .to(line2Ref.current, { y: -6, rotate: -45, duration: 0.25, ease: "power2.inOut" }, 0);

        tlRef.current = tl;

        return () => tl.kill(); 
    }, []);

    const toggleMenu = () => {
        const tl = tlRef.current;
        if (!tl) return;
        if (!isExpanded) {
            setIsHamburgerOpen(true);
            setIsExpanded(true);
            tl.play(0);
        } else {
            setIsHamburgerOpen(false);
            tl.eventCallback('onReverseComplete', () => setIsExpanded(false));
            tl.reverse();
        }
    };

    return (
        <div className="landing-page">
            <CardNav
                logo={logo}
                logoAlt="Company Logo"
                items={items}
                baseColor="#24282e"
                menuColor={menuColor}
                buttonBgColor="#3E7DFF"
                buttonTextColor="#DBF3FF"
                ease="circ.out"
                theme="dark"
            />

            <nav className="navbar navbar-expand-lg bg-body-tertiary rounded" aria-label="Thirteenth navbar example">
                <div className="container-fluid">
                    <button className="navbar-toggler collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#navbarsExample11" aria-controls="navbarsExample11" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                    </button>

                    <div className="navbar-collapse d-lg-flex collapse" id="navbarsExample11">
                        <div
                            className={`hamburger-menu ${isHamburgerOpen ? 'open' : ''}`}
                            onClick={toggleMenu}
                            onKeyDown={e => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                    e.preventDefault();
                                    toggleMenu();
                                }
                            }}
                            role="button"
                            aria-label={isExpanded ? 'Close menu' : 'Open menu'}
                            aria-expanded={isExpanded}
                            tabIndex={0}
                            style={{ color: menuColor || '#000' }}
                        >
                            {/* CORRIGIDO: Referências adicionadas aqui para o GSAP encontrar os alvos */}
                            <div className="hamburger-line" ref={line1Ref} />
                            <div className="hamburger-line" ref={line2Ref} />
                        </div>
                        <ul className="navbar-nav col-lg-6 justify-content-lg-center">
                            <li className="nav-item">
                                <a className="nav-link active" aria-current="page" href="#">Home</a>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link" href="#">Link</a>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link disabled" aria-disabled="true">Disabled</a>
                            </li>
                            <li className="nav-item dropdown">
                                <a className="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown" aria-expanded="false">Dropdown</a>
                                <ul className="dropdown-menu">
                                    <li><a className="dropdown-item" href="#">Action</a></li>
                                    <li><a className="dropdown-item" href="#">Another action</a></li>
                                    <li><a className="dropdown-item" href="#">Something else here</a></li>
                                </ul>
                            </li>
                        </ul>
                        <div className="d-lg-flex col-lg-3 justify-content-lg-end">
                            <button className="btn btn-primary">Button</button>
                        </div>
                    </div>
                </div>
            </nav>

            <div className="background-fluid">
                {/* Ferrofluid descomente aqui se for usar */}
            </div>

            <section className="content">
                <Link to="/auth" className="start-button">
                    Começar Agora
                </Link>
                <div className='titulo'>
                    <h1>Fluid
                        <span>
                            <RotatingText
                                texts={[' é inovação', ' é controle', ' é gestão', 'MES']}
                                mainclassName="px-2 sm:px-2 md:px-3 text-black overflow-hidden py-0.5 sm:py-1 md:py-2 justify-center rounded-lg"
                                style={{ backgroundColor: '#2E4E99' }}
                                staggerFrom="center"
                                initial={{ y: "100%" }}
                                animate={{ y: 0 }}
                                
                                staggerDuration={0.02}
                                splitLevelclassName="overflow-hidden pb-0.5 sm:pb-1 md:pb-1"
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
            <section></section>
            <section></section>
            <section></section>
        </div>
    );
}

export default Landing;
