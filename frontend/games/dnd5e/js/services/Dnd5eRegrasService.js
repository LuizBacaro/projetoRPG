/**
 * Cliente API — regras estáticas D&D 5e (`/api/v1/dnd5e/regras/*`).
 */
class Dnd5eRegrasService {
    _url(path) {
        return window.getApiUrl('/dnd5e/regras' + path);
    }

    _headers() {
        const headers = {};
        const token = AuthService.getToken();
        if (token) headers.Authorization = `Bearer ${token}`;
        return headers;
    }

    async _get(path, params = {}) {
        const q = new URLSearchParams();
        Object.entries(params).forEach(([k, v]) => {
            if (v != null && v !== '') q.set(k, String(v));
        });
        const qs = q.toString();
        const res = await fetch(this._url(path) + (qs ? `?${qs}` : ''), {
            headers: this._headers(),
        });
        if (res.status === 401) {
            if (typeof AuthService.logout === 'function') AuthService.logout();
            throw new Error('Sessão expirada.');
        }
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            throw new Error(e.detail || 'Erro ao carregar regras');
        }
        return res.json();
    }

    atributos() {
        return this._get('/atributos');
    }

    racas() {
        return this._get('/racas');
    }

    classes() {
        return this._get('/classes');
    }

    combate() {
        return this._get('/combate');
    }

    magias(params) {
        return this._get('/magias', params);
    }

    talentos(params) {
        return this._get('/talentos', params);
    }

    equipamento() {
        return this._get('/equipamento');
    }

    antecedentes() {
        return this._get('/antecedentes');
    }

    pericias() {
        return this._get('/pericias');
    }

    subclasses(classeSlug) {
        return this._get('/subclasses', classeSlug ? { classe_slug: classeSlug } : {});
    }

    async calcularAtributos(body) {
        const res = await fetch(this._url('/calcular-atributos'), {
            method: 'POST',
            headers: { ...this._headers(), 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (res.status === 401) {
            if (typeof AuthService.logout === 'function') AuthService.logout();
            throw new Error('Sessão expirada.');
        }
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            throw new Error(e.detail || 'Erro ao calcular atributos');
        }
        return res.json();
    }
}
