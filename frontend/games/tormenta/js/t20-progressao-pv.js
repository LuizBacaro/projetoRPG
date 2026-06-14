/**
 * Cálculo de PV máximos MB (API `/tormenta/regras/pv-preview`).
 */
(function () {
    const regras = () => new TormentaRegrasService();

    function q(id) {
        return document.getElementById(id);
    }

    function nivelPersonagem() {
        const n = Number(q('f_nivel') && q('f_nivel').value);
        return Number.isFinite(n) && n >= 1 ? n : 1;
    }

    function conValor() {
        const el = q('fichaConResumo') || q('f_dlg_attr_con');
        const n = Number(el && el.value);
        return Number.isFinite(n) ? n : 10;
    }

    function classeSlug() {
        const sel = q('f_classe_mb');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    function lerParPv() {
        const el = q('fichaPv');
        if (!el) return { atual: 1, max: 1 };
        const t = String(el.textContent || '').replace(/\s/g, '');
        const m = t.match(/^(\d+)\s*\/\s*(\d+)/);
        if (m) return { atual: parseInt(m[1], 10) || 1, max: parseInt(m[2], 10) || 1 };
        return { atual: 1, max: 1 };
    }

    function escreverParPv(atual, maximo) {
        if (typeof window.t20WritePairSlash === 'function') {
            window.t20WritePairSlash('fichaPv', atual, maximo);
        } else {
            const el = q('fichaPv');
            if (el) el.textContent = `${atual} / ${maximo}`;
        }
        const bd = q('fichaPvBreakdown');
        if (bd && bd.dataset && bd.dataset.t20PvFormula) {
            bd.textContent = bd.dataset.t20PvFormula;
        }
    }

    async function calcularPvMb(aplicar) {
        const slug = classeSlug();
        if (!slug) {
            alert('Selecione uma classe MB em Editar ficha para calcular PV.');
            return null;
        }
        try {
            const prev = await regras().obterPvPreview({
                classe_slug: slug,
                nivel: nivelPersonagem(),
                con_valor: conValor(),
            });
            if (!prev.encontrado || prev.pv_max == null) {
                alert('Classe MB não encontrada para cálculo de PV.');
                return null;
            }
            const formula = `MB: ${prev.pv_inicial} + ${prev.contrib_niveis_extras} (níveis) + ${prev.contrib_constituicao} (CON) = ${prev.pv_max}`;
            const bd = q('fichaPvBreakdown');
            if (bd) {
                bd.dataset.t20PvFormula = formula;
                bd.textContent = formula;
            }
            if (aplicar) {
                const par = lerParPv();
                const novoMax = prev.pv_max;
                const novoAtual = Math.min(par.atual, novoMax);
                escreverParPv(novoAtual, novoMax);
            }
            return prev;
        } catch (e) {
            alert(e.message || 'Erro ao calcular PV MB.');
            return null;
        }
    }

    function init() {
        const btn = q('btnT20CalcularPvMb');
        if (!btn) return;
        btn.addEventListener('click', () => calcularPvMb(true));
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.t20CalcularPvMb = calcularPvMb;
})();
