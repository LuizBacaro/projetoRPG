/**
 * Penalidade de armadura em perícias — paridade com penalidade_armadura_t20.py (RF-T07e / RF-T07e-1).
 */
(function (global) {
    'use strict';

    const PROF_ARMADURA_V13 = {
        arcanista: { leve: false, media: false, pesada: false, escudo: false },
        barbaro: { leve: true, media: true, pesada: false, escudo: true },
        bardo: { leve: true, media: false, pesada: false, escudo: true },
        bucaneiro: { leve: true, media: false, pesada: false, escudo: true },
        cacador: { leve: true, media: false, pesada: false, escudo: false },
        cavaleiro: { leve: true, media: true, pesada: true, escudo: true },
        clerigo: { leve: true, media: true, pesada: true, escudo: true },
        druida: { leve: true, media: true, pesada: false, escudo: true },
        guerreiro: { leve: true, media: true, pesada: true, escudo: true },
        inventor: { leve: true, media: true, pesada: false, escudo: false },
        ladino: { leve: true, media: false, pesada: false, escudo: false },
        lutador: { leve: true, media: true, pesada: false, escudo: false },
        nobre: { leve: true, media: false, pesada: false, escudo: true },
        paladino: { leve: true, media: true, pesada: true, escudo: true },
    };

    function proficienciasArmaduraClasse(slugClasse) {
        const s = String(slugClasse || '')
            .trim()
            .toLowerCase();
        return Object.assign(
            { leve: false, media: false, pesada: false, escudo: false },
            PROF_ARMADURA_V13[s] || {}
        );
    }

    function normalizarTipoProtecao(tipo) {
        const t = String(tipo || '')
            .trim()
            .toLowerCase();
        if (t === 'média' || t === 'media') return 'media';
        if (t === 'leve' || t === 'pesada' || t === 'escudo') return t;
        return '';
    }

    function itemEProtecaoMecanica(it) {
        if (!it || typeof it !== 'object') return false;
        const bonus = Number(it.bonus_ca) || 0;
        const pen = Number(it.penalidade) || 0;
        return bonus !== 0 || pen !== 0;
    }

    function proficienteEmProtecao(prof, it) {
        if (!it || typeof it !== 'object') return true;
        if (!itemEProtecaoMecanica(it)) return true;
        const tipo = normalizarTipoProtecao(it.tipo);
        if (!tipo) return Boolean(prof.leve);
        if (tipo === 'escudo') return Boolean(prof.escudo);
        if (tipo === 'pesada') return Boolean(prof.pesada);
        if (tipo === 'media') return Boolean(prof.media || prof.pesada);
        if (tipo === 'leve') return Boolean(prof.leve || prof.media || prof.pesada);
        return true;
    }

    function temProtecaoSemProficiencia(itensProtecao, slugClasse) {
        const slug = String(slugClasse || '').trim().toLowerCase();
        if (!slug) return false;
        const prof = proficienciasArmaduraClasse(slug);
        return (itensProtecao || []).some(
            (it) => itemEProtecaoMecanica(it) && !proficienteEmProtecao(prof, it)
        );
    }

    function penalidadeEquipadaTotal(itensProtecao) {
        return (itensProtecao || []).reduce((acc, it) => {
            const pen = Number(it && it.penalidade) || 0;
            return pen < 0 ? acc + Math.abs(pen) : acc;
        }, 0);
    }

    function periciaAplicaPenalidade(meta, usoAtletismoNatacao, naoProficienteArmadura) {
        if (!meta) return false;
        if (naoProficienteArmadura) {
            const attr = String(meta.atributo || '')
                .trim()
                .toLowerCase();
            return attr === 'for' || attr === 'des';
        }
        if (meta.penalidade_armadura === true) return true;
        if (meta.penalidade_armadura_natacao === true && usoAtletismoNatacao) return true;
        return false;
    }

    function penalidadeArmaduraPericia(meta, itensProtecao, usoAtletismoNatacao, slugClasse) {
        const naoProf =
            slugClasse != null && slugClasse !== ''
                ? temProtecaoSemProficiencia(itensProtecao, slugClasse)
                : false;
        if (!periciaAplicaPenalidade(meta, usoAtletismoNatacao, naoProf)) return 0;
        return penalidadeEquipadaTotal(itensProtecao);
    }

    function itensProtecaoPayload(itens) {
        return (itens || []).map((it) => ({
            nome: String((it && it.nome) || ''),
            tipo: String((it && it.tipo) || ''),
            penalidade: Number(it && it.penalidade) || 0,
            bonus_ca: Number(it && it.bonus_ca) || 0,
        }));
    }

    global.T20PenalidadeArmadura = {
        proficienciasArmaduraClasse,
        temProtecaoSemProficiencia,
        penalidadeEquipadaTotal,
        periciaAplicaPenalidade,
        penalidadeArmaduraPericia,
        itensProtecaoPayload,
    };
})(typeof window !== 'undefined' ? window : globalThis);
