import { Link } from 'react-router-dom'
import DarkVeil from './components/DarkVeil/DarkVeil'

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
            </div>

        </div>
    )
}

export default Landing
