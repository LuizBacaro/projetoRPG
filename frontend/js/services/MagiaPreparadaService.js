/**
 * MagiaPreparadaService.js
 * SRP: Comunicação HTTP com /magias-preparadas
 * SOLID: DIP — injetável via constructor
 */

import { getApiUrl } from '../config/api.config.js';

export class MagiaPreparadaService {
    constructor(token) {
        this.token = token || localStorage.getItem('token');
    }

    /**
     * Busca magias preparadas de um combatente
     * @param {number} combatenteId
     * @returns {Promise<Array>}
     */
    async listar(combatenteId) {
        const res = await fetch(
            getApiUrl(`/magias-preparadas/${combatenteId}`),
            { headers: { 'Authorization': `Bearer ${this.token}` } }
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }

    /**
     * Alterna magia entre usada/não-usada (lançada na arena)
     * SRP: apenas toggle — sem lógica de UI
     * @param {number} combatenteId
     * @param {number} magiaId
     * @returns {Promise<{usada: boolean}>}
     */
    async toggleUsada(combatenteId, magiaId) {
        const res = await fetch(
            getApiUrl(`/magias-preparadas/${combatenteId}/${magiaId}/usar`),
            {
                method: 'PATCH',
                headers: { 'Authorization': `Bearer ${this.token}` },
            }
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }

    /**
     * Agrupa magias preparadas por nivel_slot
     * SRP: transformação de dados, sem efeitos colaterais
     * @param {Array} preparadas - lista de MagiaPreparadaResponse
     * @returns {Object} { nivel: { preparadas: [], usadas: number, total: number } }
     */
    agruparPorNivel(preparadas) {
        const grupos = {};
        preparadas.forEach(p => {
            const n = p.nivel_slot;
            if (!grupos[n]) grupos[n] = { preparadas: [], usadas: 0, total: 0 };
            grupos[n].preparadas.push(p);
            grupos[n].total++;
            if (p.usada) grupos[n].usadas++;
        });
        return grupos;
    }
}