/**
 * Multiclasse v1.3 — UI de níveis por classe e soma automática de PM (p.34).
 */
(function (global) {
    'use strict';

    let CLASSES_OBJ = [];
    let debouncePm = null;

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

    function escHtml(s) {
        return String(s || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function suplementoAtivo() {
        if (typeof global.t20GetSuplementoFichaAtivo === 'function') {
            return global.t20GetSuplementoFichaAtivo();
        }
        return null;
    }

    function catalogoClasses() {
        return CLASSES_OBJ.slice();
    }

    function slugsLista() {
        return CLASSES_OBJ.map((c) => String(c.slug || '').trim().toLowerCase()).filter(Boolean);
    }

    async function carregarSlugsClasses(force) {
        if (CLASSES_OBJ.length && !force) return slugsLista();
        try {
            const d = await new TormentaRegrasService().obterClasses({
                regraVersao: 'v13',
                suplemento: suplementoAtivo(),
            });
            CLASSES_OBJ = Array.isArray(d.classes) ? d.classes : [];
        } catch (_e) {
            CLASSES_OBJ = [];
        }
        return slugsLista();
    }

    function nivelPersonagem() {
        const n = Number(q('f_nivel') && q('f_nivel').value);
        return Number.isFinite(n) && n >= 1 ? Math.min(40, Math.floor(n)) : 1;
    }

    function classePrincipalSlug() {
        const sel = q('f_classe_mb');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    function slugsOutrasLinhas(excluirSlug) {
        const CV = global.T20ClassesVariantesV13;
        if (CV && typeof CV.slugsSelecionadosDeDom === 'function') {
            return CV.slugsSelecionadosDeDom(q, { excluirSlug: excluirSlug || '' });
        }
        const out = [];
        const main = classePrincipalSlug();
        if (main && main !== excluirSlug) out.push(main);
        const w = q('t20MulticlasseV13Lista');
        if (w) {
            w.querySelectorAll('[data-t20-multiclasse-v13]').forEach((row) => {
                const sl = row.querySelector('.t20-multiclasse-slug');
                const sv = sl && sl.value ? String(sl.value).trim().toLowerCase() : '';
                if (sv && sv !== excluirSlug) out.push(sv);
            });
        }
        return [...new Set(out)];
    }

    function opcoesClasseHtml(slugVal, excluirSlug) {
        const sv = String(slugVal || '').trim().toLowerCase();
        const outros = slugsOutrasLinhas(excluirSlug || sv);
        const CV = global.T20ClassesVariantesV13;
        const cat = catalogoClasses();
        const parts = ['<option value="">— classe —</option>'];
        cat.forEach((row) => {
            const slug = String(row.slug || '').trim().toLowerCase();
            if (!slug) return;
            const ok = CV ? CV.classeDisponivel(row, outros, cat) : true;
            if (!ok && slug !== sv) return;
            const label = CV ? CV.labelClasseMb(row) : slug;
            parts.push(
                `<option value="${escHtml(slug)}"${slug === sv ? ' selected' : ''}>${escHtml(label)}</option>`
            );
        });
        return parts.join('');
    }

    function linhaHtml(slugVal, nivelVal, excluirSlug) {
        const sv = String(slugVal || '').trim().toLowerCase();
        const opts = opcoesClasseHtml(sv, excluirSlug || sv);
        const n = Math.max(1, Math.min(40, nivelVal != null ? Number(nivelVal) || 1 : 1));
        return `<div class="t20-niv-conj-linha" data-t20-multiclasse-v13>
            <select class="t20-input t20-multiclasse-slug" aria-label="Classe v1.3">${opts}</select>
            <input type="number" class="t20-input t20-multiclasse-niv" min="1" max="40" value="${n}" aria-label="Níveis na classe" />
            <button type="button" class="tormenta-btn t20-multiclasse-del" title="Remover linha">✕</button>
        </div>`;
    }

    function anexarRemoverRow(row) {
        if (!row) return;
        const btn = row.querySelector('.t20-multiclasse-del');
        if (btn) {
            btn.addEventListener('click', () => {
                row.remove();
                revalidarTodasLinhas();
                agendarAtualizarPm();
            });
        }
        const sl = row.querySelector('.t20-multiclasse-slug');
        if (sl && !sl.dataset.t20VarBound) {
            sl.dataset.t20VarBound = '1';
            sl.addEventListener('change', () => {
                revalidarTodasLinhas();
                agendarAtualizarPm();
            });
        }
    }

    function revalidarTodasLinhas() {
        const w = q('t20MulticlasseV13Lista');
        if (!w) return;
        w.querySelectorAll('[data-t20-multiclasse-v13]').forEach((row) => {
            const sl = row.querySelector('.t20-multiclasse-slug');
            if (!sl) return;
            const cur = String(sl.value || '').trim().toLowerCase();
            const nv = row.querySelector('.t20-multiclasse-niv');
            const n = nv ? nv.value : 1;
            const frag = document.createElement('div');
            frag.innerHTML = linhaHtml(cur, n, cur);
            const novo = frag.firstElementChild;
            if (!novo) return;
            const novoSl = novo.querySelector('.t20-multiclasse-slug');
            if (novoSl) novoSl.value = cur;
            row.replaceWith(novo);
            anexarRemoverRow(novo);
        });
        if (typeof global.popularSelectClassesMb === 'function') {
            global.popularSelectClassesMb();
        }
    }

    function renderFromJson(arr) {
        const w = q('t20MulticlasseV13Lista');
        if (!w) return;
        w.innerHTML = '';
        const rows = Array.isArray(arr) ? arr : [];
        rows.forEach((r) => {
            if (!r || typeof r !== 'object') return;
            const slug = String(r.slug || '').trim().toLowerCase();
            const nv = r.nivel != null ? parseInt(String(r.nivel), 10) : 1;
            w.insertAdjacentHTML('beforeend', linhaHtml(slug, nv, slug));
            anexarRemoverRow(w.lastElementChild);
        });
        agendarAtualizarPm();
    }

    function coletarLinhas() {
        const w = q('t20MulticlasseV13Lista');
        if (!w) return null;
        const out = [];
        const seen = new Set();
        const slugsOk = slugsLista();
        w.querySelectorAll('[data-t20-multiclasse-v13]').forEach((row) => {
            const sl = row.querySelector('.t20-multiclasse-slug');
            const nv = row.querySelector('.t20-multiclasse-niv');
            const st = String((sl && sl.value) || '').trim().toLowerCase();
            if (!st || seen.has(st)) return;
            if (slugsOk.length && !slugsOk.includes(st)) return;
            seen.add(st);
            const n = Math.max(1, Math.min(40, parseInt((nv && nv.value) || '1', 10) || 1));
            out.push({ slug: st, nivel: n });
        });
        return out.length ? out : null;
    }

    function validarAntesSalvar() {
        const CV = global.T20ClassesVariantesV13;
        if (!CV || !isV13()) return { ok: true };
        const cat = catalogoClasses();
        if (!CV.haAtivoNoCatalogo(cat)) return { ok: true };
        const slugs = CV.slugsSelecionadosDeDom(q);
        const main = classePrincipalSlug();
        if (main && !slugs.includes(main)) slugs.push(main);
        const msg = CV.validarConflito(slugs, cat);
        return msg ? { ok: false, msg } : { ok: true };
    }

    /** Linhas salvas ou, se vazias, classe principal + nível do personagem. */
    function niveisEfetivosParaPm() {
        const linhas = coletarLinhas();
        if (linhas && linhas.length) return linhas;
        const slug = classePrincipalSlug();
        if (!slug) return [];
        return [{ slug, nivel: nivelPersonagem() }];
    }

    function atualizarVisibilidade() {
        const wrap = q('wrapMulticlasseV13');
        if (!wrap) return;
        wrap.style.display = isV13() ? '' : 'none';
    }

    function escreverHint(prev) {
        const hint = q('t20MulticlassePmHint');
        const pmBd = q('fichaPmBreakdown');
        if (!prev || prev.pm_max == null) {
            if (hint) hint.textContent = 'Adicione classes ou selecione a classe principal para calcular PM.';
            return;
        }
        const txt = prev.formula
            ? `PM multiclasse (v1.3): ${prev.formula}`
            : `PM multiclasse (v1.3): ${prev.pm_max} PM`;
        if (hint) hint.textContent = txt;
        if (pmBd) {
            pmBd.dataset.t20PmFormula = txt;
            pmBd.textContent = txt;
        }
    }

    function lerParPm() {
        if (typeof global.t20ReadPairSlash === 'function') {
            return global.t20ReadPairSlash('fichaPm');
        }
        const el = q('fichaPm');
        if (!el) return { atual: 0, max: 0 };
        const t = String(el.textContent || '').replace(/\s/g, '');
        const m = t.match(/^(\d+)\s*\/\s*(\d+)/);
        if (m) return { atual: parseInt(m[1], 10) || 0, max: parseInt(m[2], 10) || 0 };
        return { atual: 0, max: 0 };
    }

    function escreverParPm(atual, maximo) {
        if (typeof global.t20WritePairSlash === 'function') {
            global.t20WritePairSlash('fichaPm', atual, maximo);
        } else {
            const el = q('fichaPm');
            if (el) el.textContent = `${atual} / ${maximo}`;
        }
    }

    async function atualizarPmSugerido(aplicar) {
        if (!isV13()) return null;
        const classes = niveisEfetivosParaPm();
        if (!classes.length) {
            escreverHint(null);
            return null;
        }
        try {
            const prev = await new TormentaRegrasService().obterPmPreviewMulticlasse({
                classes,
                regraVersao: 'v13',
            });
            escreverHint(prev);
            if (aplicar && prev.pm_max != null) {
                const par = lerParPm();
                escreverParPm(Math.min(par.atual, prev.pm_max), prev.pm_max);
            }
            return prev;
        } catch (_e) {
            if (q('t20MulticlassePmHint')) {
                q('t20MulticlassePmHint').textContent = 'Erro ao calcular PM multiclasse.';
            }
            return null;
        }
    }

    function agendarAtualizarPm() {
        if (debouncePm) clearTimeout(debouncePm);
        debouncePm = setTimeout(() => {
            debouncePm = null;
            void atualizarPmSugerido(false);
            if (typeof global.t20AtualizarVitaisSugeridos === 'function') {
                void global.t20AtualizarVitaisSugeridos();
            }
        }, 280);
    }

    function lerPayload() {
        if (!isV13()) return null;
        return coletarLinhas();
    }

    function aplicarPayload(fj) {
        if (!fj || typeof fj !== 'object') return;
        void carregarSlugsClasses().then(() => {
            renderFromJson(fj.multiclasse_v13 || []);
            atualizarVisibilidade();
        });
    }

    function bindOnce() {
        if (global.__t20MulticlasseV13Bound) return;
        global.__t20MulticlasseV13Bound = true;
        q('btnT20MulticlasseV13Add')?.addEventListener('click', () => {
            const w = q('t20MulticlasseV13Lista');
            if (!w) return;
            w.insertAdjacentHTML('beforeend', linhaHtml('', 1, ''));
            anexarRemoverRow(w.lastElementChild);
            agendarAtualizarPm();
        });
        q('btnT20AplicarPmMulticlasse')?.addEventListener('click', () => {
            void atualizarPmSugerido(true);
        });
        const w = q('t20MulticlasseV13Lista');
        if (w && !w.dataset.t20Deleg) {
            w.dataset.t20Deleg = '1';
            w.addEventListener('change', () => agendarAtualizarPm());
            w.addEventListener('input', () => agendarAtualizarPm());
        }
        q('f_classe_mb')?.addEventListener('change', () => {
            revalidarTodasLinhas();
            agendarAtualizarPm();
        });
        q('f_nivel')?.addEventListener('change', () => agendarAtualizarPm());
    }

    async function init() {
        bindOnce();
        await carregarSlugsClasses();
        atualizarVisibilidade();
    }

    global.T20MulticlasseV13 = {
        init,
        carregarSlugsClasses,
        coletarLinhas,
        niveisEfetivosParaPm,
        lerPayload,
        aplicarPayload,
        atualizarPmSugerido,
        renderFromJson,
        atualizarVisibilidade,
        revalidarTodasLinhas,
        validarAntesSalvar,
        catalogoClasses,
    };
})(typeof window !== 'undefined' ? window : globalThis);
