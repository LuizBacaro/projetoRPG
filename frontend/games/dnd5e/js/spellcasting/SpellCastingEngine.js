/**
 * Motor de lançamento — validações, CD, ataques, dano, slots e concentração.
 * Fluxo conforme `.cursor/requisitos/dnd5e/09-regra-lista-magias.md`.
 */
import { buildDiceExpression, cantripDamageDiceCount, parseDieFaces, rollDiceExpression, } from './dice.js';
export class SpellCastingEngine {
    /**
     * Lança magia contra alvo ou ponto (área sem alvo único).
     * Retorna CastResult com motivo em caso de falha nas validações.
     */
    castSpell(spell, caster, target, options = {}) {
        const slotLevel = options.slotLevel ?? spell.level;
        const ritual = options.ritual ?? false;
        if (!caster.canCastSpell(spell)) {
            return { success: false, reason: 'Magia não conhecida ou não preparada.' };
        }
        const componentCheck = this.checkComponents(spell, caster);
        if (!componentCheck.ok) {
            return { success: false, reason: componentCheck.reason };
        }
        if (spell.level > 0 && !ritual && !options.skipSlotConsumption) {
            try {
                if (slotLevel > spell.level) {
                    caster.spellSlotsManager.upcastToSlot(spell.level, slotLevel);
                }
                else if (!caster.spellSlotsManager.canCast(slotLevel)) {
                    return { success: false, reason: 'Sem slot de magia disponível.' };
                }
            }
            catch (e) {
                return {
                    success: false,
                    reason: e instanceof Error ? e.message : 'Slot inválido.',
                };
            }
        }
        if (!caster.isProficientWithArmor) {
            return { success: false, reason: 'Sem proficiência na armadura — conjuração falha.' };
        }
        if (spell.castingTime.unit === 'bonus_action' &&
            caster.castBonusActionSpellThisTurn === false) {
            caster.castBonusActionSpellThisTurn = true;
        }
        if (spell.castingTime.unit === 'action' &&
            spell.level > 0 &&
            caster.castBonusActionSpellThisTurn) {
            return {
                success: false,
                reason: 'Após magia de ação bônus, só truques podem ser lançados como ação neste turno.',
            };
        }
        let concentrationBroken = false;
        if (caster.concentrationManager.isConcentrating()) {
            caster.concentrationManager.breakConcentration();
            concentrationBroken = true;
        }
        const dc = 8 + caster.spellcastingAbilityModifier + caster.proficiencyBonus;
        const attackBonus = caster.spellcastingAbilityModifier + caster.proficiencyBonus;
        const targetChar = target && 'armorClass' in target
            ? target
            : undefined;
        const effect = this.applyEffect(spell, caster, targetChar, slotLevel, dc, attackBonus);
        if (spell.level > 0 && !ritual && !options.skipSlotConsumption) {
            caster.spellSlotsManager.useSlot(slotLevel);
        }
        caster.consumeMaterialComponent(spell);
        let concentrationStarted = false;
        if (spell.concentration) {
            caster.concentrationManager.startConcentration(spell, caster.currentTurn);
            concentrationStarted = true;
        }
        return {
            success: true,
            spell,
            slotLevelUsed: spell.level > 0 ? slotLevel : undefined,
            effect,
            concentrationStarted,
            concentrationBroken,
        };
    }
    /** Valida componentes V, S e M (PHB §2). */
    checkComponents(spell, caster) {
        const { verbal, somatic, material } = spell.components;
        if (verbal && caster.isSilenced) {
            return { ok: false, reason: 'Componente verbal bloqueado (silêncio).' };
        }
        if (somatic && !caster.hasFreeHand && !caster.warCaster) {
            return { ok: false, reason: 'Componente somático requer mão livre.' };
        }
        if (material && !caster.hasMaterialComponent(spell)) {
            return { ok: false, reason: 'Componente material ausente ou sem custo pago.' };
        }
        return { ok: true };
    }
    applyEffect(spell, caster, target, slotLevel, dc, attackBonus) {
        const result = { dc };
        if (spell.saveInfo && target) {
            const saveRoll = target.rollSave(spell.saveInfo.ability);
            result.saveRoll = saveRoll;
            result.saveSucceeded = saveRoll >= dc;
            if (spell.damageInfo) {
                const raw = this.rollSpellDamage(spell, caster, slotLevel, caster.roller);
                result.diceRolled = raw.expression;
                if (result.saveSucceeded) {
                    if (spell.saveInfo.effect === 'half') {
                        result.damageDealt = Math.floor(raw.total / 2);
                    }
                    else if (spell.saveInfo.effect === 'none') {
                        result.damageDealt = 0;
                    }
                    else {
                        result.damageDealt = 0;
                    }
                }
                else {
                    result.damageDealt = raw.total;
                }
            }
            else if (result.saveSucceeded && spell.saveInfo.effect === 'negate') {
                result.conditionsApplied = [];
            }
            return result;
        }
        if (spell.attackInfo && target) {
            const attackRoll = caster.rollD20() + attackBonus;
            result.attackRoll = attackRoll;
            result.attackHit = attackRoll >= target.armorClass;
            if (result.attackHit && spell.damageInfo) {
                const raw = this.rollSpellDamage(spell, caster, slotLevel, caster.roller);
                result.diceRolled = raw.expression;
                result.damageDealt = raw.total;
            }
            return result;
        }
        if (spell.healingInfo) {
            const raw = this.rollSpellDamage({
                ...spell,
                damageInfo: {
                    dice: spell.healingInfo.dice,
                    scaling: spell.healingInfo.scaling,
                    dicePerSlotLevel: spell.healingInfo.dicePerSlotLevel,
                },
            }, caster, slotLevel, caster.roller);
            result.healingDone = raw.total;
            result.diceRolled = raw.expression;
            return result;
        }
        if (spell.damageInfo && !target) {
            const raw = this.rollSpellDamage(spell, caster, slotLevel, caster.roller);
            result.damageDealt = raw.total;
            result.diceRolled = raw.expression;
        }
        return result;
    }
    /** Calcula dano/cura com upcast e escala de truques. */
    rollSpellDamage(spell, caster, slotLevel, roller = caster.roller) {
        const info = spell.damageInfo;
        if (!info)
            return { total: 0, expression: '0' };
        const faces = parseDieFaces(info.dice);
        let diceCount = parseInt(info.dice.split('d')[0], 10) || 1;
        if (spell.level === 0 && info.scaling === 'per_character_level') {
            diceCount = cantripDamageDiceCount(caster.level);
        }
        if (info.scaling === 'per_slot_level' && slotLevel > spell.level && info.dicePerSlotLevel) {
            const extra = parseInt(info.dicePerSlotLevel.split('d')[0], 10) || 1;
            diceCount += (slotLevel - spell.level) * extra;
        }
        const expression = buildDiceExpression(diceCount, faces);
        const total = rollDiceExpression(expression, roller);
        return { total, expression };
    }
}
//# sourceMappingURL=SpellCastingEngine.js.map