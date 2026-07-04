/**
 * Troca de perícia de origem (Heróis de Arton) na ficha v1.3 — paridade com wizard.
 */
(function (global) {
    'use strict';

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

    function slugParaLabel(slug) {
        return String(slug || '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, (c) => c.toUpperCase());
    }

    function nomePorSlug(slug) {
        const s = String(slug || '').trim().toLowerCase();
        const rows = document.querySelectorAll('#tblPericias tbody tr[data-per-slug]');
        for (const tr of rows) {
            if (String(tr.getAttribute('data-per-slug') || '').trim().toLowerCase() === s) {
                const nomeEl = tr.querySelector('.t20-p-nome');
                if (nomeEl && nomeEl.textContent.trim()) return nomeEl.textContent.trim();
            }
        }
        return slugParaLabel(s);
    }

    function getClasseRow() {
        if (typeof global.getClasseMbRowPorSlug !== 'function') return null;
        const slug = (q('f_classe_mb') && q('f_classe_mb').value) || '';
        return slug ? global.getClasseMbRowPorSlug(slug) : null;
    }

    function slugsFixas(c) {
        if (!c || !Array.isArray(c.pericias_fixas)) return [];
        return c.pericias_fixas.map((s) => String(s).trim().toLowerCase());
    }

    function slugsPoolClasse(c) {
        if (!c) return new Set();
        const out = new Set(slugsFixas(c));
        (c.pericias_escolha_de || []).forEach((s) => out.add(String(s).trim().toLowerCase()));
        (c.pericias_escolha_um_de || []).forEach((gr) => {
            (gr || []).forEach((s) => out.add(String(s).trim().toLowerCase()));
        });
        return out;
    }

    function origemBeneficios() {
        const picks = global.__t20OrigemBeneficios;
        return Array.isArray(picks) ? picks.slice() : [];
    }

    function slugsOrigemPericias() {
        return origemBeneficios()
            .filter((b) => String(b).startsWith('pericia:'))
            .map((b) => String(b).slice('pericia:'.length).trim().toLowerCase())
            .filter(Boolean);
    }

    function origemTrocasMap() {
        const raw = global.__t20OrigemTrocasPericia;
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

    function treinadosAtuaisSemOrigem(c) {
        const out = new Set(slugsFixas(c));
        document.querySelectorAll('#tblPericias tbody tr[data-per-slug]').forEach((tr) => {
            const slug = String(tr.getAttribute('data-per-slug') || '').trim().toLowerCase();
            const cb = tr.querySelector('.p-treinado');
            if (slug && cb && cb.checked) out.add(slug);
        });
        return out;
    }

    function periciasOrigemRedundantes() {
        const c = getClasseRow();
        if (!c) return [];
        const pool = slugsPoolClasse(c);
        const treinados = treinadosAtuaisSemOrigem(c);
        return slugsOrigemPericias().filter((slug) => pool.has(slug) && treinados.has(slug));
    }

    function opcoesTrocaPara(slugDe, c) {
        const pool = slugsPoolClasse(c);
        const treinados = treinadosAtuaisSemOrigem(c);
        const trocas = origemTrocasMap();
        const usados = new Set(Object.values(trocas));
        return Array.from(pool).filter((slug) => {
            if (slug === slugDe) return false;
            if (treinados.has(slug)) return false;
            if (usados.has(slug)) return false;
            return true;
        });
    }

    function origemPermiteTroca() {
        if (!global.T20OrigensV13 || typeof global.T20OrigensV13.origemPorSlug !== 'function') {
            return false;
        }
        const slug = q('f_origem_slug') && q('f_origem_slug').value;
        const row = global.T20OrigensV13.origemPorSlug(slug);
        return Boolean(row && row.troca_pericia_treinada);
    }

    function renderUi() {
        const host = q('fOrigemTrocasHost');
        if (!host || !isV13()) return;
        const c = getClasseRow();
        const permite = origemPermiteTroca();
        const redundantes = c ? periciasOrigemRedundantes() : [];
        if (!permite || !redundantes.length) {
            host.innerHTML = '';
            host.style.display = 'none';
            return;
        }
        host.style.display = '';
        const trocas = origemTrocasMap();
        host.innerHTML =
            '<p class="t20-hint" style="margin:0 0 .35rem">' +
            '<strong>Troca de perícia (Heróis de Arton):</strong> benefício de origem coincide com perícia de classe. ' +
            'Opcionalmente troque por outra da lista de classe.</p>' +
            redundantes
                .map((slugDe) => {
                    const opts = opcoesTrocaPara(slugDe, c);
                    const cur = trocas[slugDe] || '';
                    return (
                        `<div class="t20-ficha-field" style="margin:0 0 .5rem">` +
                        `<label for="fOrigemTroca_${slugDe}">${nomePorSlug(slugDe)} (já da classe) →</label>` +
                        `<select id="fOrigemTroca_${slugDe}" class="t20-input f-origem-troca-sel" data-troca-de="${slugDe}">` +
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
        host.querySelectorAll('.f-origem-troca-sel').forEach((sel) => {
            sel.addEventListener('change', () => {
                const de = String(sel.getAttribute('data-troca-de') || '').trim().toLowerCase();
                if (!global.__t20OrigemTrocasPericia) global.__t20OrigemTrocasPericia = {};
                const para = String(sel.value || '').trim().toLowerCase();
                if (para) global.__t20OrigemTrocasPericia[de] = para;
                else delete global.__t20OrigemTrocasPericia[de];
                if (typeof global.t20AplicarPericiasOrigemBeneficios === 'function') {
                    global.t20AplicarPericiasOrigemBeneficios();
                }
                renderUi();
                if (typeof global.t20ValidarPericiasOrcamentoMb === 'function') {
                    void global.t20ValidarPericiasOrcamentoMb();
                }
            });
        });
    }

    function lerPayload() {
        if (!isV13()) return {};
        const trocas = origemTrocasMap();
        if (!Object.keys(trocas).length) return {};
        return { origem_trocas_pericia: trocas };
    }

    function aplicarPayload(fj) {
        if (!fj || typeof fj !== 'object') {
            global.__t20OrigemTrocasPericia = {};
            return;
        }
        const raw = fj.origem_trocas_pericia;
        if (!raw || typeof raw !== 'object') {
            global.__t20OrigemTrocasPericia = {};
            return;
        }
        const out = {};
        Object.keys(raw).forEach((k) => {
            const de = String(k || '').trim().toLowerCase();
            const para = String(raw[k] || '').trim().toLowerCase();
            if (de && para) out[de] = para;
        });
        global.__t20OrigemTrocasPericia = out;
    }

    function bindOnce() {
        if (global.__t20OrigemTrocasFichaBound) return;
        global.__t20OrigemTrocasFichaBound = true;
        const tbl = q('tblPericias');
        if (tbl) {
            tbl.addEventListener('change', () => {
                if (isV13()) renderUi();
            });
        }
        q('f_classe_mb')?.addEventListener('change', () => renderUi());
        q('f_origem_slug')?.addEventListener('change', () => {
            global.__t20OrigemTrocasPericia = {};
            renderUi();
        });
    }

    function init() {
        bindOnce();
    }

    global.T20OrigemTrocasFichaV13 = {
        init,
        renderUi,
        origemTrocasMap,
        slugsOrigemEfetivos,
        lerPayload,
        aplicarPayload,
    };
})(typeof window !== 'undefined' ? window : globalThis);
