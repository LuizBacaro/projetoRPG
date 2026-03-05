/**
 * UsuarioService
 * SRP: comunicação HTTP com a API de usuários
 * Carregado via script dinâmico — usa window.getApiUrl e window.AuthService
 */
class UsuarioService {

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
            throw new Error(err.detail || 'Erro ao criar usuário');
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
            throw new Error(err.detail || 'Erro ao atualizar usuário');
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