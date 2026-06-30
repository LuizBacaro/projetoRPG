/**
 * Proficiência em armas v1.3 — paridade com proficiencia_arma_t20.py (RF-T05-v13c).
 */
(function (global) {
    'use strict';

    const PEN = -5;

    const PROF_KIT_MARCIAL = {
        arcanista: false,
        barbaro: true,
        bardo: true,
        bucaneiro: true,
        cacador: true,
        cavaleiro: true,
        clerigo: false,
        druida: false,
        guerreiro: true,
        inventor: true,
        ladino: true,
        lutador: true,
        nobre: true,
        paladino: true,
    };

    const PROF_OVERLAY_NOME = {
        adaga: 'simples',
        clava: 'simples',
        maca: 'simples',
        lanca: 'simples',
        bordao: 'simples',
        cajado: 'simples',
        azagaia: 'simples',
        funda: 'simples',
        estilingue: 'simples',
        dardo: 'simples',
        machadinha: 'simples',
        'mangual leve': 'simples',
        'espada curta': 'simples',
        'arco curto': 'simples',
        'espada longa': 'marcial',
        'machado de batalha': 'marcial',
        'martelo de guerra': 'marcial',
        tridente: 'marcial',
        'arco longo': 'marcial',
        'martelo leve': 'marcial',
        'mangual pesado': 'marcial',
        cimitarra: 'marcial',
        'espada bastarda': 'marcial',
        florete: 'marcial',
        'arco composto': 'marcial',
        rede: 'exotica',
    };

    function normNome(texto) {
        return String(texto || '')
            .normalize('NFD')
            .replace(/\p{M}/gu, '')
            .trim()
            .toLowerCase();
    }

    function proficienciasArmaClasse(slugClasse) {
        const s = String(slugClasse || '')
            .trim()
            .toLowerCase();
        return {
            simples: true,
            marcial: Boolean(PROF_KIT_MARCIAL[s]),
            exotica: false,
            desarmado: true,
        };
    }

    function normalizarProficienciaArma(valor) {
        const t = String(valor || 'simples')
            .trim()
            .toLowerCase();
        if (t === 'exótica' || t === 'exotica') return 'exotica';
        if (t === 'simples' || t === 'marcial' || t === 'de fogo') return t;
        return 'simples';
    }

    function proficienciaArmaPorNome(nomeArma) {
        const mapa = global.__t20ProfArmasMap || PROF_OVERLAY_NOME;
        const chave = normNome(nomeArma);
        if (!chave) return 'simples';
        if (mapa[chave]) return normalizarProficienciaArma(mapa[chave]);
        return 'simples';
    }

    function proficienteEmArma(slugClasse, proficienciaArma) {
        const profArma = normalizarProficienciaArma(proficienciaArma);
        const profCl = proficienciasArmaClasse(slugClasse);
        if (profArma === 'simples') return profCl.simples;
        if (profArma === 'marcial') return profCl.marcial;
        if (profArma === 'exotica' || profArma === 'de fogo') return profCl.exotica;
        return true;
    }

    function penalidadeAtaqueArma(slugClasse, opts) {
        const o = opts || {};
        const prof =
            o.proficienciaArma != null
                ? normalizarProficienciaArma(o.proficienciaArma)
                : proficienciaArmaPorNome(o.nomeArma);
        return proficienteEmArma(slugClasse, prof) ? 0 : PEN;
    }

    function parseBonusAtaque(raw) {
        const s = String(raw == null ? '' : raw)
            .trim()
            .replace(/^\+/, '');
        if (s === '' || s === '—' || s === '-') return 0;
        const n = Number(s);
        return Number.isFinite(n) ? Math.trunc(n) : 0;
    }

    function ajustarBonusAtaque(bonusBase, slugClasse, opts) {
        const o = opts || {};
        const prof =
            o.proficienciaArma != null
                ? normalizarProficienciaArma(o.proficienciaArma)
                : proficienciaArmaPorNome(o.nomeArma);
        const pen = penalidadeAtaqueArma(slugClasse, { proficienciaArma: prof });
        const base = parseBonusAtaque(bonusBase);
        return {
            bonus_base: base,
            bonus_efetivo: base + pen,
            penalidade_nao_proficiente: Math.abs(pen),
            proficiente: pen === 0,
            proficiencia_arma: prof,
        };
    }

    function registrarMapaProfArmas(itens) {
        const map = Object.assign({}, PROF_OVERLAY_NOME);
        (itens || []).forEach((row) => {
            const nome = normNome(row && row.nome);
            if (nome && row && row.proficiencia) {
                map[nome] = normalizarProficienciaArma(row.proficiencia);
            }
        });
        global.__t20ProfArmasMap = map;
    }

    global.T20ProficienciaArma = {
        PENALIDADE_NAO_PROFICIENTE: Math.abs(PEN),
        proficienciasArmaClasse,
        proficienciaArmaPorNome,
        proficienteEmArma,
        penalidadeAtaqueArma,
        parseBonusAtaque,
        ajustarBonusAtaque,
        registrarMapaProfArmas,
    };
})(typeof window !== 'undefined' ? window : globalThis);
