/**
 * Service de Combatente
 * Single Responsibility: comunicação HTTP + conversão para modelo de domínio
 */

import { getApiUrl } from '../config/api.config.js';
import { Combatente } from '../models/Combatente.js';

export class CombatenteService {

    /**
     * Converte JSON da API para instância de Combatente (com métodos)
     * @param {Object} data - JSON puro da API
     * @returns {Combatente}
     */
    _toModel(data) {
        return new Combatente(data);
    }

    /**
     * Lista todos os combatentes ou filtra por tipo
     * @param {string|null} tipo
     * @returns {Promise<Combatente[]>}
     */
    async listar(tipo = null) {
        try {
            const url = tipo
                ? `${getApiUrl('/combatentes')}?tipo=${tipo}`
                : getApiUrl('/combatentes');

            const response = await fetch(url);
            if (!response.ok) throw new Error('Erro ao carregar combatentes');

            const data = await response.json();
            return data.map(item => this._toModel(item)); // ✅ converte para Combatente

        } catch (error) {
            console.error('Erro ao listar combatentes:', error);
            throw error;
        }
    }

    /**
     * Obtém um combatente por ID
     * @param {number} id
     * @returns {Promise<Combatente>}
     */
    async obterPorId(id) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}`);
            if (!response.ok) throw new Error('Combatente não encontrado');

            const data = await response.json();
            return this._toModel(data); // ✅ converte para Combatente

        } catch (error) {
            console.error('Erro ao obter combatente:', error);
            throw error;
        }
    }

    /**
     * Cria um novo combatente
     * @param {FormData} formData
     * @returns {Promise<Combatente>}
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

            const data = await response.json();
            return this._toModel(data); // ✅ converte para Combatente

        } catch (error) {
            console.error('Erro ao criar combatente:', error);
            throw error;
        }
    }

    /**
     * Atualiza um combatente
     * @param {number} id
     * @param {FormData} formData
     * @returns {Promise<Combatente>}
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

            const data = await response.json();
            return this._toModel(data); // ✅ converte para Combatente

        } catch (error) {
            console.error('Erro ao atualizar combatente:', error);
            throw error;
        }
    }

    /**
     * Atualiza apenas o HP de um combatente
     * @param {number} id
     * @param {number} hpAtual
     * @returns {Promise<Combatente>}
     */
    async atualizarHP(id, hpAtual) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}/hp`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hp_atual: parseInt(hpAtual) })
            });

            if (!response.ok) throw new Error('Erro ao atualizar HP');

            const data = await response.json();
            return this._toModel(data); // ✅ converte para Combatente

        } catch (error) {
            console.error('Erro ao atualizar HP:', error);
            throw error;
        }
    }

    /**
     * Atualiza apenas a iniciativa de um combatente
     * @param {number} id
     * @param {number} iniciativa
     * @returns {Promise<Combatente>}
     */
    async atualizarIniciativa(id, iniciativa) {
        try {
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}/iniciativa`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ iniciativa: parseInt(iniciativa) })
            });

            if (!response.ok) throw new Error('Erro ao atualizar iniciativa');

            const data = await response.json();
            return this._toModel(data); // ✅ converte para Combatente

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