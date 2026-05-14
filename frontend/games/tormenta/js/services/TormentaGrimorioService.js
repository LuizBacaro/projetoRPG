/**
 * Grimório Tormenta 20 — catálogo MB (`/tormenta/regras/*`) + vínculos por personagem.
 * Usa `TormentaPersonagemService` e `TormentaRegrasService` (JWT + getApiUrl).
 */
class TormentaGrimorioService {
    constructor() {
        this._personagem = new TormentaPersonagemService();
        this._regras = new TormentaRegrasService();
    }

    obterConjuracaoMb() {
        return this._regras.obterConjuracaoMb();
    }

    listarCatalogoMb(params = {}) {
        return this._regras.listarMagiasCatalogo(params);
    }

    listarVinculos(personagemId) {
        return this._personagem.listarMagias(personagemId);
    }

    adicionarVinculo(personagemId, payload) {
        return this._personagem.adicionarMagia(personagemId, payload);
    }

    removerVinculo(personagemId, vinculoId) {
        return this._personagem.removerMagia(personagemId, vinculoId);
    }

    migrarMagiasTextoDoJson(personagemId) {
        return this._personagem.migrarMagiasDoJson(personagemId);
    }

    obterPersonagem(personagemId) {
        return this._personagem.obter(personagemId);
    }
}
