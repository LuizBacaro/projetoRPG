/**
 * UsuarioService
 * SRP: comunicação HTTP com a API de usuários
 * Carregado via <script> dinâmico — usa window.getApiUrl
 */
class UsuarioService {

    /**
     * Lista todos os usuários
     * @param {boolean} apenasAtivos
     * @returns {Promise<{total: number, usuarios: Array}>}
     */
    async listar(apenasAtivos = false) {
        const url = apenasAtivos
            ? `${getApiUrl('/usuarios')}?apenas_ativos=true`
            : getApiUrl('/usuarios');

        const res = await fetch(url);
        if (!res.ok) throw new Error('Erro ao listar usuários');
        return res.json();
    }

    /**
     * Busca um usuário por ID
     * @param {number} id
     * @returns {Promise<Object>}
     */
    async buscarPorId(id) {
        const res = await fetch(`${getApiUrl('/usuarios')}/${id}`);
        if (!res.ok) throw new Error('Usuário não encontrado');
        return res.json();
    }

    /**
     * Cria um novo usuário
     * @param {{nome, email, senha, perfil, ativo}} dados
     * @returns {Promise<Object>}
     */
    async criar(dados) {
        const res = await fetch(getApiUrl('/usuarios'), {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(dados)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Erro ao criar usuário');
        }
        return res.json();
    }

    /**
     * Atualiza dados de um usuário
     * @param {number} id
     * @param {Object} dados - apenas os campos a alterar
     * @returns {Promise<Object>}
     */
    async atualizar(id, dados) {
        const res = await fetch(`${getApiUrl('/usuarios')}/${id}`, {
            method:  'PUT',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(dados)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Erro ao atualizar usuário');
        }
        return res.json();
    }

    /**
     * Exclusão lógica — muda status para Inativo
     * @param {number} id
     * @returns {Promise<Object>}
     */
    async inativar(id) {
        const res = await fetch(`${getApiUrl('/usuarios')}/${id}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error('Erro ao inativar usuário');
        return res.json();
    }
}