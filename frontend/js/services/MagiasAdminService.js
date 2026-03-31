import { getApiUrl } from '../config/api.config.js';

function parseErrorPayload(payload, fallback) {
    if (!payload) return fallback;
    if (typeof payload.detail === 'string') return payload.detail;
    if (Array.isArray(payload.detail)) {
        const first = payload.detail[0];
        if (first && typeof first.msg === 'string') return first.msg;
    }
    return fallback;
}

export class MagiasAdminService {
    constructor() {
        this.limit = 20;
    }

    _authHeaders() {
        const authHeader = (window.AuthService && typeof window.AuthService.getAuthHeader === 'function')
            ? window.AuthService.getAuthHeader()
            : {};
        return { ...authHeader };
    }

    _headers() {
        return {
            'Content-Type': 'application/json',
            ...this._authHeaders(),
        };
    }

    _buildQuery(filters = {}) {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            if (value === undefined || value === null || value === '') return;
            params.append(key, String(value));
        });
        const qs = params.toString();
        return qs ? `?${qs}` : '';
    }

    async listar(filters = {}) {
        const query = this._buildQuery({
            limit: this.limit,
            ...filters,
        });
        const response = await fetch(getApiUrl(`/magias/${query}`), {
            headers: this._headers(),
        });

        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(payload, `Falha ao carregar magias (HTTP ${response.status})`));
        }

        const items = await response.json();
        const total = Number(response.headers.get('X-Total-Count') || items.length || 0);
        const skip = Number(response.headers.get('X-Skip') || filters.skip || 0);
        const limit = Number(response.headers.get('X-Limit') || filters.limit || this.limit);
        return { items, total, skip, limit };
    }

    async listarClasses() {
        const response = await fetch(getApiUrl('/magias/classes'), {
            headers: this._headers(),
        });

        if (!response.ok) {
            throw new Error(`Falha ao carregar classes de magias (HTTP ${response.status})`);
        }

        return response.json();
    }

    async listarDominios() {
        const response = await fetch(getApiUrl('/magias/dominios'), {
            headers: this._headers(),
        });

        if (!response.ok) {
            throw new Error(`Falha ao carregar dominios de magias (HTTP ${response.status})`);
        }

        return response.json();
    }

    async obter(magiaId) {
        const response = await fetch(getApiUrl(`/magias/${magiaId}`), {
            headers: this._headers(),
        });

        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(payload, `Falha ao carregar magia (HTTP ${response.status})`));
        }

        return response.json();
    }

    async criar(payload) {
        const response = await fetch(getApiUrl('/magias/'), {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const body = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(body, `Falha ao criar magia (HTTP ${response.status})`));
        }

        return response.json();
    }

    async atualizar(magiaId, payload) {
        const response = await fetch(getApiUrl(`/magias/${magiaId}`), {
            method: 'PUT',
            headers: this._headers(),
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const body = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(body, `Falha ao atualizar magia (HTTP ${response.status})`));
        }

        return response.json();
    }

    async desativar(magiaId) {
        const response = await fetch(getApiUrl(`/magias/${magiaId}/desativar`), {
            method: 'PATCH',
            headers: this._headers(),
        });

        if (!response.ok) {
            const body = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(body, `Falha ao desativar magia (HTTP ${response.status})`));
        }

        return response.json();
    }

    async reativar(magiaId) {
        const response = await fetch(getApiUrl(`/magias/${magiaId}/reativar`), {
            method: 'PATCH',
            headers: this._headers(),
        });

        if (!response.ok) {
            const body = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(body, `Falha ao reativar magia (HTTP ${response.status})`));
        }

        return response.json();
    }

    async excluir(magiaId) {
        const response = await fetch(getApiUrl(`/magias/${magiaId}`), {
            method: 'DELETE',
            headers: this._headers(),
        });

        if (!response.ok) {
            const body = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(body, `Falha ao excluir magia (HTTP ${response.status})`));
        }
    }

    async baixarModeloImportacao() {
        const response = await fetch(getApiUrl('/magias/importacao/modelo'), {
            headers: this._authHeaders(),
        });

        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(payload, `Falha ao baixar modelo (HTTP ${response.status})`));
        }

        return response.blob();
    }

    async previewImportacao(file) {
        const formData = new FormData();
        formData.append('arquivo', file);

        const response = await fetch(getApiUrl('/magias/importacao/preview'), {
            method: 'POST',
            headers: this._authHeaders(),
            body: formData,
        });

        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(payload, `Falha no preview da importacao (HTTP ${response.status})`));
        }

        return response.json();
    }

    async confirmarImportacao(importId) {
        const response = await fetch(getApiUrl('/magias/importacao/confirmar'), {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify({ import_id: importId }),
        });

        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(payload, `Falha ao confirmar importacao (HTTP ${response.status})`));
        }

        return response.json();
    }

    async listarHistorico(magiaId, limit = 50) {
        const response = await fetch(getApiUrl(`/magias/${magiaId}/historico?limit=${Number(limit) || 50}`), {
            headers: this._headers(),
        });

        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(parseErrorPayload(payload, `Falha ao carregar historico (HTTP ${response.status})`));
        }

        return response.json();
    }
}
