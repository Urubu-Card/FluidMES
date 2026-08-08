import { Link } from 'react-router-dom'
import DarkVeil from './components/DarkVeil/DarkVeil'
import RotatingText from './components/RotatingText/RotatingText'

function Landing() {
    return (
        <div className="landing-page">

            <div className="background-darkveil">
                <DarkVeil
                    hueShift={0}
                    noiseIntensity={0}
                    scanlineIntensity={0}
                    speed={.2}
                    scanlineFrequency={0}
                    warpAmount={0}
                />

            </div>

            <div className="content">
                {/* Tudo que você colocar aqui ficará acima do DarkVeil */}

                <Link to="/auth" className="start-button">
                    Começar Agora
                </Link>
                <div className='titulo'>
                    <h1>Fluid
                        <span>
                            <RotatingText
                                texts={[' é inovação', ' é controle', ' é gestão', 'MES']}
                                mainClassName="px-2 sm:px-2 md:px-3 bg-cyan-300 text-black overflow-hidden py-0.5 sm:py-1 md:py-2 justify-center rounded-lg"
                                staggerFrom="last"
                                initial={{ y: "100%", opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                exit={{ y: "-120%", opacity: 0 }}
                                staggerDuration={0.025}
                                animatePresenceInitial={true}
                                splitLevelClassName="overflow-hidden pb-0.5 sm:pb-1 md:pb-1"
                                transition={{ type: "spring", damping: 30, stiffness: 400 }}
                                rotationInterval={1000}
                                splitBy="characters"
                                auto
                                loop={false}
                            />
                        </span>
                    </h1>
                </div>
            </div>

        </div>
    )
}

export default Landing
