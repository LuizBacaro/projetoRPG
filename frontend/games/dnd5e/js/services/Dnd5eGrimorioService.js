/**
 * Grimório D&D 5e — API `/api/v1/dnd5e/grimorio/{personagemId}`.
 * Contrato compatível com GrimorioService (dnd35).
 */
import { getApiUrl } from '/games/dnd35/js/config/api.config.js';

export class Dnd5eGrimorioService {
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

    async listar(personagemId, opts = {}) {
        const {
            classe,
            favorita,
            nome,
            nivel,
            escola,
            componentes,
            magia_ids,
            skip,
            limit,
        } = opts;
        const skipSeguro = Number.isFinite(Number(skip))
            ? Math.max(0, Math.trunc(Number(skip)))
            : undefined;
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
        const url = getApiUrl(`/dnd5e/grimorio/${personagemId}${query}`);
        const response = await fetch(url, { headers: this._headers() });
        if (!response.ok) {
            throw new Error(`Falha ao carregar grimório (HTTP ${response.status})`);
        }
        const items = await response.json();
        const totalHeader = Number(response.headers.get('X-Total-Count'));
        return {
            items: Array.isArray(items) ? items : [],
            total: Number.isFinite(totalHeader)
                ? totalHeader
                : Array.isArray(items)
                  ? items.length
                  : 0,
            skip: Number(skipSeguro || 0),
            limit: Number(
                limitSeguro || (Array.isArray(items) ? items.length : 0)
            ),
        };
    }

    async adicionar(personagemId, payload) {
        const url = getApiUrl(`/dnd5e/grimorio/${personagemId}`);
        const response = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Erro ao adicionar magia (${response.status})`);
        }
        return response.json();
    }

    async atualizar(personagemId, magiaId, classe, payload) {
        const query = this._query({ classe });
        const url = getApiUrl(`/dnd5e/grimorio/${personagemId}/${magiaId}${query}`);
        const response = await fetch(url, {
            method: 'PATCH',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Erro ao atualizar magia (${response.status})`);
        }
        return response.json();
    }

    async remover(personagemId, magiaId, classe) {
        const query = this._query({ classe });
        const url = getApiUrl(`/dnd5e/grimorio/${personagemId}/${magiaId}${query}`);
        const response = await fetch(url, {
            method: 'DELETE',
            headers: this._headers(),
        });
        if (!response.ok && response.status !== 204) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Erro ao remover magia (${response.status})`);
        }
    }

    async trocar(personagemId, payload) {
        const url = getApiUrl(`/dnd5e/grimorio/${personagemId}/troca`);
        const response = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Erro ao trocar magia (${response.status})`);
        }
        return response.json();
    }

    async listarHistoricoTroca(personagemId, { classe, limit = 20 } = {}) {
        const query = this._query({ classe, limit });
        const url = getApiUrl(`/dnd5e/grimorio/${personagemId}/historico${query}`);
        const response = await fetch(url, { headers: this._headers() });
        if (!response.ok) {
            throw new Error(`Falha ao carregar histórico de trocas (HTTP ${response.status})`);
        }
        return response.json();
    }

    async listarNotificacoes(
        personagemId,
        { classe, apenasNaoLidas = false, limit = 30, forceSync = true } = {}
    ) {
        const query = this._query({
            classe,
            apenas_nao_lidas: apenasNaoLidas,
            limit,
            force_sync: forceSync,
        });
        const url = getApiUrl(`/dnd5e/grimorio/${personagemId}/notificacoes${query}`);
        const response = await fetch(url, { headers: this._headers() });
        if (!response.ok) {
            throw new Error(`Falha ao carregar notificações (HTTP ${response.status})`);
        }
        return response.json();
    }

    async marcarNotificacaoLida(personagemId, notificacaoId, lida = true) {
        const url = getApiUrl(
            `/dnd5e/grimorio/${personagemId}/notificacoes/${notificacaoId}`
        );
        const response = await fetch(url, {
            method: 'PATCH',
            headers: this._headers(),
            body: JSON.stringify({ lida: !!lida }),
        });
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Erro ao atualizar notificação (${response.status})`);
        }
        return response.json();
    }

    async descartarNotificacao(personagemId, notificacaoId) {
        const url = getApiUrl(
            `/dnd5e/grimorio/${personagemId}/notificacoes/${notificacaoId}`
        );
        const response = await fetch(url, {
            method: 'DELETE',
            headers: this._headers(),
        });
        if (!response.ok && response.status !== 204) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Erro ao descartar notificação (${response.status})`);
        }
    }
}
