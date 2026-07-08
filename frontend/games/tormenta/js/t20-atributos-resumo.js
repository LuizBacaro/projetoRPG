(function (global, factory) {
    'use strict';

    const api = factory();
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
    global.T20AtributosResumo = api;
})(typeof window !== 'undefined' ? window : globalThis, function () {
    'use strict';

    const ATTR_KEYS = ['for', 'des', 'con', 'int', 'sab', 'car'];
    const DEFAULT_IDS = {
        for: 'fichaForResumo',
        des: 'fichaDesResumo',
        con: 'fichaConResumo',
        int: 'fichaIntResumo',
        sab: 'fichaSabResumo',
        car: 'fichaCarResumo',
    };

    function q(id) {
        return typeof document !== 'undefined' ? document.getElementById(id) : null;
    }

    /**
     * Normaliza um valor de atributo para exibição no INPUT de resumo.
     * opts.v13Score (legado): se true, converte nativo → score 4d6 — só no wizard de criação.
     */
    function normalizarValorResumoAtributo(valor, fallback, opts) {
        const fb = Number.isFinite(Number(fallback)) ? Number(fallback) : 0;
        const n = Number(valor);
        if (!Number.isFinite(n)) return opts && opts.v13Score ? 10 + 2 * fb : fb;
        const native = Math.trunc(n);
        if (opts && opts.v13Score) return 10 + 2 * native;
        return native;
    }

    function normalizarValoresResumoAtributos(valores, opts) {
        const fallback = Number.isFinite(Number(opts && opts.fallback)) ? Number(opts.fallback) : 0;
        const v13Score = !!(opts && opts.v13Score);
        const out = {};
        ATTR_KEYS.forEach((attr) => {
            out[attr] = String(normalizarValorResumoAtributo(valores && valores[attr], fallback, { v13Score }));
        });
        return out;
    }

    function aplicarValoresResumoAtributos(valores, opts) {
        const fallback = Number.isFinite(Number(opts && opts.fallback)) ? Number(opts.fallback) : 0;
        const ids = opts && opts.ids && typeof opts.ids === 'object' ? opts.ids : DEFAULT_IDS;
        const v13Score = !!(opts && opts.v13Score);
        const normalized = normalizarValoresResumoAtributos(valores, { fallback, v13Score });
        ATTR_KEYS.forEach((attr) => {
            const el = ids && ids[attr] ? q(ids[attr]) : null;
            if (el) el.value = normalized[attr];
        });
        return normalized;
    }

    return {
        ATTR_KEYS,
        DEFAULT_IDS,
        normalizarValorResumoAtributo,
        normalizarValoresResumoAtributos,
        aplicarValoresResumoAtributos,
    };
});
