(function () {
    function normalizeText(value) {
        if (!value) return '';
        return String(value)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toUpperCase()
            .trim();
    }

    function normalizeCombatenteTipo(tipo) {
        var value = (tipo || '').toString().toLowerCase().trim();
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
        var normalized = normalizeCombatenteTipo(tipo);
        return normalized === 'monstro' || normalized === 'npc';
    }

    function tipoPermitidoParaPerfil(tipo, isMestre) {
        var normalized = normalizeCombatenteTipo(tipo);
        if (!normalized) return isMestre ? null : 'jogador';
        if (isMestre) return normalized;
        return isTipoRestritoParaMestre(normalized) ? 'jogador' : normalized;
    }

    function countByTipo(combatentes, tipo) {
        var alvo = normalizeCombatenteTipo(tipo);
        if (!Array.isArray(combatentes) || !alvo) return 0;
        return combatentes.filter(function (c) { return normalizeCombatenteTipo(c.tipo) === alvo; }).length;
    }

    var CANONICAL_CLASSES = {
        MAGO: 'Mago',
        FEITICEIRO: 'Feiticeiro',
        CLERIGO: 'Clérigo',
        DRUIDA: 'Druida',
        BARDO: 'Bardo',
        PALADINO: 'Paladino',
        RANGER: 'Ranger'
    };

    function extractConjuradoraClasses(classe) {
        return Array.from(new Set(
            String(classe || '')
                .split(/[\/,;|]+/)
                .map(function (parte) { return CANONICAL_CLASSES[normalizeText(parte)] || ''; })
                .filter(Boolean)
        ));
    }

    function normalizeClasseConjuradora(classe) {
        var normalized = normalizeText(classe);
        if (CANONICAL_CLASSES[normalized]) return CANONICAL_CLASSES[normalized];
        return extractConjuradoraClasses(classe)[0] || '';
    }

    function isClasseConjuradora(classe) {
        return extractConjuradoraClasses(classe).length > 0;
    }

    function classeTabelaMagias(classe) {
        var canonical = normalizeClasseConjuradora(classe);
        if (!canonical) return '';
        return canonical === 'Feiticeiro' ? 'Mago' : canonical;
    }

    window.CombatRules = window.CombatRules || {
        normalizeCombatenteTipo: normalizeCombatenteTipo,
        isTipoJogador: isTipoJogador,
        isTipoMonstro: isTipoMonstro,
        isTipoNpc: isTipoNpc,
        isTipoRestritoParaMestre: isTipoRestritoParaMestre,
        tipoPermitidoParaPerfil: tipoPermitidoParaPerfil,
        countByTipo: countByTipo,
        extractConjuradoraClasses: extractConjuradoraClasses,
        normalizeClasseConjuradora: normalizeClasseConjuradora,
        isClasseConjuradora: isClasseConjuradora,
        classeTabelaMagias: classeTabelaMagias,
    };
})();