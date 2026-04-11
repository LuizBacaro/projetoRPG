import { getApiUrl } from '../config/api.config.js';

export class GrimorioService {
    constructor(token) {
        this.token = token || localStorage.getItem('token');
    }

    _headers() {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) headers.Authorization = `Bearer ${this.token}`;
        return headers;
    }

    _query(params = {}) {
        const query = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value === undefined || value === null || value === '') return;
            query.append(key, String(value));
        });
        const encoded = query.toString();
        return encoded ? `?${encoded}` : '';
    }

    _clampLimit(limit) {
        const limitNumerico = Number(limit);
        if (!Number.isFinite(limitNumerico)) return undefined;
        return Math.min(200, Math.max(1, Math.trunc(limitNumerico)));
    }

    async listar(combatenteId, {
        classe,
        favorita,
        nome,
        nivel,
        escola,
        componentes,
        magia_ids,
        skip,
        limit,
    } = {}) {
        const skipSeguro = Number.isFinite(Number(skip)) ? Math.max(0, Math.trunc(Number(skip))) : undefined;
        const limitSeguro = this._clampLimit(limit);

        const query = this._query({
            classe,
            favorita,
            nome,
            nivel,
            escola,
            componentes,
            magia_ids,
            skip: skipSeguro,
            limit: limitSeguro,
        });
        const url = getApiUrl(`/grimorio/${combatenteId}${query}`);
        const response = await fetch(url, { headers: this._headers() });
        if (!response.ok) {
            throw new Error(`Falha ao carregar grimorio (HTTP ${response.status})`);
        }

        const items = await response.json();
        const totalHeader = Number(response.headers.get('X-Total-Count'));
        const skipHeader = Number(response.headers.get('X-Skip'));
        const limitHeader = Number(response.headers.get('X-Limit'));

        return {
            items: Array.isArray(items) ? items : [],
            total: Number.isFinite(totalHeader) ? totalHeader : (Array.isArray(items) ? items.length : 0),
            skip: Number.isFinite(skipHeader) ? skipHeader : Number(skipSeguro || 0),
            limit: Number.isFinite(limitHeader)
                ? limitHeader
                : Number(limitSeguro || (Array.isArray(items) ? items.length : 0)),
        };
    }

    async adicionar(combatenteId, payload) {
        const url = getApiUrl(`/grimorio/${combatenteId}`);
        const response = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || `Falha ao adicionar magia (HTTP ${response.status})`);
        }
        return response.json();
    }

    async atualizar(combatenteId, magiaId, classe, payload) {
        const query = this._query({ classe });
        const url = getApiUrl(`/grimorio/${combatenteId}/${magiaId}${query}`);
        const response = await fetch(url, {
            method: 'PATCH',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || `Falha ao atualizar item do grimorio (HTTP ${response.status})`);
        }
        return response.json();
    }

    async remover(combatenteId, magiaId, classe) {
        const query = this._query({ classe });
        const url = getApiUrl(`/grimorio/${combatenteId}/${magiaId}${query}`);
        const response = await fetch(url, {
            method: 'DELETE',
            headers: this._headers(),
        });
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || `Falha ao remover magia do grimorio (HTTP ${response.status})`);
        }
    }

    async trocar(combatenteId, payload) {
        const url = getApiUrl(`/grimorio/${combatenteId}/troca`);
        const response = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || `Falha ao trocar magia (HTTP ${response.status})`);
        }
        return response.json();
    }

    async listarHistoricoTroca(combatenteId, { classe, limit = 20 } = {}) {
        const query = this._query({ classe, limit });
        const url = getApiUrl(`/grimorio/${combatenteId}/historico${query}`);
        const response = await fetch(url, { headers: this._headers() });
        if (!response.ok) {
            throw new Error(`Falha ao carregar historico de trocas (HTTP ${response.status})`);
        }
        return response.json();
    }

    async listarNotificacoes(combatenteId, { classe, apenasNaoLidas = false, limit = 30, forceSync = false } = {}) {
        const query = this._query({ classe, apenas_nao_lidas: apenasNaoLidas, limit, force_sync: forceSync || undefined });
        const url = getApiUrl(`/grimorio/${combatenteId}/notificacoes${query}`);
        const response = await fetch(url, { headers: this._headers() });
        if (!response.ok) {
            throw new Error(`Falha ao carregar notificacoes do grimorio (HTTP ${response.status})`);
        }
        return response.json();
    }

    async marcarNotificacaoLida(combatenteId, notificacaoId, lida = true) {
        const url = getApiUrl(`/grimorio/${combatenteId}/notificacoes/${notificacaoId}`);
        const response = await fetch(url, {
            method: 'PATCH',
            headers: this._headers(),
            body: JSON.stringify({ lida: !!lida }),
        });
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || `Falha ao atualizar notificacao (HTTP ${response.status})`);
        }
        return response.json();
    }

    async descartarNotificacao(combatenteId, notificacaoId) {
        const url = getApiUrl(`/grimorio/${combatenteId}/notificacoes/${notificacaoId}`);
        const response = await fetch(url, {
            method: 'DELETE',
            headers: this._headers(),
        });
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            throw new Error(data.detail || `Falha ao descartar notificacao (HTTP ${response.status})`);
        }
    }
}
