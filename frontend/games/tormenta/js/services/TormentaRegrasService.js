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
}
