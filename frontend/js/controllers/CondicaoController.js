/**
 * CondicaoController
 * SOLID:
 *   SRP - orquestra apenas o fluxo de condições
 *   DIP - usa CondicaoService global e ModalCondicao global
 */
export class CondicaoController {
    constructor() {
        this.service         = new CondicaoService('/api');
        this.combatenteAtual = null;
    }

    init() {
    }

    async carregarCondicoesDoCombatente(combatenteId) {
        this.combatenteAtual = combatenteId;
        try {
            const data = await this.service.listarDoCombatente(combatenteId);
            
            if (typeof modalCondicaoInstance !== 'undefined') {
                // ✅ Passar callback correto para onRemover
                modalCondicaoInstance.renderizarCondicoesAtivas(
                    data.condicoes,
                    combatenteId,
                    (cid, condId) => this._removerCondicao(cid, condId)
                );
            }
        } catch (err) {
            console.error('❌ Erro ao carregar condições:', err);
        }
    }

    async atualizarBadgesOrdem(cardEl, combatenteId) {
        try {
            const data = await this.service.listarDoCombatente(combatenteId);
            if (typeof modalCondicaoInstance !== 'undefined') {
                modalCondicaoInstance.renderizarBadgesOrdem(cardEl, data.condicoes);
            }
        } catch (err) {
            console.error('❌ Erro ao atualizar badges:', err);
        }
    }

    // ✅ REFATORADO: _removerCondicao com async/await
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
            
            if (typeof Toast !== 'undefined') {
                Toast.success('✅ Condição removida!');
            }
        } catch (err) {
            console.error('❌ Erro ao remover condição:', err);
            if (typeof Toast !== 'undefined') {
                Toast.error(`Erro ao remover condição: ${err.message}`);
            }
        }
    }
}