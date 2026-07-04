/**
 * Duende — raça modular Heróis de Arton (wizard + ficha v1.3).
 */
(function (global) {
    'use strict';

    const ATTRS = ['for', 'des', 'con', 'int', 'sab', 'car'];
    const ATTR_LABEL = {
        for: 'Força',
        des: 'Destreza',
        con: 'Constituição',
        int: 'Inteligência',
        sab: 'Sabedoria',
        car: 'Carisma',
    };

    const CONTEXTS = {
        wizard: {
            wrap: 'cadWrapDuende',
            natureza: 'cadDuendeNatureza',
            naturezaAttr: 'cadDuendeNaturezaAttr',
            wrapNatAttr: 'cadWrapDuendeNaturezaAttr',
            tamanho: 'cadDuendeTamanho',
            donA: 'cadDuendeDonA',
            donB: 'cadDuendeDonB',
            presentesHost: 'cadDuendePresentesHost',
            presentesHint: 'cadDuendePresentesHint',
            wrapOpcoes: 'cadWrapDuendePresentesOpcoes',
            opcoesHost: 'cadDuendePresentesOpcoesHost',
            tabuTexto: 'cadDuendeTabuTexto',
            tabuPen: 'cadDuendeTabuPenalidade',
            aleatorio: 'cadDuendeGeracaoAleatoria',
            btnRolar: 'cadBtnDuendeRolar',
            racaSel: 'cadRacaSelect',
        },
        ficha: {
            wrap: 'fWrapDuende',
            natureza: 'f_duende_natureza',
            naturezaAttr: 'f_duende_natureza_attr',
            wrapNatAttr: 'fWrapDuendeNaturezaAttr',
            tamanho: 'f_duende_tamanho',
            donA: 'f_duende_don_a',
            donB: 'f_duende_don_b',
            presentesHost: 'f_duende_presentes_host',
            presentesHint: 'f_duende_presentes_hint',
            wrapOpcoes: 'fWrapDuendePresentesOpcoes',
            opcoesHost: 'f_duende_presentes_opcoes_host',
            wrapTrocas: 'fWrapDuendeTrocas',
            trocasHost: 'f_duende_trocas_host',
            trocasHint: 'f_duende_trocas_hint',
            tabuTexto: 'f_duende_tabu_texto',
            tabuPen: 'f_duende_tabu_penalidade',
            aleatorio: 'f_duende_geracao_aleatoria',
            btnRolar: 'fBtnDuendeRolar',
            racaSel: 'f_raca_select',
            nivelInput: 'f_nivel',
        },
    };

    let ctx = CONTEXTS.wizard;
    let opcoes = null;
    let presentes = [];
    let qtdPresentes = 3;
    const PATAMARES_TROCA_PADRAO = [5, 10, 15, 20];

    function q(id) {
        return document.getElementById(id);
    }

    function ids() {
        return ctx;
    }

    function setContext(name) {
        ctx = CONTEXTS[name] || CONTEXTS.wizard;
    }

    function isDuendeSelecionado() {
        const sel = q(ids().racaSel);
        return sel && String(sel.value || '').trim().toLowerCase() === 'duende';
    }

    function slugParaLabel(slug) {
        return String(slug || '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, (c) => c.toUpperCase());
    }

    async function carregarCatalogos() {
        if (!isDuendeSelecionado()) {
            opcoes = null;
            presentes = [];
            return;
        }
        try {
            const svc = new TormentaRegrasService();
            const [op, pres] = await Promise.all([
                svc.obterDuendeOpcoes(),
                svc.obterPresentesDuende(),
            ]);
            opcoes = op || {};
            presentes = Array.isArray(pres.presentes) ? pres.presentes : [];
            qtdPresentes = Number(pres.qtd_presentes) || 3;
        } catch (_e) {
            opcoes = null;
            presentes = [];
        }
    }

    function popularSelectAttrs(sel, cur) {
        if (!sel) return;
        const v = cur || sel.value || '';
        sel.innerHTML = '';
        const o0 = document.createElement('option');
        o0.value = '';
        o0.textContent = '— Atributo —';
        sel.appendChild(o0);
        ATTRS.forEach((k) => {
            const o = document.createElement('option');
            o.value = k;
            o.textContent = ATTR_LABEL[k] || k.toUpperCase();
            sel.appendChild(o);
        });
        if (v && ATTRS.includes(v)) sel.value = v;
    }

    function popularSelectFromRows(sel, rows, placeholder, cur) {
        if (!sel) return;
        sel.innerHTML = '';
        const o0 = document.createElement('option');
        o0.value = '';
        o0.textContent = placeholder;
        sel.appendChild(o0);
        (rows || []).forEach((row) => {
            const o = document.createElement('option');
            o.value = row.slug;
            o.textContent = row.nome || slugParaLabel(row.slug);
            sel.appendChild(o);
        });
        if (cur) sel.value = cur;
    }

    function presentesMarcados() {
        const host = q(ids().presentesHost);
        if (!host) return [];
        return Array.from(host.querySelectorAll('input[data-duende-presente]:checked')).map((inp) =>
            String(inp.getAttribute('data-duende-presente') || '').trim().toLowerCase()
        );
    }

    function renderPresentes() {
        const host = q(ids().presentesHost);
        if (!host) return;
        const saved = new Set(presentesMarcados());
        if (!presentes.length) {
            host.innerHTML = '<p class="t20-hint" style="margin:0">Carregando presentes…</p>';
            return;
        }
        host.innerHTML = presentes
            .map((p) => {
                const slug = String(p.slug || '').trim().toLowerCase();
                return (
                    `<label style="display:block;margin:.25rem 0;cursor:pointer">` +
                    `<input type="checkbox" data-duende-presente="${slug}" ${saved.has(slug) ? 'checked' : ''}/> ` +
                    `<strong>${p.nome || slugParaLabel(slug)}</strong>` +
                    (p.descricao ? ` <span class="t20-hint">— ${p.descricao}</span>` : '') +
                    `</label>`
                );
            })
            .join('');
        host.querySelectorAll('input[data-duende-presente]').forEach((inp) => {
            inp.addEventListener('change', () => {
                const picks = presentesMarcados();
                if (picks.length > qtdPresentes) {
                    inp.checked = false;
                    if (global.Toast) {
                        global.Toast.error(`Máximo ${qtdPresentes} presentes.`);
                    }
                    return;
                }
                renderOpcoesPresentes();
                atualizarHintPresentes();
                notificarMudanca();
            });
        });
        atualizarHintPresentes();
        renderOpcoesPresentes();
    }

    function atualizarHintPresentes() {
        const hint = q(ids().presentesHint);
        if (!hint) return;
        const n = presentesMarcados().length;
        const lim =
            opcoes && Array.isArray(opcoes.limitacoes_fixas)
                ? opcoes.limitacoes_fixas
                      .filter((x) => x && x.slug !== 'tabu')
                      .map((x) => x.nome)
                      .join(', ')
                : '';
        let txt = `${n}/${qtdPresentes} presentes escolhidos.`;
        if (lim) txt += ` Limitações fixas: ${lim}.`;
        if (opcoes && opcoes.pm_bonus_geracao_aleatoria) {
            txt += ` Geração aleatória: +${opcoes.pm_bonus_geracao_aleatoria} PM.`;
        }
        hint.textContent = txt;
    }

    function renderOpcoesPresentes() {
        const wrap = q(ids().wrapOpcoes);
        const host = q(ids().opcoesHost);
        if (!wrap || !host || !opcoes) return;
        const picks = presentesMarcados();
        const parts = [];
        if (picks.includes('afinidade_elemental')) {
            parts.push(
                `<div class="t20-dash-field"><label>Afinidade Elemental — elemento</label>` +
                    `<select id="${ids().opcoesHost}_elem" class="t20-input">` +
                    (opcoes.afinidade_elementos || [])
                        .map(
                            (e) =>
                                `<option value="${e.slug}">${e.nome || e.slug}</option>`
                        )
                        .join('') +
                    `</select></div>`
            );
        }
        if (picks.includes('maldicao')) {
            parts.push(
                `<div class="t20-dash-field"><label>Maldição — resistência</label>` +
                    `<select id="${ids().opcoesHost}_mal_res" class="t20-input">` +
                    (opcoes.maldicao_resistencias || [])
                        .map((e) => `<option value="${e.slug}">${e.nome}</option>`)
                        .join('') +
                    `</select></div>` +
                    `<div class="t20-dash-field"><label>Maldição — efeito</label>` +
                    `<select id="${ids().opcoesHost}_mal_efe" class="t20-input">` +
                    (opcoes.maldicao_efeitos || [])
                        .map((e) => `<option value="${e.slug}">${e.nome}</option>`)
                        .join('') +
                    `</select></div>`
            );
        }
        if (picks.includes('metamorfose_animal')) {
            parts.push(
                `<div class="t20-dash-field"><label>Metamorfose — forma selvagem</label>` +
                    `<select id="${ids().opcoesHost}_meta" class="t20-input">` +
                    (opcoes.formas_selvagem_metamorfose || [])
                        .map((e) => `<option value="${e.slug}">${e.nome}</option>`)
                        .join('') +
                    `</select></div>`
            );
        }
        if (!parts.length) {
            wrap.style.display = 'none';
            host.innerHTML = '';
            return;
        }
        wrap.style.display = '';
        host.innerHTML = parts.join('');
    }

    function lerPresentesOpcoes() {
        const out = {};
        const picks = presentesMarcados();
        const base = ids().opcoesHost;
        if (picks.includes('afinidade_elemental')) {
            const el = q(`${base}_elem`);
            if (el && el.value) out.afinidade_elemental = el.value;
        }
        if (picks.includes('maldicao')) {
            const res = q(`${base}_mal_res`);
            const efe = q(`${base}_mal_efe`);
            if (res && efe && res.value && efe.value) {
                out.maldicao = { resistencia: res.value, efeito: efe.value };
            }
        }
        if (picks.includes('metamorfose_animal')) {
            const meta = q(`${base}_meta`);
            if (meta && meta.value) out.metamorfose_animal = meta.value;
        }
        return out;
    }

    function aplicarPresentesOpcoes(po) {
        if (!po || typeof po !== 'object') return;
        renderOpcoesPresentes();
        const base = ids().opcoesHost;
        if (po.afinidade_elemental) {
            const el = q(`${base}_elem`);
            if (el) el.value = po.afinidade_elemental;
        }
        if (po.maldicao && typeof po.maldicao === 'object') {
            const res = q(`${base}_mal_res`);
            const efe = q(`${base}_mal_efe`);
            if (res && po.maldicao.resistencia) res.value = po.maldicao.resistencia;
            if (efe && po.maldicao.efeito) efe.value = po.maldicao.efeito;
        }
        if (po.metamorfose_animal) {
            const meta = q(`${base}_meta`);
            if (meta) meta.value = po.metamorfose_animal;
        }
    }

    function patamaresTroca() {
        const p = opcoes && opcoes.patamares_troca_poder;
        return Array.isArray(p) && p.length ? p.slice() : PATAMARES_TROCA_PADRAO.slice();
    }

    function nivelPersonagem() {
        if (ctx !== CONTEXTS.ficha) return 20;
        const el = q(ids().nivelInput);
        const n = parseInt(el && el.value, 10);
        return Number.isFinite(n) && n >= 1 ? n : 1;
    }

    function isFichaComTrocas() {
        return ctx === CONTEXTS.ficha && !!q(ids().trocasHost);
    }

    function prefixOpcoesTroca(nivel) {
        return `${ids().trocasHost}_troca_${nivel}`;
    }

    function renderOpcoesTroca(nivel, opcoesSalvas) {
        const host = document.querySelector(`[data-duende-troca-opcoes="${nivel}"]`);
        const sel = document.querySelector(`select[data-duende-troca-presente="${nivel}"]`);
        if (!host || !sel || !opcoes) return;
        const slug = String(sel.value || '').trim().toLowerCase();
        const prefix = prefixOpcoesTroca(nivel);
        const saved = opcoesSalvas && typeof opcoesSalvas === 'object' ? opcoesSalvas : {};
        const parts = [];
        if (slug === 'afinidade_elemental') {
            parts.push(
                `<div class="t20-dash-field"><label>Afinidade Elemental — elemento</label>` +
                    `<select id="${prefix}_elem" class="t20-input">` +
                    (opcoes.afinidade_elementos || [])
                        .map(
                            (e) =>
                                `<option value="${e.slug}">${e.nome || e.slug}</option>`
                        )
                        .join('') +
                    `</select></div>`
            );
        }
        if (slug === 'maldicao') {
            parts.push(
                `<div class="t20-dash-field"><label>Maldição — resistência</label>` +
                    `<select id="${prefix}_mal_res" class="t20-input">` +
                    (opcoes.maldicao_resistencias || [])
                        .map((e) => `<option value="${e.slug}">${e.nome}</option>`)
                        .join('') +
                    `</select></div>` +
                    `<div class="t20-dash-field"><label>Maldição — efeito</label>` +
                    `<select id="${prefix}_mal_efe" class="t20-input">` +
                    (opcoes.maldicao_efeitos || [])
                        .map((e) => `<option value="${e.slug}">${e.nome}</option>`)
                        .join('') +
                    `</select></div>`
            );
        }
        if (slug === 'metamorfose_animal') {
            parts.push(
                `<div class="t20-dash-field"><label>Metamorfose — forma selvagem</label>` +
                    `<select id="${prefix}_meta" class="t20-input">` +
                    (opcoes.formas_selvagem_metamorfose || [])
                        .map((e) => `<option value="${e.slug}">${e.nome}</option>`)
                        .join('') +
                    `</select></div>`
            );
        }
        if (!parts.length) {
            host.innerHTML = '';
            host.style.display = 'none';
            return;
        }
        host.style.display = '';
        host.innerHTML = parts.join('');
        if (saved.afinidade_elemental) {
            const el = q(`${prefix}_elem`);
            if (el) el.value = saved.afinidade_elemental;
        }
        if (saved.maldicao && typeof saved.maldicao === 'object') {
            const res = q(`${prefix}_mal_res`);
            const efe = q(`${prefix}_mal_efe`);
            if (res && saved.maldicao.resistencia) res.value = saved.maldicao.resistencia;
            if (efe && saved.maldicao.efeito) efe.value = saved.maldicao.efeito;
        }
        if (saved.metamorfose_animal) {
            const meta = q(`${prefix}_meta`);
            if (meta) meta.value = saved.metamorfose_animal;
        }
        host.querySelectorAll('select').forEach((el) => {
            el.addEventListener('change', () => notificarMudanca());
        });
    }

    function lerOpcoesTroca(nivel) {
        const out = {};
        const prefix = prefixOpcoesTroca(nivel);
        const elem = q(`${prefix}_elem`);
        if (elem && elem.value) out.afinidade_elemental = elem.value;
        const res = q(`${prefix}_mal_res`);
        const efe = q(`${prefix}_mal_efe`);
        if (res && efe && res.value && efe.value) {
            out.maldicao = { resistencia: res.value, efeito: efe.value };
        }
        const meta = q(`${prefix}_meta`);
        if (meta && meta.value) out.metamorfose_animal = meta.value;
        return out;
    }

    function lerTrocasPoderPresente() {
        if (!isFichaComTrocas()) return [];
        const host = q(ids().trocasHost);
        if (!host) return [];
        const out = [];
        host.querySelectorAll('select[data-duende-troca-presente]').forEach((sel) => {
            const nivel = parseInt(sel.getAttribute('data-duende-troca-presente'), 10);
            const presente = String(sel.value || '').trim().toLowerCase();
            if (!presente) return;
            const entry = { nivel, presente };
            const op = lerOpcoesTroca(nivel);
            if (Object.keys(op).length) entry.opcoes = op;
            out.push(entry);
        });
        return out.sort((a, b) => a.nivel - b.nivel);
    }

    function atualizarHintTrocas() {
        const hint = q(ids().trocasHint);
        if (!hint || !isFichaComTrocas()) return;
        const n = lerTrocasPoderPresente().length;
        const nv = nivelPersonagem();
        hint.textContent =
            n === 0
                ? `Nível ${nv}: nenhuma troca registrada (opcional).`
                : `${n} troca(s) registrada(s) · nível do personagem: ${nv}.`;
    }

    function renderTrocas() {
        const wrap = q(ids().wrapTrocas);
        const host = q(ids().trocasHost);
        if (!isFichaComTrocas()) {
            if (wrap) wrap.style.display = 'none';
            return;
        }
        if (wrap) wrap.style.display = '';
        if (!host) return;
        const curMap = Object.fromEntries(
            lerTrocasPoderPresente().map((t) => [t.nivel, t])
        );
        const nvChar = nivelPersonagem();
        if (!presentes.length) {
            host.innerHTML = '<p class="t20-hint" style="margin:0">Carregando presentes…</p>';
            return;
        }
        host.innerHTML = patamaresTroca()
            .map((nivel) => {
                const cur = curMap[nivel] || {};
                const disabled = nvChar < nivel;
                let opts = '<option value="">— Manter poder de classe —</option>';
                presentes.forEach((p) => {
                    const slug = String(p.slug || '').trim().toLowerCase();
                    opts +=
                        `<option value="${slug}" ${cur.presente === slug ? 'selected' : ''}>` +
                        `${p.nome || slugParaLabel(slug)}</option>`;
                });
                return (
                    `<div class="t20-duende-troca-row" data-duende-troca-nivel="${nivel}" ` +
                    `style="margin:.4rem 0;padding:.35rem 0;border-bottom:1px solid rgba(128,128,128,.25)">` +
                    `<div style="display:flex;flex-wrap:wrap;gap:.5rem;align-items:center">` +
                    `<label style="min-width:4.2rem;font-weight:600">Nível ${nivel}</label>` +
                    `<select data-duende-troca-presente="${nivel}" class="t20-input" ` +
                    `${disabled ? 'disabled' : ''} style="flex:1;min-width:12rem">${opts}</select>` +
                    (disabled
                        ? '<span class="t20-hint">(disponível ao atingir este nível)</span>'
                        : '') +
                    `</div>` +
                    `<div data-duende-troca-opcoes="${nivel}" style="margin-top:.35rem"></div>` +
                    `</div>`
                );
            })
            .join('');
        host.querySelectorAll('select[data-duende-troca-presente]').forEach((sel) => {
            const nivel = parseInt(sel.getAttribute('data-duende-troca-presente'), 10);
            const cur = curMap[nivel];
            renderOpcoesTroca(nivel, cur && cur.opcoes);
            sel.addEventListener('change', () => {
                renderOpcoesTroca(nivel);
                atualizarHintTrocas();
                notificarMudanca();
            });
        });
        atualizarHintTrocas();
    }

    function aplicarTrocas(trocas) {
        if (!isFichaComTrocas()) return;
        renderTrocas();
        const map = Object.fromEntries(
            (Array.isArray(trocas) ? trocas : []).map((t) => [Number(t.nivel), t])
        );
        patamaresTroca().forEach((nivel) => {
            const sel = document.querySelector(`select[data-duende-troca-presente="${nivel}"]`);
            if (!sel) return;
            const row = map[nivel];
            sel.value = row && row.presente ? row.presente : '';
            renderOpcoesTroca(nivel, row && row.opcoes);
        });
        atualizarHintTrocas();
    }

    function validarTrocas() {
        if (!isFichaComTrocas()) return { ok: true };
        const trocas = lerTrocasPoderPresente();
        const seen = new Set();
        const nvChar = nivelPersonagem();
        for (const t of trocas) {
            if (seen.has(t.nivel)) {
                return { ok: false, msg: 'Duende: patamar duplicado na troca poder→presente.' };
            }
            seen.add(t.nivel);
            if (nvChar < t.nivel) {
                return {
                    ok: false,
                    msg: `Duende: troca no nível ${t.nivel} exige personagem de nível ${t.nivel} ou superior.`,
                };
            }
            if (t.presente === 'afinidade_elemental' && !(t.opcoes && t.opcoes.afinidade_elemental)) {
                return {
                    ok: false,
                    msg: `Duende: troca no nível ${t.nivel} — Afinidade Elemental exige elemento.`,
                };
            }
            if (
                t.presente === 'maldicao' &&
                !(t.opcoes && t.opcoes.maldicao && t.opcoes.maldicao.resistencia && t.opcoes.maldicao.efeito)
            ) {
                return {
                    ok: false,
                    msg: `Duende: troca no nível ${t.nivel} — Maldição exige resistência e efeito.`,
                };
            }
            if (
                t.presente === 'metamorfose_animal' &&
                !(t.opcoes && t.opcoes.metamorfose_animal)
            ) {
                return {
                    ok: false,
                    msg: `Duende: troca no nível ${t.nivel} — Metamorfose Animal exige forma selvagem.`,
                };
            }
        }
        return { ok: true };
    }

    function atualizarUiNaturezaAttr() {
        const wrap = q(ids().wrapNatAttr);
        const nat = q(ids().natureza);
        const show = nat && String(nat.value || '').toLowerCase() === 'animal';
        if (wrap) wrap.style.display = show ? '' : 'none';
        if (!show && q(ids().naturezaAttr)) q(ids().naturezaAttr).value = '';
    }

    function notificarMudanca() {
        if (global.T20TracosRaciaisV13 && isDuendeSelecionado()) {
            if (ctx === CONTEXTS.ficha) {
                void global.T20TracosRaciaisV13.aplicarTracosRaciais('duende');
            } else {
                void global.T20TracosRaciaisV13.aplicarTracosRaciaisCadastro('duende');
            }
        }
        if (typeof global.__t20AtualizarModRacialDash === 'function') {
            global.__t20AtualizarModRacialDash();
        }
        if (ctx === CONTEXTS.ficha && typeof global.t20AtualizarEstadoBotaoSalvar === 'function') {
            global.t20AtualizarEstadoBotaoSalvar();
        }
        if (global.T20DashWizardV13 && global.T20DashWizardV13.renderResumo) {
            global.T20DashWizardV13.renderResumo();
        }
    }

    async function atualizarUi() {
        const wrap = q(ids().wrap);
        const show = isDuendeSelecionado();
        if (wrap) wrap.style.display = show ? '' : 'none';
        if (!show) return;
        await carregarCatalogos();
        if (opcoes) {
            popularSelectFromRows(
                q(ids().natureza),
                opcoes.naturezas,
                '— Natureza —',
                q(ids().natureza) && q(ids().natureza).value
            );
            popularSelectFromRows(
                q(ids().tamanho),
                opcoes.tamanhos,
                '— Tamanho —',
                q(ids().tamanho) && q(ids().tamanho).value
            );
            popularSelectFromRows(
                q(ids().tabuPen),
                opcoes.tabu_penalidades,
                '— Penalidade —',
                q(ids().tabuPen) && q(ids().tabuPen).value
            );
        }
        popularSelectAttrs(q(ids().naturezaAttr), q(ids().naturezaAttr) && q(ids().naturezaAttr).value);
        popularSelectAttrs(q(ids().donA), q(ids().donA) && q(ids().donA).value);
        popularSelectAttrs(q(ids().donB), q(ids().donB) && q(ids().donB).value);
        renderPresentes();
        renderTrocas();
        atualizarUiNaturezaAttr();
    }

    function modificadoresAtributos() {
        if (!isDuendeSelecionado()) {
            return { for: 0, des: 0, con: 0, int: 0, sab: 0, car: 0 };
        }
        const d = { for: 0, des: 0, con: 0, int: 0, sab: 0, car: 0 };
        const nat = q(ids().natureza) && q(ids().natureza).value;
        if (String(nat || '').toLowerCase() === 'animal') {
            const na = q(ids().naturezaAttr) && q(ids().naturezaAttr).value;
            if (na && ATTRS.includes(na)) d[na] += 1;
        }
        [q(ids().donA) && q(ids().donA).value, q(ids().donB) && q(ids().donB).value].forEach((k) => {
            if (k && ATTRS.includes(k)) d[k] += 1;
        });
        const tam = q(ids().tamanho) && q(ids().tamanho).value;
        const row = (opcoes && opcoes.tamanhos) || [];
        const tr = row.find((x) => x.slug === tam);
        if (tr) {
            if (tr.mod_for) d.for += Number(tr.mod_for);
            if (tr.mod_des) d.des += Number(tr.mod_des);
        }
        return d;
    }

    function optsPreviewTracos() {
        if (!isDuendeSelecionado()) return {};
        const tam = q(ids().tamanho) && q(ids().tamanho).value;
        const pres = presentesMarcados().slice();
        lerTrocasPoderPresente().forEach((t) => {
            if (t.presente && !pres.includes(t.presente)) pres.push(t.presente);
        });
        const out = {
            duendeTamanho: tam || 'medio',
            duendePresentes: pres.join(','),
        };
        const nat = q(ids().natureza) && q(ids().natureza).value;
        if (nat) out.duendeNatureza = nat;
        const pen = q(ids().tabuPen) && q(ids().tabuPen).value;
        if (pen) out.duendeTabuPenalidade = pen;
        const tabu = q(ids().tabuTexto) && q(ids().tabuTexto).value.trim();
        if (tabu) out.duendeTabuTexto = tabu;
        return out;
    }

    function validar() {
        if (!isDuendeSelecionado()) return { ok: true };
        const nat = (q(ids().natureza) && q(ids().natureza).value) || '';
        if (!nat) return { ok: false, msg: 'Duende: escolha a natureza (animal, vegetal ou mineral).' };
        if (nat === 'animal') {
            const na = (q(ids().naturezaAttr) && q(ids().naturezaAttr).value) || '';
            if (!na) return { ok: false, msg: 'Duende animal: escolha o atributo +1 da natureza.' };
        }
        const tam = (q(ids().tamanho) && q(ids().tamanho).value) || '';
        if (!tam) return { ok: false, msg: 'Duende: escolha o tamanho.' };
        const a = (q(ids().donA) && q(ids().donA).value) || '';
        const b = (q(ids().donB) && q(ids().donB).value) || '';
        if (!a || !b) return { ok: false, msg: 'Duende: escolha dois Dons (+1 em atributos diferentes).' };
        if (a === b) return { ok: false, msg: 'Duende: os dois Dons devem ser atributos diferentes.' };
        const pres = presentesMarcados();
        if (pres.length !== qtdPresentes) {
            return { ok: false, msg: `Duende: escolha exatamente ${qtdPresentes} presentes.` };
        }
        if (pres.includes('afinidade_elemental') && !lerPresentesOpcoes().afinidade_elemental) {
            return { ok: false, msg: 'Duende: Afinidade Elemental exige elemento.' };
        }
        if (pres.includes('maldicao') && !lerPresentesOpcoes().maldicao) {
            return { ok: false, msg: 'Duende: Maldição exige resistência e efeito.' };
        }
        if (pres.includes('metamorfose_animal') && !lerPresentesOpcoes().metamorfose_animal) {
            return { ok: false, msg: 'Duende: Metamorfose Animal exige forma selvagem.' };
        }
        const tabu = (q(ids().tabuTexto) && q(ids().tabuTexto).value.trim()) || '';
        if (tabu.length < 3) {
            return { ok: false, msg: 'Duende: descreva o tabu (mínimo 3 caracteres).' };
        }
        const pen = (q(ids().tabuPen) && q(ids().tabuPen).value) || '';
        if (!pen) return { ok: false, msg: 'Duende: escolha a penalidade do tabu.' };
        const vt = validarTrocas();
        if (!vt.ok) return vt;
        return { ok: true };
    }

    function lerPayload() {
        if (!isDuendeSelecionado()) return {};
        const dons = [
            (q(ids().donA) && q(ids().donA).value) || '',
            (q(ids().donB) && q(ids().donB).value) || '',
        ].filter(Boolean);
        const out = {
            duende: {
                natureza: (q(ids().natureza) && q(ids().natureza).value) || null,
                tamanho_raca: (q(ids().tamanho) && q(ids().tamanho).value) || null,
                dons,
                presentes: presentesMarcados(),
                tabu_texto: (q(ids().tabuTexto) && q(ids().tabuTexto).value.trim()) || '',
                tabu_penalidade: (q(ids().tabuPen) && q(ids().tabuPen).value) || null,
                geracao_aleatoria: !!(q(ids().aleatorio) && q(ids().aleatorio).checked),
                presentes_opcoes: lerPresentesOpcoes(),
            },
        };
        if (String(out.duende.natureza || '').toLowerCase() === 'animal') {
            out.duende.natureza_atributo =
                (q(ids().naturezaAttr) && q(ids().naturezaAttr).value) || null;
        }
        if (isFichaComTrocas()) {
            const trocas = lerTrocasPoderPresente();
            if (trocas.length) out.duende.trocas_poder_presente = trocas;
        }
        return out;
    }

    function preencher(dados) {
        const du = dados && dados.duende;
        if (!du || typeof du !== 'object') return;
        if (q(ids().natureza) && du.natureza) q(ids().natureza).value = du.natureza;
        if (q(ids().naturezaAttr) && du.natureza_atributo) {
            q(ids().naturezaAttr).value = du.natureza_atributo;
        }
        if (q(ids().tamanho) && du.tamanho_raca) q(ids().tamanho).value = du.tamanho_raca;
        const dons = Array.isArray(du.dons) ? du.dons : [];
        if (q(ids().donA) && dons[0]) q(ids().donA).value = dons[0];
        if (q(ids().donB) && dons[1]) q(ids().donB).value = dons[1];
        if (q(ids().tabuTexto) && du.tabu_texto != null) q(ids().tabuTexto).value = du.tabu_texto;
        if (q(ids().tabuPen) && du.tabu_penalidade) q(ids().tabuPen).value = du.tabu_penalidade;
        if (q(ids().aleatorio)) q(ids().aleatorio).checked = !!du.geracao_aleatoria;
        void atualizarUi().then(() => {
            const saved = Array.isArray(du.presentes) ? du.presentes : [];
            const host = q(ids().presentesHost);
            if (host) {
                host.querySelectorAll('input[data-duende-presente]').forEach((inp) => {
                    const s = String(inp.getAttribute('data-duende-presente') || '').toLowerCase();
                    inp.checked = saved.includes(s);
                });
            }
            aplicarPresentesOpcoes(du.presentes_opcoes || {});
            aplicarTrocas(du.trocas_poder_presente || []);
            atualizarHintPresentes();
        });
    }

    function resumo() {
        if (!isDuendeSelecionado()) return '';
        const parts = [];
        const nat = q(ids().natureza) && q(ids().natureza).selectedOptions[0];
        if (nat) parts.push(`Duende ${nat.textContent}`);
        const tam = q(ids().tamanho) && q(ids().tamanho).selectedOptions[0];
        if (tam) parts.push(tam.textContent);
        const n = presentesMarcados().length;
        if (n) parts.push(`${n} presente(s)`);
        const nt = lerTrocasPoderPresente().length;
        if (nt) parts.push(`${nt} troca(s)`);
        return parts.join(' · ');
    }

    function reset() {
        [
            ids().natureza,
            ids().naturezaAttr,
            ids().tamanho,
            ids().donA,
            ids().donB,
            ids().tabuTexto,
            ids().tabuPen,
        ].forEach((id) => {
            const el = q(id);
            if (el) el.value = '';
        });
        if (q(ids().aleatorio)) q(ids().aleatorio).checked = false;
        const host = q(ids().presentesHost);
        if (host) host.innerHTML = '';
        const op = q(ids().opcoesHost);
        if (op) op.innerHTML = '';
        const th = q(ids().trocasHost);
        if (th) th.innerHTML = '';
    }

    async function rolarAleatorio() {
        try {
            const data = await new TormentaRegrasService().obterDuendeAleatorio();
            const cfg = (data && data.config) || {};
            preencher({ duende: cfg });
            if (q(ids().aleatorio)) q(ids().aleatorio).checked = true;
            if (global.Toast) {
                global.Toast.info('Duende aleatório rolado — defina o tabu e revise as escolhas.');
            }
            notificarMudanca();
        } catch (e) {
            if (global.Toast) global.Toast.error('Falha ao rolar Duende aleatório.');
        }
    }

    function bindOnce() {
        if (global.__t20DuendeV13Bound) return;
        global.__t20DuendeV13Bound = true;
        Object.keys(CONTEXTS).forEach((name) => {
            const c = CONTEXTS[name];
            q(c.natureza)?.addEventListener('change', () => {
                atualizarUiNaturezaAttr();
                notificarMudanca();
            });
            [c.tamanho, c.donA, c.donB, c.naturezaAttr].forEach((id) => {
                q(id)?.addEventListener('change', () => notificarMudanca());
            });
            q(c.btnRolar)?.addEventListener('click', () => void rolarAleatorio());
            if (c.nivelInput) {
                q(c.nivelInput)?.addEventListener('change', () => {
                    if (ctx === CONTEXTS.ficha && isDuendeSelecionado()) {
                        renderTrocas();
                        notificarMudanca();
                    }
                });
            }
        });
    }

    function init() {
        bindOnce();
    }

    function initFicha() {
        setContext('ficha');
        bindOnce();
    }

    global.T20DuendeV13 = {
        init,
        initFicha,
        setContext,
        atualizarUi,
        validar,
        lerPayload,
        preencher,
        aplicarPayload: preencher,
        resumo,
        reset,
        modificadoresAtributos,
        optsPreviewTracos,
        isDuendeSelecionado,
    };
})(typeof window !== 'undefined' ? window : globalThis);
