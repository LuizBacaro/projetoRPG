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

    async _buildHttpError(res, contexto) {
        let detalhe = '';
        try {
            const data = await res.clone().json();
            if (data && typeof data.detail === 'string' && data.detail.trim()) {
                detalhe = data.detail.trim();
            }
        } catch (_) {
            // Sem JSON válido.
        }

        if (!detalhe) {
            try {
                const txt = (await res.text()).trim();
                if (txt) detalhe = txt;
            } catch (_) {
                // Ignora erro de leitura.
            }
        }

        return new Error(
            detalhe
                ? `${contexto} (HTTP ${res.status}): ${detalhe}`
                : `${contexto} (HTTP ${res.status})`
        );
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
        if (!res.ok) {
            throw await this._buildHttpError(
                res,
                `Erro ao listar magias preparadas do combatente #${combatenteId}`
            );
        }
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
        if (!res.ok) {
            throw await this._buildHttpError(
                res,
                `Erro ao alternar uso da magia #${magiaId} do combatente #${combatenteId}`
            );
        }
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