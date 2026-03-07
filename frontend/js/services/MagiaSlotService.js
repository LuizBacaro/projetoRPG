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
        if (!res.ok) throw new Error('Erro ao buscar slots de magia');
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
        if (!res.ok) throw new Error('Erro ao atualizar slot de magia');
        return res.json();
    }
}