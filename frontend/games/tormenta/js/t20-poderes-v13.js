/**
 * Poderes v1.3 — filtro por categoria, custo PM, ativação e catálogo Heróis de Arton.
 */
(function (global) {
    'use strict';

    const SUPLEMENTO_HA =
        global.T20RegraVersao && global.T20RegraVersao.SUPLEMENTO_HEROIS_ARTON
            ? global.T20RegraVersao.SUPLEMENTO_HEROIS_ARTON
            : 'herois_arton';

    const CATEGORIAS = [
        { slug: '', label: 'Todas as categorias' },
        { slug: 'geral', label: 'Gerais' },
        { slug: 'combate', label: 'Combate' },
        { slug: 'destino', label: 'Destino' },
        { slug: 'magia', label: 'Magia' },
        { slug: 'concedido', label: 'Concedidos' },
        { slug: 'tormenta', label: 'Tormenta' },
        { slug: 'classe', label: 'Classe' },
        { slug: 'raca', label: 'Raça (HA)' },
        { slug: 'treinador', label: 'Treinador (HA)' },
        { slug: 'grupo', label: 'Grupo (HA)' },
        { slug: 'distincao', label: 'Distinção (HA)' },
    ];

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

    function isHaAtivo() {
        if (typeof global.t20GetSuplementoFichaAtivo === 'function') {
            return global.t20GetSuplementoFichaAtivo() === SUPLEMENTO_HA;
        }
        return false;
    }

    function labelCategoria(slug) {
        const s = String(slug || '').trim().toLowerCase();
        const row = CATEGORIAS.find((c) => c.slug === s);
        return row ? row.label : slug || '';
    }

    function getSlugsFicha() {
        const racaRaw = (q('f_raca_select') && q('f_raca_select').value) || '';
        const raca = racaRaw === '__livre__' ? '' : String(racaRaw).trim().toLowerCase();
        const classes = new Set();
        if (global.T20MulticlasseV13 && typeof global.T20MulticlasseV13.niveisEfetivosParaPm === 'function') {
            (global.T20MulticlasseV13.niveisEfetivosParaPm() || []).forEach((row) => {
                const cs = String((row && row.slug) || '').trim().toLowerCase();
                if (cs) classes.add(cs);
            });
        } else {
            const main = ((q('f_classe_mb') && q('f_classe_mb').value) || '').trim().toLowerCase();
            if (main) classes.add(main);
        }
        return { raca, classes: [...classes] };
    }

    function classeAtendeExigencia(classeExigida, classesFicha) {
        const req = String(classeExigida || '').trim().toLowerCase();
        if (!req) return true;
        return (classesFicha || []).some(
            (c) => c === req || (req === 'treinador' && c.startsWith('treinador'))
        );
    }

    function poderElegivelParaFicha(item, ctx) {
        if (!item || item.fonte_catalogo !== SUPLEMENTO_HA) return true;
        const racaReq = String(item.raca_exigida || '').trim().toLowerCase();
        if (racaReq && racaReq !== ctx.raca) return false;
        const classeReq = String(item.classe_exigida || '').trim().toLowerCase();
        if (classeReq && !classeAtendeExigencia(classeReq, ctx.classes)) return false;
        return true;
    }

    function filtrarItensElegiveis(itens) {
        const ctx = getSlugsFicha();
        return (itens || []).filter((it) => poderElegivelParaFicha(it, ctx));
    }

    function somenteElegiveisHaAtivo() {
        const cb = q('talentosMbHaSomenteElegiveis');
        return !!(cb && cb.checked && isHaAtivo());
    }

    function montarFiltroCategoriaModal() {
        const host = q('talentosMbControlesV13');
        const sel = q('talentosMbCategoriaV13');
        if (!host || !sel) return;
        if (!isV13()) {
            host.style.display = 'none';
            return;
        }
        host.style.display = '';
        if (sel.options.length > 1) return;
        CATEGORIAS.forEach((c) => {
            const op = document.createElement('option');
            op.value = c.slug;
            op.textContent = c.label;
            sel.appendChild(op);
        });
    }

    function montarControlesHaModal() {
        const host = q('talentosMbHaControles');
        if (!host) return;
        if (!isV13() || !isHaAtivo()) {
            host.style.display = 'none';
            return;
        }
        host.style.display = '';
        if (host.dataset.boundHa) return;
        host.dataset.boundHa = '1';
        const cb = q('talentosMbHaSomenteElegiveis');
        if (cb) {
            cb.addEventListener('change', () => {
                if (typeof global.carregarTalCatalogoTormenta === 'function') {
                    global.carregarTalCatalogoTormenta(true);
                }
            });
        }
    }

    function atualizarUiModalHa() {
        montarControlesHaModal();
        const sub = q('subModalGerenciarTalentos');
        if (sub && isV13() && isHaAtivo()) {
            sub.innerHTML =
                'Catálogo v1.3 + <strong>Heróis de Arton</strong>. Use categoria ou «só elegíveis» para filtrar. <span class="t20-hint">Esc fecha.</span>';
        }
    }

    function paramsCatalogoPoderes(base) {
        const p = Object.assign({}, base || {});
        if (isV13()) {
            const cat = q('talentosMbCategoriaV13');
            if (cat && cat.value) p.categoria_v13 = cat.value;
        }
        if (isHaAtivo()) {
            p.suplemento = SUPLEMENTO_HA;
            if (somenteElegiveisHaAtivo()) {
                p.limit = Math.max(Number(p.limit) || 25, 200);
            }
        }
        return p;
    }

    function posProcessarItensCatalogo(itens) {
        if (!somenteElegiveisHaAtivo()) return itens || [];
        return filtrarItensElegiveis(itens);
    }

    function badgeHaHtml(item) {
        if (!item || item.fonte_catalogo !== SUPLEMENTO_HA) return '';
        const parts = ['HA'];
        if (item.raca_exigida) parts.push(`raça: ${item.raca_exigida}`);
        if (item.classe_exigida) parts.push(`classe: ${item.classe_exigida}`);
        return `<span class="talento-linha-secao t20-poder-ha-badge" title="Heróis de Arton">${parts.join(' · ')}</span>`;
    }

    function atualizarPmNaFicha(depois, max) {
        const el = q('fichaPm');
        if (!el) return;
        const s = `${depois} / ${max}`;
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') el.value = s;
        else el.textContent = s;
    }

    async function ativarPoder(vinculoId, custoPm) {
        const fid = q('fichaId') && q('fichaId').value;
        if (!fid) throw new Error('Salve a ficha antes de ativar poderes.');
        const svc = new TormentaPersonagemService();
        const res = await svc.ativarPoder(fid, { vinculo_id: vinculoId, custo_pm: custoPm });
        atualizarPmNaFicha(res.pa_atual_depois, res.pa_max);
        if (global.Toast && global.Toast.success) {
            global.Toast.success(
                `${res.nome}: −${res.custo_pm} PM (restam ${res.pa_atual_depois}/${res.pa_max}).`
            );
        }
        return res;
    }

    function decorarLinha(row, opts) {
        if (!row || !isV13()) return;
        const o = opts || {};
        const custo = Number(o.custo_pm);
        if (!Number.isFinite(custo) || custo <= 0 || !o.vinculoId) return;
        if (row.querySelector('.t20-poder-ativar-btn')) return;

        const badge = document.createElement('span');
        badge.className = 't20-hint t20-poder-pm-badge';
        badge.style.marginLeft = '0.35rem';
        badge.textContent = `${custo} PM`;
        const inp = row.querySelector('.t20-tal-nome');
        if (inp && inp.parentNode) inp.parentNode.insertBefore(badge, inp.nextSibling);

        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'tormenta-btn t20-poder-ativar-btn';
        btn.textContent = 'Ativar';
        btn.title = `Gasta ${custo} PM ao ativar`;
        btn.addEventListener('click', async () => {
            btn.disabled = true;
            try {
                await ativarPoder(o.vinculoId, custo);
            } catch (e) {
                if (global.Toast && global.Toast.error) {
                    global.Toast.error(e.message || 'Erro ao ativar poder');
                }
            } finally {
                btn.disabled = false;
            }
        });
        const pick = row.querySelector('.t20-eq-pick');
        if (pick && pick.parentNode) {
            pick.parentNode.insertBefore(btn, pick);
        } else {
            row.appendChild(btn);
        }
    }

    function wireModalFiltro() {
        if (global.__t20PoderesV13ModalBound) return;
        global.__t20PoderesV13ModalBound = true;
        q('talentosMbCategoriaV13')?.addEventListener('change', () => {
            if (typeof global.carregarTalCatalogoTormenta === 'function') {
                global.carregarTalCatalogoTormenta(true);
            }
        });
    }

    function coletarNomesPoderesFicha() {
        const nomes = [];
        document.querySelectorAll('#t20FichaTalentosMb .t20-tal-nome').forEach((inp) => {
            const v = (inp.value || '').trim();
            if (v.length >= 2) nomes.push(v);
        });
        return nomes;
    }

    async function validarAntesDeAdicionar(nome, getContext) {
        if (!isV13()) return { valido: true };
        const ctx = typeof getContext === 'function' ? getContext() : null;
        if (!ctx) return { valido: true };
        const regras = new TormentaRegrasService();
        const res = await regras.validarPreRequisitosPoder({
            nome_poder: nome,
            regra_versao: 'v13',
            nivel: ctx.nivel,
            for_valor: ctx.for_valor,
            des_valor: ctx.des_valor,
            con_valor: ctx.con_valor,
            int_valor: ctx.int_valor,
            sab_valor: ctx.sab_valor,
            car_valor: ctx.car_valor,
            ficha_json: ctx.ficha_json,
            poderes_escolhidos: ctx.poderes_escolhidos || [],
        });
        if (!res.valido && global.Toast && global.Toast.error) {
            const msg =
                res.motivo ||
                (res.faltando || []).map((f) => f.descricao).filter(Boolean).join('; ') ||
                'Pré-requisitos não atendidos';
            global.Toast.error(`«${nome}»: ${msg}`);
        }
        return res;
    }

    function init() {
        montarFiltroCategoriaModal();
        montarControlesHaModal();
        wireModalFiltro();
    }

    global.T20PoderesV13 = {
        init,
        decorarLinha,
        paramsCatalogoPoderes,
        posProcessarItensCatalogo,
        badgeHaHtml,
        filtrarItensElegiveis,
        poderElegivelParaFicha,
        atualizarUiModalHa,
        labelCategoria,
        validarAntesDeAdicionar,
        coletarNomesPoderesFicha,
        isHaAtivo,
        CATEGORIAS,
        SUPLEMENTO_HA,
    };
})(typeof window !== 'undefined' ? window : globalThis);
