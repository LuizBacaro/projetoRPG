/**
 * Adapta MagiaPreparadaService (3.5) para conjuração 5e (lista em ficha_json).
 */
import { Dnd5eConjuracaoFichaService } from './Dnd5eConjuracaoFichaService.js';

export class Dnd5eMagiaPreparadaAdapter {
    constructor(token) {
        this.conjuracao = new Dnd5eConjuracaoFichaService(token);
        this._estado = null;
    }

    async listar(personagemId) {
        const estado = await this.conjuracao.obter(personagemId);
        this._estado = estado;
        return (estado.magias_preparadas_ids || []).map((magiaId) => ({
            magia_id: Number(magiaId),
            quantidade: 1,
            nivel_slot: 0,
            usos_realizados: 0,
        }));
    }

    async preparar(personagemId, payload) {
        const estado = this._estado || (await this.conjuracao.obter(personagemId));
        const ids = [...(estado.magias_preparadas_ids || [])].map(Number);
        const magiaId = Number(payload?.magia_id);
        const qty = Math.max(0, Number(payload?.quantidade ?? 1));

        let next;
        if (qty <= 0) {
            next = ids.filter((id) => id !== magiaId);
        } else if (!ids.includes(magiaId)) {
            next = [...ids, magiaId];
        } else {
            next = ids;
        }

        const atualizado = await this.conjuracao.preparar(personagemId, next);
        this._estado = atualizado;
        window.__dnd5eConjuracaoEstado = atualizado;
        return { magia_id: magiaId, quantidade: qty > 0 ? 1 : 0 };
    }

    async desmarcar(personagemId, magiaId) {
        const estado = await this.conjuracao.obter(personagemId);
        const next = (estado.magias_preparadas_ids || [])
            .map(Number)
            .filter((id) => id !== Number(magiaId));
        const atualizado = await this.conjuracao.preparar(personagemId, next);
        this._estado = atualizado;
        window.__dnd5eConjuracaoEstado = atualizado;
        return true;
    }

    async descansoLongo(personagemId) {
        const res = await this.conjuracao.descansoLongo(personagemId);
        this._estado = res.estado || res;
        window.__dnd5eConjuracaoEstado = this._estado;
        return res;
    }
}
