/**
 * CondicaoController
 * SOLID:
 *   SRP - orquestra apenas o fluxo de condições
 *   DIP - usa CondicaoService global e ModalCondicao global
 */
export class CondicaoController {
    constructor() {
        // CondicaoService é global — carregado via <script> no index.html
        this.service         = new CondicaoService('/api');
        this.combatenteAtual = null;
    }

    init() {
        // ModalCondicao cuida do próprio init — nada a fazer aqui
        console.log('✅ CondicaoController inicializado');
    }

    async carregarCondicoesDoCombatente(combatenteId) {
        this.combatenteAtual = combatenteId;
        try {
            const data = await this.service.listarDoCombatente(combatenteId);
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

    async _removerCondicao(combatenteId, condicaoId) {
        try {
            const data = await this.service.remover(combatenteId, condicaoId);
            if (typeof modalCondicaoInstance !== 'undefined') {
                modalCondicaoInstance.renderizarCondicoesAtivas(
                    data.condicoes,
                    combatenteId,
                    (cid, condId) => this._removerCondicao(cid, condId)
                );
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