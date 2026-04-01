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
    'Clérigo': [
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

const SPELL_BONUS_BY_ABILITY_MOD = {
    1: [1, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [1, 1, 0, 0, 0, 0, 0, 0, 0],
    3: [1, 1, 1, 0, 0, 0, 0, 0, 0],
    4: [1, 1, 1, 1, 0, 0, 0, 0, 0],
    5: [2, 1, 1, 1, 1, 0, 0, 0, 0],
    6: [2, 2, 1, 1, 1, 1, 0, 0, 0],
    7: [2, 2, 2, 1, 1, 1, 1, 0, 0],
    8: [2, 2, 2, 2, 1, 1, 1, 1, 0],
    9: [2, 2, 2, 2, 2, 1, 1, 1, 1],
};

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
    const tabela = SPELL_SLOT_TABLES[canonical];
    if (!canonical || !tabela) return [];

    const nivel = Math.min(20, Math.max(1, Number(nivelPersonagem || 1)));
    const linhaNivel = tabela[nivel - 1] || [];
    const atributoChave = SPELLCASTING_ABILITY_BY_CLASS[canonical];
    const valorAtributo = Math.max(1, Number(atributos?.[atributoChave] || 10));
    const modificador = Math.floor((valorAtributo - 10) / 2);
    const bonusAtributo = SPELL_BONUS_BY_ABILITY_MOD[Math.max(0, modificador)] || [];

    return linhaNivel.reduce((slots, base, nivelMagia) => {
        if (base === null || base === undefined) return slots;
        const bonus = nivelMagia > 0 ? Number(bonusAtributo[nivelMagia - 1] || 0) : 0;
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
    CombatRules,
};