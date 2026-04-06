/**
 * TalentoService.js
 * SRP: Comunicação HTTP com API de Talentos
 * SOLID: Dependency Injection do token, abstração da URL
 */

import { getApiUrl } from '../config/api.config.js';

export class TalentoService {
    constructor() {
        this.baseUrl = getApiUrl('/talentos');
        this.token = localStorage.getItem('token');
    }

    /**
     * Lista todos os talentos disponíveis
     * @param {number} skip
     * @param {number} limit
     * @returns {Promise<Array>}
     */
    async listarTalentos(skip = 0, limit = 100) {
        try {
            const url = `${this.baseUrl}?skip=${skip}&limit=${limit}`;

            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao listar talentos`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Erro em listarTalentos:', error);
            throw error;
        }
    }

    /**
     * Lista talentos do combatente
     * @param {number} combatenteId
     * @returns {Promise<Array>}
     */
    async listarTalentosJogador(combatenteId) {
        try {
            const url = `${this.baseUrl}/${combatenteId}/listar`;

            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao listar talentos`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Erro em listarTalentosJogador:', error);
            throw error;
        }
    }

    /**
     * Cria um novo talento
     * @param {Object} talento - {nome, descricao, pagina_referencia}
     * @returns {Promise<Object>}
     */
    async criarTalento(talento) {
        try {
            const url = this.baseUrl;

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(talento)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao criar talento`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Erro em criarTalento:', error);
            throw error;
        }
    }

    /**
     * Adiciona um talento ao combatente
     * @param {number} combatenteId
     * @param {Object} talentoJogador - {talento_id}
     * @returns {Promise<Object>}
     */
    async adicionarTalento(combatenteId, talentoJogador) {
        try {
            const url = `${this.baseUrl}/${combatenteId}/adicionar`;

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(talentoJogador)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao adicionar talento`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Erro em adicionarTalento:', error);
            throw error;
        }
    }

    /**
     * Remove um talento do combatente
     * @param {number} combatenteId
     * @param {number} talentoId
     * @returns {Promise<void>}
     */
    async removerTalento(combatenteId, talentoId) {
        try {
            const url = `${this.baseUrl}/${combatenteId}/remover/${talentoId}`;

            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok && response.status !== 204) {
                throw new Error(`HTTP ${response.status}: Erro ao remover talento`);
            }


        } catch (error) {
            console.error('❌ Erro em removerTalento:', error);
            throw error;
        }
    }
}
