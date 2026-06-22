/**
 * Geração de atributos T20 MB — compra por pontos e 4d6 (paridade com atributos_t20.py).
 */
(function (global) {
    'use strict';

    const T20_ATTR_KEYS = ['for', 'des', 'con', 'int', 'sab', 'car'];
    const T20_METODO_COMPRA = 'compra_pontos';
    const T20_METODO_4D6 = '4d6';

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

    function somaModificadoresValores(valores) {
        return (valores || []).reduce((s, v) => s + modificadorAtributoT20(v), 0);
    }

    function qualidadeGeracao4d6(valores) {
        const vals = (valores || []).map((v) => Math.floor(Number(v)));
        if (vals.length !== 6) return false;
        if (vals.some((v) => !Number.isFinite(v) || v < 3 || v > 18)) return false;
        if (vals.some((v) => v >= 14)) return true;
        return somaModificadoresValores(vals) >= 4;
    }

    function rolarUm4d6() {
        const dados = [];
        for (let i = 0; i < 4; i++) dados.push(1 + Math.floor(Math.random() * 6));
        dados.sort((a, b) => a - b);
        return dados[1] + dados[2] + dados[3];
    }

    function gerarSeisValores4d6Local(opts) {
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

    function basesPadraoCompra() {
        const out = {};
        T20_ATTR_KEYS.forEach((k) => {
            out[k] = 10;
        });
        return out;
    }

    function aplicarBasesNosCampos(bases, campoIds, racialDeltas) {
        const rDel = racialDeltas || {};
        T20_ATTR_KEYS.forEach((a) => {
            const id = campoIds[a];
            const inp = id ? document.getElementById(id) : null;
            if (!inp) return;
            const base = Math.floor(Number(bases[a]));
            const fin = Math.max(1, (Number.isFinite(base) ? base : 10) + (rDel[a] || 0));
            inp.value = String(fin);
        });
    }

    function validarBases4d6(bases) {
        const vals = T20_ATTR_KEYS.map((k) => Math.floor(Number(bases[k])));
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
        rolarUm4d6,
        gerarSeisValores4d6Local,
        valoresParaMapa,
        basesPadraoCompra,
        aplicarBasesNosCampos,
        validarBases4d6,
    };
})(typeof window !== 'undefined' ? window : globalThis);
