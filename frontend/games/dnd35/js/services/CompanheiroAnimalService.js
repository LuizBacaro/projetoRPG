import { getApiUrl } from '../config/api.config.js';

export class CompanheiroAnimalService {
    constructor() {
        this.baseUrl = getApiUrl('/companheiros-animais');
    }

    get token() {
        return localStorage.getItem('token');
    }

    _headers() {
        return {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.token}`,
        };
    }

    _formatarErro(body, fallback) {
        const detail = body?.detail;
        if (typeof detail === 'string' && detail.trim()) return detail;
        if (Array.isArray(detail)) {
            return detail
                .map((d) => d?.msg || d?.message || JSON.stringify(d))
                .filter(Boolean)
                .join('; ');
        }
        return fallback;
    }

    async listarEspecies() {
        const res = await fetch(`${this.baseUrl}/especies`, {
            method: 'GET',
            headers: this._headers(),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }

    async elegibilidade(combatenteId) {
        const res = await fetch(`${this.baseUrl}/${combatenteId}/elegibilidade`, {
            method: 'GET',
            headers: this._headers(),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }

    async obter(combatenteId) {
        const res = await fetch(`${this.baseUrl}/${combatenteId}`, {
            method: 'GET',
            headers: this._headers(),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        return data || null;
    }

    async calcular(combatenteId, payload) {
        const res = await fetch(`${this.baseUrl}/${combatenteId}/calcular`, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(this._formatarErro(err, `HTTP ${res.status}`));
        }
        return res.json();
    }

    async salvar(combatenteId, payload) {
        const res = await fetch(`${this.baseUrl}/${combatenteId}`, {
            method: 'PUT',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(this._formatarErro(err, `HTTP ${res.status}`));
        }
        return res.json();
    }

    async criarRapido(combatenteId, payload) {
        const res = await fetch(`${this.baseUrl}/${combatenteId}/criar-rapido`, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(this._formatarErro(err, `HTTP ${res.status}`));
        }
        return res.json();
    }

    async remover(combatenteId) {
        const res = await fetch(`${this.baseUrl}/${combatenteId}`, {
            method: 'DELETE',
            headers: this._headers(),
        });
        if (!res.ok && res.status !== 204) throw new Error(`HTTP ${res.status}`);
        return null;
    }
}
