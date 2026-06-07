/**
 * API — conjuração na ficha (`/api/v1/dnd5e/personagens/{id}/conjuracao`).
 */
import { getApiUrl } from '/games/dnd35/js/config/api.config.js';

function _detailFromApiError(err) {
    const d = err?.detail;
    if (typeof d === 'string' && d.trim()) return d.trim();
    if (Array.isArray(d)) {
        return d
            .map((item) => {
                if (typeof item === 'string') return item;
                if (item && typeof item.msg === 'string') return item.msg;
                return '';
            })
            .filter(Boolean)
            .join('; ');
    }
    return '';
}

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
            throw new Error(
                _detailFromApiError(err) || `Erro ao carregar conjuração (${res.status})`
            );
        }
        return res.json();
    }

    async gastarSlot(personagemId, nivelMagia, quantidade = 1, magiaId = null) {
        const url = getApiUrl(`/dnd5e/personagens/${personagemId}/conjuracao/gastar-slot`);
        const body = { nivel_magia: nivelMagia, quantidade };
        if (magiaId != null) body.magia_id = Number(magiaId);
        const res = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Não foi possível gastar o espaço');
        }
        return res.json();
    }

    async devolverSlot(personagemId, nivelMagia, quantidade = 1, magiaId = null) {
        const url = getApiUrl(
            `/dnd5e/personagens/${personagemId}/conjuracao/devolver-slot`
        );
        const body = { nivel_magia: nivelMagia, quantidade };
        if (magiaId != null) body.magia_id = Number(magiaId);
        const res = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Não foi possível devolver o espaço');
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

    async preparar(personagemId, magiaIds, magiasQuantidade = null) {
        const url = getApiUrl(
            `/dnd5e/personagens/${personagemId}/conjuracao/preparar`
        );
        const body = { magia_ids: magiaIds };
        if (magiasQuantidade && typeof magiasQuantidade === 'object') {
            body.magias_quantidade = magiasQuantidade;
        }
        const res = await fetch(url, {
            method: 'PUT',
            headers: this._headers(),
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(
                _detailFromApiError(err) || 'Não foi possível preparar magias'
            );
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
            throw new Error(_detailFromApiError(err) || 'Descanso curto falhou');
        }
        return res.json();
    }

    async criarSlotPontosFeiticaria(personagemId, nivelSlot) {
        const url = getApiUrl(
            `/dnd5e/personagens/${personagemId}/conjuracao/pontos-feiticaria/criar-slot`
        );
        const res = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify({ nivel_slot: nivelSlot }),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(_detailFromApiError(err) || 'Falha ao criar slot');
        }
        return res.json();
    }

    async converterSlotPontosFeiticaria(personagemId, nivelSlot) {
        const url = getApiUrl(
            `/dnd5e/personagens/${personagemId}/conjuracao/pontos-feiticaria/converter`
        );
        const res = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify({ nivel_slot: nivelSlot }),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(_detailFromApiError(err) || 'Falha ao converter slot');
        }
        return res.json();
    }

    async definirConcentracao(personagemId, magiaId = null) {
        const url = getApiUrl(
            `/dnd5e/personagens/${personagemId}/conjuracao/concentracao`
        );
        const body = { magia_id: magiaId != null ? Number(magiaId) : null };
        const res = await fetch(url, {
            method: 'PUT',
            headers: this._headers(),
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(_detailFromApiError(err) || 'Falha ao salvar concentração');
        }
        return res.json();
    }

    async recuperacaoArcana(personagemId, slots) {
        const url = getApiUrl(
            `/dnd5e/personagens/${personagemId}/conjuracao/recuperacao-arcana`
        );
        const res = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify({ slots }),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(_detailFromApiError(err) || 'Recuperação arcana falhou');
        }
        return res.json();
    }
}
