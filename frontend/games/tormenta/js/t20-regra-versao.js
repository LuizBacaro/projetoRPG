/**
 * Versão de regras Tormenta 20 — MB legado vs v1.3 (Edição Jogo do Ano).
 * Paridade com backend/regra_versao_t20.py e atributos_t20.py.
 */
(function (global) {
    'use strict';

    const RV_MB = 'mb';
    const RV_V13 = 'v13';
    const DEFAULT_NOVA_FICHA = RV_V13;
    const SUPLEMENTO_HEROIS_ARTON = 'herois_arton';

    function normalizar(valor) {
        const s = String(valor == null ? '' : valor)
            .trim()
            .toLowerCase();
        if (s === RV_V13 || s === 've' || s === '1.3' || s === 'v1.3') return RV_V13;
        return RV_MB;
    }

    /** Ficha legada sem campo = MB; ficha nova deve gravar regra_versao: v13. */
    function getRegraVersaoFicha(fichaJson) {
        if (!fichaJson || fichaJson.regra_versao == null || fichaJson.regra_versao === '') {
            return RV_MB;
        }
        return normalizar(fichaJson.regra_versao);
    }

    function isV13(regraVersao) {
        return normalizar(regraVersao) === RV_V13;
    }

    function modificadorAtributoMb(val) {
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

    /**
     * Converte atributo nativo v1.3 (−2 a +4) para score d20-equivalente
     * (ex.: 2 → 14, 1 → 12, 0 → 10).  Exibição nos círculos da ficha.
     */
    function v13AttrToScore(attr) {
        const n = Number(attr);
        return Number.isFinite(n) ? 10 + 2 * Math.trunc(n) : 10;
    }

    /**
     * Contribuição mecânica do atributo para fórmulas.
     * v1.3: val é o score d20-equivalente (10+2×attr); retorna o atributo nativo (−2 a +4).
     * MB:   val é o score MB (8–18+); retorna o modificador pelo livro.
     */
    function contribuicaoAtributo(val, regraVersao) {
        if (isV13(regraVersao)) {
            const n = Number(val);
            return Number.isFinite(n) ? Math.trunc((n - 10) / 2) : 0;
        }
        return modificadorAtributoMb(val);
    }

    function labelVersaoCurta(regraVersao) {
        return isV13(regraVersao) ? 'T20 v1.3' : 'MB';
    }

    function valorBaseCompraPadrao(regraVersao) {
        return isV13(regraVersao) ? 0 : 10;
    }

    /** CA base sem armadura da lista: 10 + contribuição de DES. */
    function defesaBaseCa(desValor, regraVersao, outrosBonus) {
        const des = contribuicaoAtributo(desValor, regraVersao);
        const outros = Number(outrosBonus) || 0;
        return 10 + des + outros;
    }

    function temArmaduraPesada(itensProtecao) {
        return (itensProtecao || []).some(
            (it) => String((it && it.tipo) || '').trim().toLowerCase() === 'pesada'
        );
    }

    function somaBonusProtecao(itensProtecao) {
        if (global.T20LimitesEquipamento && global.T20LimitesEquipamento.somaBonusCaAtivos) {
            return global.T20LimitesEquipamento.somaBonusCaAtivos(itensProtecao);
        }
        return (itensProtecao || []).reduce(
            (acc, it) => acc + (Number(it && it.bonus_ca) || 0),
            0
        );
    }

    /** CA total v1.3: 10 + DES (exceto com armadura pesada) + bônus armadura/escudo. */
    function defesaTotalV13(desValor, itensProtecao, outrosBonus) {
        const bonus = somaBonusProtecao(itensProtecao);
        const des = temArmaduraPesada(itensProtecao)
            ? 0
            : contribuicaoAtributo(desValor, RV_V13);
        const outros = Number(outrosBonus) || 0;
        return 10 + des + bonus + outros;
    }

    function getGameSuplementoFicha(fichaJson) {
        if (!fichaJson || fichaJson.game_suplemento == null) return null;
        const s = String(fichaJson.game_suplemento).trim().toLowerCase();
        return s === SUPLEMENTO_HEROIS_ARTON ? s : null;
    }

    global.T20RegraVersao = {
        RV_MB,
        RV_V13,
        DEFAULT_NOVA_FICHA,
        SUPLEMENTO_HEROIS_ARTON,
        normalizar,
        getRegraVersaoFicha,
        isV13,
        modificadorAtributoMb,
        v13AttrToScore,
        contribuicaoAtributo,
        labelVersaoCurta,
        valorBaseCompraPadrao,
        defesaBaseCa,
        temArmaduraPesada,
        somaBonusProtecao,
        defesaTotalV13,
        getGameSuplementoFicha,
    };
})(typeof window !== 'undefined' ? window : globalThis);
