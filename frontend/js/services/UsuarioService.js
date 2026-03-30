/**
 * UsuarioService
 * SRP: comunicação HTTP com a API de usuários
 * Carregado via script dinâmico — usa window.getApiUrl e window.AuthService
 */
class UsuarioService {

    _extrairMensagemErro(errPayload, fallback) {
        if (!errPayload) return fallback;

        if (typeof errPayload.detail === 'string' && errPayload.detail.trim()) {
            return errPayload.detail;
        }

        if (Array.isArray(errPayload.detail) && errPayload.detail.length > 0) {
            const mensagens = errPayload.detail.map((item) => {
                if (!item || typeof item !== 'object') return null;

                const loc = Array.isArray(item.loc)
                    ? item.loc.filter((p) => p !== 'body').join('.')
                    : '';
                const msg = item.msg || 'valor inválido';

                return loc ? `${loc}: ${msg}` : msg;
            }).filter(Boolean);

            if (mensagens.length > 0) {
                return mensagens.join(' | ');
            }
        }

        return fallback;
    }

    // Monta headers com Content-Type e JWT
    _headers() {
        const headers = { 'Content-Type': 'application/json' };

        if (typeof AuthService !== 'undefined') {
            const token = AuthService.getToken();
            if (token) headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    _url(path = '') {
        // window.getApiUrl garantido pelo import no usuarios.html
        return window.getApiUrl(`/usuarios${path}`);
    }

    async listar(apenasAtivos = false) {
        const url = apenasAtivos ? `${this._url()}?apenas_ativos=true` : this._url();
        const res = await fetch(url, { headers: this._headers() });

        if (res.status === 401) { AuthService?.logout(); return { usuarios: [] }; }
        if (!res.ok) throw new Error('Erro ao listar usuários');
        return res.json();
    }

    async buscarPorId(id) {
        const res = await fetch(this._url(`/${id}`), { headers: this._headers() });

        if (res.status === 401) { AuthService?.logout(); return null; }
        if (!res.ok) throw new Error('Usuário não encontrado');
        return res.json();
    }

    async criar(dados) {
        const res = await fetch(this._url(), {
            method:  'POST',
            headers: this._headers(),
            body:    JSON.stringify(dados)
        });

        if (res.status === 401) {
            AuthService?.logout();
            throw new Error('Sessão expirada. Faça login novamente.');
        }
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(this._extrairMensagemErro(err, 'Erro ao criar usuário'));
        }
        return res.json();
    }

    async atualizar(id, dados) {
        const res = await fetch(this._url(`/${id}`), {
            method:  'PUT',
            headers: this._headers(),
            body:    JSON.stringify(dados)
        });

        if (res.status === 401) {
            AuthService?.logout();
            throw new Error('Sessão expirada. Faça login novamente.');
        }
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(this._extrairMensagemErro(err, 'Erro ao atualizar usuário'));
        }
        return res.json();
    }

    async inativar(id) {
        const res = await fetch(this._url(`/${id}`), {
            method:  'DELETE',
            headers: this._headers()
        });

        if (res.status === 401) { AuthService?.logout(); return null; }
        if (!res.ok) throw new Error('Erro ao inativar usuário');
        return res.json();
    }
}