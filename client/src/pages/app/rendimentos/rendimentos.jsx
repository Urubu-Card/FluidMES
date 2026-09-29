import React from 'react';
import './style.css';
import TituloPagina from '../../components/Titulo/titulo';

const MinhaPagina = () => {
    return (
        <div className='app-page'>
            <TituloPagina titulo="Rendimentos:" />
            {/* O conteúdo da página vai aqui */}
        </div>
    );
};

export default MinhaPagina;
