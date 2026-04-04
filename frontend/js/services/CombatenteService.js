/**
 * CombatenteService.js
 * SRP: Comunicação HTTP com a API de combatentes
 * SOLID: DIP - Dependency Injection via constructor (será usado se necessário)
 */

import { getApiUrl } from '../config/api.config.js';
import { Combatente } from '../models/Combatente.js';

export class CombatenteService {
    constructor() {
        this.token = localStorage.getItem('token');
        console.log('✅ CombatenteService inicializado');
    }

    /**
     * Converte JSON da API para instância de Combatente
     * @param {Object} data - JSON puro da API
     * @returns {Combatente}
     */
    _toModel(data) {
        return new Combatente(data);
    }

    /**
     * Lista todos os combatentes ou filtra por tipo
     * @param {string|null} tipo - 'jogador', 'monstro', 'npc'
     * @returns {Promise<Combatente[]>}
     */
    async listar(tipo = null) {
        try {
            const url = tipo
                ? `${getApiUrl('/combatentes')}?tipo=${tipo}`
                : getApiUrl('/combatentes');

            console.log('📡 GET:', url);

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('✅ Combatentes carregados:', data.length);
            return data.map(item => this._toModel(item));

        } catch (error) {
            console.error('❌ Erro ao listar combatentes:', error);
            throw error;
        }
    }

    /**
     * Obtém um combatente por ID (FUNÇÃO RENOMEADA PARA CLAREZA)
     * @param {number} id - ID do combatente
     * @returns {Promise<Combatente>}
     */
    async obterCombatente(id) {
        try {
            const url = `${getApiUrl('/combatentes')}/${id}`;
            console.log('📡 GET:', url);

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Combatente não encontrado`);
            }

            const data = await response.json();
            console.log('✅ Combatente carregado:', data.nome);
            return this._toModel(data);

        } catch (error) {
            console.error('❌ Erro ao obter combatente:', error);
            throw error;
        }
    }

    /**
     * Alias para obterCombatente (compatibilidade)
     * @param {number} id
     * @returns {Promise<Combatente>}
     */
    async obterPorId(id) {
        return this.obterCombatente(id);
    }

    /**
     * Cria um novo combatente
     * @param {FormData} formData
     * @returns {Promise<Combatente>}
     */
    async criar(formData) {
        try {
            const url = getApiUrl('/combatentes');
            console.log('📡 POST:', url);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao criar combatente');
            }

            const data = await response.json();
            console.log('✅ Combatente criado:', data.nome);
            return this._toModel(data);

        } catch (error) {
            console.error('❌ Erro ao criar combatente:', error);
            throw error;
        }
    }

    /**
     * Atualiza um combatente completo
     * @param {number} id
     * @param {FormData} formData
     * @returns {Promise<Combatente>}
     */
    async atualizar(id, formData) {
        try {
            const url = `${getApiUrl('/combatentes')}/${id}`;
            console.log('📡 PUT:', url);

            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao atualizar combatente');
            }

            const data = await response.json();
            console.log('✅ Combatente atualizado:', data.nome);
            return this._toModel(data);

        } catch (error) {
            console.error('❌ Erro ao atualizar combatente:', error);
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
            const url = `${getApiUrl('/combatentes')}/${id}/hp`;
            console.log('📡 PATCH:', url);

            const response = await fetch(url, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ hp_atual: parseInt(hpAtual) })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao atualizar HP`);
            }

            const data = await response.json();
            console.log('✅ HP atualizado para:', hpAtual);
            return this._toModel(data);

        } catch (error) {
            console.error('❌ Erro ao atualizar HP:', error);
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
            const url = `${getApiUrl('/combatentes')}/${id}/iniciativa`;
            console.log('📡 PATCH:', url);

            const response = await fetch(url, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ iniciativa: parseInt(iniciativa) })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao atualizar iniciativa`);
            }

            const data = await response.json();
            console.log('✅ Iniciativa atualizada para:', iniciativa);
            return this._toModel(data);

        } catch (error) {
            console.error('❌ Erro ao atualizar iniciativa:', error);
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
            const url = `${getApiUrl('/combatentes')}/${id}`;
            console.log('📡 DELETE:', url);

            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao deletar combatente`);
            }

            console.log('✅ Combatente deletado');
            return true;

        } catch (error) {
            console.error('❌ Erro ao deletar combatente:', error);
            throw error;
        }
    }
}