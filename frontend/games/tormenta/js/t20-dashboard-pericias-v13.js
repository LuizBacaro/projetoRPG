/**
 * Dashboard wizard v1.3 — passo Perícias (orçamento classe + INT + racial + origem).
 */
(function (global) {
    'use strict';

    let cfg = null;
    let catalogo = [];
    let cfgClasse = null;
    let slugToNome = {};
    let atributosCatalogo = [];

    function q(id) {
        return document.getElementById(id);
    }

    function isV13Wizard() {
        return (
            cfg &&
            cfg.regraVersao === 'v13' &&
            global.T20DashWizardV13 &&
            global.T20DashWizardV13.isWizardAtivo &&
            global.T20DashWizardV13.isWizardAtivo()
        );
    }

    function classeSlug() {
        const sel = q('cadClasseMb');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    function slugRaca() {
        const sel = q('cadRacaSelect');
        const v = sel && sel.value;
        if (!v || v === '__livre__') return '';
        return String(v).trim().toLowerCase();
    }

    function getCadRacialDeltasPericias() {
        return (global.__t20GetCadRacialDeltas && global.__t20GetCadRacialDeltas()) || {};
    }

    function intValorFinal() {
        const n = Number(q('cadInt') && q('cadInt').value);
        const base = Number.isFinite(n) ? Math.floor(n) : 0;
        return base + (getCadRacialDeltasPericias().int || 0);
    }

    function nivelCadastro() {
        const n = parseInt(String(q('cadNivel') && q('cadNivel').value || '1'), 10);
        return Number.isFinite(n) && n >= 0 ? n : 1;
    }

    function humanoVersatilModo() {
        const el = q('cadHumanoVersatil');
        const v = el && el.value ? String(el.value).trim() : '';
        return v && v !== 'duas_pericias' ? v : null;
    }

    function origemSlug() {
        const sel = q('cadOrigemSlug');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    function origemBeneficios() {
        const picks = global.__cadOrigemBeneficios;
        return Array.isArray(picks) ? picks.slice() : [];
    }

    function slugsOrigemPericias() {
        return origemBeneficios()
            .filter((b) => String(b).startsWith('pericia:'))
            .map((b) => String(b).slice('pericia:'.length).trim().toLowerCase())
            .filter(Boolean);
    }

    function origemTrocasMap() {
        const raw = global.__cadOrigemTrocasPericia;
        if (!raw || typeof raw !== 'object') return {};
        const out = {};
        Object.keys(raw).forEach((k) => {
            const de = String(k || '').trim().toLowerCase();
            const para = String(raw[k] || '').trim().toLowerCase();
            if (de && para) out[de] = para;
        });
        return out;
    }

    function slugsOrigemEfetivos() {
        const trocas = origemTrocasMap();
        const out = new Set();
        slugsOrigemPericias().forEach((slug) => {
            if (trocas[slug]) out.add(trocas[slug]);
            else out.add(slug);
        });
        return out;
    }

    function treinadosAtuaisSemOrigem() {
        const out = new Set(slugsFixas());
        const host = q('cadPericiasHost');
        if (host) {
            host.querySelectorAll('input[data-pericia-slug]').forEach((inp) => {
                const slug = String(inp.getAttribute('data-pericia-slug') || '').trim().toLowerCase();
                if (slug && inp.checked) out.add(slug);
            });
        }
        return out;
    }

    function periciasOrigemRedundantes() {
        const pool = slugsPoolClasse();
        const treinados = treinadosAtuaisSemOrigem();
        return slugsOrigemPericias().filter((slug) => pool.has(slug) && treinados.has(slug));
    }

    function opcoesTrocaPara(slugDe) {
        const pool = slugsPoolClasse();
        const treinados = treinadosAtuaisSemOrigem();
        const trocas = origemTrocasMap();
        const usados = new Set(Object.values(trocas));
        return Array.from(pool).filter((slug) => {
            if (slug === slugDe) return false;
            if (treinados.has(slug)) return false;
            if (usados.has(slug)) return false;
            return true;
        });
    }

    function renderOrigemTrocas() {
        const host = q('cadOrigemTrocasHost');
        if (!host) return;
        const permite = Boolean(global.__cadOrigemPermiteTroca);
        const redundantes = periciasOrigemRedundantes();
        if (!permite || !redundantes.length) {
            host.innerHTML = '';
            host.style.display = 'none';
            return;
        }
        host.style.display = '';
        const trocas = origemTrocasMap();
        host.innerHTML =
            '<p class="t20-dash-hint" style="margin:0 0 .35rem">' +
            '<strong>Troca de perícia (Heróis de Arton):</strong> benefício de origem coincide com perícia de classe. ' +
            'Opcionalmente troque por outra da lista de classe.</p>' +
            redundantes
                .map((slugDe) => {
                    const opts = opcoesTrocaPara(slugDe);
                    const cur = trocas[slugDe] || '';
                    return (
                        `<div class="t20-dash-field" style="margin:0 0 .5rem">` +
                        `<label for="cadOrigemTroca_${slugDe}">${nomePorSlug(slugDe)} (já da classe) →</label>` +
                        `<select id="cadOrigemTroca_${slugDe}" class="t20-input cad-origem-troca-sel" data-troca-de="${slugDe}">` +
                        `<option value="">— Manter sem vaga extra —</option>` +
                        opts
                            .map(
                                (slug) =>
                                    `<option value="${slug}" ${cur === slug ? 'selected' : ''}>${nomePorSlug(slug)}</option>`
                            )
                            .join('') +
                        `</select></div>`
                    );
                })
                .join('');
        host.querySelectorAll('.cad-origem-troca-sel').forEach((sel) => {
            sel.addEventListener('change', () => {
                const de = String(sel.getAttribute('data-troca-de') || '').trim().toLowerCase();
                if (!global.__cadOrigemTrocasPericia) global.__cadOrigemTrocasPericia = {};
                const para = String(sel.value || '').trim().toLowerCase();
                if (para) global.__cadOrigemTrocasPericia[de] = para;
                else delete global.__cadOrigemTrocasPericia[de];
                renderUiPericias();
                void atualizarHintOrcamento();
            });
        });
    }

    function slugsBloqueadosOrigem() {
        return slugsOrigemEfetivos();
    }

    function nomePorSlug(slug) {
        const s = String(slug || '').trim().toLowerCase();
        if (slugToNome[s]) return slugToNome[s];
        return s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    }

    async function carregarCatalogos() {
        if (!isV13Wizard()) return;
        const slug = classeSlug();
        if (!slug) {
            catalogo = [];
            atributosCatalogo = [];
            cfgClasse = null;
            return;
        }
        try {
            const svc = new TormentaRegrasService();
            const [atributos, cls] = await Promise.all([
                svc.obterAtributos({ regraVersao: 'v13' }),
                svc.obterPericiasClassePreview(slug),
            ]);
            atributosCatalogo = Array.isArray(atributos && atributos.pericias) ? atributos.pericias : [];
            catalogo = atributosCatalogo.map((p) => ({
                slug: String(p.slug || '').trim().toLowerCase(),
                nome: String(p.nome || '').trim(),
                somente_treinado: Boolean(p.somente_treinado),
                penalidade_armadura: Boolean(p.penalidade_armadura),
            })).filter((p) => p.slug && p.nome);
            slugToNome = {};
            catalogo.forEach((p) => {
                if (p.slug && p.nome) slugToNome[p.slug] = p.nome;
            });
            cfgClasse = cls || null;
        } catch (_e) {
            catalogo = [];
            atributosCatalogo = [];
            cfgClasse = null;
        }
    }

    function slugsFixas() {
        if (!cfgClasse || !Array.isArray(cfgClasse.pericias_fixas)) return [];
        return cfgClasse.pericias_fixas.map((s) => String(s).trim().toLowerCase());
    }

    function slugsPoolClasse() {
        if (!cfgClasse) return new Set();
        const out = new Set(slugsFixas());
        (cfgClasse.pericias_escolha_de || []).forEach((s) => out.add(String(s).trim().toLowerCase()));
        (cfgClasse.pericias_escolha_um_de || []).forEach((gr) => {
            (gr || []).forEach((s) => out.add(String(s).trim().toLowerCase()));
        });
        return out;
    }

    function renderUiPericias() {
        const host = q('cadPericiasHost');
        const hint = q('cadPericiasHint');
        if (!host) return;
        if (!isV13Wizard() || !classeSlug()) {
            host.innerHTML = '';
            if (hint) hint.textContent = '';
            const trocaHost = q('cadOrigemTrocasHost');
            if (trocaHost) {
                trocaHost.innerHTML = '';
                trocaHost.style.display = 'none';
            }
            return;
        }
        renderOrigemTrocas();
        const fixas = new Set(slugsFixas());
        const pool = slugsPoolClasse();
        const origemSlugs = slugsBloqueadosOrigem();
        const prev = global.__cadPericiasTreinadas || {};
        const rows = catalogo.length
            ? catalogo
            : Object.keys(slugToNome).map((slug) => ({ slug, nome: slugToNome[slug] }));

        rows.sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));

        host.innerHTML = rows
            .map((p) => {
                const checked =
                    fixas.has(p.slug) ||
                    origemSlugs.has(p.slug) ||
                    Boolean(prev[p.slug]);
                const disabled = fixas.has(p.slug) || origemSlugs.has(p.slug);
                let tag = '';
                if (fixas.has(p.slug)) tag = ' <span class="t20-dash-hint">(classe)</span>';
                else if (origemSlugs.has(p.slug)) tag = ' <span class="t20-dash-hint">(origem)</span>';
                else if (pool.has(p.slug)) tag = ' <span class="t20-dash-hint">(lista classe)</span>';
                return (
                    `<label class="cad-pericia-check" style="display:flex;align-items:flex-start;gap:0.5rem;margin:0;cursor:pointer;line-height:1.35">` +
                    `<input type="checkbox" data-pericia-slug="${p.slug}" ${checked ? 'checked' : ''} ${disabled ? 'disabled' : ''} />` +
                    `<span>${p.nome}${tag}</span></label>`
                );
            })
            .join('');

        host.querySelectorAll('input[data-pericia-slug]').forEach((inp) => {
            if (inp.disabled) return;
            inp.addEventListener('change', () => {
                renderOrigemTrocas();
                void atualizarHintOrcamento();
            });
        });
        void atualizarHintOrcamento();
    }

    function coletarPericiasPayload() {
        const out = [];
        const host = q('cadPericiasHost');
        if (!host) return out;
        host.querySelectorAll('input[data-pericia-slug]').forEach((inp) => {
            const slug = inp.getAttribute('data-pericia-slug') || '';
            const nome = nomePorSlug(slug);
            const meta = catalogo.find((p) => String(p.slug || '').toLowerCase() === slug) || {};
            out.push({
                nome,
                treinado: Boolean(inp.checked),
                graduacao: 0,
                somente_treinado: Boolean(meta.somente_treinado),
                penalidade_armadura: Boolean(meta.penalidade_armadura),
            });
        });
        return out;
    }

    function salvarEstadoChecks() {
        const map = {};
        const host = q('cadPericiasHost');
        if (!host) return;
        host.querySelectorAll('input[data-pericia-slug]').forEach((inp) => {
            const slug = inp.getAttribute('data-pericia-slug') || '';
            if (slug && inp.checked) map[slug] = true;
        });
        global.__cadPericiasTreinadas = map;
    }

    async function atualizarHintOrcamento() {
        salvarEstadoChecks();
        const hint = q('cadPericiasHint');
        const slug = classeSlug();
        if (!hint || !slug) return;
        try {
            const preview = await new TormentaRegrasService().validarPericiasCriacao({
                nivel: Math.max(1, nivelCadastro()),
                classe_slug: slug,
                int_valor: intValorFinal(),
                slug_raca: slugRaca() || null,
                pericias: coletarPericiasPayload(),
                regraVersao: 'v13',
                humanoVersatil: humanoVersatilModo(),
                origem_beneficios: origemBeneficios(),
                origemSlug: origemSlug() || null,
                origemTrocasPericia: origemTrocasMap(),
            });
            const tr = `${preview.usadas_treinadas}/${preview.vagas_treinadas} treinadas`;
            const ok = preview.valido ? 'OK' : 'incompleto';
            hint.textContent = preview.motivo
                ? `${tr} — ${preview.motivo}`
                : `Orçamento v1.3 (${ok}): ${tr}.`;
            hint.className = preview.valido
                ? 't20-dash-hint t20-compra-pontos-ok'
                : 't20-dash-hint t20-compra-pontos-erro';
            global.__cadPericiasOrcamentoOk = Boolean(preview.valido);
            global.__cadPericiasOrcamentoMsg = preview.motivo || '';
            if (preview.valido) {
                global.__cadPericiasWizardCompleto = true;
            }
        } catch (e) {
            hint.textContent = e.message || 'Erro ao validar perícias.';
            hint.className = 't20-dash-hint t20-compra-pontos-erro';
            global.__cadPericiasOrcamentoOk = false;
        }
    }

    async function prepararPassoPericias() {
        if (!isV13Wizard()) return;
        await carregarCatalogos();
        renderUiPericias();
    }

    async function validarPassoPericias() {
        if (!isV13Wizard()) return { ok: true };
        const slug = classeSlug();
        if (!slug) {
            return { ok: false, msg: 'Selecione a classe no passo Raça e classe.' };
        }
        await atualizarHintOrcamento();
        if (!global.__cadPericiasOrcamentoOk) {
            return {
                ok: false,
                msg:
                    global.__cadPericiasOrcamentoMsg ||
                    'Complete o orçamento de perícias treinadas (v1.3).',
            };
        }
        return { ok: true };
    }

    function lerPayloadPericias() {
        if (!isV13Wizard()) return {};
        const lista = coletarPericiasPayload().filter((p) => p.treinado);
        const out = {};
        if (lista.length) {
            out.pericias = lista;
            out.pericias_wizard_v13 = true;
        }
        const trocas = origemTrocasMap();
        if (Object.keys(trocas).length) {
            out.origem_trocas_pericia = trocas;
        }
        return out;
    }

    function resumoPericias() {
        if (!isV13Wizard()) return '';
        const n = coletarPericiasPayload().filter((p) => p.treinado).length;
        const v = q('cadPericiasHint') && q('cadPericiasHint').textContent;
        return n ? `Perícias: ${n} treinadas${v ? ' · ' + v.split('—')[0].trim() : ''}` : '';
    }

    function invalidarPericias() {
        global.__cadPericiasWizardCompleto = false;
        global.__cadPericiasOrcamentoOk = false;
        global.__cadPericiasOrcamentoMsg = '';
    }

    function statusRevisao() {
        const treinadas = coletarPericiasPayload().filter((p) => p.treinado);
        const confirmado = Boolean(global.__cadPericiasWizardCompleto);
        const ok = Boolean(global.__cadPericiasOrcamentoOk) && confirmado && treinadas.length > 0;
        let msg = '';
        if (!classeSlug()) {
            msg = 'Selecione a classe.';
        } else if (!confirmado || treinadas.length === 0) {
            msg = 'Complete o passo Perícias antes de criar.';
        } else if (!global.__cadPericiasOrcamentoOk) {
            msg = global.__cadPericiasOrcamentoMsg || 'Orçamento de perícias incompleto.';
        }
        const hint = q('cadPericiasHint') && q('cadPericiasHint').textContent;
        return {
            ok,
            msg,
            detalhe: hint || '',
            treinadas: treinadas.length,
        };
    }

    async function refreshOrcamento() {
        if (!isV13Wizard() || !classeSlug()) return statusRevisao();
        if (!catalogo.length) await carregarCatalogos();
        if (q('cadPericiasHost') && !q('cadPericiasHost').querySelector('input[data-pericia-slug]')) {
            renderUiPericias();
        }
        await atualizarHintOrcamento();
        return statusRevisao();
    }

    function resetPericias() {
        global.__cadPericiasTreinadas = {};
        global.__cadOrigemTrocasPericia = {};
        global.__cadPericiasWizardCompleto = false;
        global.__cadPericiasOrcamentoOk = false;
        global.__cadPericiasOrcamentoMsg = '';
        if (q('cadPericiasHost')) q('cadPericiasHost').innerHTML = '';
        const trocaHost = q('cadOrigemTrocasHost');
        if (trocaHost) {
            trocaHost.innerHTML = '';
            trocaHost.style.display = 'none';
        }
        if (q('cadPericiasHint')) q('cadPericiasHint').textContent = '';
    }

    function init(config) {
        cfg = config || {};
    }

    global.T20DashPericiasV13 = {
        init,
        prepararPassoPericias,
        validarPassoPericias,
        lerPayloadPericias,
        resumoPericias,
        resetPericias,
        invalidarPericias,
        refreshOrcamento,
        statusRevisao,
    };
})(typeof window !== 'undefined' ? window : globalThis);
