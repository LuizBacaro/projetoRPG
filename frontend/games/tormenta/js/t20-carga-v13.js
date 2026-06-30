/**
 * Carga v1.3 — paridade com carga_t20.py (RF-T07f).
 */
(function (global) {
    'use strict';

    function normalizarChave(texto) {
        return String(texto == null ? '' : texto)
            .normalize('NFD')
            .replace(/\p{M}/gu, '')
            .trim()
            .toLowerCase();
    }

    function limiteCargaFor(forValor) {
        const f = Math.trunc(Number(forValor) || 0);
        if (f >= 0) return Math.max(0, 10 + 2 * f);
        return Math.max(0, 10 + f);
    }

    function limiteCargaMaximo(forValor) {
        return Math.max(0, 2 * limiteCargaFor(forValor));
    }

    function espacosMoedas(moedasTotal) {
        const n = Math.max(0, Math.trunc(Number(moedasTotal) || 0));
        return n > 0 ? Math.floor(n / 1000) : 0;
    }

    function espacosPorItem(item, cfg) {
        const it = item || {};
        if (it.espacos != null && Number.isFinite(Number(it.espacos))) {
            return Math.max(0, Number(it.espacos));
        }
        if (it.ocupa_espaco === false) return 0;

        const cfgLocal = cfg || {};
        const nome = String(it.nome || '').trim();
        const nomeNorm = normalizarChave(nome);

        const zeros = cfgLocal.zero_espacos_nomes || ['mochila'];
        if (zeros.some((z) => normalizarChave(z) === nomeNorm)) return 0;

        const porNome = cfgLocal.por_nome || {};
        for (const [chave, val] of Object.entries(porNome)) {
            if (normalizarChave(chave) === nomeNorm) return Number(val);
        }

        const tipo = String(it.tipo || '').trim().toLowerCase();
        const porTipo = cfgLocal.por_tipo_protecao || { leve: 2, media: 2, pesada: 5, escudo: 1 };
        if (tipo && porTipo[tipo] != null) {
            if (tipo === 'escudo') {
                if (nomeNorm.includes('pesad')) return 2;
                return 1;
            }
            return Number(porTipo[tipo]);
        }

        if (nomeNorm.includes('escudo') || nomeNorm.includes('broquel')) {
            return nomeNorm.includes('pesad') ? 2 : 1;
        }

        const cat = normalizarChave(it.categoria || '');
        const porCat = cfgLocal.por_categoria || {};
        for (const [chave, val] of Object.entries(porCat)) {
            const ck = normalizarChave(chave);
            if (cat.includes(ck) || ck.includes(cat)) return Number(val);
        }

        const meios = cfgLocal.meio_espaco_padroes || ['poção', 'pocao', 'pergaminho', 'frasco'];
        if (meios.some((frag) => nomeNorm.includes(normalizarChave(frag)))) return 0.5;

        if (cat.includes('armadura pesada') || tipo === 'pesada') return 5;
        if (cat.includes('armadura leve') || tipo === 'leve') return 2;
        if (cat.includes('armadura') || nomeNorm.includes('armadura')) return 2;

        return 1;
    }

    function espacosInventario(itens, cfg) {
        return (itens || []).reduce((acc, raw) => {
            const qtd = Math.max(1, Math.trunc(Number(raw && raw.quantidade) || 1));
            return acc + espacosPorItem(raw, cfg) * qtd;
        }, 0);
    }

    function estadoCarga(forValor, espacosUsados) {
        const lim = limiteCargaFor(forValor);
        const maxLim = limiteCargaMaximo(forValor);
        const usado = Number(espacosUsados) || 0;
        if (usado <= lim) return 'normal';
        if (usado <= maxLim) return 'sobrecarregado';
        return 'acima_maximo';
    }

    function previewCargaLocal(forValor, itens, moedasTotal, cfg) {
        const lim = limiteCargaFor(forValor);
        const maxLim = limiteCargaMaximo(forValor);
        const espMoedas = espacosMoedas(moedasTotal);
        const espItens = espacosInventario(itens, cfg);
        const usado = espItens + espMoedas;
        const estado = estadoCarga(forValor, usado);
        const sobrecarga = estado === 'sobrecarregado' || estado === 'acima_maximo';
        return {
            limite: lim,
            limite_maximo: maxLim,
            espacos_usados: Math.round(usado * 100) / 100,
            espacos_itens: Math.round(espItens * 100) / 100,
            espacos_moedas: espMoedas,
            estado,
            sobrecarga,
            penalidade_armadura_extra: sobrecarga ? 5 : 0,
            deslocamento_extra_m: sobrecarga ? 3 : 0,
        };
    }

    function formatarEspacos(valor) {
        const v = Number(valor) || 0;
        if (Math.abs(v - Math.round(v)) < 0.001) return String(Math.round(v));
        if (Math.abs(v * 2 - Math.round(v * 2)) < 0.001) return String(Math.round(v * 2) / 2);
        return String(Math.round(v * 100) / 100);
    }

    function labelEstado(estado) {
        if (estado === 'sobrecarregado') return 'Sobrecarregado (−5 armadura, −3 m)';
        if (estado === 'acima_maximo') return 'Acima do máximo (2× limite)';
        return 'Normal';
    }

    global.T20CargaV13 = {
        limiteCargaFor,
        limiteCargaMaximo,
        espacosMoedas,
        espacosPorItem,
        espacosInventario,
        estadoCarga,
        previewCargaLocal,
        formatarEspacos,
        labelEstado,
    };
})(typeof window !== 'undefined' ? window : globalThis);
