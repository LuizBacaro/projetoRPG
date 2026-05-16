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

    _urlIdentidadeMb() {
        return window.getApiUrl('/tormenta/regras/identidade-mb');
    }

    /** PM por classe, chave de conjuração e custo em PM por círculo (MB). */
    _urlConjuracaoMb() {
        return window.getApiUrl('/tormenta/regras/conjuracao-mb');
    }

    /** Tendências (alinhamento) e divindades (Os Vinte) do MB para combos na ficha. */
    async obterIdentidadeMb() {
        const res = await fetch(this._urlIdentidadeMb(), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar tendências/divindades MB');
    }

    async obterConjuracaoMb() {
        const res = await fetch(this._urlConjuracaoMb(), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar regras de conjuração MB');
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

    _urlMagias() {
        return window.getApiUrl('/tormenta/regras/magias');
    }

    /**
     * Catálogo MB de magias — metadados (grimório / listagens).
     * @param {{ q?: string, circulo?: number, tipo?: 'arcana'|'divina', escola?: string, skip?: number, limit?: number, catalogo_por_classe_mb?: boolean, classe_mb_slug?: string, nivel_mb?: number, conjuracao_manual_mb?: boolean }} params
     */
    async listarMagiasCatalogo(params = {}) {
        const sp = new URLSearchParams();
        if (params.q) sp.set('q', params.q);
        if (params.circulo != null && params.circulo !== '') sp.set('circulo', String(params.circulo));
        if (params.tipo) sp.set('tipo', params.tipo);
        if (params.escola) sp.set('escola', params.escola);
        if (params.skip != null) sp.set('skip', String(params.skip));
        if (params.limit != null) sp.set('limit', String(params.limit));
        if (params.catalogo_por_classe_mb) sp.set('catalogo_por_classe_mb', 'true');
        if (params.classe_mb_slug) sp.set('classe_mb_slug', String(params.classe_mb_slug).trim());
        if (params.nivel_mb != null && params.nivel_mb !== '') sp.set('nivel_mb', String(params.nivel_mb));
        if (params.conjuracao_manual_mb) sp.set('conjuracao_manual_mb', 'true');
        const qs = sp.toString();
        const res = await fetch(this._urlMagias() + (qs ? `?${qs}` : ''), { headers: this._headers() });
        return this._handleJson(res, 'Erro ao carregar magias MB');
    }

    _urlConjuracaoPreview() {
        return window.getApiUrl('/tormenta/regras/conjuracao-preview');
    }

    /**
     * CD base (10+mod), modificador da chave e PM máx. de conjuração MB.
     * @param {{ classe_slug: string, nivel?: number, nivel_conjurador?: number|null, for_valor?: number, des_valor?: number, con_valor?: number, int_valor?: number, sab_valor?: number, car_valor?: number }} p
     */
    async obterConjuracaoPreview(p) {
        const sp = new URLSearchParams();
        sp.set('classe_slug', String(p.classe_slug || '').trim());
        sp.set('nivel', String(p.nivel != null ? p.nivel : 1));
        if (p.nivel_conjurador != null && p.nivel_conjurador !== '') {
            sp.set('nivel_conjurador', String(p.nivel_conjurador));
        }
        ['for', 'des', 'con', 'int', 'sab', 'car'].forEach((k) => {
            const key = `${k}_valor`;
            if (p[key] != null) sp.set(key, String(p[key]));
        });
        const qs = sp.toString();
        const res = await fetch(`${this._urlConjuracaoPreview()}?${qs}`, { headers: this._headers() });
        return this._handleJson(res, 'Erro ao calcular pré-visualização de conjuração MB');
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
