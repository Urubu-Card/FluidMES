import { Link } from 'react-router-dom'
import DarkVeil from '../components/DarkVeil/DarkVeil'
import RotatingText from '../components/RotatingText/RotatingText'
import Ferrofluid from '../components/Ferrofluid/Ferrofluid';
import CardNav from '../components/NavBar/navbar'
import logo from '../../../public/logo/android-chrome-192x192.png';

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
    return (
        <div className="landing-page">
            <CardNav
                logo={logo}
                logoAlt="Company Logo"
                items={items}
                baseColor="#24282e"
                menuColor="#DBF3FF"
                buttonBgColor="#3E7DFF"
                buttonTextColor="#DBF3FF"
                ease="circ.out"
                theme="dark"
            />

            <div className="background-fluid">
                {/*
                <Ferrofluid
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
                />*/}

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
                                mainClassName="px-2 sm:px-2 md:px-3 text-black overflow-hidden py-0.5 sm:py-1 md:py-2 justify-center rounded-lg"
                                style={{ backgroundColor: '#2E4E99' }}
                                staggerFrom="center"
                                initial={{ y: "100%" }}
                                animate={{ y: 0 }}
                                exit={{ y: "-120%" }}
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
            <section></section>
            <section></section>
            <section></section>

        </div>
    )
}

export default Landing
