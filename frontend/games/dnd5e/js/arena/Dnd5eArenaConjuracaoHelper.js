/**
 * Helpers para conjuração na arena D&D 5e — payload da API /combate/conjurar.
 */

const MAPA_SAVE = {
    reflexos: 'dexterity',
    fortitude: 'constitution',
    vontade: 'wisdom',
    dex: 'dexterity',
    con: 'constitution',
    wis: 'wisdom',
};

export function modAtributo(combatente, hab) {
    const key = String(hab || 'int').toLowerCase();
    const mapa = {
        int: 'intelligence_mod',
        intelligence: 'intelligence_mod',
        wis: 'wisdom_mod',
        wisdom: 'wisdom_mod',
        cha: 'charisma_mod',
        charisma: 'charisma_mod',
        dex: 'dexterity_mod',
        dexterity: 'dexterity_mod',
        con: 'constitution_mod',
        constitution: 'constitution_mod',
    };
    const campo = mapa[key];
    if (campo && Number.isFinite(combatente?.[campo])) {
        return Number(combatente[campo]);
    }
    const scoreMap = {
        int: 'inteligencia',
        intelligence: 'inteligencia',
        wis: 'sabedoria',
        wisdom: 'sabedoria',
        cha: 'carisma',
        charisma: 'carisma',
        dex: 'destreza',
        dexterity: 'destreza',
        con: 'constituicao',
        constitution: 'constituicao',
    };
    const score = Number(combatente?.[scoreMap[key] || 'inteligencia'] ?? 10);
    return Math.floor((score - 10) / 2);
}

export function normalizarSave(slug) {
    const s = String(slug || 'nenhum').trim().toLowerCase();
    const mapa = {
        dex: 'reflexos',
        destreza: 'reflexos',
        con: 'fortitude',
        constituicao: 'fortitude',
        wis: 'vontade',
        sabedoria: 'vontade',
        int: 'vontade',
        cha: 'vontade',
        for: 'fortitude',
        str: 'fortitude',
        nenhum: 'nenhum',
    };
    return mapa[s] || s;
}

export function modSalvamento(alvo, tipoSave) {
    if (!alvo) return 0;
    const tipo = normalizarSave(tipoSave);
    const salvamentos = alvo.salvamentos || [];
    const row = salvamentos.find((s) => s.slug === tipo || s.tipo === tipo);
    if (row && Number.isFinite(row.bonus)) return Number(row.bonus);
    const attr = MAPA_SAVE[tipo] || 'wisdom';
    return modAtributo(alvo, attr);
}

export function slotsParaPayload(estado) {
    const slots = Array.isArray(estado?.slots) ? estado.slots : [];
    const porNivel = new Map(slots.map((s) => [Number(s.nivel), s]));
    const espacos_por_nivel = [];
    const espacos_usados_por_nivel = [];
    for (let n = 0; n <= 9; n += 1) {
        const s = porNivel.get(n) || { total: 0, usados: 0 };
        espacos_por_nivel.push(Math.max(0, Number(s.total) || 0));
        espacos_usados_por_nivel.push(Math.max(0, Number(s.usados) || 0));
    }
    return { espacos_por_nivel, espacos_usados_por_nivel };
}

export function magiaPrecisaAlvo(magia) {
    if (!magia) return false;
    const atk = String(magia.magia_ataque_magico || '').trim().toLowerCase();
    if (atk === 'ranged' || atk === 'melee') return true;
    const temDano = !!(magia.magia_dano && String(magia.magia_dano).trim());
    const save = normalizarSave(magia.teste_resistencia);
    if (save !== 'nenhum' && temDano) return true;
    if (temDano) return true;
    return false;
}

export function habilidadePrimaria(estado) {
    return String(estado?.habilidade_primaria || 'int').toLowerCase();
}

export function montarPayloadConjurar(combatente, magia, estado, opts = {}) {
    const { espacos_por_nivel, espacos_usados_por_nivel } = slotsParaPayload(estado);
    const hab = habilidadePrimaria(estado);
    const alvo = opts.alvo || null;
    const nivelMagia = Number(magia?.magia_nivel ?? opts.nivel ?? 0) || 0;
    const modo = estado?.modo_lista || '';
    const preparado = modo === 'preparado' || estado?.prepara_magias === true;

    const payload = {
        conjurador_id: combatente.id,
        nome: combatente.nome,
        classe: combatente.classe,
        nivel_personagem: combatente.nivel || 1,
        magia_id: Number(magia.magia_id),
        personagem_id: combatente.personagemId,
        bonus_proficiencia: combatente.bonus_proficiencia ?? 2,
        mod_inteligencia: modAtributo(combatente, 'int'),
        mod_sabedoria: modAtributo(combatente, 'wis'),
        mod_carisma: modAtributo(combatente, 'cha'),
        mod_destreza: modAtributo(combatente, 'dex'),
        mod_constituicao: modAtributo(combatente, 'con'),
        espacos_por_nivel,
        espacos_usados_por_nivel,
        magia_concentracao_id: combatente.magia_concentracao_id || null,
        validar_preparacao: preparado,
        magias_preparadas_ids: estado?.magias_preparadas_ids || [],
        condicoes_atacante: opts.condicoes_atacante || [],
        condicoes_alvo: opts.condicoes_alvo || [],
        como_ritual: !!opts.como_ritual,
        confirmar_material_consumido: !!opts.confirmar_material,
    };

    if (opts.nivel_slot != null && nivelMagia >= 1) {
        payload.nivel_slot_usado = Number(opts.nivel_slot);
    }

    const atk = String(magia.magia_ataque_magico || '').trim().toLowerCase();
    if (atk === 'ranged' || atk === 'melee') {
        if (alvo) {
            payload.ac_alvo = alvo.ca;
            payload.condicoes_alvo = opts.condicoes_alvo || [];
        }
    }

    const save = normalizarSave(magia.teste_resistencia);
    if (save !== 'nenhum' && alvo) {
        payload.teste_resistencia_mod_alvo = modSalvamento(alvo, save);
    }

    return payload;
}
