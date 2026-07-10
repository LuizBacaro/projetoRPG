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
        const res = await fetch(this._url(), {
            headers: this._headers(false),
            cache: 'no-store',
        });
        return this._handleResponse(res, 'Erro ao carregar campanhas');
    }

    async listarDisponiveis() {
        const res = await fetch(this._url('/disponiveis'), {
            headers: this._headers(false),
            cache: 'no-store',
        });
        return this._handleResponse(res, 'Erro ao carregar campanhas disponíveis');
    }

    async listarSolicitacoesPendentes() {
        const res = await fetch(this._url('/solicitacoes/pendentes'), {
            headers: this._headers(false),
            cache: 'no-store',
        });
        return this._handleResponse(res, 'Erro ao carregar solicitações');
    }

    async listarHistoricoSolicitacoes() {
        const res = await fetch(this._url('/solicitacoes/historico'), {
            headers: this._headers(false),
            cache: 'no-store',
        });
        return this._handleResponse(res, 'Erro ao carregar histórico de solicitações');
    }

    async obterMinhaSolicitacao(personagemId) {
        const res = await fetch(
            this._url(`/solicitacoes/minhas?personagem_id=${encodeURIComponent(String(personagemId))}`),
            { headers: this._headers(false), cache: 'no-store' }
        );
        if (res.status === 204) return null;
        return this._handleResponse(res, 'Erro ao carregar solicitação');
    }

    async criarSolicitacao(payload) {
        const res = await fetch(this._url('/solicitacoes'), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao solicitar entrada na campanha');
    }

    async aceitarSolicitacao(solicitacaoId) {
        const res = await fetch(this._url(`/solicitacoes/${solicitacaoId}/aceitar`), {
            method: 'POST',
            headers: this._headers(true),
            body: '{}',
        });
        return this._handleResponse(res, 'Erro ao aceitar solicitação');
    }

    async recusarSolicitacao(solicitacaoId) {
        const res = await fetch(this._url(`/solicitacoes/${solicitacaoId}/recusar`), {
            method: 'POST',
            headers: this._headers(true),
            body: '{}',
        });
        return this._handleResponse(res, 'Erro ao recusar solicitação');
    }

    async cancelarSolicitacao(solicitacaoId) {
        const res = await fetch(this._url(`/solicitacoes/${solicitacaoId}`), {
            method: 'DELETE',
            headers: this._headers(false),
        });
        await this._handleResponse(res, 'Erro ao cancelar solicitação');
        return true;
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

    async listarHandouts(campanhaId) {
        const q =
            campanhaId != null && campanhaId !== ''
                ? `?campanha_id=${encodeURIComponent(String(campanhaId))}`
                : '';
        const res = await fetch(this._url(`/handouts${q}`), {
            headers: this._headers(false),
            cache: 'no-store',
        });
        return this._handleResponse(res, 'Erro ao carregar handouts');
    }

    async listarHandoutsVisiveis(campanhaId) {
        const q =
            campanhaId != null && campanhaId !== ''
                ? `?campanha_id=${encodeURIComponent(String(campanhaId))}`
                : '';
        const res = await fetch(this._url(`/handouts/visiveis${q}`), {
            headers: this._headers(false),
            cache: 'no-store',
        });
        return this._handleResponse(res, 'Erro ao carregar handouts revelados');
    }

    async listarSessoesVisiveis() {
        const res = await fetch(this._url('/sessoes/visiveis'), {
            headers: this._headers(false),
            cache: 'no-store',
        });
        return this._handleResponse(res, 'Erro ao carregar sessões visíveis');
    }

    async criarHandout(payload) {
        const res = await fetch(this._url('/handouts'), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao criar handout');
    }

    async atualizarHandout(handoutId, payload) {
        const res = await fetch(this._url(`/handouts/${handoutId}`), {
            method: 'PUT',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao atualizar handout');
    }

    async deletarHandout(handoutId) {
        const res = await fetch(this._url(`/handouts/${handoutId}`), {
            method: 'DELETE',
            headers: this._headers(false),
        });
        await this._handleResponse(res, 'Erro ao excluir handout');
        return true;
    }
}

window.TormentaCampanhaService = TormentaCampanhaService;
