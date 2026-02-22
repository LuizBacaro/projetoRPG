/**
 * CondicaoController
 * SOLID:
 *   SRP - orquestra apenas o fluxo de condições
 *   DIP - depende das abstrações CondicaoService e CondicaoUI
 */
import { CondicaoService } from '../services/CondicaoService.js';
import { CondicaoUI }      from '../ui/CondicaoUI.js';

export class CondicaoController {
    constructor() {
        this.service         = new CondicaoService();
        this.ui              = new CondicaoUI();
        this.todasCondicoes  = [];
        this.combatenteAtual = null;
    }

    async init() {
        this.todasCondicoes = await this.service.listarTodas();
        this._bindEventosBotaoCondicao();
        this._bindEventosModal();
    }

    async carregarCondicoesDoCombatente(combatenteId) {
        this.combatenteAtual = combatenteId;
        try {
            const data = await this.service.listarDoCombatente(combatenteId);
            this.ui.renderizarCondicoesAtivas(
                data.condicoes,
                combatenteId,
                (cid, condId) => this._removerCondicao(cid, condId)
            );
        } catch (err) {
            console.error('Erro ao carregar condições:', err);
        }
    }

    async atualizarBadgesOrdem(cardEl, combatenteId) {
        try {
            const data = await this.service.listarDoCombatente(combatenteId);
            this.ui.renderizarBadgesOrdem(cardEl, data.condicoes);
        } catch (err) {
            console.error('Erro ao atualizar badges:', err);
        }
    }

    // ── Privados ──────────────────────────────────────────────────────────────

    _bindEventosBotaoCondicao() {
        document.addEventListener('click', async (e) => {
            const btn = e.target.closest('[data-acao="condicao"]');
            if (!btn) return;

            const combatenteId = Number(btn.dataset.combatenteId);
            if (!combatenteId) return;

            this.combatenteAtual = combatenteId;
            await this._abrirModal(combatenteId);
        });
    }

    _bindEventosModal() {
        document.getElementById('btn-fechar-modal-condicao')
            ?.addEventListener('click', () => this.ui.fecharModal());

        document.getElementById('modal-condicao')
            ?.addEventListener('click', (e) => {
                if (e.target.id === 'modal-condicao') this.ui.fecharModal();
            });

        document.getElementById('select-condicao')
            ?.addEventListener('change', (e) => {
                this.ui.mostrarEfeitoNoModal(this.todasCondicoes, e.target.value);
            });

        document.getElementById('btn-aplicar-condicao')
            ?.addEventListener('click', () => this._aplicarCondicao());
    }

    async _abrirModal(combatenteId) {
        const data = await this.service.listarDoCombatente(combatenteId);
        this.ui.popularSelectModal(this.todasCondicoes, data.condicoes);
        this.ui.abrirModal();
    }

    async _aplicarCondicao() {
        const select     = document.getElementById('select-condicao');
        const condicaoId = Number(select?.value);
        if (!condicaoId || !this.combatenteAtual) return;

        try {
            const data = await this.service.aplicar(this.combatenteAtual, condicaoId);
            this.ui.renderizarCondicoesAtivas(
                data.condicoes,
                this.combatenteAtual,
                (cid, condId) => this._removerCondicao(cid, condId)
            );
            this.ui.fecharModal();

            const cardOrdem = document.querySelector(
                `.combatente-ordem-item[data-combatente-id="${this.combatenteAtual}"]`
            );
            if (cardOrdem) this.ui.renderizarBadgesOrdem(cardOrdem, data.condicoes);

        } catch (err) {
            console.error('Erro ao aplicar condição:', err);
        }
    }

    async _removerCondicao(combatenteId, condicaoId) {
        try {
            const data = await this.service.remover(combatenteId, condicaoId);
            this.ui.renderizarCondicoesAtivas(
                data.condicoes,
                combatenteId,
                (cid, condId) => this._removerCondicao(cid, condId)
            );

            const cardOrdem = document.querySelector(
                `.combatente-ordem-item[data-combatente-id="${combatenteId}"]`
            );
            if (cardOrdem) this.ui.renderizarBadgesOrdem(cardOrdem, data.condicoes);

        } catch (err) {
            console.error('Erro ao remover condição:', err);
        }
    }
}