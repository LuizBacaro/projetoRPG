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
        this._cacheCondicoes = new Map();
        this._cacheTtlMs     = 2000;
    }

    init() {
    }

    _chaveCacheCombatente(combatenteId) {
        return Number(combatenteId);
    }

    _atualizarCacheCondicoes(combatenteId, data) {
        const chave = this._chaveCacheCombatente(combatenteId);
        this._cacheCondicoes.set(chave, {
            timestamp: Date.now(),
            data,
        });
    }

    _invalidarCacheCondicoes(combatenteId) {
        if (combatenteId === undefined || combatenteId === null) {
            this._cacheCondicoes.clear();
            return;
        }
        this._cacheCondicoes.delete(this._chaveCacheCombatente(combatenteId));
    }

    async _obterCondicoesCombatente(combatenteId, opcoes = {}) {
        const usarCache = opcoes.usarCache !== false;
        const forcarRefresh = opcoes.forcarRefresh === true;
        const chave = this._chaveCacheCombatente(combatenteId);

        if (usarCache && !forcarRefresh) {
            const entradaCache = this._cacheCondicoes.get(chave);
            if (entradaCache && (Date.now() - entradaCache.timestamp) <= this._cacheTtlMs) {
                return entradaCache.data;
            }
        }

        const data = await this.service.listarDoCombatente(combatenteId);
        this._atualizarCacheCondicoes(combatenteId, data);
        return data;
    }

    async carregarCondicoesDoCombatente(combatenteId, opcoes = {}) {
        this.combatenteAtual = combatenteId;
        try {
            const data = await this._obterCondicoesCombatente(combatenteId, {
                usarCache: opcoes.usarCache !== false,
                forcarRefresh: opcoes.forcarRefresh === true,
            });
            
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

    async atualizarBadgesOrdem(cardEl, combatenteId, opcoes = {}) {
        try {
            const data = await this._obterCondicoesCombatente(combatenteId, {
                usarCache: opcoes.usarCache !== false,
                forcarRefresh: opcoes.forcarRefresh === true,
            });
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
            this._atualizarCacheCondicoes(combatenteId, data);
            
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
            this._invalidarCacheCondicoes(combatenteId);
            console.error('❌ Erro ao remover condição:', err);
            if (typeof Toast !== 'undefined') {
                Toast.error(`Erro ao remover condição: ${err.message}`);
            }
        }
    }
}