/**
 * Percepção passiva v1.3/MB — 10 + bônus total de Percepção (API calcular-bonus).
 */
(function (global) {
    'use strict';

    let debounce = null;

    function q(id) {
        return document.getElementById(id);
    }

    function linhaPercepcao() {
        const R = global.T20PericiasRolador;
        if (!R) return null;
        return R.encontrarLinhaPorSlug('percepcao') || R.encontrarLinhaPorNome('Percepção');
    }

    function escreverUi(passiva, bonus, pen) {
        const val = q('fichaPercepcaoPassiva');
        const bd = q('fichaPercepcaoPassivaBreakdown');
        const inline = q('fichaPercepcaoPassivaInline');
        if (passiva == null) {
            if (val) val.textContent = '—';
            if (bd) bd.textContent = 'Marque Percepção na tabela';
            if (inline) inline.textContent = '';
            return;
        }
        if (val) val.textContent = String(passiva);
        let txt =
            bonus != null ? `10 ${bonus >= 0 ? '+' : ''}${bonus} (Percepção)` : '10 + — (Percepção)';
        if (pen > 0) txt += ` · pen. armadura −${pen}`;
        if (bd) bd.textContent = txt;
        if (inline) inline.textContent = `Percepção passiva: ${passiva} (${txt})`;
    }

    async function calcularPassiva() {
        const tr = linhaPercepcao();
        if (!tr || !global.T20PericiasRolador) {
            escreverUi(null);
            return null;
        }
        try {
            const calc = await global.T20PericiasRolador.calcularBonusLinha(tr);
            const pp =
                calc.percepcao_passiva != null
                    ? calc.percepcao_passiva
                    : 10 + (calc.bonus_total != null ? calc.bonus_total : 0);
            escreverUi(pp, calc.bonus_total, calc.penalidade_armadura_aplicada || 0);
            return pp;
        } catch (_e) {
            escreverUi(null);
            return null;
        }
    }

    function agendarAtualizacao() {
        if (debounce) clearTimeout(debounce);
        debounce = setTimeout(() => {
            debounce = null;
            void calcularPassiva();
        }, 280);
    }

    function bindOnce() {
        if (global.__t20PercepcaoPassivaBound) return;
        global.__t20PercepcaoPassivaBound = true;
        const tb = document.querySelector('#tblPericias tbody');
        if (tb) {
            tb.addEventListener('change', () => agendarAtualizacao());
            tb.addEventListener('input', () => agendarAtualizacao());
        }
        ['f_nivel', 'f_raca_select', 'fichaSabResumo'].forEach((id) => {
            q(id)?.addEventListener('change', () => agendarAtualizacao());
            q(id)?.addEventListener('input', () => agendarAtualizacao());
        });
    }

    function init() {
        bindOnce();
        agendarAtualizacao();
    }

    global.t20AtualizarPercepcaoPassiva = calcularPassiva;
    global.T20PercepcaoPassiva = {
        init,
        calcularPassiva,
        agendarAtualizacao,
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(typeof window !== 'undefined' ? window : globalThis);
