import React from 'react';
import Particles from '../components/Particles/particles.jsx';
import './style.css';


const MinhaPagina = () => {
    return (
        <div>
            {/* O conteúdo da página vai aqui */}
            <div className='background-particles'>
                {<Particles 
                    quantity={50}
                    color="#3E7DFF"
                    speed={2.5}
                    lineDistance={200}
                />}
            </div>
        </div>
    );
};

export default MinhaPagina;
