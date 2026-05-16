/**
 * Cliente API — personagens D&D 5e (`/api/v1/dnd5e/personagens`).
 */
class Dnd5ePersonagemService {
    _url(path = '') {
        return window.getApiUrl('/dnd5e/personagens' + path);
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
            throw new Error('Sessão expirada. Faça login novamente.');
        }
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            let d = e.detail;
            if (Array.isArray(d)) {
                d = d.map((x) => (typeof x === 'string' ? x : x.msg || JSON.stringify(x))).join('; ');
            } else if (d && typeof d === 'object') {
                d = JSON.stringify(d);
            }
            throw new Error(typeof d === 'string' && d ? d : fallbackMessage);
        }
        if (res.status === 204) return null;
        return res.json();
    }

    async listar(params = {}) {
        const q = new URLSearchParams();
        if (params.tipo) q.set('tipo', params.tipo);
        if (params.meus) q.set('meus', 'true');
        if (params.skip != null) q.set('skip', String(params.skip));
        if (params.limit != null) q.set('limit', String(params.limit));
        const qs = q.toString();
        const res = await fetch(this._url(qs ? `?${qs}` : ''), { headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao listar personagens');
    }

    async obter(id) {
        const res = await fetch(this._url(`/${id}`), { headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao carregar personagem');
    }

    async criar(payload) {
        const res = await fetch(this._url(''), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao criar personagem');
    }

    async atualizar(id, payload) {
        const res = await fetch(this._url(`/${id}`), {
            method: 'PATCH',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao salvar personagem');
    }

    async enviarFoto(id, file) {
        const fd = new FormData();
        fd.append('foto', file);
        const headers = {};
        const token = AuthService.getToken();
        if (token) headers.Authorization = `Bearer ${token}`;
        const res = await fetch(this._url(`/${id}/foto`), {
            method: 'POST',
            headers,
            body: fd,
        });
        return this._handleResponse(res, 'Erro ao enviar foto');
    }
}
