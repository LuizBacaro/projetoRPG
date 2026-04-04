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

    async preparar(combatenteId, payload) {
        const res = await fetch(
            getApiUrl(`/magias-preparadas/${combatenteId}`),
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            }
        );
        if (!res.ok) {
            throw await this._buildHttpError(
                res,
                `Erro ao preparar magia para o combatente #${combatenteId}`
            );
        }
        return res.json();
    }

    async descansoLongo(combatenteId, confirmar = true) {
        const res = await fetch(
            getApiUrl(`/magias-preparadas/${combatenteId}/descanso`),
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ confirmar: !!confirmar }),
            }
        );
        if (!res.ok) {
            throw await this._buildHttpError(
                res,
                `Erro ao realizar descanso longo do combatente #${combatenteId}`
            );
        }
        return res.json();
    }

    async desmarcar(combatenteId, magiaId) {
        const res = await fetch(
            getApiUrl(`/magias-preparadas/${combatenteId}/${magiaId}`),
            {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${this.token}` },
            }
        );
        if (!res.ok) {
            throw await this._buildHttpError(
                res,
                `Erro ao desmarcar magia #${magiaId} do combatente #${combatenteId}`
            );
        }
        return true;
    }

    /**
     * Alterna magia entre usada/não-usada (lançada na arena)
     * SRP: apenas toggle — sem lógica de UI
     * @param {number} combatenteId
     * @param {number} magiaId
     * @returns {Promise<{usada: boolean}>}
     */
    async toggleUsada(combatenteId, magiaId, action = null) {
        const sufixo = action ? `?action=${encodeURIComponent(action)}` : '';
        const res = await fetch(
            getApiUrl(`/magias-preparadas/${combatenteId}/${magiaId}/usar${sufixo}`),
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

    _expandirPreparadas(preparadas = []) {
        return (Array.isArray(preparadas) ? preparadas : []).flatMap((registro) => {
            const quantidade = Math.max(1, Number(registro?.quantidade || 1));
            const usosRealizados = Math.max(
                0,
                Math.min(quantidade, Number(registro?.usos_realizados ?? (registro?.usada ? 1 : 0) ?? 0))
            );

            return Array.from({ length: quantidade }, (_, index) => ({
                ...registro,
                quantidade,
                usos_realizados: usosRealizados,
                _instanceIndex: index + 1,
                _instanceTotal: quantidade,
                usada: index < usosRealizados,
            }));
        });
    }

    /**
     * Agrupa magias preparadas por nivel_slot
     * SRP: transformação de dados, sem efeitos colaterais
     * @param {Array} preparadas - lista de MagiaPreparadaResponse
     * @returns {Object} { nivel: { preparadas: [], usadas: number, total: number } }
     */
    agruparPorNivel(preparadas, slots = []) {
        const grupos = {};
        const mapaSlots = new Map(
            (Array.isArray(slots) ? slots : []).map((slot) => [
                Number(slot?.nivel || 0),
                Math.max(0, Number(slot?.total || 0)),
            ])
        );

        this._expandirPreparadas(preparadas).forEach((p) => {
            const n = Number(p?.nivel_slot || p?.magia_nivel || 0);
            if (!grupos[n]) grupos[n] = { preparadas: [], usadas: 0, total: 0, preparadasCount: 0 };
            grupos[n].preparadas.push(p);
            grupos[n].preparadasCount += 1;
            if (p.usada) grupos[n].usadas += 1;
        });

        Object.keys(grupos).forEach((nivelKey) => {
            const nivel = Number(nivelKey);
            const grupo = grupos[nivel];
            const totalSlots = Math.max(mapaSlots.get(nivel) || 0, grupo.preparadasCount || 0);
            grupo.total = totalSlots;
            grupo.disponiveis = Math.max(totalSlots - grupo.usadas, 0);
        });

        return grupos;
    }
}