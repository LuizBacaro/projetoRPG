/**
 * Cálculo automático de PV/PM máximos — T20 v1.3 (padrão) e MB legado.
 * PV: cálculo local via CLASSES_MB (sem depender de API no carregamento da ficha).
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

    function classeRow(slug) {
        if (typeof window.getClasseMbRowPorSlug === 'function') {
            return window.getClasseMbRowPorSlug(String(slug || '').trim().toLowerCase());
        }
        return null;
    }

    function contribCon(val) {
        const rv = regraVersaoAtiva();
        if (window.T20RegraVersao && typeof window.T20RegraVersao.contribuicaoAtributo === 'function') {
            return window.T20RegraVersao.contribuicaoAtributo(val, rv);
        }
        const n = Number(val);
        return Number.isFinite(n) ? Math.trunc(n) : 0;
    }

    function arcanistaCaminho() {
        const el = q('f_arcanista_caminho');
        const v = el && el.value ? String(el.value).trim().toLowerCase() : '';
        return v || null;
    }

    function nivelPersonagem() {
        const n = Number(q('f_nivel') && q('f_nivel').value);
        return Number.isFinite(n) && n >= 1 ? Math.min(40, Math.floor(n)) : 1;
    }

    function attrCampo(k) {
        const el = q(`ficha${k.charAt(0).toUpperCase()}${k.slice(1)}Resumo`) || q(`f_dlg_attr_${k}`);
        const n = Number(el && el.value);
        if (Number.isFinite(n)) return n;
        return isV13() ? 0 : 10;
    }

    function conValor() {
        return attrCampo('con');
    }

    function classeSlug() {
        const sel = q('f_classe_mb');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    /** Lista multiclasse preenchida na ficha (v1.3 p.34); vazia = classe única. */
    function linhasMulticlasseV13() {
        if (!isV13() || !window.T20MulticlasseV13) return null;
        if (typeof window.T20MulticlasseV13.coletarLinhas !== 'function') return null;
        return window.T20MulticlasseV13.coletarLinhas();
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

    function formulaPvSimples(prev) {
        const lv = labelVersao();
        const conLbl = isV13() ? 'CON' : 'mod. CON';
        return `${lv}: ${prev.pv_inicial} + ${prev.contrib_niveis_extras} (níveis) + ${prev.contrib_constituicao} (${conLbl}) = ${prev.pv_max}`;
    }

    function formulaPvMulticlasse(prev) {
        if (prev.formula) return `PV multiclasse (v1.3): ${prev.formula}`;
        return `PV multiclasse (v1.3): ${prev.pv_max}`;
    }

    function previewPvClasseUnicaLocal(slug, nivel, con) {
        const row = classeRow(slug);
        if (!row) return null;
        const nv = Math.max(1, Math.min(40, Math.floor(Number(nivel) || 1)));
        const pvIni = Number(row.pv_inicial) || 8;
        const pvPn = Number(row.pv_por_nivel) || 0;
        const modCon = contribCon(con);
        const contribNiveis = Math.max(0, nv - 1) * pvPn;
        const deCon = nv * modCon;
        const pvMax = pvIni + contribNiveis + deCon;
        let pmMax = null;
        let pmPn = null;
        if (isV13() && row.pm_por_nivel != null && Number(row.pm_por_nivel) > 0) {
            pmPn = Number(row.pm_por_nivel);
            pmMax = nv * pmPn;
        }
        return {
            encontrado: true,
            pv_max: pvMax,
            pv_inicial: pvIni,
            pv_por_nivel: pvPn,
            contrib_niveis_extras: contribNiveis,
            contrib_constituicao: deCon,
            nivel: nv,
            mod_con: modCon,
            pm_max: pmMax,
            pm_por_nivel: pmPn,
        };
    }

    function previewPvMulticlasseLocal(classes, slugPrimario, con) {
        if (!Array.isArray(classes) || !classes.length) return null;
        const pri = String(slugPrimario || '').trim().toLowerCase();
        const niveisMap = {};
        classes.forEach((item) => {
            const slug = String(item && item.slug ? item.slug : '')
                .trim()
                .toLowerCase();
            if (!slug) return;
            const nv = Math.max(1, Math.min(40, Math.floor(Number(item.nivel) || 1)));
            niveisMap[slug] = (niveisMap[slug] || 0) + nv;
        });
        const slugs = Object.keys(niveisMap).sort();
        if (!slugs.length) return null;
        let base = 0;
        let totalNv = 0;
        const partes = [];
        for (const slug of slugs) {
            const nv = niveisMap[slug];
            const row = classeRow(slug);
            if (!row) return null;
            const pvIni = Number(row.pv_inicial) || 8;
            const pvPn = Number(row.pv_por_nivel) || 0;
            const primaria = slug === pri;
            const nome = row.nome || slug;
            let pvClasse;
            if (primaria) {
                pvClasse = pvIni + Math.max(0, nv - 1) * pvPn;
                partes.push(`${nome} ${pvIni}+${Math.max(0, nv - 1)}×${pvPn}=${pvClasse}`);
            } else {
                pvClasse = nv * pvPn;
                partes.push(`${nome} ${nv}×${pvPn}=${pvClasse}`);
            }
            base += pvClasse;
            totalNv += nv;
        }
        const modCon = contribCon(con);
        const deCon = totalNv * modCon;
        const pvMax = base + deCon;
        const conTxt = modCon !== 0 ? `${totalNv}×${modCon}` : `${totalNv}×CON`;
        const formula = `${partes.join(' + ')} + ${conTxt} = ${pvMax} PV`;
        return {
            encontrado: true,
            pv_max: pvMax,
            mod_con: modCon,
            contrib_constituicao: deCon,
            formula,
            nivel_total_classes: totalNv,
        };
    }

    async function previewPvViaApi(slug, mcLinhas) {
        if (mcLinhas && mcLinhas.length) {
            return regras().obterPvPreviewMulticlasse({
                classes: mcLinhas,
                slug_primario: slug,
                con_valor: conValor(),
                regraVersao: 'v13',
            });
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
        return regras().obterPvPreview(payload);
    }

    async function calcularPvMb(aplicar) {
        const slug = classeSlug();
        if (!slug) {
            return null;
        }
        const mcLinhas = linhasMulticlasseV13();
        try {
            let prev =
                mcLinhas && mcLinhas.length
                    ? previewPvMulticlasseLocal(mcLinhas, slug, conValor())
                    : previewPvClasseUnicaLocal(slug, nivelPersonagem(), conValor());

            if (!prev || !prev.encontrado || prev.pv_max == null) {
                prev = await previewPvViaApi(slug, mcLinhas);
            }

            if (!prev || !prev.encontrado || prev.pv_max == null) {
                return null;
            }

            const formula =
                mcLinhas && mcLinhas.length ? formulaPvMulticlasse(prev) : formulaPvSimples(prev);

            const pvBd = q('fichaPvBreakdown');
            if (pvBd) {
                pvBd.dataset.t20PvFormula = formula;
                pvBd.textContent = formula;
            }

            const pmBd = q('fichaPmBreakdown');
            if (pmBd) {
                if (isV13() && window.T20MulticlasseV13) {
                    await window.T20MulticlasseV13.atualizarPmSugerido(!!aplicar);
                } else if (!mcLinhas && prev.pm_max != null) {
                    const pmTxt = `PM conj. máx. (regra ${labelVersao()}): ${prev.pm_max}`;
                    pmBd.dataset.t20PmFormula = pmTxt;
                    pmBd.textContent = pmTxt;
                    if (aplicar) {
                        const parPm = lerPar('fichaPm');
                        escreverPar('fichaPm', Math.min(parPm.atual, prev.pm_max), prev.pm_max);
                    }
                }
            }

            if (aplicar) {
                const parPv = lerPar('fichaPv');
                const novoMaxPv = prev.pv_max;
                const estavaCheio = parPv.atual >= parPv.max;
                const novoAtual = estavaCheio ? novoMaxPv : Math.min(parPv.atual, novoMaxPv);
                escreverPar('fichaPv', novoAtual, novoMaxPv);
                if (!isV13() && prev.pm_max != null) {
                    const parPm = lerPar('fichaPm');
                    escreverPar('fichaPm', Math.min(parPm.atual, prev.pm_max), prev.pm_max);
                }
            }
            return prev;
        } catch (e) {
            console.warn('[t20-progressao-pv]', e);
            return null;
        }
    }

    async function atualizarVitaisSugeridos() {
        const slug = classeSlug();
        if (!slug) return null;
        return calcularPvMb(true);
    }

    window.t20CalcularPvMb = calcularPvMb;
    window.t20AtualizarVitaisSugeridos = atualizarVitaisSugeridos;
})();
