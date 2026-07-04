/**
 * HA-3 — exclusão mútua entre classes variantes Heróis de Arton e bases (v1.3).
 */
(function (global) {
    'use strict';

    function normSlug(s) {
        return String(s || '').trim().toLowerCase();
    }

    function getRowPorSlug(slug, catalogoClasses) {
        const s = normSlug(slug);
        if (!s || !Array.isArray(catalogoClasses)) return null;
        return catalogoClasses.find((x) => normSlug(x.slug) === s) || null;
    }

    /**
     * @param {object} row — item do catálogo de classes
     * @param {string[]} slugsSelecionados — slugs já escolhidos (outras linhas / classe principal)
     * @param {object[]} catalogoClasses
     */
    function classeDisponivel(row, slugsSelecionados, catalogoClasses) {
        if (!row) return false;
        const slug = normSlug(row.slug);
        const selecionados = (slugsSelecionados || []).map(normSlug).filter(Boolean);
        if (!selecionados.length) return true;
        if (selecionados.includes(slug)) return true;

        for (let i = 0; i < selecionados.length; i += 1) {
            const cur = selecionados[i];
            const excl = Array.isArray(row.exclusivo_com) ? row.exclusivo_com.map(normSlug) : [];
            if (excl.includes(cur)) return false;
            const curRow = getRowPorSlug(cur, catalogoClasses);
            if (!curRow) continue;
            const curExcl = Array.isArray(curRow.exclusivo_com)
                ? curRow.exclusivo_com.map(normSlug)
                : [];
            if (curExcl.includes(slug)) return false;
            const base = row.classe_variante_base ? normSlug(row.classe_variante_base) : '';
            if (base && cur === base) return false;
            const curBase = curRow.classe_variante_base
                ? normSlug(curRow.classe_variante_base)
                : '';
            if (curBase && slug === curBase) return false;
        }
        return true;
    }

    function tagClasseMb(row) {
        if (!row || row.fonte_catalogo !== 'herois_arton') return '';
        return row.classe_variante_base ? ' [variante]' : ' [HA]';
    }

    function labelClasseMb(row) {
        const nome = row.nome || row.slug || '';
        const abrev = row.abreviatura ? ` (${row.abreviatura})` : '';
        return `${nome}${abrev}${tagClasseMb(row)}`;
    }

    function slugsSelecionadosDeFicha(fichaJson) {
        const fj = fichaJson && typeof fichaJson === 'object' ? fichaJson : {};
        const out = [];
        const main =
            fj.tormenta_classe_mb_slug ||
            (Array.isArray(fj.tormenta_niveis_classe_mb) &&
                fj.tormenta_niveis_classe_mb[0] &&
                fj.tormenta_niveis_classe_mb[0].classe_slug);
        if (main) out.push(normSlug(main));
        const mc = fj.multiclasse_v13;
        if (Array.isArray(mc)) {
            mc.forEach((r) => {
                if (r && r.slug) out.push(normSlug(r.slug));
            });
        }
        return [...new Set(out.filter(Boolean))];
    }

    function slugsSelecionadosDeDom(qFn, opts) {
        const q =
            typeof qFn === 'function'
                ? qFn
                : (id) => (global.document ? global.document.getElementById(id) : null);
        const o = opts || {};
        const excluir = normSlug(o.excluirSlug || o.excluir);
        const out = [];
        const mainSel = q('f_classe_mb');
        const main = mainSel && mainSel.value ? normSlug(mainSel.value) : '';
        if (main && main !== excluir) out.push(main);
        const w = q('t20MulticlasseV13Lista');
        if (w) {
            w.querySelectorAll('[data-t20-multiclasse-v13]').forEach((row) => {
                const sl = row.querySelector('.t20-multiclasse-slug');
                const sv = sl && sl.value ? normSlug(sl.value) : '';
                if (sv && sv !== excluir) out.push(sv);
            });
        }
        const cadSel = q('cadClasseMb');
        const cad = cadSel && cadSel.value ? normSlug(cadSel.value) : '';
        if (cad && cad !== excluir) out.push(cad);
        return [...new Set(out.filter(Boolean))];
    }

    function validarConflito(slugsSelecionados, catalogoClasses) {
        const slugs = (slugsSelecionados || []).map(normSlug).filter(Boolean);
        const unicos = [...new Set(slugs)];
        for (let i = 0; i < unicos.length; i += 1) {
            const slug = unicos[i];
            const row = getRowPorSlug(slug, catalogoClasses);
            if (!row) continue;
            const outros = unicos.filter((s) => s !== slug);
            if (!classeDisponivel(row, outros, catalogoClasses)) {
                const nome = row.nome || slug;
                return `Classes variantes incompatíveis: «${nome}» conflita com outra classe selecionada.`;
            }
        }
        return null;
    }

    function haAtivoNoCatalogo(catalogoClasses) {
        return (
            Array.isArray(catalogoClasses) &&
            catalogoClasses.some((r) => r && r.fonte_catalogo === 'herois_arton')
        );
    }

    global.T20ClassesVariantesV13 = {
        classeDisponivel,
        getRowPorSlug,
        tagClasseMb,
        labelClasseMb,
        slugsSelecionadosDeFicha,
        slugsSelecionadosDeDom,
        validarConflito,
        haAtivoNoCatalogo,
    };
})(typeof window !== 'undefined' ? window : globalThis);
