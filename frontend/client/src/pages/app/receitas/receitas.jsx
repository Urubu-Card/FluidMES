import React from 'react';
import './style.css';
import TituloPagina from '../../components/Titulo/titulo';
import BotaoModal from "../../components/ButtonAdd/button";

const MinhaPagina = () => {
    return (
        <div className='app-page'>
            <TituloPagina titulo="Receitas:" />
            <BotaoModal target="modalAddPlanta" label="Adicionar planta" />
        </div>
    );
};

export default MinhaPagina;
