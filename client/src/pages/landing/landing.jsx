import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import RotatingText from '../components/RotatingText/rotatingText';
import Ferrofluid from '../components/Ferrofluid/ferrofluid';
import CardNav from '../components/NavBar/navBar';
import logo from '../../../public/logo/android-chrome-192x192.png';
import './style.css';

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

    return (
        <div className="landing-page">
            <CardNav
                logo={logo}
                logoAlt="Company Logo"
                items={items}
                baseColor="#24282e"
                menuColor={"var(--branco-azulado)"}
                buttonBgColor="var(--azul-ceu)"
                buttonTextColor="var(--branco-azulado)"
                ease="circ.out"
                theme="dark"
            />

            <section className="landing-hero">
                <Ferrofluid
                    className="ferrofluid"
                    colors={["#2E4E99", "#3E7DFF", "#DBF3FF"]}
                    speed={0.1}
                    scale={1.6}
                    turbulence={1}
                    fluidity={0.15}
                    rimWidth={0.2}
                    sharpness={2.5}
                    shimmer={1.5}
                    glow={3}
                    flowDirection="down"
                    opacity={1}
                    mouseInteraction={false}
                />
                <div className='content'>
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
