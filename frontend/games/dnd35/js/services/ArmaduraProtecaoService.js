import { getApiUrl } from '../config/api.config.js';

export class ArmaduraProtecaoService {
    constructor() {
        this.token = localStorage.getItem('token');
        this.baseUrl = getApiUrl('/armaduras_protecao');
    }

    get token() {
        return localStorage.getItem('token');
    }

    set token(_value) {
        // Compatibilidade: evita token congelado no constructor legado.
    }

    _headers() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`,
        };
    }

    async listarItens(skip = 0, limit = 100) {
        const response = await fetch(`${this.baseUrl}?skip=${skip}&limit=${limit}`, {
            method: 'GET',
            headers: this._headers(),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}: Erro ao listar itens de proteção`);
        return response.json();
    }

    async criarItem(payload) {
        const response = await fetch(this.baseUrl, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}: Erro ao criar item de proteção`);
        return response.json();
    }

    async listarItensJogador(combatenteId) {
        const response = await fetch(`${this.baseUrl}/${combatenteId}/listar`, {
            method: 'GET',
            headers: this._headers(),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}: Erro ao listar itens do personagem`);
        return response.json();
    }

    async adicionarItem(combatenteId, itemId) {
        const response = await fetch(`${this.baseUrl}/${combatenteId}/adicionar`, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify({ item_id: itemId }),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}: Erro ao adicionar item de proteção`);
        return response.json();
    }

    async removerItem(combatenteId, itemId) {
        const response = await fetch(`${this.baseUrl}/${combatenteId}/remover/${itemId}`, {
            method: 'DELETE',
            headers: this._headers(),
        });
        if (!response.ok && response.status !== 204) {
            throw new Error(`HTTP ${response.status}: Erro ao remover item de proteção`);
        }
    }

    async obterBonusCaTotal(combatenteId) {
        const response = await fetch(`${this.baseUrl}/${combatenteId}/bonus-ca`, {
            method: 'GET',
            headers: this._headers(),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}: Erro ao calcular bônus de CA`);
        const data = await response.json();
        return Number(data?.bonus_ca_total || 0);
    }

    filtrarPorBusca(itens, termo) {
        if (!termo || !String(termo).trim()) return itens;
        const texto = String(termo).toLowerCase().trim();
        return (itens || []).filter((item) => {
            const alvo = [
                item.nome,
                item.tipo,
                item.propriedades_especiais,
            ].filter(Boolean).join(' ').toLowerCase();
            return alvo.includes(texto);
        });
    }
}
