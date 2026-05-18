/**
 * Motor de lançamento — validações, CD, ataques, dano, slots e concentração.
 * Fluxo conforme `.cursor/requisitos/dnd5e/09-regra-lista-magias.md`.
 */
import type { CastResult, DiceRoller, Point, Spell } from './types.js';
import { SpellCasterCharacter, SpellTargetCharacter } from './Character.js';
export interface CastSpellOptions {
    slotLevel?: number;
    ritual?: boolean;
    /** Se true, não gasta slot (ritual ou truque). */
    skipSlotConsumption?: boolean;
}
export declare class SpellCastingEngine {
    /**
     * Lança magia contra alvo ou ponto (área sem alvo único).
     * Retorna CastResult com motivo em caso de falha nas validações.
     */
    castSpell(spell: Spell, caster: SpellCasterCharacter, target?: SpellTargetCharacter | Point, options?: CastSpellOptions): CastResult;
    /** Valida componentes V, S e M (PHB §2). */
    checkComponents(spell: Spell, caster: SpellCasterCharacter): {
        ok: true;
    } | {
        ok: false;
        reason: string;
    };
    private applyEffect;
    /** Calcula dano/cura com upcast e escala de truques. */
    rollSpellDamage(spell: Spell, caster: SpellCasterCharacter, slotLevel: number, roller?: DiceRoller): {
        total: number;
        expression: string;
    };
}
//# sourceMappingURL=SpellCastingEngine.d.ts.map