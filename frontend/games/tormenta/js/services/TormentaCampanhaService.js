class TormentaCampanhaService {
    _url(path = '') {
        return window.getApiUrl('/tormenta/campanhas' + path);
    }

    _headers(json = true) {
        const headers = {};
        if (json) headers['Content-Type'] = 'application/json';
        if (typeof AuthService !== 'undefined') {
            const token = AuthService.getToken();
            if (token) headers.Authorization = `Bearer ${token}`;
        }
        return headers;
    }

    async _handleResponse(res, fallbackMessage) {
        if (res.status === 401) {
            if (typeof AuthService !== 'undefined' && typeof AuthService.logout === 'function') {
                AuthService.logout();
            }
            throw new Error('Token inválido ou expirado. Faça login novamente.');
        }
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            throw new Error(e.detail || fallbackMessage);
        }
        if (res.status === 204) return null;
        return res.json();
    }

    async listar() {
        const res = await fetch(this._url(), { headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao carregar campanhas');
    }

    async criar(payload) {
        const res = await fetch(this._url(), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao criar campanha');
    }

    async atualizar(campanhaId, payload) {
        const res = await fetch(this._url(`/${campanhaId}`), {
            method: 'PUT',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao atualizar campanha');
    }

    async deletar(campanhaId) {
        const res = await fetch(this._url(`/${campanhaId}`), {
            method: 'DELETE',
            headers: this._headers(false),
        });
        await this._handleResponse(res, 'Erro ao excluir campanha');
        return true;
    }

    async listarSessoes() {
        const res = await fetch(this._url('/sessoes'), { headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao carregar sessões');
    }

    async criarSessao(payload) {
        const res = await fetch(this._url('/sessoes'), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao criar sessão');
    }

    async atualizarSessao(sessaoId, payload) {
        const res = await fetch(this._url(`/sessoes/${sessaoId}`), {
            method: 'PUT',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao atualizar sessão');
    }

    async deletarSessao(sessaoId) {
        const res = await fetch(this._url(`/sessoes/${sessaoId}`), {
            method: 'DELETE',
            headers: this._headers(false),
        });
        await this._handleResponse(res, 'Erro ao excluir sessão');
        return true;
    }
}

window.TormentaCampanhaService = TormentaCampanhaService;
