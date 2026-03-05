/**
 * UsuarioService
 * SRP: comunicação HTTP com a API de usuários
 * Usa AuthService para enviar o token JWT em todas as requisições
 */
class UsuarioService {

    _headers() {
        return {
            'Content-Type': 'application/json',
            ...AuthService.getAuthHeader()
        };
    }

    async listar(apenasAtivos = false) {
        const url = apenasAtivos
            ? `${getApiUrl('/usuarios')}?apenas_ativos=true`
            : getApiUrl('/usuarios');
        const res = await fetch(url, { headers: this._headers() });
        if (!res.ok) throw new Error('Erro ao listar usuários');
        return res.json();
    }

    async buscarPorId(id) {
        const res = await fetch(`${getApiUrl('/usuarios')}/${id}`, { headers: this._headers() });
        if (!res.ok) throw new Error('Usuário não encontrado');
        return res.json();
    }

    async criar(dados) {
        const res = await fetch(getApiUrl('/usuarios'), {
            method:  'POST',
            headers: this._headers(),
            body:    JSON.stringify(dados)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Erro ao criar usuário');
        }
        return res.json();
    }

    async atualizar(id, dados) {
        const res = await fetch(`${getApiUrl('/usuarios')}/${id}`, {
            method:  'PUT',
            headers: this._headers(),
            body:    JSON.stringify(dados)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Erro ao atualizar usuário');
        }
        return res.json();
    }

    async inativar(id) {
        const res = await fetch(`${getApiUrl('/usuarios')}/${id}`, {
            method:  'DELETE',
            headers: this._headers()
        });
        if (!res.ok) throw new Error('Erro ao inativar usuário');
        return res.json();
    }
}