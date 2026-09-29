import React from 'react';
import './style.css';
import TituloPagina from '../../components/Titulo/titulo';

const Home = () => {
    return (
        <div className='home-page app-page text-white'>

            <TituloPagina titulo="Visão Geral:">
                <div style={{ width: '180px' }}>
                    <select className='form-select form-select-sm custom-select'>
                        <option>Selecione o período</option>
                    </select>
                </div>
            </TituloPagina>

            <div className='row g-3 mb-4'>

                {/* Card 1 (Azul Escuro) */}
                <div className='col-12 col-md-6 col-lg-3'>
                    <div className='card card-dark-blue border-0 h-100 rounded-3 p-4 d-flex flex-column align-items-center justify-content-center text-center'>
                        <div className='rounded-circle d-flex align-items-center justify-content-center mb-2 card-icon-bg'>
                            <i className='bi bi-graph-up-arrow'></i>
                        </div>
                        <small className='text-white-50 text-uppercase tracking-wider fs-7'>Métrica 1</small>
                    </div>
                </div>

                {/* Card 2 (Claro) */}
                <div className='col-12 col-md-6 col-lg-3'>
                    <div className='card card-light-gray border-0 h-100 rounded-3 p-4 d-flex flex-column align-items-center justify-content-center text-center shadow-sm'>
                        <div className='rounded-circle d-flex align-items-center justify-content-center mb-2 bg-success text-white' style={{ width: '42px', height: '42px' }}>
                            <i className='bi bi-star-fill fs-5'></i>
                        </div>
                        <small className='text-muted text-uppercase tracking-wider fs-7'>Métrica 2</small>
                    </div>
                </div>

                {/* Card 3 (Claro) */}
                <div className='col-12 col-md-6 col-lg-3'>
                    <div className='card card-light-gray border-0 h-100 rounded-3 p-4 d-flex flex-column align-items-center justify-content-center text-center shadow-sm'>
                        <div className='rounded-circle d-flex align-items-center justify-content-center mb-2 bg-success text-white' style={{ width: '42px', height: '42px' }}>
                            <i className='bi bi-droplet-fill fs-5'></i>
                        </div>

                        <small className='text-muted text-uppercase tracking-wider fs-7'>Métrica 3</small>
                    </div>
                </div>

                {/* Card 4 (Claro) */}
                <div className='col-12 col-md-6 col-lg-3'>
                    <div className='card card-light-gray border-0 h-100 rounded-3 p-4 d-flex flex-column align-items-center justify-content-center text-center shadow-sm'>
                        <div className='rounded-circle d-flex align-items-center justify-content-center mb-2 bg-primary text-white' style={{ width: '42px', height: '42px' }}>
                            <i className='bi bi-exclamation-triangle-fill fs-5'></i>
                        </div>

                        <small className='text-muted text-uppercase tracking-wider fs-7'>Métrica 4</small>
                    </div>
                </div>

            </div>

            {/* Seção de Análise Inferior */}
            <div className='mb-3'>
                <div className='d-inline-flex align-items-center text-secondary small cursor-pointer hover-white'>
                    <span className='me-1'>Análise de </span>
                    <div style={{ width: '180px' }}>
                        <select className='form-select form-select-sm custom-select'>
                            <option>Eficiência</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Grid dos Gráficos */}
            <div className='row g-3'>

                {/* Bloco Esquerdo: Gráfico Circular */}
                <div className='col-12 col-md-6'>
                    <div className='card card-gauge-container border-0 rounded-3 p-4 h-100 d-flex flex-column justify-content-between align-items-center text-center' style={{ minHeight: '340px' }}>
                        <div className='w-100 text-start opacity-75 fst-italic small' style={{ color: 'var(--branco-azulado)' }}>
                            Um aumento em potencial...
                        </div>

                        {/* SVG do Arco de Progresso */}
                        <div className='position-relative d-flex align-items-center justify-content-center my-3' style={{ width: '180px', height: '180px' }}>
                            <svg className='gauge-svg w-100 h-100' viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="40" stroke="#334155" strokeWidth="7" fill="transparent" strokeDasharray="251.2" strokeDashoffset="62.8" strokeLinecap="round" />
                                <circle cx="50" cy="50" r="40" stroke="#10b981" strokeWidth="7" fill="transparent" strokeDasharray="251.2" strokeDashoffset="140" strokeLinecap="round" />
                            </svg>
                            <div className='position-absolute d-flex flex-column align-items-center'>
                                <div className='bg-success rounded-circle d-flex align-items-center justify-content-center shadow mb-1' style={{ width: '32px', height: '32px' }}>
                                    <i className='bi bi-plus text-white'></i>
                                </div>
                            </div>
                        </div>

                        <div className='w-100 text-center text-white-50 small'>
                            Nota informativa de rodapé
                        </div>
                    </div>
                </div>

                {/* Bloco Direito: Gráfico de Barras */}
                <div className='col-12 col-md-6'>
                    <div className='card bg-white border-0 text-dark rounded-3 p-4 h-100 d-flex flex-column justify-content-between' style={{ minHeight: '340px' }}>
                        <div>
                            <h5 className='fw-bold text-secondary mb-3'>Título do Gráfico</h5>
                            <div className='d-flex gap-4 small fw-medium text-muted'>
                                <div className='d-flex align-items-center gap-1'>
                                    <span className='d-inline-block bg-danger rounded-1' style={{ width: '12px', height: '12px', color: 'var(--azul-ceu)' }}></span>
                                    <span>Item X</span>
                                </div>
                                <div className='d-flex align-items-center gap-1'>
                                    <span className='d-inline-block bg-primary rounded-1' style={{ width: '12px', height: '12px' }}></span>
                                    <span>Item Y</span>
                                </div>
                                <div className='d-flex align-items-center gap-1'>
                                    <span className='d-inline-block bg-warning rounded-1' style={{ width: '12px', height: '12px' }}></span>
                                    <span>Item Z</span>
                                </div>
                            </div>
                        </div>

                        {/* Container das Linhas e Barras */}
                        <div className='chart-container d-flex align-items-end justify-content-around px-2 mt-4'>
                            <div className='chart-grid-line' style={{ top: '0%' }}></div>
                            <div className='chart-grid-line' style={{ top: '33.3%' }}></div>
                            <div className='chart-grid-line' style={{ top: '66.6%' }}></div>
                            <div className='chart-grid-line' style={{ top: '100%' }}></div>

                            <div className='bar bg-danger' style={{ height: '50%' }}></div>
                            <div className='bar bg-primary' style={{ height: '85%' }}></div>
                            <div className='bar bg-warning' style={{ height: '30%' }}></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;