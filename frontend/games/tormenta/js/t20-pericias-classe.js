/** Perícias de classe v1.3 — fixas automáticas, grupos «ou» e destaque do pool. */
(function () {
    function q(id) {
        return document.getElementById(id);
    }

    function isV13() {
        return (
            window.T20RegraVersao &&
            typeof window.getRegraVersaoAtiva === 'function' &&
            window.T20RegraVersao.isV13(window.getRegraVersaoAtiva())
        );
    }

    function getClasseRow() {
        if (typeof window.getClasseMbRowPorSlug !== 'function') return null;
        const slug = (q('f_classe_mb') && q('f_classe_mb').value) || '';
        return slug ? window.getClasseMbRowPorSlug(slug) : null;
    }

    function slugPorIndicePericia(idx) {
        const rows = document.querySelectorAll('#tblPericias tbody tr');
        const tr = rows[idx];
        if (!tr) return '';
        return String(tr.getAttribute('data-per-slug') || '').trim().toLowerCase();
    }

    function linhaPorSlug(slug) {
        const s = String(slug || '').trim().toLowerCase();
        if (!s) return null;
        const rows = document.querySelectorAll('#tblPericias tbody tr');
        for (const tr of rows) {
            if (String(tr.getAttribute('data-per-slug') || '').trim().toLowerCase() === s) {
                return tr;
            }
        }
        return null;
    }

    function marcarTreinado(slug, on) {
        const tr = linhaPorSlug(slug);
        if (!tr) return;
        const ck = tr.querySelector('.p-treinado');
        if (ck) ck.checked = Boolean(on);
    }

    function renderGruposOu(c) {
        const wrap = q('wrapPericiasClasseOu');
        const host = q('t20PericiasClasseOuHost');
        if (!wrap || !host) return;
        const grupos = (c && c.pericias_escolha_um_de) || [];
        if (!isV13() || !grupos.length) {
            wrap.style.display = 'none';
            host.innerHTML = '';
            return;
        }
        wrap.style.display = '';
        const salvos =
            (window.__t20PericiasClasseOu && typeof window.__t20PericiasClasseOu === 'object'
                ? window.__t20PericiasClasseOu
                : {}) || {};
        host.innerHTML = grupos
            .map((gr, gi) => {
                const opts = (gr || [])
                    .map((slug) => {
                        const sel = salvos[String(gi)] === slug ? ' selected' : '';
                        const lab = slug.replace(/_/g, ' ');
                        return `<option value="${slug}"${sel}>${lab}</option>`;
                    })
                    .join('');
                return `<div class="t20-ficha-field" style="margin-top:0.35rem"><label>Escolha ${gi + 1}</label><select class="t20-input t20-pericia-ou-grupo" data-grupo-idx="${gi}"><option value="">—</option>${opts}</select></div>`;
            })
            .join('');
        host.querySelectorAll('.t20-pericia-ou-grupo').forEach((sel) => {
            sel.addEventListener('change', () => aplicarGruposOu(c));
        });
        aplicarGruposOu(c);
    }

    function aplicarGruposOu(c) {
        const grupos = (c && c.pericias_escolha_um_de) || [];
        const map = {};
        document.querySelectorAll('.t20-pericia-ou-grupo').forEach((sel) => {
            const gi = sel.getAttribute('data-grupo-idx');
            const v = String(sel.value || '').trim().toLowerCase();
            if (gi != null && v) map[gi] = v;
        });
        window.__t20PericiasClasseOu = map;
        grupos.forEach((gr, gi) => {
            const pick = map[String(gi)];
            (gr || []).forEach((slug) => marcarTreinado(slug, pick === slug));
        });
        if (typeof window.t20ValidarPericiasOrcamentoMb === 'function') {
            window.t20ValidarPericiasOrcamentoMb();
        }
    }

    function aplicarFixas(c) {
        if (!isV13() || !c) return;
        (c.pericias_fixas || []).forEach((slug) => marcarTreinado(slug, true));
    }

    function atualizarPericiasClasseUi() {
        const c = getClasseRow();
        if (!isV13() || !c) {
            const wrap = q('wrapPericiasClasseOu');
            if (wrap) wrap.style.display = 'none';
            return;
        }
        aplicarFixas(c);
        renderGruposOu(c);
        if (typeof window.destacarPericiasClasseMb === 'function') {
            window.destacarPericiasClasseMb();
        }
        if (typeof window.t20ValidarPericiasOrcamentoMb === 'function') {
            window.t20ValidarPericiasOrcamentoMb();
        }
    }

    function init() {
        const sc = q('f_classe_mb');
        if (sc && !sc.dataset.t20PerClasseBound) {
            sc.dataset.t20PerClasseBound = '1';
            sc.addEventListener('change', () => {
                window.__t20PericiasClasseOu = {};
                atualizarPericiasClasseUi();
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.t20AplicarPericiasClasseV13 = atualizarPericiasClasseUi;
})();
