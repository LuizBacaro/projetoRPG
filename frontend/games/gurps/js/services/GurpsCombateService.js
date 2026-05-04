/** Cliente API — combate GURPS (Arena). */
class GurpsCombateService {
    _url(path = '') {
        return window.getApiUrl('/gurps/combate' + path);
    }

    _headers(json = true) {
        const headers = {};
        if (json) headers['Content-Type'] = 'application/json';
        const token = AuthService.getToken();
        if (token) headers.Authorization = `Bearer ${token}`;
        return headers;
    }

    async _handleResponse(res, fallbackMessage) {
        if (res.status === 401) {
            if (typeof AuthService.logout === 'function') AuthService.logout();
            throw new Error('Sessão expirada.');
        }
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            let d = e.detail;
            if (Array.isArray(d)) {
                d = d
                    .map((x) => (typeof x === 'string' ? x : x.msg || JSON.stringify(x)))
                    .join('; ');
            } else if (d && typeof d === 'object') {
                d = JSON.stringify(d);
            }
            throw new Error(d || fallbackMessage);
        }
        return res.json();
    }

    async status(resumido = false) {
        const q = resumido ? '?resumido=true' : '';
        const res = await fetch(this._url(`/status${q}`), { headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao obter status do combate');
    }

    async iniciar(personagemIds) {
        const res = await fetch(this._url('/iniciar'), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify({ personagem_ids: personagemIds }),
        });
        return this._handleResponse(res, 'Erro ao iniciar combate');
    }

    async avancarTurno() {
        const res = await fetch(this._url('/avancar-turno'), {
            method: 'POST',
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao avançar turno');
    }

    async finalizar() {
        const res = await fetch(this._url('/finalizar'), {
            method: 'POST',
            headers: this._headers(false),
        });
        return this._handleResponse(res, 'Erro ao finalizar combate');
    }

    async ataque(payload) {
        const res = await fetch(this._url('/ataque'), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload || {}),
        });
        return this._handleResponse(res, 'Erro ao executar ataque');
    }

    async ajustarPv(payload) {
        const res = await fetch(this._url('/ajustar-pv'), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload || {}),
        });
        return this._handleResponse(res, 'Erro ao ajustar PV');
    }

    async definirPostura(payload) {
        const res = await fetch(this._url('/postura-atual'), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload || {}),
        });
        return this._handleResponse(res, 'Erro ao definir postura');
    }
}
