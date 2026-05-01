import { getApiUrl } from '../config/api.config.js';

export class ConsumivelService {
    constructor() {
        this.baseUrl = getApiUrl('/consumiveis');
    }

    get token() {
        return localStorage.getItem('token');
    }

    _headers() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`,
        };
    }

    async listarConsumiveis({
        skip = 0,
        limit = 100,
        filtroTipo = 'todos',
        busca = '',
    } = {}) {
        const params = new URLSearchParams();
        params.set('skip', String(skip));
        params.set('limit', String(limit));

        const filtro = String(filtroTipo || 'todos').toLowerCase();
        if (filtro === 'poção' || filtro === 'óleo') {
            params.set('tipo', filtro);
        } else if (filtro === 'pergaminho') {
            params.set('categoria', 'Pergaminho');
        }

        const termoBusca = String(busca || '').trim();
        if (termoBusca) {
            params.set('busca', termoBusca);
        }

        const res = await fetch(`${this.baseUrl}?${params.toString()}`, {
            method: 'GET',
            headers: this._headers(),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }

    async listarConsumiveisJogador(combatenteId) {
        const res = await fetch(`${this.baseUrl}/${combatenteId}/listar`, {
            method: 'GET',
            headers: this._headers(),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }

    async adicionarConsumivel(combatenteId, payload) {
        const res = await fetch(`${this.baseUrl}/${combatenteId}/adicionar`, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }

    async removerConsumivel(combatenteId, consumivelId) {
        const res = await fetch(
            `${this.baseUrl}/${combatenteId}/remover/${consumivelId}`,
            { method: 'DELETE', headers: this._headers() }
        );
        if (!res.ok && res.status !== 204) throw new Error(`HTTP ${res.status}`);
        return null;
    }

    async criarConsumivel(payload) {
        const res = await fetch(this.baseUrl, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }

    filtrarPorBusca(itens, termo) {
        if (!termo?.trim()) return itens;
        const t = termo.toLowerCase();
        return itens.filter((i) =>
            [i.nome, i.descricao, i.categoria, i.tipo, i.custo, i.pagina_referencia]
                .filter(Boolean)
                .join(' ')
                .toLowerCase()
                .includes(t)
        );
    }
}
