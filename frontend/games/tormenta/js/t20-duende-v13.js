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
            tabuTexto: 'f_duende_tabu_texto',
            tabuPen: 'f_duende_tabu_penalidade',
            aleatorio: 'f_duende_geracao_aleatoria',
            btnRolar: 'fBtnDuendeRolar',
            racaSel: 'f_raca_select',
        },
    };

    let ctx = CONTEXTS.wizard;
    let opcoes = null;
    let presentes = [];
    let qtdPresentes = 3;

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
        hint.textContent = `${n}/${qtdPresentes} presentes escolhidos.`;
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

    function atualizarUiNaturezaAttr() {
        const wrap = q(ids().wrapNatAttr);
        const nat = q(ids().natureza);
        const show = nat && String(nat.value || '').toLowerCase() === 'animal';
        if (wrap) wrap.style.display = show ? '' : 'none';
        if (!show && q(ids().naturezaAttr)) q(ids().naturezaAttr).value = '';
    }

    function notificarMudanca() {
        if (global.T20TracosRaciaisV13 && isDuendeSelecionado()) {
            void global.T20TracosRaciaisV13.aplicarTracosRaciaisCadastro('duende');
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
        const pres = presentesMarcados();
        return {
            duendeTamanho: tam || 'medio',
            duendePresentes: pres.join(','),
        };
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
