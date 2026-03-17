/**
 * PericiaService.js
 * SRP: Comunicação HTTP com API de perícias
 * SOLID: DIP - Dependency Injection via constructor
 */

import { getApiUrl } from '../config/api.config.js';

export class PericiaService {
    constructor() {
        this.token = localStorage.getItem('token');
        this.baseUrl = getApiUrl('/pericias');
        console.log('✅ PericiaService inicializado');
    }

    /**
     * Lista todas as perícias disponíveis
     * @param {number} skip - Offset para paginação
     * @param {number} limit - Limite de resultados
     * @param {string|null} atributo - Filtro por atributo (FOR, DES, CON, INT, SAB, CAR)
     * @returns {Promise<Array>}
     */
    async listarPericias(skip = 0, limit = 100, atributo = null) {
        try {
            let url = `${this.baseUrl}?skip=${skip}&limit=${limit}`;
            if (atributo) url += `&atributo=${atributo.toUpperCase()}`;

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
            console.log('✅ Perícias carregadas:', data.length);
            return data;

        } catch (error) {
            console.error('❌ Erro em listarPericias:', error);
            throw error;
        }
    }

    /**
     * Obtém uma perícia por ID
     * @param {number} periciaId
     * @returns {Promise<Object>}
     */
    async obterPericia(periciaId) {
        try {
            const url = `${this.baseUrl}/${periciaId}`;
            console.log('📡 GET:', url);

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Perícia não encontrada`);
            }

            const data = await response.json();
            console.log('✅ Perícia obtida:', data.nome);
            return data;

        } catch (error) {
            console.error('❌ Erro em obterPericia:', error);
            throw error;
        }
    }

    /**
     * Lista perícias por atributo
     * @param {string} atributo - FOR, DES, CON, INT, SAB, CAR
     * @returns {Promise<Array>}
     */
    async listarPorAtributo(atributo) {
        return this.listarPericias(0, 100, atributo);
    }

    /**
     * Agrupa perícias por atributo
     * @param {Array} pericias - Array de perícias
     * @returns {Object} Perícias agrupadas por atributo
     */
    agruparPorAtributo(pericias) {
        const grupos = {
            'FOR': [],
            'DES': [],
            'CON': [],
            'INT': [],
            'SAB': [],
            'CAR': []
        };

        pericias.forEach(pericia => {
            if (grupos[pericia.atributo]) {
                grupos[pericia.atributo].push(pericia);
            }
        });

        return grupos;
    }

    /**
     * Mapeia atributo para label legível
     * @param {string} atributo
     * @returns {Object} {label, emoji, cor}
     */
    obterInfoAtributo(atributo) {
        const info = {
            'FOR': { label: 'Força', emoji: '💪', cor: '#8B0000' },
            'DES': { label: 'Destreza', emoji: '🎯', cor: '#8B4513' },
            'CON': { label: 'Constituição', emoji: '❤️', cor: '#A9A9A9' },
            'INT': { label: 'Inteligência', emoji: '🧠', cor: '#4B0082' },
            'SAB': { label: 'Sabedoria', emoji: '👁️', cor: '#228B22' },
            'CAR': { label: 'Carisma', emoji: '💬', cor: '#DC143C' }
        };

        return info[atributo] || { label: 'Desconhecido', emoji: '❓', cor: '#888888' };
    }

    /**
     * Filtra perícias por termo de busca
     * @param {Array} pericias
     * @param {string} termo
     * @returns {Array}
     */
    filtrarPorBusca(pericias, termo) {
        if (!termo || termo.trim() === '') return pericias;

        const termoLower = termo.toLowerCase();
        return pericias.filter(p =>
            p.nome.toLowerCase().includes(termoLower) ||
            (p.descricao && p.descricao.toLowerCase().includes(termoLower))
        );
    }
}