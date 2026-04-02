/*
   MagiaSlotService.js
   SRP: comunicação HTTP exclusivamente para slots de magia
   ✅ CORRIGIDO: usa import de api.config em vez de window.getApiUrl
*/

import { getApiUrl } from '../config/api.config.js';

export class MagiaSlotService {

    _headers() {
        const h = { 'Content-Type': 'application/json' };
        // Token via localStorage (padrão do projeto)
        const token = localStorage.getItem('token');
        if (token) h['Authorization'] = 'Bearer ' + token;
        return h;
    }

    async _buildHttpError(res, contexto) {
        let detalhe = '';
        try {
            const data = await res.clone().json();
            if (data && typeof data.detail === 'string' && data.detail.trim()) {
                detalhe = data.detail.trim();
            }
        } catch (_) {
            // Sem JSON válido; tenta texto bruto abaixo.
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
     * Busca todos os slots de magia de um combatente
     * @param {number} combatenteId
     * @returns {Promise<Array>}
     */
    async listarPorCombatente(combatenteId) {
        const res = await fetch(
            getApiUrl('/magias_slots/?combatente_id=' + combatenteId),
            { headers: this._headers() }
        );
        if (!res.ok) {
            throw await this._buildHttpError(
                res,
                `Erro ao buscar slots de magia do combatente #${combatenteId}`
            );
        }
        return res.json();
    }

    /**
     * Persiste/atualiza todos os slots de magia de um combatente
     * @param {number} combatenteId
     * @param {Array} slots
     * @returns {Promise<Array>}
     */
    async salvarPorCombatente(combatenteId, slots) {
        const payload = Array.isArray(slots)
            ? slots.map((slot) => ({
                nivel: Number(slot?.nivel || 0),
                total: Math.max(0, Number(slot?.total || 0)),
                usados: Math.max(0, Number(slot?.usados || 0)),
            }))
            : [];

        const res = await fetch(
            getApiUrl('/combatentes/' + combatenteId + '/magias'),
            {
                method: 'PUT',
                headers: this._headers(),
                body: JSON.stringify({ slots: payload }),
            }
        );
        if (!res.ok) {
            throw await this._buildHttpError(
                res,
                `Erro ao salvar slots de magia do combatente #${combatenteId}`
            );
        }
        return res.json();
    }

    /**
     * Atualiza quantidade de slots usados
     * @param {number} slotId
     * @param {number} usados
     * @returns {Promise<Object>}
     */
    async atualizarUsados(slotId, usados) {
        const res = await fetch(
            getApiUrl('/magias_slots/' + slotId + '/usados'),
            {
                method:  'PATCH',
                headers: this._headers(),
                body:    JSON.stringify({ usados: usados })
            }
        );
        if (!res.ok) {
            throw await this._buildHttpError(
                res,
                `Erro ao atualizar slot #${slotId} para ${usados} usados`
            );
        }
        return res.json();
    }
}