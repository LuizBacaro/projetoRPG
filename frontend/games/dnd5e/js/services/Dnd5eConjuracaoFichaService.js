/**
 * API — conjuração na ficha (`/api/v1/dnd5e/personagens/{id}/conjuracao`).
 */
import { getApiUrl } from '/games/dnd35/js/config/api.config.js';

export class Dnd5eConjuracaoFichaService {
    constructor(token) {
        this.token = token || localStorage.getItem('token');
    }

    _headers() {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) headers.Authorization = `Bearer ${this.token}`;
        return headers;
    }

    async obter(personagemId) {
        const url = getApiUrl(`/dnd5e/personagens/${personagemId}/conjuracao`);
        const res = await fetch(url, { headers: this._headers() });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Erro ao carregar conjuração (${res.status})`);
        }
        return res.json();
    }

    async gastarSlot(personagemId, nivelMagia, quantidade = 1) {
        const url = getApiUrl(`/dnd5e/personagens/${personagemId}/conjuracao/gastar-slot`);
        const res = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify({ nivel_magia: nivelMagia, quantidade }),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Não foi possível gastar o espaço');
        }
        return res.json();
    }

    async descansoLongo(personagemId) {
        const url = getApiUrl(
            `/dnd5e/personagens/${personagemId}/conjuracao/descanso-longo`
        );
        const res = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Descanso longo falhou');
        }
        return res.json();
    }

    async preparar(personagemId, magiaIds) {
        const url = getApiUrl(
            `/dnd5e/personagens/${personagemId}/conjuracao/preparar`
        );
        const res = await fetch(url, {
            method: 'PUT',
            headers: this._headers(),
            body: JSON.stringify({ magia_ids: magiaIds }),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Não foi possível preparar magias');
        }
        return res.json();
    }

    async descansoCurto(personagemId) {
        const url = getApiUrl(
            `/dnd5e/personagens/${personagemId}/conjuracao/descanso-curto`
        );
        const res = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Descanso curto falhou');
        }
        return res.json();
    }
}
