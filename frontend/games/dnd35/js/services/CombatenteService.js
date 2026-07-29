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
    }

    get token() {
        return localStorage.getItem('token');
    }

    set token(_value) {
        // Compatibilidade: evita token congelado no constructor legado.
    }

    /**
     * Converte JSON da API para instância de Combatente
     * @param {Object} data - JSON puro da API
     * @returns {Combatente}
     */
    _toModel(data) {
        return new Combatente(data);
    }

    _tratar401(response) {
        if (response.status !== 401) return false;
        if (typeof window !== 'undefined' && window.AuthService && typeof window.AuthService.logout === 'function') {
            window.AuthService.logout();
        }
        return true;
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


            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                if (this._tratar401(response)) {
                    throw new Error('HTTP 401: Token inválido ou expirado');
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
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

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                let detail = '';
                try {
                    const errorData = await response.json();
                    detail = (errorData && errorData.detail) ? String(errorData.detail) : '';
                } catch {
                    detail = '';
                }

                if (this._tratar401(response)) {
                    throw new Error(`HTTP 401: ${detail || 'Token inválido ou expirado'}`);
                }

                if (response.status === 403) {
                    throw new Error(`HTTP 403: Sem permissão para acessar este personagem${detail ? ` (${detail})` : ''}`);
                }

                if (response.status === 404) {
                    throw new Error(`HTTP 404: Personagem não encontrado${detail ? ` (${detail})` : ''}`);
                }

                throw new Error(`HTTP ${response.status}: ${detail || 'Erro ao obter personagem'}`);
            }

            const data = await response.json();
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
            return this._toModel(data);

        } catch (error) {
            console.error('❌ Erro ao criar combatente:', error);
            throw error;
        }
    }

    /**
     * Atualiza campos específicos via PATCH JSON (evita sobrescrever a ficha inteira).
     * @param {number} id
     * @param {Object} campos
     * @returns {Promise<Combatente>}
     */
    async atualizarCampos(id, campos) {
        try {
            const url = `${getApiUrl('/combatentes')}/${id}`;

            const response = await fetch(url, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(campos)
            });

            if (!response.ok) {
                let detail = 'Erro ao atualizar combatente';
                try {
                    const errorData = await response.json();
                    detail = errorData.detail || detail;
                } catch {
                    // mantém mensagem padrão
                }
                throw new Error(detail);
            }

            const data = await response.json();
            return this._toModel(data);

        } catch (error) {
            console.error('❌ Erro ao atualizar campos do combatente:', error);
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

            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Erro ao deletar combatente`);
            }

            return true;

        } catch (error) {
            console.error('❌ Erro ao deletar combatente:', error);
            throw error;
        }
    }

    /**
     * Importa monstro/NPC a partir do catálogo do Livro dos Monstros.
     * @param {{ slug: string, tipo?: string, campanha_id?: number, nome_override?: string, foto_url?: string }} payload
     * @returns {Promise<Combatente>}
     */
    async importarBestiario(payload) {
        try {
            const response = await fetch(getApiUrl('/combatentes/importar-bestiario'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`,
                },
                body: JSON.stringify(payload || {}),
            });

            if (!response.ok) {
                let detail = 'Erro ao importar do bestiário';
                try {
                    const errorData = await response.json();
                    detail = errorData.detail || detail;
                } catch {
                    /* ignore */
                }
                if (this._tratar401(response)) {
                    throw new Error('HTTP 401: Token inválido ou expirado');
                }
                throw new Error(detail);
            }

            const data = await response.json();
            return this._toModel(data);
        } catch (error) {
            console.error('❌ Erro ao importar bestiário:', error);
            throw error;
        }
    }

    /**
     * Envia retrato do combatente (multipart).
     * @param {number} id
     * @param {File} file
     * @returns {Promise<Combatente>}
     */
    async enviarFoto(id, file) {
        try {
            const fd = new FormData();
            fd.append('foto', file);
            const response = await fetch(`${getApiUrl('/combatentes')}/${id}/foto`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                },
                body: fd,
            });

            if (!response.ok) {
                let detail = 'Erro ao enviar foto';
                try {
                    const errorData = await response.json();
                    detail = errorData.detail || detail;
                } catch {
                    /* ignore */
                }
                if (this._tratar401(response)) {
                    throw new Error('HTTP 401: Token inválido ou expirado');
                }
                throw new Error(detail);
            }

            const data = await response.json();
            return this._toModel(data);
        } catch (error) {
            console.error('❌ Erro ao enviar foto:', error);
            throw error;
        }
    }
}