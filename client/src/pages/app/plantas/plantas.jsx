import { useEffect, useMemo, useState } from 'react';
import api from '../../../services/api';
import './style.css';
import BotaoModal from "../../components/ButtonAdd/button";

const STATUS_CONFIG = {
    produzindo: { label: 'Produzindo', className: 'produzindo' },
    parada: { label: 'Risco de parada', className: 'parada' },
    manutencao: { label: 'Manutenção mecânica', className: 'manutencao' },
    manutencao_mecanica: { label: 'Manutenção mecânica', className: 'manutencao' },
};

function normalizarStatus(status) {
    return String(status || 'produzindo').toLowerCase().normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '_');
}

function formatarQuantidade(valor) {
    const numero = Number(valor);
    return Number.isFinite(numero)
        ? `${numero.toLocaleString('pt-BR', { maximumFractionDigits: 2 })} L`
        : '—';
}

export default function Plantas() {
    const [plantas, setPlantas] = useState([]);
    const [busca, setBusca] = useState('');
    const [ordenacao, setOrdenacao] = useState('numero');
    const [carregando, setCarregando] = useState(true);
    const [erro, setErro] = useState('');

    useEffect(() => {
        async function buscarPlantas() {
            try {
                setCarregando(true);
                const response = await api.get('/api/plantas/');
                setPlantas(Array.isArray(response.data) ? response.data : response.data.results || []);
            } catch (error) {
                console.error(error);
                setErro('Erro ao carregar plantas.');
            } finally {
                setCarregando(false);
            }
        }
        buscarPlantas();
    }, []);

    const plantasFiltradas = useMemo(() => {
        const texto = busca.trim().toLowerCase();
        return plantas.filter((planta) => {
            const numero = planta.numero ?? planta.numero_planta ?? planta.id;
            return !texto || [numero, planta.nome, planta.produto, planta.receita, planta.status]
                .some((valor) => String(valor || '').toLowerCase().includes(texto));
        }).sort((a, b) => ordenacao === 'status'
            ? String(a.status || '').localeCompare(String(b.status || ''))
            : Number(a.numero ?? a.numero_planta ?? a.id) - Number(b.numero ?? b.numero_planta ?? b.id));
    }, [busca, ordenacao, plantas]);

    const quantidadePlanejada = plantas.reduce((total, planta) => total + Number(planta.quantidade_planejada ?? planta.quantidadePlanejada ?? 0), 0);
    const quantidadeProduzida = plantas.reduce((total, planta) => total + Number(planta.quantidade_produzida ?? planta.quantidadeProduzida ?? 0), 0);
    const percentualGeral = quantidadePlanejada ? Math.min(quantidadeProduzida / quantidadePlanejada * 100, 100) : 0;

    return (
        <div className="plantas-page">
            <header className="plantas-header">
                <h1>Plantas:</h1>
                <div className=" col-md-4">
                    <form className="input-group app-search-group" onSubmit={(event) => event.preventDefault()}>
                        <select className="form-select" value={ordenacao} onChange={(event) => setOrdenacao(event.target.value)} aria-label="Ordenar plantas">
                            <option value="numero">Núm. planta</option><option value="status">Status</option>
                        </select>
                        <input className="form-control" type="search" placeholder="Buscar planta" value={busca} onChange={(event) => setBusca(event.target.value)} />
                        <button className="btn btn-primary" type="submit"><i className="bi bi-search me-2" aria-hidden="true" />Buscar</button>
                    </form>
                </div>
            </header>

            {carregando && <p className="plantas-message">Carregando plantas...</p>}
            {!carregando && erro && <p className="plantas-message error">{erro}</p>}
            {!carregando && !erro && <section className="plantas-grid" aria-label="Lista de plantas">
                {plantas.length > 2 && <article className="factory-summary">
                    <h2>Geral da Fábrica</h2><p>Qtd. Produzida / Qtd. Planejada</p><strong>{formatarQuantidade(quantidadeProduzida)} / {formatarQuantidade(quantidadePlanejada)}</strong>
                    <div className="factory-summary-content"><Progress value={percentualGeral} /><div className="factory-summary-metrics"><span>Disponibilidade</span><div><i style={{ width: `${percentualGeral}%` }} /></div><span>Performance</span><div><i style={{ width: `${percentualGeral}%` }} /></div></div></div>
                </article>}
                {plantasFiltradas.map((planta) => <PlantCard key={planta.id ?? planta.numero ?? planta.numero_planta} planta={planta} />)}
            </section>}
            {!carregando && !erro && plantasFiltradas.length === 0 && <p className="plantas-message">Nenhuma planta encontrada.</p>}
            <BotaoModal target="modalAddPlanta" label="Adicionar planta" />


            <div class="modal fade" id="modalAddPlanta" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="staticBackdropLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h1 class="modal-title fs-5" id="staticBackdropLabel">Adicionar planta:</h1>
                            <button type="button" class="btn-close text-light" data-bs-theme="dark" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            ...
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="button" class="btn btn-primary">Criar</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Progress({ value }) {
    return <div className="plant-progress" style={{ '--progress': `${value}%` }}><span>{value.toFixed(1).replace('.', ',')}%</span><small>OEE</small></div>;
}

function PlantCard({ planta }) {
    const status = STATUS_CONFIG[normalizarStatus(planta.status)] || STATUS_CONFIG.produzindo;
    const numero = planta.numero ?? planta.numero_planta ?? planta.id;
    const planejada = Number(planta.quantidade_planejada ?? planta.quantidadePlanejada ?? 0);
    const produzida = Number(planta.quantidade_produzida ?? planta.quantidadeProduzida ?? 0);
    const oee = planejada ? Math.min(produzida / planejada * 100, 100) : Number(planta.oee ?? 0);
    return <article className="plant-card">
        <header className={`plant-card-status ${status.className}`}><strong>Planta #{numero}</strong><span>{status.label}</span><span>{planta.tipo ?? planta.categoria ?? 'Refrigerante'}</span></header>
        <div className="plant-card-body"><p><i className="bi bi-box-seam" /> {planta.produto ?? planta.receita ?? 'Não informado'}</p><p><i className="bi bi-key" /> Código de rastreio: <em>{planta.codigo_rastreio ?? planta.codigoRastreio ?? '—'}</em></p><div className="plant-quantity"><span>{formatarQuantidade(produzida)} / {formatarQuantidade(planejada)}</span><i><b style={{ width: `${oee}%` }} /></i></div><div className="plant-card-footer"><Progress value={oee} /><p><strong>Qtd. Produzida</strong>{formatarQuantidade(produzida)}</p></div></div>
    </article>;
}
