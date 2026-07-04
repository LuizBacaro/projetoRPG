/**
 * Wizard v1.3 — passo Poderes Heróis de Arton (HA-4).
 */
(function (global) {
    'use strict';

    const SUPLEMENTO_HA =
        global.T20RegraVersao && global.T20RegraVersao.SUPLEMENTO_HEROIS_ARTON
            ? global.T20RegraVersao.SUPLEMENTO_HEROIS_ARTON
            : 'herois_arton';

    let catalogoCache = [];

    function q(id) {
        return document.getElementById(id);
    }

    function passoAplica() {
        const cb = q('cadUsarHeroisArton');
        return !!(
            cb &&
            cb.checked &&
            global.T20RegraVersao &&
            global.T20DashWizardV13 &&
            global.T20DashWizardV13.isWizardAtivo &&
            global.T20DashWizardV13.isWizardAtivo()
        );
    }

    function nivelCadastro() {
        const n = parseInt(String(q('cadNivel') && q('cadNivel').value || '1'), 10);
        return Number.isFinite(n) && n >= 1 ? n : 1;
    }

    function contextoElegibilidade() {
        const racaRaw = (q('cadRacaSelect') && q('cadRacaSelect').value) || '';
        const raca = racaRaw === '__livre__' ? '' : String(racaRaw).trim().toLowerCase();
        const cls = String((q('cadClasseMb') && q('cadClasseMb').value) || '')
            .trim()
            .toLowerCase();
        return { raca, classes: cls ? [cls] : [] };
    }

    function selecionados() {
        if (!Array.isArray(global.__cadPoderesHa)) global.__cadPoderesHa = [];
        return global.__cadPoderesHa;
    }

    function attrsCadastro() {
        const read = (id) => {
            const n = Number(q(id) && q(id).value);
            return Number.isFinite(n) ? Math.floor(n) : 0;
        };
        const deltas =
            typeof global.__t20GetCadRacialDeltas === 'function'
                ? global.__t20GetCadRacialDeltas()
                : {};
        const d = deltas || {};
        return {
            for_valor: read('cadFor') + (d.for || 0),
            des_valor: read('cadDes') + (d.des || 0),
            con_valor: read('cadCon') + (d.con || 0),
            int_valor: read('cadInt') + (d.int || 0),
            sab_valor: read('cadSab') + (d.sab || 0),
            car_valor: read('cadCar') + (d.car || 0),
        };
    }

    function fichaJsonParcial() {
        const slugR = (q('cadRacaSelect') && q('cadRacaSelect').value) || '';
        const out = {
            regra_versao: 'v13',
            raca_tormenta_slug: slugR === '__livre__' ? '__livre__' : slugR || null,
            tormenta_classe_mb_slug: (q('cadClasseMb') && q('cadClasseMb').value) || null,
            game_suplemento: SUPLEMENTO_HA,
        };
        if (global.T20DashStep2V13 && global.T20DashStep2V13.lerPayloadPasso2) {
            Object.assign(out, global.T20DashStep2V13.lerPayloadPasso2());
        }
        if (global.T20DuendeV13 && global.T20DuendeV13.lerPayload) {
            Object.assign(out, global.T20DuendeV13.lerPayload());
        }
        return out;
    }

    function somenteElegiveis() {
        const cb = q('cadPoderesHaSomenteElegiveis');
        return !cb || cb.checked;
    }

    function filtrarCatalogo(itens) {
        let rows = Array.isArray(itens) ? itens.slice() : [];
        const ctx = contextoElegibilidade();
        const PV = global.T20PoderesV13;
        if (somenteElegiveis() && PV && PV.poderElegivelParaFicha) {
            rows = rows.filter((it) => PV.poderElegivelParaFicha(it, ctx));
        }
        const busca = String((q('cadPoderesHaBusca') && q('cadPoderesHaBusca').value) || '')
            .trim()
            .toLowerCase();
        if (busca) {
            rows = rows.filter((it) => {
                const nom = String(it.nome || '').toLowerCase();
                const slug = String(it.slug || '').toLowerCase();
                return nom.includes(busca) || slug.includes(busca);
            });
        }
        return rows;
    }

    function renderSelecionados() {
        const host = q('cadPoderesHaSelecionadosHost');
        const hint = q('cadPoderesHaHint');
        if (!host) return;
        const sel = selecionados();
        if (!sel.length) {
            host.innerHTML = '<p class="t20-dash-hint" style="margin:0">Nenhum poder escolhido (opcional).</p>';
        } else {
            host.innerHTML =
                '<ul class="t20-dash-poderes-ha-lista">' +
                sel
                    .map(
                        (p, i) =>
                            `<li>` +
                            `<span>${escapeHtml(p.nome)}</span>` +
                            `<button type="button" class="tormenta-btn t20-dash-poderes-ha-rm" data-idx="${i}">Remover</button>` +
                            `</li>`
                    )
                    .join('') +
                '</ul>';
            host.querySelectorAll('.t20-dash-poderes-ha-rm').forEach((btn) => {
                btn.addEventListener('click', () => {
                    const idx = parseInt(btn.getAttribute('data-idx') || '-1', 10);
                    if (idx >= 0) {
                        sel.splice(idx, 1);
                        renderSelecionados();
                        renderCatalogo();
                    }
                });
            });
        }
        if (hint) {
            hint.textContent = sel.length
                ? `${sel.length} poder(es) serão vinculados ao criar o personagem.`
                : 'Opcional — você pode adicionar mais poderes na ficha depois.';
        }
    }

    function escapeHtml(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function renderCatalogo() {
        const host = q('cadPoderesHaCatalogoHost');
        if (!host) return;
        const rows = filtrarCatalogo(catalogoCache);
        const selNomes = new Set(selecionados().map((p) => p.nome.toLowerCase()));
        if (!rows.length) {
            host.innerHTML =
                '<p class="t20-dash-hint" style="margin:0">Nenhum poder encontrado. Ajuste filtros ou raça/classe.</p>';
            return;
        }
        host.innerHTML =
            '<ul class="t20-dash-poderes-ha-lista t20-dash-poderes-ha-lista--catalogo">' +
            rows
                .slice(0, 80)
                .map((it) => {
                    const nome = String(it.nome || it.slug || '').trim();
                    const ja = selNomes.has(nome.toLowerCase());
                    const badge =
                        global.T20PoderesV13 && global.T20PoderesV13.badgeHaHtml
                            ? global.T20PoderesV13.badgeHaHtml(it)
                            : '';
                    const cat =
                        global.T20PoderesV13 && global.T20PoderesV13.labelCategoria
                            ? global.T20PoderesV13.labelCategoria(it.categoria_v13)
                            : '';
                    return (
                        `<li>` +
                        `<div class="t20-dash-poderes-ha-item">` +
                        `<strong>${escapeHtml(nome)}</strong> ${badge}` +
                        (cat ? `<span class="t20-dash-hint"> · ${escapeHtml(cat)}</span>` : '') +
                        `<button type="button" class="tormenta-btn" data-nome="${escapeHtml(nome)}" ${ja ? 'disabled' : ''}>${ja ? 'Adicionado' : 'Adicionar'}</button>` +
                        `</div></li>`
                    );
                })
                .join('') +
            '</ul>';
        host.querySelectorAll('button[data-nome]').forEach((btn) => {
            btn.addEventListener('click', () => void adicionarPoder(btn.getAttribute('data-nome') || ''));
        });
    }

    async function adicionarPoder(nome) {
        const nom = String(nome || '').trim();
        if (nom.length < 2) return;
        const sel = selecionados();
        if (sel.some((p) => p.nome.toLowerCase() === nom.toLowerCase())) return;

        if (global.T20PoderesV13 && global.T20PoderesV13.validarAntesDeAdicionar) {
            const attrs = attrsCadastro();
            const vr = await global.T20PoderesV13.validarAntesDeAdicionar(nom, () => ({
                nivel: nivelCadastro(),
                ...attrs,
                ficha_json: fichaJsonParcial(),
                poderes_escolhidos: sel.map((p) => p.nome),
            }));
            if (!vr.valido) return;
        }

        sel.push({ nome: nom });
        renderSelecionados();
        renderCatalogo();
        if (global.T20DashWizardV13 && global.T20DashWizardV13.renderResumo) {
            global.T20DashWizardV13.renderResumo();
        }
    }

    async function carregarCatalogo() {
        if (!passoAplica()) {
            catalogoCache = [];
            return;
        }
        const host = q('cadPoderesHaCatalogoHost');
        if (host) host.innerHTML = '<p class="t20-dash-hint" style="margin:0">Carregando…</p>';
        try {
            const params = {
                suplemento: SUPLEMENTO_HA,
                limit: 200,
            };
            const cat = q('cadPoderesHaCategoria');
            if (cat && cat.value) params.categoria_v13 = cat.value;
            const ctx = contextoElegibilidade();
            if (ctx.raca) params.raca = ctx.raca;
            if (ctx.classes[0]) params.classe_exigida = ctx.classes[0];
            const data = await new TormentaRegrasService().listarPoderesCatalogo(params);
            catalogoCache = Array.isArray(data.itens) ? data.itens : [];
        } catch (_e) {
            catalogoCache = [];
            if (global.Toast) global.Toast.error('Falha ao carregar poderes HA.');
        }
        renderCatalogo();
    }

    function popularCategorias() {
        const sel = q('cadPoderesHaCategoria');
        if (!sel || sel.options.length > 1) return;
        const cats = global.T20PoderesV13 && global.T20PoderesV13.CATEGORIAS;
        (cats || []).forEach((c) => {
            if (!c.slug) return;
            const op = document.createElement('option');
            op.value = c.slug;
            op.textContent = c.label;
            sel.appendChild(op);
        });
    }

    async function prepararPasso() {
        if (!passoAplica()) return;
        popularCategorias();
        renderSelecionados();
        await carregarCatalogo();
    }

    function reset() {
        global.__cadPoderesHa = [];
        if (q('cadPoderesHaBusca')) q('cadPoderesHaBusca').value = '';
        if (q('cadPoderesHaCategoria')) q('cadPoderesHaCategoria').value = '';
        if (q('cadPoderesHaSomenteElegiveis')) q('cadPoderesHaSomenteElegiveis').checked = true;
        catalogoCache = [];
        const host = q('cadPoderesHaCatalogoHost');
        if (host) host.innerHTML = '';
        renderSelecionados();
    }

    function lerPayload() {
        const sel = selecionados();
        if (!sel.length) return {};
        return {
            talentos_mb_lista: sel.map((p) => ({ nome: p.nome })),
        };
    }

    function resumo() {
        const sel = selecionados();
        if (!sel.length) return '';
        return `Poderes HA: ${sel.map((p) => p.nome).join(', ')}`;
    }

    function validar() {
        return { ok: true };
    }

    function bindOnce() {
        if (global.__t20DashPoderesHaBound) return;
        global.__t20DashPoderesHaBound = true;
        q('cadPoderesHaBusca')?.addEventListener('input', () => renderCatalogo());
        q('cadPoderesHaCategoria')?.addEventListener('change', () => void carregarCatalogo());
        q('cadPoderesHaSomenteElegiveis')?.addEventListener('change', () => renderCatalogo());
        q('cadUsarHeroisArton')?.addEventListener('change', () => {
            if (passoAplica()) void carregarCatalogo();
        });
        q('cadRacaSelect')?.addEventListener('change', () => {
            if (passoAplica()) void carregarCatalogo();
        });
        q('cadClasseMb')?.addEventListener('change', () => {
            if (passoAplica()) void carregarCatalogo();
        });
    }

    function init() {
        bindOnce();
    }

    global.T20DashPoderesHaV13 = {
        init,
        passoAplica,
        prepararPasso,
        reset,
        lerPayload,
        resumo,
        validar,
        selecionados,
    };
})(typeof window !== 'undefined' ? window : globalThis);
