import React from 'react';
import './style.css';
import BotaoModal from "../../components/ButtonAdd/button";

const MinhaPagina = () => {
    return (
        <div>
            <BotaoModal target="modalAddPlanta" label="Adicionar planta" />
        </div>
    );
};

export default MinhaPagina;
