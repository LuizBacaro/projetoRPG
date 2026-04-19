/**
 * EquipamentoService.js
 * SRP: Comunicação HTTP com API de equipamentos
 * SOLID: DIP - Dependency Injection via constructor
 */

import { getApiUrl } from '../config/api.config.js';

export class EquipamentoService {
    constructor() {
        this.token = localStorage.getItem('token');
        this.baseUrl = getApiUrl('/equipamentos');
    }

    get token() {
        return localStorage.getItem('token');
    }

    set token(_value) {
        // Compatibilidade: evita token congelado no constructor legado.
    }

    /**
     * Lista todos os equipamentos disponíveis
     * @param {number} skip - Offset para paginação
     * @param {number} limit - Limite de resultados
     * @returns {Promise<Array>}
     */
    async listarEquipamentos(skip = 0, limit = 100) {
        try {
            const url = `${this.baseUrl}?skip=${skip}&limit=${limit}`;

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
            return data;

        } catch (error) {
            console.error('❌ Erro em listarEquipamentos:', error);
            throw error;
        }
    }

    /**
     * Obtém um equipamento por ID
     * @param {number} equipamentoId
     * @returns {Promise<Object>}
     */
    async obterEquipamento(equipamentoId) {
        try {
            const url = `${this.baseUrl}/${equipamentoId}`;

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Equipamento não encontrado`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Erro em obterEquipamento:', error);
            throw error;
        }
    }

    /**
     * Cria um novo equipamento (Admin only)
     * @param {Object} equipamento - {nome, descricao, pagina_referencia, ativo}
     * @returns {Promise<Object>}
     */
    async criarEquipamento(equipamento) {
        try {
            const url = this.baseUrl;

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(equipamento)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao criar equipamento`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Erro em criarEquipamento:', error);
            throw error;
        }
    }

    /**
     * Remove um item do catálogo global (soft delete). Apenas administrador.
     * @param {number} equipamentoId
     * @returns {Promise<void>}
     */
    async deletarEquipamentoDoCatalogo(equipamentoId) {
        try {
            const url = `${this.baseUrl}/catalogo/${equipamentoId}`;

            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok && response.status !== 204) {
                let detail = `HTTP ${response.status}`;
                try {
                    const err = await response.json();
                    if (err.detail !== undefined) {
                        detail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
                    }
                } catch {
                    /* ignore */
                }
                throw new Error(detail);
            }

            return null;

        } catch (error) {
            console.error('❌ Erro em deletarEquipamentoDoCatalogo:', error);
            throw error;
        }
    }

    /**
     * Lista equipamentos de um combatente
     * @param {number} combatenteId
     * @returns {Promise<Array>}
     */
    async listarEquipamentosJogador(combatenteId) {
        try {
            const url = `${this.baseUrl}/${combatenteId}/listar`;

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao listar equipamentos`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Erro em listarEquipamentosJogador:', error);
            throw error;
        }
    }

    /**
     * Adiciona um equipamento ao combatente
     * @param {number} combatenteId
     * @param {Object} equipamentoJogador - {equipamento_id, quantidade}
     * @returns {Promise<Object>}
     */
    async adicionarEquipamento(combatenteId, equipamentoJogador) {
        try {
            const url = `${this.baseUrl}/${combatenteId}/adicionar`;

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(equipamentoJogador)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao adicionar equipamento`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Erro em adicionarEquipamento:', error);
            throw error;
        }
    }

    /**
     * Remove um equipamento do combatente
     * @param {number} combatenteId
     * @param {number} equipamentoId
     * @returns {Promise<void>}
     */
    async removerEquipamento(combatenteId, equipamentoId) {
        try {
            const url = `${this.baseUrl}/${combatenteId}/remover/${equipamentoId}`;

            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok && response.status !== 204) {
                throw new Error(`HTTP ${response.status}: Erro ao remover equipamento`);
            }

            return null;

        } catch (error) {
            console.error('❌ Erro em removerEquipamento:', error);
            throw error;
        }
    }

    /**
     * Atualiza a quantidade de um equipamento
     * @param {number} combatenteId
     * @param {number} equipamentoId
     * @param {number} quantidade
     * @returns {Promise<Object>}
     */
    async atualizarQuantidade(combatenteId, equipamentoId, quantidade) {
        try {
            const url = `${this.baseUrl}/${combatenteId}/quantidade/${equipamentoId}?quantidade=${quantidade}`;

            const response = await fetch(url, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao atualizar quantidade`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Erro em atualizarQuantidade:', error);
            throw error;
        }
    }

    /**
     * Filtra equipamentos por termo de busca
     * @param {Array} equipamentos
     * @param {string} termo
     * @returns {Array}
     */
    filtrarPorBusca(equipamentos, termo) {
        if (!termo || termo.trim() === '') return equipamentos;

        const termoLower = termo.toLowerCase();
        return equipamentos.filter((e) => {
            const blob = [
                e.nome,
                e.descricao,
                e.categoria,
                e.subcategoria,
                e.custo,
                e.dano_pequeno,
                e.dano_medio,
                e.tipo_dano,
                e.critico,
                e.alcance_incremento,
                e.peso,
                e.pagina_referencia,
            ]
                .filter(Boolean)
                .join(' ')
                .toLowerCase();
            return blob.includes(termoLower);
        });
    }
}
