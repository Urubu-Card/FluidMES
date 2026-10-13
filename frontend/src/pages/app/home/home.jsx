import React from 'react';
import './style.css';
import TituloPagina from '../../components/Titulo/titulo';

/*----------Dados (troque pelos reais depois)----------*/

const METRICAS = [
    { id: 1, valor: '53,8%', label: 'OEE Geral', icon: 'bi-graph-up-arrow', variant: 'dark', iconClass: 'icon-glass' },
    { id: 2, valor: '5.358', label: 'Pedidos Totais', icon: 'bi-star', variant: 'light', iconClass: 'icon-success', trend: { tipo: 'up', valor: '4,2%' } },
    { id: 3, valor: '367L', label: 'Volume Produzido', icon: 'bi-droplet-half', variant: 'light', iconClass: 'icon-success', trend: { tipo: 'down', valor: '4,2%' } },
    { id: 4, valor: '45', label: 'Falhas de Conexão com a planta', icon: 'bi-wifi-off', variant: 'light', iconClass: 'icon-primary' },
];

const SERIE_BARRAS = [
    { id: 'x', label: 'Item X', value: 66.6     , color: 'var(--chart-red)' },
    { id: 'y', label: 'Item Y', value: 85, color: 'var(--chart-blue)' },
    { id: 'z', label: 'Item Z', value: 30, color: 'var(--chart-yellow)' },
    { id: 'h', label: 'Item H', value: 67, color: 'var(--chart-yellow)' },
    { id: 'h', label: 'Item H', value: 67, color: 'var(--chart-yellow)' },
    { id: 'h', label: 'Item H', value: 67, color: 'var(--chart-yellow)' },
    { id: 'h', label: 'Item H', value: 67, color: 'var(--chart-yellow)' },
    { id: 'h', label: 'Item H', value: 67, color: 'var(--chart-yellow)' },
    { id: 'h', label: 'Item H', value: 67, color: 'var(--chart-yellow)' },
    { id: 'h', label: 'Item H', value: 67, color: 'var(--chart-yellow)' },


];

/*----------Componentes----------*/

const SelectPeriodo = ({ children, ...props }) => (
    <div className='select-wrapper'>
        <select className='form-select form-select-sm custom-select' {...props}>
            {children}
        </select>
    </div>
);

const MetricCard = ({ valor, label, icon, variant = 'light', iconClass, trend }) => (
    <div className='col-12 col-md-6 col-lg-3'>
        <div className={`card metric-card metric-${variant} border-0`}>
            <div className={`metric-icon rounded-circle ${iconClass}`}>
                <i className={`bi ${icon}`}></i>
            </div>
            <div className='metric-value'>
                {valor}
                {trend && (
                    <span className={`metric-trend trend-${trend.tipo}`}>
                        <i className={`bi bi-caret-${trend.tipo}-fill`}></i>
                        <small>{trend.valor}</small>
                    </span>
                )}
            </div>
            <span className='metric-label'>{label}</span>
        </div>
    </div>
);

/*value: 0–100 sobre o trecho útil do arco (270°)*/
const GaugeCard = ({ titulo, rodape, value = 59 }) => {
    const R = 40;
    const C = 2 * Math.PI * R;          // circunferência ≈ 251.2
    const trilho = C * 0.75;            // 3/4 do círculo
    const progresso = trilho * (value / 100);

    return (
        <div className='col-12 col-md-6'>
            <div className='card card-gauge-container border-0 rounded-3 p-4 h-100'>
                <div className='gauge-title'>{titulo}</div>

                <div className='gauge-wrapper'>
                    <svg className='gauge-svg' viewBox='0 0 100 100'>
                        <circle cx='50' cy='50' r={R} className='gauge-track'
                            strokeDasharray={`${trilho} ${C}`} />
                        <circle cx='50' cy='50' r={R} className='gauge-progress'
                            strokeDasharray={`${progresso} ${C}`} />
                    </svg>
                    <div className='gauge-badge'>
                        <i className='bi bi-plus'></i>
                    </div>
                </div>

                <div className='gauge-footer'>{rodape}</div>
            </div>
        </div>
    );
};

const BarChartCard = ({ titulo, series }) => {
    const linhas = [0, 33.3, 66.6, 100];

    return (
        <div className='col-12 col-md-6'>
            <div className='card chart-card border-0 rounded-3 p-4 h-100'>
                <div>
                    <h5 className='chart-title'>{titulo}</h5>
                    <div className='chart-legend'>
                        {series.map(s => (
                            <div key={s.id} className='legend-item'>
                                <span className='legend-dot' style={{ backgroundColor: s.color }}></span>
                                <span>{s.value} {s.label}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className='chart-container'>
                    {linhas.map(top => (
                        <div key={top} className='chart-grid-line' style={{ top: `${top}%` }}></div>
                    ))}
                    {series.map(s => (
                        <div key={s.id} className='bar' style={{ height: `${s.value}%`, backgroundColor: s.color }}></div>
                    ))}
                </div>
            </div>
        </div>
    );
};

/*---------Página-------*/

const Home = () => {
    return (
        <div className='home-page app-page text-white'>

            <TituloPagina titulo='Visão Geral:'>
                <SelectPeriodo>
                    <option>Selecione o período</option>
                </SelectPeriodo>
            </TituloPagina>

            <div className='row g-3 mb-4'>
                {METRICAS.map(m => <MetricCard key={m.id} {...m} />)}
            </div>

            <div className='analise-de'>
                <span>Análise de</span>
                <SelectPeriodo>
                    <option>Eficiência</option>
                </SelectPeriodo>
            </div>

            <div className='row g-3'>
                <GaugeCard
                    titulo='Um aumento em potencial...'
                    rodape='Nota informativa de rodapé'
                    value={10}
                />
                <BarChartCard titulo='Grafico de Pedidos' series={SERIE_BARRAS} />
            </div>
        </div>
    );
};

export default Home;