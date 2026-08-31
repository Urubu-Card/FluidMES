import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../../services/api'
import './style.css';

function Home() {
    return (
        <div className='container'>
            <div className='header'>
                <div className='cimaSts'>
                <h1 className='title'>Pedidos:</h1>                
                <input type='text' placeholder='Pesquisar pedido' className='pesquisaPedidos' />
                </div>
                <div className='stsPedidos'>
                    <div className='totalPedidos'>
                        <div className="caixinha"><i className="bi bi-card-checklist"></i></div>
                        <div>
                            <h3>Total pedidos:</h3>
                            <p>numero legal em porcentagem</p>
                        </div>     
                    </div>
                    <div className='totalRealizados'>Pedidos realizados:</div>
                    <div className='totalCancelados'>Pedidos cancelados:</div>
                </div>
                <div className='filtroPedidos'>
                    <input type='radio' />
                    <h3>Ordem de id</h3><select name="ordem" id="ordem"></select>
                    <h3>Receita</h3>
                    <h3>Data</h3><select name="data" id="data"></select>
                    <h3>Quantidade</h3><select name="quantidade" id="quantiade"></select>
                    <h3>Status</h3><select name="status" id="status"></select>
                </div>
            </div>
            <div className='container-pedidos'>
                <div className='linha azul'>
                    wfefwfwfwef
                </div>
                <div className='linha escuro'>
                    wfefwfwfwef
                </div>
            </div>
        </div>
    )
}
export default Home