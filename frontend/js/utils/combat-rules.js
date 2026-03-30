const CANONICAL_CLASSES = {
    MAGO: 'Mago',
    FEITICEIRO: 'Feiticeiro',
    CLERIGO: 'Clérigo',
    DRUIDA: 'Druida',
    BARDO: 'Bardo',
    PALADINO: 'Paladino',
    RANGER: 'Ranger',
};

function normalizeText(value) {
    if (!value) return '';
    return String(value)
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toUpperCase()
        .trim();
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
    return CANONICAL_CLASSES[normalized] || '';
}

function isClasseConjuradora(classe) {
    return !!normalizeClasseConjuradora(classe);
}

function classeTabelaMagias(classe) {
    const canonical = normalizeClasseConjuradora(classe);
    if (!canonical) return '';
    return canonical === 'Feiticeiro' ? 'Mago' : canonical;
}

const CombatRules = {
    normalizeCombatenteTipo,
    isTipoJogador,
    isTipoMonstro,
    isTipoNpc,
    isTipoRestritoParaMestre,
    tipoPermitidoParaPerfil,
    countByTipo,
    normalizeClasseConjuradora,
    isClasseConjuradora,
    classeTabelaMagias,
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
    normalizeClasseConjuradora,
    isClasseConjuradora,
    classeTabelaMagias,
    CombatRules,
};