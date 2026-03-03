/**
 * Service de Combatente (Business Logic + API Calls)
 * Single Responsibility: apenas lógica de combatente
 * Carregado via <script> — sem módulos ES6
 */

class CombatenteService {

    /**
     * Lista todos os combatentes ou filtra por tipo
     * @param {string|null} tipo
     * @returns {Promise<Array>}
     */
    async listar(tipo = null) {
        try {
            const url = tipo
                ? `${getApiUrl('/combatentes')}?tipo=${tipo}`
                : getApiUrl('/combatentes');

            const response = await fetch(url);

            if (!response.ok) throw new Error('Erro ao carregar combatentes');

            return await response.json();

        } catch (error) {
            console.error('Erro ao listar combatentes:', error);
            throw error;
        }
    }

    /**
     * Obtém um combatente por ID
     * @param {number} id
     * @returns {Promise<Object>}
     */
    async obterPorId(id) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}`);

            if (!response.ok) throw new Error('Combatente não encontrado');

            return await response.json();

        } catch (error) {
            console.error('Erro ao obter combatente:', error);
            throw error;
        }
    }

    /**
     * Cria um novo combatente
     * @param {FormData} formData
     * @returns {Promise<Object>}
     */
    async criar(formData) {
        try {
            const response = await fetch(getApiUrl('/combatentes'), {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao criar combatente');
            }

            return await response.json();

        } catch (error) {
            console.error('Erro ao criar combatente:', error);
            throw error;
        }
    }

    /**
     * Atualiza um combatente
     * @param {number} id
     * @param {FormData} formData
     * @returns {Promise<Object>}
     */
    async atualizar(id, formData) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}`, {
                method: 'PUT',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao atualizar combatente');
            }

            return await response.json();

        } catch (error) {
            console.error('Erro ao atualizar combatente:', error);
            throw error;
        }
    }

    /**
     * Atualiza apenas o HP de um combatente
     * @param {number} id
     * @param {number} hpAtual
     * @returns {Promise<Object>}
     */
    async atualizarHP(id, hpAtual) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}/hp`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hp_atual: parseInt(hpAtual) })
            });

            if (!response.ok) throw new Error('Erro ao atualizar HP');

            return await response.json();

        } catch (error) {
            console.error('Erro ao atualizar HP:', error);
            throw error;
        }
    }

    /**
     * Atualiza apenas a iniciativa de um combatente
     * @param {number} id
     * @param {number} iniciativa
     * @returns {Promise<Object>}
     */
    async atualizarIniciativa(id, iniciativa) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}/iniciativa`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ iniciativa: parseInt(iniciativa) })
            });

            if (!response.ok) throw new Error('Erro ao atualizar iniciativa');

            return await response.json();

        } catch (error) {
            console.error('Erro ao atualizar iniciativa:', error);
            throw error;
        }
    }

    /**
     * Deleta um combatente
     * @param {number} id
     * @returns {Promise<boolean>}
     */
    async deletar(id) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Erro ao deletar combatente');

            return true;

        } catch (error) {
            console.error('Erro ao deletar combatente:', error);
            throw error;
        }
    }
}