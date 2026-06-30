/**
 * Dinheiro inicial v1.3 — Tabela 3-1 para personagens acima do 1º nível.
 */
(function (global) {
    'use strict';

    function q(id) {
        return document.getElementById(id);
    }

    function isV13() {
        return (
            global.T20RegraVersao &&
            typeof global.getRegraVersaoAtiva === 'function' &&
            global.T20RegraVersao.isV13(global.getRegraVersaoAtiva())
        );
    }

    function nivelFicha() {
        const n = q('f_nivel') && parseInt(String(q('f_nivel').value || '1'), 10);
        return Number.isFinite(n) && n > 0 ? n : 1;
    }

    function nivelCadastro() {
        const n = q('cadNivel') && parseInt(String(q('cadNivel').value || '1'), 10);
        return Number.isFinite(n) && n > 0 ? n : 1;
    }

    function formatarValor(data) {
        if (!data) return '—';
        if (data.tipo === '4d6') return '4d6 T$ (role no kit nv 1)';
        if (data.valor != null) return `T$ ${Number(data.valor).toLocaleString('pt-BR')}`;
        return '—';
    }

    async function obterDinheiro(nivel) {
        return new TormentaRegrasService().obterDinheiroInicial({
            nivel,
            regraVersao: 'v13',
        });
    }

    async function atualizarUiFicha() {
        const wrap = q('wrapDinheiroTabelaV13');
        if (!wrap) return;
        const v13 = isV13();
        const nv = nivelFicha();
        wrap.style.display = v13 && nv > 1 ? '' : 'none';
        if (!v13 || nv <= 1) return;
        const lbl = q('t20DinheiroTabelaValor');
        if (lbl) lbl.textContent = 'Carregando…';
        try {
            const data = await obterDinheiro(nv);
            global.__t20DinheiroTabelaV13 = data;
            if (lbl) lbl.textContent = formatarValor(data);
        } catch (_e) {
            if (lbl) lbl.textContent = 'Erro ao carregar Tabela 3-1.';
        }
    }

    async function atualizarUiWizard() {
        const wrapKit = q('cadWrapKitNv1');
        const wrapTab = q('cadWrapDinheiroTabela');
        const hint = q('cadWizardStepKitHint');
        if (!wrapTab) return;
        const v13 =
            global.T20DashWizardV13 &&
            typeof global.T20DashWizardV13.isWizardAtivo === 'function' &&
            global.T20DashWizardV13.isWizardAtivo();
        const nv = nivelCadastro();
        const showTab = v13 && nv > 1;
        if (wrapKit) wrapKit.style.display = v13 && nv <= 1 ? '' : 'none';
        wrapTab.style.display = showTab ? '' : 'none';
        if (hint) {
            hint.textContent =
                nv <= 1
                    ? 'Kit inicial (nível 1) — p.140 v1.3. Mochila, saco de dormir e traje são adicionados automaticamente.'
                    : 'Personagens acima do 1º nível recebem T$ da Tabela 3-1 (v1.3).';
        }
        if (!showTab) return;
        const lbl = q('cadDinheiroTabelaValor');
        if (lbl) lbl.textContent = 'Carregando…';
        try {
            const data = await obterDinheiro(nv);
            global.__cadDinheiroTabela = data;
            if (lbl) lbl.textContent = formatarValor(data);
        } catch (_e) {
            if (lbl) lbl.textContent = 'Erro ao carregar Tabela 3-1.';
        }
    }

    function aplicarNaFicha() {
        const data = global.__t20DinheiroTabelaV13;
        if (!data || data.tipo !== 'fixo' || data.valor == null) return false;
        if (typeof global.t20AplicarDinheiroDoJson === 'function') {
            const prev = global.__t20DinheiroPersist || { pc: 0, pp: 0, po: 0, pl: 0 };
            global.t20AplicarDinheiroDoJson({ ...prev, pp: data.valor }, {});
        }
        if (typeof Toast !== 'undefined') {
            Toast.success(`T$ ${data.valor} aplicados (Tabela 3-1, nv ${data.nivel}).`);
        }
        return true;
    }

    function aplicarNoWizard() {
        const data = global.__cadDinheiroTabela;
        if (!data || data.tipo !== 'fixo' || data.valor == null) return false;
        if (!global.__cadKitInicial) global.__cadKitInicial = {};
        global.__cadKitInicial.dinheiro_tabela_pp = data.valor;
        const lbl = q('cadDinheiroTabelaValor');
        if (lbl) lbl.textContent = `${formatarValor(data)} — aplicado`;
        if (global.T20DashWizardV13 && global.T20DashWizardV13.renderResumo) {
            global.T20DashWizardV13.renderResumo();
        }
        return true;
    }

    function lerDinheiroWizardPayload(nivel) {
        const nv = Number(nivel);
        if (!Number.isFinite(nv) || nv <= 1) return null;
        const v =
            global.__cadKitInicial &&
            global.__cadKitInicial.dinheiro_tabela_pp != null
                ? global.__cadKitInicial.dinheiro_tabela_pp
                : global.__cadDinheiroTabela && global.__cadDinheiroTabela.valor;
        if (v == null) return null;
        return { pc: 0, pp: Number(v), po: 0, pl: 0 };
    }

    function bindOnce() {
        if (global.__t20DinheiroTabelaBound) return;
        global.__t20DinheiroTabelaBound = true;
        q('btnAplicarDinheiroTabela')?.addEventListener('click', () => aplicarNaFicha());
        q('cadBtnAplicarDinheiroTabela')?.addEventListener('click', () => {
            aplicarNoWizard();
            if (typeof Toast !== 'undefined') {
                const v = global.__cadKitInicial && global.__cadKitInicial.dinheiro_tabela_pp;
                Toast.success(v != null ? `T$ ${v} marcados para a ficha.` : 'Dinheiro aplicado.');
            }
        });
        q('f_nivel')?.addEventListener('change', () => void atualizarUiFicha());
        q('cadNivel')?.addEventListener('change', () => void atualizarUiWizard());
    }

    function init() {
        bindOnce();
        void atualizarUiFicha();
    }

    global.T20DinheiroTabelaV13 = {
        init,
        obterDinheiro,
        formatarValor,
        atualizarUiFicha,
        atualizarUiWizard,
        aplicarNaFicha,
        aplicarNoWizard,
        lerDinheiroWizardPayload,
    };
})(typeof window !== 'undefined' ? window : globalThis);
