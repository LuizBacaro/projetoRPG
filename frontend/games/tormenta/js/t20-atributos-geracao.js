/**
 * Geração de atributos T20 — compra por pontos e 4d6 (MB e v1.3).
 */
(function (global) {
    'use strict';

    const T20_ATTR_KEYS = ['for', 'des', 'con', 'int', 'sab', 'car'];
    const T20_METODO_COMPRA = 'compra_pontos';
    const T20_METODO_4D6 = '4d6';

    const TABELA_4D6_V13 = [
        { min: 0, max: 7, attr: -2 },
        { min: 8, max: 9, attr: -1 },
        { min: 10, max: 11, attr: 0 },
        { min: 12, max: 13, attr: 1 },
        { min: 14, max: 15, attr: 2 },
        { min: 16, max: 17, attr: 3 },
        { min: 18, max: 99, attr: 4 },
    ];
    const SOMA_MINIMA_4D6_V13 = 6;

    function isV13Rv(opts) {
        const rv = opts && opts.regraVersao;
        return global.T20RegraVersao && global.T20RegraVersao.isV13(rv);
    }

    function modificadorAtributoT20(val) {
        const n = Number(val);
        if (!Number.isFinite(n)) return 0;
        const v = Math.max(1, Math.floor(n));
        if (v <= 1) return -5;
        if (v <= 3) return -4;
        if (v <= 5) return -3;
        if (v <= 7) return -2;
        if (v <= 9) return -1;
        if (v <= 11) return 0;
        if (v <= 13) return 1;
        if (v <= 15) return 2;
        if (v <= 17) return 3;
        if (v <= 19) return 4;
        if (v <= 21) return 5;
        if (v <= 23) return 6;
        if (v <= 25) return 7;
        return 7 + Math.floor((v - 25 + 1) / 2);
    }

    function somaModificadoresValores(valores, opts) {
        const rv = opts && opts.regraVersao;
        if (global.T20RegraVersao && global.T20RegraVersao.isV13(rv)) {
            return (valores || []).reduce((s, v) => s + Math.trunc(Number(v) || 0), 0);
        }
        return (valores || []).reduce((s, v) => s + modificadorAtributoT20(v), 0);
    }

    function converterSoma4d6V13(soma) {
        const s = Math.floor(Number(soma));
        for (let i = 0; i < TABELA_4D6_V13.length; i++) {
            const row = TABELA_4D6_V13[i];
            if (s >= row.min && s <= row.max) return row.attr;
        }
        return 0;
    }

    function qualidadeGeracao4d6(valores) {
        const vals = (valores || []).map((v) => Math.floor(Number(v)));
        if (vals.length !== 6) return false;
        if (vals.some((v) => !Number.isFinite(v) || v < 3 || v > 18)) return false;
        if (vals.some((v) => v >= 14)) return true;
        return somaModificadoresValores(vals) >= 4;
    }

    function qualidadeGeracao4d6V13(valores) {
        const vals = (valores || []).map((v) => Math.floor(Number(v)));
        if (vals.length !== 6) return false;
        if (vals.some((v) => !Number.isFinite(v) || v < -2 || v > 4)) return false;
        return vals.reduce((a, b) => a + b, 0) >= SOMA_MINIMA_4D6_V13;
    }

    function rolarUm4d6() {
        const dados = [];
        for (let i = 0; i < 4; i++) dados.push(1 + Math.floor(Math.random() * 6));
        dados.sort((a, b) => a - b);
        return dados[1] + dados[2] + dados[3];
    }

    function gerarSeisValores4d6Local(opts) {
        const rv = opts && opts.regraVersao;
        if (global.T20RegraVersao && global.T20RegraVersao.isV13(rv)) {
            const maxTentativas = (opts && opts.maxTentativas) || 100;
            let convertidos = [];
            for (let t = 0; t < maxTentativas; t++) {
                const brutos = [];
                for (let i = 0; i < 6; i++) brutos.push(rolarUm4d6());
                convertidos = brutos.map((s) => converterSoma4d6V13(s));
                if (qualidadeGeracao4d6V13(convertidos)) return convertidos.slice();
                let idx = 0;
                for (let i = 1; i < 6; i++) {
                    if (convertidos[i] < convertidos[idx]) idx = i;
                }
                convertidos[idx] = converterSoma4d6V13(rolarUm4d6());
                if (qualidadeGeracao4d6V13(convertidos)) return convertidos.slice();
            }
            return convertidos;
        }
        const exigir = !(opts && opts.exigirQualidadeMb === false);
        const maxTentativas = (opts && opts.maxTentativas) || 100;
        let ultima = [];
        for (let t = 0; t < maxTentativas; t++) {
            ultima = [];
            for (let i = 0; i < 6; i++) ultima.push(rolarUm4d6());
            if (!exigir || qualidadeGeracao4d6(ultima)) return ultima.slice();
        }
        return ultima;
    }

    function valoresParaMapa(valores) {
        const out = {};
        T20_ATTR_KEYS.forEach((k, i) => {
            out[k] = Math.floor(Number(valores[i]));
        });
        return out;
    }

    function basesPadraoCompra(opts) {
        const rv = opts && opts.regraVersao;
        const base =
            global.T20RegraVersao && global.T20RegraVersao.isV13(rv)
                ? global.T20RegraVersao.valorBaseCompraPadrao(rv)
                : 10;
        const out = {};
        T20_ATTR_KEYS.forEach((k) => {
            out[k] = base;
        });
        return out;
    }

    function aplicarBasesNosCampos(bases, campoIds, racialDeltas, opts) {
        const rDel = racialDeltas || {};
        const rv = opts && opts.regraVersao;
        const isV13 = global.T20RegraVersao && global.T20RegraVersao.isV13(rv);
        const fallbackBase = isV13 ? 0 : 10;
        const minFin = isV13 ? -99 : 1;
        T20_ATTR_KEYS.forEach((a) => {
            const id = campoIds[a];
            const inp = id ? document.getElementById(id) : null;
            if (!inp) return;
            const base = Math.floor(Number(bases[a]));
            const fin = Math.max(minFin, (Number.isFinite(base) ? base : fallbackBase) + (rDel[a] || 0));
            inp.value = String(fin);
        });
    }

    function validarBases4d6(bases, opts) {
        const rv = opts && opts.regraVersao;
        const vals = T20_ATTR_KEYS.map((k) => Math.floor(Number(bases[k])));
        if (global.T20RegraVersao && global.T20RegraVersao.isV13(rv)) {
            if (vals.some((v) => !Number.isFinite(v) || v < -2 || v > 4)) {
                return {
                    ok: false,
                    msg: 'Rolagem 4d6 v1.3: cada valor-base deve estar entre −2 e +4 (Tabela 1-1).',
                };
            }
            if (!qualidadeGeracao4d6V13(vals)) {
                return {
                    ok: false,
                    msg: 'Rolagem 4d6 inválida v1.3: a soma dos seis atributos deve ser pelo menos 6. Role novamente.',
                };
            }
            return { ok: true };
        }
        if (vals.some((v) => !Number.isFinite(v) || v < 3 || v > 18)) {
            return {
                ok: false,
                msg: 'Rolagem 4d6: cada valor-base deve estar entre 3 e 18 (sem bônus racial).',
            };
        }
        if (!qualidadeGeracao4d6(vals)) {
            return {
                ok: false,
                msg: 'Rolagem 4d6 inválida: soma dos modificadores deve ser pelo menos +4 ou pelo menos um valor-base 14+ (MB). Role novamente.',
            };
        }
        return { ok: true };
    }

    global.T20AtributosGeracao = {
        ATTR_KEYS: T20_ATTR_KEYS,
        METODO_COMPRA: T20_METODO_COMPRA,
        METODO_4D6: T20_METODO_4D6,
        modificadorAtributoT20,
        somaModificadoresValores,
        qualidadeGeracao4d6,
        qualidadeGeracao4d6V13,
        converterSoma4d6V13,
        rolarUm4d6,
        gerarSeisValores4d6Local,
        valoresParaMapa,
        basesPadraoCompra,
        aplicarBasesNosCampos,
        validarBases4d6,
    };
})(typeof window !== 'undefined' ? window : globalThis);
