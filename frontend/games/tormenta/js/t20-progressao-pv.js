/**
 * Cálculo de PV/PM máximos (API `/tormenta/regras/pv-preview`) — MB e v1.3.
 */
(function () {
    const regras = () => new TormentaRegrasService();

    function q(id) {
        return document.getElementById(id);
    }

    function regraVersaoAtiva() {
        if (typeof window.getRegraVersaoAtiva === 'function') {
            return window.getRegraVersaoAtiva();
        }
        return 'mb';
    }

    function labelVersao() {
        if (window.T20RegraVersao && typeof window.T20RegraVersao.labelVersaoCurta === 'function') {
            return window.T20RegraVersao.labelVersaoCurta(regraVersaoAtiva());
        }
        return regraVersaoAtiva() === 'v13' ? 'v1.3' : 'MB';
    }

    function isV13() {
        return window.T20RegraVersao && window.T20RegraVersao.isV13(regraVersaoAtiva());
    }

    function arcanistaCaminho() {
        const el = q('f_arcanista_caminho');
        const v = el && el.value ? String(el.value).trim().toLowerCase() : '';
        return v || null;
    }

    function nivelPersonagem() {
        const n = Number(q('f_nivel') && q('f_nivel').value);
        return Number.isFinite(n) && n >= 1 ? n : 1;
    }

    function attrCampo(k) {
        const el = q(`ficha${k.charAt(0).toUpperCase()}${k.slice(1)}Resumo`) || q(`f_dlg_attr_${k}`);
        const n = Number(el && el.value);
        return Number.isFinite(n) ? n : 10;
    }

    function conValor() {
        return attrCampo('con');
    }

    function classeSlug() {
        const sel = q('f_classe_mb');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    function lerPar(id) {
        const el = q(id);
        if (!el) return { atual: id === 'fichaPm' ? 0 : 1, max: id === 'fichaPm' ? 0 : 1 };
        const t = String(el.textContent || '').replace(/\s/g, '');
        const m = t.match(/^(\d+)\s*\/\s*(\d+)/);
        if (m) return { atual: parseInt(m[1], 10) || 0, max: parseInt(m[2], 10) || 0 };
        return { atual: id === 'fichaPm' ? 0 : 1, max: id === 'fichaPm' ? 0 : 1 };
    }

    function escreverPar(id, atual, maximo) {
        if (typeof window.t20WritePairSlash === 'function') {
            window.t20WritePairSlash(id, atual, maximo);
        } else {
            const el = q(id);
            if (el) el.textContent = `${atual} / ${maximo}`;
        }
    }

    function formulaPvPm(prev) {
        const lv = labelVersao();
        const conLbl = isV13() ? 'CON' : 'mod. CON';
        let pv =
            `${lv}: ${prev.pv_inicial} + ${prev.contrib_niveis_extras} (níveis) + ${prev.contrib_constituicao} (${conLbl}) = ${prev.pv_max}`;
        if (prev.pm_max != null && prev.pm_por_nivel != null) {
            pv += ` · PM: ${prev.nivel} × ${prev.pm_por_nivel} = ${prev.pm_max}`;
        } else if (prev.pm_max != null) {
            pv += ` · PM máx.: ${prev.pm_max}`;
        }
        return pv;
    }

    function atualizarBotaoCalcularPv() {
        const btn = q('btnT20CalcularPvMb');
        if (!btn) return;
        const lv = labelVersao();
        btn.textContent = `Calcular PV (${lv})`;
        btn.title = `Calcular PV máximos (${lv}: classe + nível + CON)`;
    }

    async function calcularPvMb(aplicar) {
        const slug = classeSlug();
        if (!slug) {
            alert('Selecione uma classe em Editar ficha para calcular PV.');
            return null;
        }
        const rv = regraVersaoAtiva();
        const payload = {
            classe_slug: slug,
            nivel: nivelPersonagem(),
            con_valor: conValor(),
            regraVersao: rv,
            for_valor: attrCampo('for'),
            des_valor: attrCampo('des'),
            int_valor: attrCampo('int'),
            sab_valor: attrCampo('sab'),
            car_valor: attrCampo('car'),
        };
        if (isV13() && slug === 'arcanista' && arcanistaCaminho()) {
            payload.arcanista_caminho = arcanistaCaminho();
        }
        try {
            const prev = await regras().obterPvPreview(payload);
            if (!prev.encontrado || prev.pv_max == null) {
                alert('Classe não encontrada para cálculo de PV.');
                return null;
            }
            const formula = formulaPvPm(prev);
            const pvBd = q('fichaPvBreakdown');
            if (pvBd) {
                pvBd.dataset.t20PvFormula = formula;
                pvBd.textContent = formula;
            }
            const pmBd = q('fichaPmBreakdown');
            if (pmBd && prev.pm_max != null) {
                const pmTxt = isV13()
                    ? `Sugestão: ${prev.nivel} × ${prev.pm_por_nivel} = ${prev.pm_max} PM`
                    : `PM conj. máx. (regra ${labelVersao()}): ${prev.pm_max}`;
                pmBd.dataset.t20PmFormula = pmTxt;
                pmBd.textContent = pmTxt;
            }
            if (aplicar) {
                const parPv = lerPar('fichaPv');
                const novoMaxPv = prev.pv_max;
                escreverPar('fichaPv', Math.min(parPv.atual, novoMaxPv), novoMaxPv);
                if (prev.pm_max != null) {
                    const parPm = lerPar('fichaPm');
                    const novoMaxPm = prev.pm_max;
                    escreverPar('fichaPm', Math.min(parPm.atual, novoMaxPm), novoMaxPm);
                }
            }
            return prev;
        } catch (e) {
            alert(e.message || 'Erro ao calcular PV.');
            return null;
        }
    }

    async function atualizarVitaisSugeridos() {
        const slug = classeSlug();
        if (!slug) return null;
        return calcularPvMb(false);
    }

    function init() {
        atualizarBotaoCalcularPv();
        const btn = q('btnT20CalcularPvMb');
        if (btn) btn.addEventListener('click', () => calcularPvMb(true));
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.t20CalcularPvMb = calcularPvMb;
    window.t20AtualizarVitaisSugeridos = atualizarVitaisSugeridos;
    window.t20AtualizarBotaoCalcularPv = atualizarBotaoCalcularPv;
})();
