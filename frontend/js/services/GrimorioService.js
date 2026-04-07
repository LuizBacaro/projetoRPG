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

    async listar(combatenteId, { classe, favorita } = {}) {
        const query = this._query({ classe, favorita });
        const url = getApiUrl(`/grimorio/${combatenteId}${query}`);
        const response = await fetch(url, { headers: this._headers() });
        if (!response.ok) {
            throw new Error(`Falha ao carregar grimorio (HTTP ${response.status})`);
        }
        return response.json();
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
