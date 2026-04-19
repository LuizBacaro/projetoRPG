const CANONICAL_CLASSES = {
    MAGO: 'Mago',
    FEITICEIRO: 'Feiticeiro',
    CLERIGO: 'Clérigo',
    DRUIDA: 'Druida',
    BARDO: 'Bardo',
    PALADINO: 'Paladino',
    RANGER: 'Ranger',
};

const SPELL_SLOT_TABLES = {
    Mago: [
        [3, 1, null, null, null, null, null, null, null, null],
        [4, 2, null, null, null, null, null, null, null, null],
        [4, 2, 1, null, null, null, null, null, null, null],
        [4, 3, 2, null, null, null, null, null, null, null],
        [4, 3, 2, 1, null, null, null, null, null, null],
        [4, 3, 3, 2, null, null, null, null, null, null],
        [4, 4, 3, 2, 1, null, null, null, null, null],
        [4, 4, 3, 3, 2, null, null, null, null, null],
        [4, 4, 4, 3, 2, 1, null, null, null, null],
        [4, 4, 4, 3, 3, 2, null, null, null, null],
        [4, 4, 4, 4, 3, 2, 1, null, null, null],
        [4, 4, 4, 4, 3, 3, 2, null, null, null],
        [4, 4, 4, 4, 4, 3, 2, 1, null, null],
        [4, 4, 4, 4, 4, 3, 3, 2, null, null],
        [4, 4, 4, 4, 4, 4, 3, 2, 1, null],
        [4, 4, 4, 4, 4, 4, 3, 3, 2, null],
        [4, 4, 4, 4, 4, 4, 4, 3, 2, 1],
        [4, 4, 4, 4, 4, 4, 4, 3, 3, 2],
        [4, 4, 4, 4, 4, 4, 4, 4, 3, 3],
        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    ],
    Feiticeiro: [
        [5, 3, null, null, null, null, null, null, null, null],
        [6, 4, null, null, null, null, null, null, null, null],
        [6, 5, null, null, null, null, null, null, null, null],
        [6, 6, 3, null, null, null, null, null, null, null],
        [6, 6, 4, null, null, null, null, null, null, null],
        [6, 6, 5, 3, null, null, null, null, null, null],
        [6, 6, 6, 4, null, null, null, null, null, null],
        [6, 6, 6, 5, 3, null, null, null, null, null],
        [6, 6, 6, 6, 4, null, null, null, null, null],
        [6, 6, 6, 6, 5, 3, null, null, null, null],
        [6, 6, 6, 6, 6, 4, null, null, null, null],
        [6, 6, 6, 6, 6, 5, 3, null, null, null],
        [6, 6, 6, 6, 6, 6, 4, null, null, null],
        [6, 6, 6, 6, 6, 6, 5, 3, null, null],
        [6, 6, 6, 6, 6, 6, 6, 4, null, null],
        [6, 6, 6, 6, 6, 6, 6, 5, 3, null],
        [6, 6, 6, 6, 6, 6, 6, 6, 4, null],
        [6, 6, 6, 6, 6, 6, 6, 6, 5, 3],
        [6, 6, 6, 6, 6, 6, 6, 6, 6, 4],
        [6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    ],
    Druida: [
        [3, 1, null, null, null, null, null, null, null, null],
        [4, 2, null, null, null, null, null, null, null, null],
        [4, 2, 1, null, null, null, null, null, null, null],
        [5, 3, 2, null, null, null, null, null, null, null],
        [5, 3, 2, 1, null, null, null, null, null, null],
        [5, 3, 3, 2, null, null, null, null, null, null],
        [6, 4, 3, 2, 1, null, null, null, null, null],
        [6, 4, 3, 3, 2, null, null, null, null, null],
        [6, 4, 4, 3, 2, 1, null, null, null, null],
        [6, 4, 4, 3, 3, 2, null, null, null, null],
        [6, 5, 4, 4, 3, 2, 1, null, null, null],
        [6, 5, 4, 4, 3, 3, 2, null, null, null],
        [6, 5, 5, 4, 4, 3, 2, 1, null, null],
        [6, 5, 5, 4, 4, 3, 3, 2, null, null],
        [6, 5, 5, 5, 4, 4, 3, 2, 1, null],
        [6, 5, 5, 5, 4, 4, 3, 3, 2, null],
        [6, 5, 5, 5, 5, 4, 4, 3, 2, 1],
        [6, 5, 5, 5, 5, 4, 4, 3, 3, 2],
        [6, 5, 5, 5, 5, 5, 4, 4, 3, 3],
        [6, 5, 5, 5, 5, 5, 4, 4, 4, 4],
    ],
    Bardo: [
        [2, null, null, null, null, null, null],
        [3, 0, null, null, null, null, null],
        [3, 1, null, null, null, null, null],
        [3, 2, 0, null, null, null, null],
        [3, 3, 1, null, null, null, null],
        [3, 3, 2, null, null, null, null],
        [3, 3, 2, 0, null, null, null],
        [3, 3, 3, 1, null, null, null],
        [3, 3, 3, 2, null, null, null],
        [3, 3, 3, 2, 0, null, null],
        [3, 3, 3, 3, 1, null, null],
        [3, 3, 3, 3, 2, null, null],
        [3, 3, 3, 3, 2, 0, null],
        [4, 3, 3, 3, 3, 1, null],
        [4, 4, 3, 3, 3, 2, null],
        [4, 4, 4, 3, 3, 2, 0],
        [4, 4, 4, 4, 3, 3, 1],
        [4, 4, 4, 4, 4, 3, 2],
        [4, 4, 4, 4, 4, 4, 3],
        [4, 4, 4, 4, 4, 4, 4],
    ],
    Paladino: [
        [null, null, null, null], [null, null, null, null], [null, null, null, null],
        [0, null, null, null], [0, null, null, null], [1, null, null, null],
        [1, null, null, null], [1, 0, null, null], [1, 0, null, null], [1, 1, null, null],
        [1, 1, 0, null], [1, 1, 1, null], [1, 1, 1, null], [2, 1, 1, 0], [2, 1, 1, 1],
        [2, 2, 1, 1], [2, 2, 2, 1], [3, 2, 2, 1], [3, 3, 3, 2], [3, 3, 3, 3],
    ],
    Ranger: [
        [null, null, null, null], [null, null, null, null], [null, null, null, null],
        [0, null, null, null], [0, null, null, null], [1, null, null, null],
        [1, null, null, null], [1, 0, null, null], [1, 0, null, null], [1, 1, null, null],
        [1, 1, 0, null], [1, 1, 1, null], [1, 1, 1, null], [2, 1, 1, 0], [2, 1, 1, 1],
        [2, 2, 1, 1], [2, 2, 2, 1], [3, 2, 2, 1], [3, 3, 3, 2], [3, 3, 3, 3],
    ],
};

/**
 * Magias por dia (Normal) — Clérigo.
 * Layout da planilha Magias por dia clerigo.xlsx (aba Clérigo): coluna C = nível de magia 0;
 * pares (Normal, Domínio) a partir das colunas D–E para os níveis 1–9. O segundo número da
 * coluna D não é domínio de truque — era erro de leitura antigo.
 */
const CLERIC_SPELLS_PER_DAY_NORMAL = [
    [3, 1, null, null, null, null, null, null, null, null],
    [4, 2, null, null, null, null, null, null, null, null],
    [5, 2, 1, null, null, null, null, null, null, null],
    [5, 3, 2, null, null, null, null, null, null, null],
    [5, 3, 2, 1, null, null, null, null, null, null],
    [6, 3, 3, 2, null, null, null, null, null, null],
    [6, 4, 3, 2, 1, null, null, null, null, null],
    [6, 4, 3, 3, 2, null, null, null, null, null],
    [6, 4, 4, 3, 2, 1, null, null, null, null],
    [6, 4, 4, 3, 3, 2, null, null, null, null],
    [6, 5, 4, 4, 3, 2, 1, null, null, null],
    [6, 5, 4, 4, 3, 3, 2, null, null, null],
    [6, 5, 5, 4, 4, 3, 2, 1, null, null],
    [6, 5, 5, 4, 4, 3, 3, 2, null, null],
    [6, 5, 5, 5, 4, 4, 3, 2, 1, null],
    [6, 5, 5, 5, 4, 4, 3, 3, 2, null],
    [6, 5, 5, 5, 5, 4, 4, 3, 2, 1],
    [6, 5, 5, 5, 5, 4, 4, 3, 3, 2],
    [6, 5, 5, 5, 5, 5, 4, 4, 3, 3],
    [6, 5, 5, 5, 5, 5, 4, 4, 4, 4],
];

/** Slots de domínio por nível de magia (1 onde a planilha tem coluna Domínio). Truques (nível 0): 0 — par Normal/Domínio só a partir do nível 1 (colunas D–E). */
const CLERIC_SPELLS_PER_DAY_DOMINIO = [
    [0, 1, null, null, null, null, null, null, null, null],
    [0, 1, null, null, null, null, null, null, null, null],
    [0, 1, 1, null, null, null, null, null, null, null],
    [0, 1, 1, null, null, null, null, null, null, null],
    [0, 1, 1, 1, null, null, null, null, null, null],
    [0, 1, 1, 1, null, null, null, null, null, null],
    [0, 1, 1, 1, 1, null, null, null, null, null],
    [0, 1, 1, 1, 1, null, null, null, null, null],
    [0, 1, 1, 1, 1, 1, null, null, null, null],
    [0, 1, 1, 1, 1, 1, null, null, null, null],
    [0, 1, 1, 1, 1, 1, 1, null, null, null],
    [0, 1, 1, 1, 1, 1, 1, null, null, null],
    [0, 1, 1, 1, 1, 1, 1, 1, null, null],
    [0, 1, 1, 1, 1, 1, 1, 1, null, null],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, null],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, null],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
];

/** Magias adicionais por modificador do atributo de conjuração (níveis 0–9). Fonte: tabela1-1_mod_habilidades_e_magias.xlsx (Tabela 1-1). */
const SPELL_BONUS_BY_MODIFIER = {
    '-5': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    '-4': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    '-3': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    '-2': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    '-1': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    0: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    1: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    4: [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    5: [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
    6: [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    7: [1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    8: [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    9: [1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    10: [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    11: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    12: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    13: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    14: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    15: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    16: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    17: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    18: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    19: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    20: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    21: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    22: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    23: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    24: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    25: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    26: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    27: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    28: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    29: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    30: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    31: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    32: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    33: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    34: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    35: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    36: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    37: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    38: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    39: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    40: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    41: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    42: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    43: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    44: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    45: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
};

function bonusMagiasPorNivelDoModificador(modificador) {
    const m = Math.max(-5, Math.min(45, Math.floor(Number(modificador) || 0)));
    const row = SPELL_BONUS_BY_MODIFIER[m] ?? SPELL_BONUS_BY_MODIFIER[String(m)];
    return row ?? SPELL_BONUS_BY_MODIFIER[0];
}

/** Atributo que fornece o modificador para magias adicionais (Tabela 1-1). */
const SPELLCASTING_ABILITY_BY_CLASS = {
    Mago: 'inteligencia',
    Feiticeiro: 'carisma',
    'Clérigo': 'sabedoria',
    Druida: 'sabedoria',
    Bardo: 'carisma',
    Paladino: 'sabedoria',
    Ranger: 'sabedoria',
};

function normalizeText(value) {
    if (!value) return '';
    return String(value)
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toUpperCase()
        .trim();
}

function extractConjuradoraClasses(classe) {
    return Array.from(new Set(
        String(classe || '')
            .split(/[\/,;|]+/)
            .map((parte) => CANONICAL_CLASSES[normalizeText(parte)] || '')
            .filter(Boolean)
    ));
}

function normalizeCombatenteTipo(tipo) {
    const value = (tipo || '').toString().toLowerCase().trim();
    if (value === 'jogador' || value === 'monstro' || value === 'npc') return value;
    return '';
}

function isTipoJogador(tipo) {
    return normalizeCombatenteTipo(tipo) === 'jogador';
}

function isTipoMonstro(tipo) {
    return normalizeCombatenteTipo(tipo) === 'monstro';
}

function isTipoNpc(tipo) {
    return normalizeCombatenteTipo(tipo) === 'npc';
}

function isTipoRestritoParaMestre(tipo) {
    const normalized = normalizeCombatenteTipo(tipo);
    return normalized === 'monstro' || normalized === 'npc';
}

function tipoPermitidoParaPerfil(tipo, isMestre) {
    const normalized = normalizeCombatenteTipo(tipo);
    if (!normalized) return isMestre ? null : 'jogador';
    if (isMestre) return normalized;
    return isTipoRestritoParaMestre(normalized) ? 'jogador' : normalized;
}

function countByTipo(combatentes, tipo) {
    const alvo = normalizeCombatenteTipo(tipo);
    if (!Array.isArray(combatentes) || !alvo) return 0;
    return combatentes.filter((c) => normalizeCombatenteTipo(c.tipo) === alvo).length;
}

function normalizeClasseConjuradora(classe) {
    const normalized = normalizeText(classe);
    if (CANONICAL_CLASSES[normalized]) return CANONICAL_CLASSES[normalized];
    return extractConjuradoraClasses(classe)[0] || '';
}

function isClasseConjuradora(classe) {
    return extractConjuradoraClasses(classe).length > 0;
}

function classeTabelaMagias(classe) {
    const canonical = normalizeClasseConjuradora(classe);
    if (!canonical) return '';
    return canonical === 'Feiticeiro' ? 'Mago' : canonical;
}

function getFallbackSpellSlots(classe, nivelPersonagem, atributos = {}) {
    const canonical = normalizeClasseConjuradora(classe);
    if (!canonical) return [];

    const nivel = Math.min(20, Math.max(1, Number(nivelPersonagem || 1)));
    const atributoChave = SPELLCASTING_ABILITY_BY_CLASS[canonical];
    const valorAtributo = Math.max(1, Number(atributos?.[atributoChave] || 10));
    const modificador = Math.floor((valorAtributo - 10) / 2);
    const bonusPorNivel = bonusMagiasPorNivelDoModificador(modificador);

    if (canonical === 'Clérigo') {
        const linhaN = CLERIC_SPELLS_PER_DAY_NORMAL[nivel - 1] || [];
        const linhaD = CLERIC_SPELLS_PER_DAY_DOMINIO[nivel - 1] || [];
        const slots = [];
        for (let sl = 0; sl < 10; sl++) {
            const rawN = linhaN[sl];
            const rawD = linhaD[sl];
            if (rawN == null && rawD == null) continue;
            const bonusSab = Number(bonusPorNivel[sl] || 0);
            const baseN = rawN == null ? 0 : Number(rawN);
            const baseD = rawD == null ? 0 : Number(rawD);
            const totalN = Math.max(0, baseN + bonusSab);
            const totalD = Math.max(0, baseD);
            slots.push({
                nivel: sl,
                total: totalN + totalD,
                total_normal: totalN,
                total_dominio: totalD,
                usados: 0,
                origem: 'tabela',
            });
        }
        return slots;
    }

    const tabela = SPELL_SLOT_TABLES[canonical];
    if (!tabela) return [];

    const linhaNivel = tabela[nivel - 1] || [];

    return linhaNivel.reduce((slots, base, nivelMagia) => {
        if (base === null || base === undefined) return slots;
        const bonus = Number(bonusPorNivel[nivelMagia] || 0);
        const total = Math.max(0, Number(base || 0) + bonus);
        slots.push({
            nivel: nivelMagia,
            total,
            usados: 0,
            origem: 'tabela',
        });
        return slots;
    }, []);
}

/**
 * Texto curto para UI: magias por dia (inclui bônus por atributo de conjuração) vs slots de domínio.
 * Só relevante quando `slot` tem total_normal / total_dominio (Clérigo).
 */
function textoSlotsClerigoBreakdown(slot) {
    if (!slot || slot.total_normal == null || slot.total_dominio == null) return '';
    const tn = Number(slot.total_normal);
    const td = Number(slot.total_dominio);
    if (Number.isNaN(tn) || Number.isNaN(td)) return '';
    if (td > 0) return `${tn} por dia · ${td} domínio`;
    return `${tn} por dia`;
}

function resolveCombatenteSpellSlots(combatente, classe = null) {
    const calculados = getFallbackSpellSlots(classe || combatente?.classe, combatente?.nivel, combatente || {});
    const existentes = Array.isArray(combatente?.magias_slots) ? combatente.magias_slots : [];

    if (!existentes.length) {
        return calculados;
    }

    const mapa = new Map();
    calculados.forEach((slot) => {
        mapa.set(Number(slot.nivel || 0), { ...slot });
    });

    existentes.forEach((slot) => {
        const nivel = Number(slot?.nivel || 0);
        const atual = mapa.get(nivel) || { nivel, total: 0, usados: 0, origem: 'api' };
        const totalExistente = Math.max(0, Number(slot?.total || 0));
        const totalCalculado = Math.max(0, Number(atual.total || 0));
        const usados = Math.max(0, Number(slot?.usados || atual.usados || 0));

        mapa.set(nivel, {
            ...atual,
            ...slot,
            nivel,
            total: Math.max(totalExistente, totalCalculado),
            total_normal: atual.total_normal,
            total_dominio: atual.total_dominio,
            usados: Math.min(Math.max(totalExistente, totalCalculado), usados),
            origem: totalExistente > 0 || slot?.id ? 'api' : atual.origem,
        });
    });

    return [...mapa.values()].sort((a, b) => Number(a.nivel || 0) - Number(b.nivel || 0));
}

const CombatRules = {
    normalizeCombatenteTipo,
    isTipoJogador,
    isTipoMonstro,
    isTipoNpc,
    isTipoRestritoParaMestre,
    tipoPermitidoParaPerfil,
    countByTipo,
    extractConjuradoraClasses,
    normalizeClasseConjuradora,
    isClasseConjuradora,
    classeTabelaMagias,
    getFallbackSpellSlots,
    resolveCombatenteSpellSlots,
    textoSlotsClerigoBreakdown,
    bonusMagiasPorNivelDoModificador,
};

if (typeof window !== 'undefined') {
    window.CombatRules = window.CombatRules || CombatRules;
}

export {
    normalizeCombatenteTipo,
    isTipoJogador,
    isTipoMonstro,
    isTipoNpc,
    isTipoRestritoParaMestre,
    tipoPermitidoParaPerfil,
    countByTipo,
    extractConjuradoraClasses,
    normalizeClasseConjuradora,
    isClasseConjuradora,
    classeTabelaMagias,
    getFallbackSpellSlots,
    resolveCombatenteSpellSlots,
    textoSlotsClerigoBreakdown,
    bonusMagiasPorNivelDoModificador,
    CombatRules,
};