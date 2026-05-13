/**
 * Regras estáticas da ficha Tormenta (`/api/v1/tormenta/regras/*`).
 */
class TormentaRegrasService {
    _urlAtributos() {
        return window.getApiUrl('/tormenta/regras/atributos');
    }

    _urlRacas() {
        return window.getApiUrl('/tormenta/regras/racas');
    }

    _headers() {
        const headers = {};
        const token = AuthService.getToken();
        if (token) headers.Authorization = `Bearer ${token}`;
        return headers;
    }

    async _handleJson(res, fallbackMessage) {
        if (res.status === 401) {
            if (typeof AuthService.logout === 'function') AuthService.logout();
            throw new Error('Sessão expirada. Faça login novamente.');
        }
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            const d = e.detail;
            const msg = typeof d === 'string' && d ? d : fallbackMessage;
            throw new Error(msg);
        }
        return res.json();
    }

    async obterAtributos() {
        const res = await fetch(this._urlAtributos(), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar regras Tormenta');
    }

    async obterRacas() {
        const res = await fetch(this._urlRacas(), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar raças Tormenta');
    }

    _urlClasses() {
        return window.getApiUrl('/tormenta/regras/classes');
    }

    async obterClasses() {
        const res = await fetch(this._urlClasses(), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar classes Tormenta');
    }

    _urlEquipamentos() {
        return window.getApiUrl('/tormenta/regras/equipamentos');
    }

    _urlTalentos() {
        return window.getApiUrl('/tormenta/regras/talentos');
    }

    /**
     * Catálogo MB de equipamento (paginação + busca).
     * @param {{ q?: string, skip?: number, limit?: number }} params
     */
    async listarEquipamentosCatalogo(params = {}) {
        const q = new URLSearchParams();
        if (params.q) q.set('q', params.q);
        if (params.skip != null) q.set('skip', String(params.skip));
        if (params.limit != null) q.set('limit', String(params.limit));
        const qs = q.toString();
        const res = await fetch(this._urlEquipamentos() + (qs ? `?${qs}` : ''), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar equipamentos MB');
    }

    async listarTalentosCatalogo(params = {}) {
        const q = new URLSearchParams();
        if (params.q) q.set('q', params.q);
        if (params.skip != null) q.set('skip', String(params.skip));
        if (params.limit != null) q.set('limit', String(params.limit));
        const qs = q.toString();
        const res = await fetch(this._urlTalentos() + (qs ? `?${qs}` : ''), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar talentos MB');
    }

    _urlArmadurasProtecao() {
        return window.getApiUrl('/tormenta/regras/armaduras-protecao');
    }

    /**
     * Catálogo de armaduras / proteção (paginação + busca).
     * @param {{ q?: string, skip?: number, limit?: number }} params
     */
    async listarArmadurasProtecaoCatalogo(params = {}) {
        const sp = new URLSearchParams();
        if (params.q) sp.set('q', params.q);
        if (params.skip != null) sp.set('skip', String(params.skip));
        if (params.limit != null) sp.set('limit', String(params.limit));
        const qs = sp.toString();
        const res = await fetch(this._urlArmadurasProtecao() + (qs ? `?${qs}` : ''), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar catálogo de armaduras');
    }
}
