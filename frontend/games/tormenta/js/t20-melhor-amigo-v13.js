/**
 * Melhor Amigo — Treinador (Heróis de Arton) no wizard de criação e na ficha v1.3.
 */
(function (global) {
    'use strict';

    const CONTEXTS = {
        wizard: {
            wrap: 'cadWrapMelhorAmigo',
            nome: 'cadMelhorAmigoNome',
            tipo: 'cadMelhorAmigoTipo',
            tipoHint: 'cadMelhorAmigoTipoHint',
            truquesHost: 'cadMelhorAmigoTruquesHost',
            truquesHint: 'cadMelhorAmigoTruquesHint',
            classeSel: 'cadClasseMb',
            nivel: 'cadNivel',
            truquesState: '__cadMelhorAmigoTruques',
        },
        ficha: {
            wrap: 'fWrapMelhorAmigo',
            nome: 'f_melhor_amigo_nome',
            tipo: 'f_melhor_amigo_tipo',
            tipoHint: 'f_melhor_amigo_tipo_hint',
            truquesHost: 'f_melhor_amigo_truques_host',
            truquesHint: 'f_melhor_amigo_truques_hint',
            classeSel: 'f_classe_mb',
            nivel: 'f_nivel',
            truquesState: '__fichaMelhorAmigoTruques',
        },
    };

    let ctx = CONTEXTS.wizard;
    let tipos = [];
    let truques = [];
    let qtdMaxTruques = 2;

    function q(id) {
        return document.getElementById(id);
    }

    function ids() {
        return ctx;
    }

    function setContext(name) {
        ctx = CONTEXTS[name] || CONTEXTS.wizard;
    }

    function isFichaMode() {
        return ctx === CONTEXTS.ficha;
    }

    function linhasMulticlasseTreinador() {
        if (!isFichaMode()) return [];
        const w = q('t20MulticlasseV13Lista');
        if (!w) return [];
        const out = [];
        w.querySelectorAll('[data-t20-multiclasse-v13]').forEach((row) => {
            const sl = row.querySelector('.t20-multiclasse-slug');
            const nv = row.querySelector('.t20-multiclasse-niv');
            const st = String((sl && sl.value) || '').trim().toLowerCase();
            if (st !== 'treinador') return;
            const n = Math.max(1, parseInt(String((nv && nv.value) || '1'), 10) || 1);
            out.push(n);
        });
        return out;
    }

    function isTreinadorSelecionado() {
        const sel = q(ids().classeSel);
        if (sel && String(sel.value || '').trim().toLowerCase() === 'treinador') return true;
        if (isFichaMode() && linhasMulticlasseTreinador().length) return true;
        return false;
    }

    function nivelTreinador() {
        if (isFichaMode()) {
            const linhas = linhasMulticlasseTreinador();
            if (linhas.length) {
                return Math.max(1, linhas.reduce((acc, n) => acc + n, 0));
            }
            const sel = q(ids().classeSel);
            if (sel && String(sel.value || '').trim().toLowerCase() === 'treinador') {
                const n = parseInt(String(q(ids().nivel) && q(ids().nivel).value || '1'), 10);
                return Number.isFinite(n) && n >= 1 ? n : 1;
            }
            return 1;
        }
        const n = parseInt(String(q(ids().nivel) && q(ids().nivel).value || '1'), 10);
        return Number.isFinite(n) && n >= 1 ? n : 1;
    }

    function slugParaLabel(slug) {
        return String(slug || '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, (c) => c.toUpperCase());
    }

    async function carregarCatalogos() {
        if (!isTreinadorSelecionado()) {
            tipos = [];
            truques = [];
            return;
        }
        try {
            const svc = new TormentaRegrasService();
            const nv = nivelTreinador();
            const [tTipos, tTruques] = await Promise.all([
                svc.obterTiposMelhorAmigo(),
                svc.obterTruquesMelhorAmigo({ nivelTreinador: nv }),
            ]);
            tipos = Array.isArray(tTipos.tipos) ? tTipos.tipos : [];
            truques = Array.isArray(tTruques.truques) ? tTruques.truques : [];
            qtdMaxTruques = Number(tTruques.qtd_maxima_truques) || 2;
        } catch (_e) {
            tipos = [];
            truques = [];
            qtdMaxTruques = 2;
        }
    }

    function truquesSelecionados() {
        const key = ids().truquesState;
        if (Array.isArray(global[key]) && global[key].length) {
            return global[key].slice();
        }
        const host = q(ids().truquesHost);
        if (!host) return [];
        return Array.from(host.querySelectorAll('input[data-ma-truque]:checked')).map((inp) =>
            String(inp.getAttribute('data-ma-truque') || '').trim().toLowerCase()
        );
    }

    function salvarTruquesEstado() {
        global[ids().truquesState] = truquesSelecionados();
    }

    function renderTruques() {
        const host = q(ids().truquesHost);
        const hint = q(ids().truquesHint);
        if (!host) return;
        const saved = new Set(truquesSelecionados());
        if (!truques.length) {
            host.innerHTML = '<p class="t20-hint" style="margin:0">Carregando truques…</p>';
            if (hint) hint.textContent = '';
            return;
        }
        host.innerHTML = truques
            .map((t) => {
                const slug = String(t.slug || '').trim().toLowerCase();
                const pre = t.pre_requisito
                    ? ` <span class="t20-hint">(exige ${slugParaLabel(t.pre_requisito)})</span>`
                    : '';
                return (
                    `<label style="display:block;margin:.2rem 0;cursor:pointer">` +
                    `<input type="checkbox" data-ma-truque="${slug}" ${saved.has(slug) ? 'checked' : ''}/> ` +
                    `${t.nome || slugParaLabel(slug)}${pre}` +
                    `</label>`
                );
            })
            .join('');
        host.querySelectorAll('input[data-ma-truque]').forEach((inp) => {
            inp.addEventListener('change', () => {
                const picks = truquesSelecionados();
                if (picks.length > qtdMaxTruques) {
                    inp.checked = false;
                    if (global.Toast) global.Toast.error(`Máximo ${qtdMaxTruques} truques neste nível.`);
                    return;
                }
                const slug = String(inp.getAttribute('data-ma-truque') || '').toLowerCase();
                const row = truques.find((x) => x.slug === slug);
                const pre = row && row.pre_requisito ? String(row.pre_requisito).toLowerCase() : '';
                if (pre && inp.checked && !picks.includes(pre)) {
                    inp.checked = false;
                    if (global.Toast) {
                        global.Toast.error(`Truque exige «${slugParaLabel(pre)}» marcado antes.`);
                    }
                    return;
                }
                atualizarHintTruques();
                salvarTruquesEstado();
                if (isFichaMode() && typeof global.t20AtualizarEstadoBotaoSalvar === 'function') {
                    global.t20AtualizarEstadoBotaoSalvar();
                }
            });
        });
        salvarTruquesEstado();
        atualizarHintTruques();
    }

    function atualizarHintTruques() {
        const hint = q(ids().truquesHint);
        if (!hint) return;
        const n = truquesSelecionados().length;
        hint.textContent = `${n}/${qtdMaxTruques} truques escolhidos (nível ${nivelTreinador()} do Treinador).`;
    }

    function renderTipoBonus() {
        const el = q(ids().tipoHint);
        const sel = q(ids().tipo);
        if (!el || !sel) return;
        const row = tipos.find((t) => t.slug === String(sel.value || '').toLowerCase());
        if (!row) {
            el.textContent = '';
            return;
        }
        const attrs = row.bonus_atributos || {};
        const parts = Object.keys(attrs)
            .map((k) => `${k.toUpperCase()} ${attrs[k] >= 0 ? '+' : ''}${attrs[k]}`)
            .join(', ');
        const per = row.bonus_pericias || {};
        const perParts = Object.keys(per)
            .map((k) => `${slugParaLabel(k)} +${per[k]}`)
            .join(', ');
        let txt = parts ? `Bônus: ${parts}.` : '';
        if (perParts) txt += (txt ? ' ' : '') + `Perícias: ${perParts}.`;
        if (row.notas) txt += (txt ? ' ' : '') + row.notas;
        el.textContent = txt;
    }

    async function atualizarUi() {
        const wrap = q(ids().wrap);
        if (!wrap) return;
        const show = isTreinadorSelecionado();
        wrap.style.display = show ? '' : 'none';
        if (!show) return;
        await carregarCatalogos();
        const selTipo = q(ids().tipo);
        if (selTipo) {
            const prev = selTipo.value;
            selTipo.innerHTML = '<option value="">— Tipo do parceiro —</option>';
            tipos.forEach((t) => {
                const op = document.createElement('option');
                op.value = t.slug;
                op.textContent = t.nome || slugParaLabel(t.slug);
                selTipo.appendChild(op);
            });
            if (prev) selTipo.value = prev;
        }
        renderTruques();
        renderTipoBonus();
    }

    function validar() {
        if (!isTreinadorSelecionado()) return { ok: true };
        const nome = (q(ids().nome) && q(ids().nome).value.trim()) || '';
        const tipo = (q(ids().tipo) && q(ids().tipo).value) || '';
        const picks = truquesSelecionados();
        if (!nome) {
            return { ok: false, msg: 'Treinador: informe o nome do Melhor Amigo.' };
        }
        if (!tipo) {
            return { ok: false, msg: 'Treinador: escolha o tipo do Melhor Amigo.' };
        }
        if (!picks.length) {
            return { ok: false, msg: 'Treinador: escolha ao menos 1 truque do Melhor Amigo.' };
        }
        if (picks.length > qtdMaxTruques) {
            return {
                ok: false,
                msg: `Treinador: máximo ${qtdMaxTruques} truques do Melhor Amigo neste nível.`,
            };
        }
        for (const slug of picks) {
            const row = truques.find((t) => t.slug === slug);
            const pre = row && row.pre_requisito ? String(row.pre_requisito).toLowerCase() : '';
            if (pre && !picks.includes(pre)) {
                return {
                    ok: false,
                    msg: `Truque «${slugParaLabel(slug)}» exige «${slugParaLabel(pre)}».`,
                };
            }
        }
        return { ok: true };
    }

    function lerPayload() {
        if (!isTreinadorSelecionado()) return {};
        const nome = (q(ids().nome) && q(ids().nome).value.trim()) || '';
        const tipo = (q(ids().tipo) && q(ids().tipo).value) || '';
        if (!nome || !tipo) return {};
        return {
            melhor_amigo: {
                nome,
                tipo: String(tipo).trim().toLowerCase(),
                truques: truquesSelecionados(),
                nivel: nivelTreinador(),
            },
        };
    }

    function aplicarPayload(fj) {
        if (!fj || typeof fj !== 'object') return;
        const ma = fj.melhor_amigo;
        if (!ma || typeof ma !== 'object') {
            reset();
            return;
        }
        global[ids().truquesState] = Array.isArray(ma.truques)
            ? ma.truques.map((s) => String(s || '').trim().toLowerCase()).filter(Boolean)
            : [];
        if (q(ids().nome)) q(ids().nome).value = ma.nome != null ? String(ma.nome) : '';
        if (q(ids().tipo)) q(ids().tipo).value = ma.tipo != null ? String(ma.tipo).trim().toLowerCase() : '';
        void atualizarUi();
    }

    function resumo() {
        if (!isTreinadorSelecionado()) return '';
        const nome = (q(ids().nome) && q(ids().nome).value.trim()) || '';
        const tipo = (q(ids().tipo) && q(ids().tipo).selectedOptions[0]);
        if (!nome) return '';
        const tr = truquesSelecionados();
        return `Melhor Amigo: ${nome} (${tipo ? tipo.textContent : '—'}) · ${tr.length} truque(s)`;
    }

    function reset() {
        global[ids().truquesState] = [];
        if (q(ids().nome)) q(ids().nome).value = '';
        if (q(ids().tipo)) q(ids().tipo).value = '';
        const host = q(ids().truquesHost);
        if (host) host.innerHTML = '';
        if (q(ids().truquesHint)) q(ids().truquesHint).textContent = '';
        if (q(ids().tipoHint)) q(ids().tipoHint).textContent = '';
    }

    function bindOnce() {
        if (global.__t20MelhorAmigoV13Bound) return;
        global.__t20MelhorAmigoV13Bound = true;
        ['cadMelhorAmigoTipo', 'f_melhor_amigo_tipo'].forEach((id) => {
            q(id)?.addEventListener('change', () => {
                renderTipoBonus();
                if (global.T20DashWizardV13 && global.T20DashWizardV13.renderResumo) {
                    global.T20DashWizardV13.renderResumo();
                }
                if (typeof global.t20AtualizarEstadoBotaoSalvar === 'function') {
                    global.t20AtualizarEstadoBotaoSalvar();
                }
            });
        });
        ['cadMelhorAmigoNome', 'f_melhor_amigo_nome'].forEach((id) => {
            q(id)?.addEventListener('input', () => {
                if (global.T20DashWizardV13 && global.T20DashWizardV13.renderResumo) {
                    global.T20DashWizardV13.renderResumo();
                }
                if (typeof global.t20AtualizarEstadoBotaoSalvar === 'function') {
                    global.t20AtualizarEstadoBotaoSalvar();
                }
            });
        });
    }

    function initFicha() {
        setContext('ficha');
        bindOnce();
        const w = q('t20MulticlasseV13Lista');
        if (w && !w.dataset.t20MaBound) {
            w.dataset.t20MaBound = '1';
            w.addEventListener('change', () => {
                void atualizarUi();
            });
            w.addEventListener('input', () => {
                void atualizarUi();
            });
        }
    }

    bindOnce();

    global.T20MelhorAmigoV13 = {
        setContext,
        initFicha,
        atualizarUi,
        validar,
        lerPayload,
        aplicarPayload,
        resumo,
        reset,
        isTreinadorSelecionado,
    };
})(typeof window !== 'undefined' ? window : globalThis);
