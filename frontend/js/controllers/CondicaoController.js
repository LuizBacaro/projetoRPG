/**
 * CondicaoController
 * SOLID:
 *   SRP - orquestra apenas o fluxo de condições (sem responsabilidade de UI do modal)
 *   DIP - depende das abstrações CondicaoService e ModalCondicao (global)
 */

export class CondicaoController {
    constructor() {
        this.service         = new CondicaoService();
        this.combatenteAtual = null;
    }

    /**
     * Inicializa o controller.
     * O ModalCondicao (global) cuida do próprio init via main.js.
     */
    init() {
        // Nada a inicializar aqui — ModalCondicao é instanciado globalmente
        // O bind do botão data-acao="condicao" é feito no ArenaController
    }

    /**
     * Carrega e renderiza condições do combatente ativo na arena
     */
    async carregarCondicoesDoCombatente(combatenteId) {
        this.combatenteAtual = combatenteId;
        try {
            const data = await this.service.listarDoCombatente(combatenteId);

            // Delega renderização para o ModalCondicao global
            if (typeof modalCondicaoInstance !== 'undefined') {
                modalCondicaoInstance.renderizarCondicoesAtivas(
                    data.condicoes,
                    combatenteId,
                    (cid, condId) => this._removerCondicao(cid, condId)
                );
            }
        } catch (err) {
            console.error('Erro ao carregar condições:', err);
        }
    }

    /**
     * Atualiza badges no card da ordem de iniciativa
     */
    async atualizarBadgesOrdem(cardEl, combatenteId) {
        try {
            const data = await this.service.listarDoCombatente(combatenteId);
            if (typeof modalCondicaoInstance !== 'undefined') {
                modalCondicaoInstance.renderizarBadgesOrdem(cardEl, data.condicoes);
            }
        } catch (err) {
            console.error('Erro ao atualizar badges:', err);
        }
    }

    // ── Privados 

    async _removerCondicao(combatenteId, condicaoId) {
        try {
            const data = await this.service.remover(combatenteId, condicaoId);

            if (typeof modalCondicaoInstance !== 'undefined') {
                modalCondicaoInstance.renderizarCondicoesAtivas(
                    data.condicoes,
                    combatenteId,
                    (cid, condId) => this._removerCondicao(cid, condId)
                );

                // Atualiza badge na ordem de iniciativa
                const cardOrdem = document.querySelector(
                    `.combatente-ordem-item[data-combatente-id="${combatenteId}"]`
                );
                if (cardOrdem) {
                    modalCondicaoInstance.renderizarBadgesOrdem(cardOrdem, data.condicoes);
                }
            }
        } catch (err) {
            console.error('Erro ao remover condição:', err);
        }
    }
}