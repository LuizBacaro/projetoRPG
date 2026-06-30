/**
 * Penalidade de armadura em perícias — paridade com penalidade_armadura_t20.py (RF-T07e).
 */
(function (global) {
    'use strict';

    function penalidadeEquipadaTotal(itensProtecao) {
        return (itensProtecao || []).reduce((acc, it) => {
            const pen = Number(it && it.penalidade) || 0;
            return pen < 0 ? acc + Math.abs(pen) : acc;
        }, 0);
    }

    function periciaAplicaPenalidade(meta, usoAtletismoNatacao) {
        if (!meta) return false;
        if (meta.penalidade_armadura === true) return true;
        if (meta.penalidade_armadura_natacao === true && usoAtletismoNatacao) return true;
        return false;
    }

    function penalidadeArmaduraPericia(meta, itensProtecao, usoAtletismoNatacao) {
        if (!periciaAplicaPenalidade(meta, usoAtletismoNatacao)) return 0;
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
        penalidadeEquipadaTotal,
        periciaAplicaPenalidade,
        penalidadeArmaduraPericia,
        itensProtecaoPayload,
    };
})(typeof window !== 'undefined' ? window : globalThis);
