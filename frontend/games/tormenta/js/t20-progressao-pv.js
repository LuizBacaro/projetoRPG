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

    function slugRacaFicha() {
        const el = q('f_raca_select');
        const v = el && el.value ? String(el.value).trim().toLowerCase() : '';
        return v && v !== '__livre__' ? v : '';
    }

    function formulaPvSimples(prev) {
        const lv = labelVersao();
        const conLbl = isV13() ? 'CON' : 'mod. CON';
        let s = `${lv}: ${prev.pv_inicial} + ${prev.contrib_niveis_extras} (níveis) + ${prev.contrib_constituicao} (${conLbl})`;
        if (prev.contrib_pv_racial) s += ` + ${prev.contrib_pv_racial} (raça)`;
        s += ` = ${prev.pv_max}`;
        return s;
    }

    function formulaPvMulticlasse(prev) {
        if (prev.formula) return `PV multiclasse (v1.3): ${prev.formula}`;
        return `PV multiclasse (v1.3): ${prev.pv_max}`;
    }

    function contribPvPmRacialLocal(nivel) {
        const c = window.__t20TracosRaciaisCache;
        const nv = Math.max(1, Math.min(40, Math.floor(Number(nivel) || 1)));
        if (!c || c.encontrado === false) return { pv: 0, pm: 0 };
        const n1 = Number(c.pv_bonus_nivel1) || 0;
        const pn = Number(c.pv_bonus_por_nivel) || 0;
        const pmPn = Number(c.pm_bonus_por_nivel) || 0;
        return {
            pv: n1 + Math.max(0, nv - 1) * pn,
            pm: nv * pmPn,
        };
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
        const racial = contribPvPmRacialLocal(nv);
        const pvMax = pvIni + contribNiveis + deCon + racial.pv;
        let pmMax = null;
        let pmPn = null;
        if (isV13() && row.pm_por_nivel != null && Number(row.pm_por_nivel) > 0) {
            pmPn = Number(row.pm_por_nivel);
            pmMax = nv * pmPn + racial.pm;
        } else if (racial.pm) {
            pmMax = racial.pm;
        }
        return {
            encontrado: true,
            pv_max: pvMax,
            pv_inicial: pvIni,
            pv_por_nivel: pvPn,
            contrib_niveis_extras: contribNiveis,
            contrib_constituicao: deCon,
            contrib_pv_racial: racial.pv,
            contrib_pm_racial: racial.pm,
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
        const racial = contribPvPmRacialLocal(totalNv);
        const pvMax = base + deCon + racial.pv;
        const conTxt = modCon !== 0 ? `${totalNv}×${modCon}` : `${totalNv}×CON`;
        let formula = `${partes.join(' + ')} + ${conTxt}`;
        if (racial.pv) formula += ` + ${racial.pv} (raça)`;
        formula += ` = ${pvMax} PV`;
        return {
            encontrado: true,
            pv_max: pvMax,
            mod_con: modCon,
            contrib_constituicao: deCon,
            contrib_pv_racial: racial.pv,
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
                slug_raca: slugRacaFicha() || undefined,
                regraVersao: 'v13',
            });
        }
        const rv = regraVersaoAtiva();
        const payload = {
            classe_slug: slug,
            nivel: nivelPersonagem(),
            con_valor: conValor(),
            slug_raca: slugRacaFicha() || undefined,
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

    let _debounceVitais = null;
    let _vitaisInFlight = null;

    async function atualizarVitaisSugeridos() {
        const slug = classeSlug();
        if (!slug) return null;
        return calcularPvMb(true);
    }

    /** Coalesce rajadas ao fechar «Editar ficha» / input de atributos (evita N POSTs 503). */
    function atualizarVitaisSugeridosDebounced(delayMs) {
        const wait = delayMs == null ? 280 : Number(delayMs);
        if (_debounceVitais) clearTimeout(_debounceVitais);
        return new Promise((resolve) => {
            _debounceVitais = setTimeout(() => {
                _debounceVitais = null;
                if (_vitaisInFlight) {
                    resolve(_vitaisInFlight);
                    return;
                }
                _vitaisInFlight = atualizarVitaisSugeridos().finally(() => {
                    _vitaisInFlight = null;
                });
                resolve(_vitaisInFlight);
            }, Number.isFinite(wait) ? wait : 280);
        });
    }

    window.t20CalcularPvMb = calcularPvMb;
    window.t20AtualizarVitaisSugeridos = atualizarVitaisSugeridos;
    window.t20AtualizarVitaisSugeridosDebounced = atualizarVitaisSugeridosDebounced;
})();
