/** Cliente API — campanhas GURPS. */
class GurpsCampanhaService {
    _url(path = '') {
        return window.getApiUrl('/gurps/campanhas' + path);
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
            throw new Error(e.detail || fallbackMessage);
        }
        if (res.status === 204) return null;
        return res.json();
    }

    async listar() {
        const res = await fetch(this._url(''), {
            headers: this._headers(false),
            cache: 'no-store',
        });
        return this._handleResponse(res, 'Erro ao listar campanhas');
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
        const res = await fetch(this._url(''), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao criar campanha');
    }

    async atualizar(id, payload) {
        const res = await fetch(this._url(`/${id}`), {
            method: 'PUT',
            headers: this._headers(true),
            body: JSON.stringify(payload),
        });
        return this._handleResponse(res, 'Erro ao atualizar campanha');
    }

    /** Adiciona personagens à campanha sem remover os já vinculados (paridade com D&D 3.5). */
    async associarPersonagens(campanhaId, personagemIds) {
        const res = await fetch(this._url(`/${campanhaId}/personagens`), {
            method: 'POST',
            headers: this._headers(true),
            body: JSON.stringify({ personagem_ids: personagemIds || [] }),
        });
        return this._handleResponse(res, 'Erro ao associar personagens');
    }

    async deletar(id) {
        const res = await fetch(this._url(`/${id}`), { method: 'DELETE', headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao remover campanha');
    }

    async listarSessoesVisiveis() {
        const res = await fetch(this._url('/sessoes/visiveis'), { headers: this._headers(false) });
        return this._handleResponse(res, 'Erro ao carregar resumos de sessão');
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
