/**
 * Concentração D&D 5e — uma magia ativa; quebra por dano, nova magia ou incapacitação.
 */
import type { ConcentrationInfo, DiceRoller, Spell } from './types.js';
import type { SpellCasterCharacter } from './Character.js';
export declare class ConcentrationManager {
    private info;
    /** Registra magia em concentração no turno atual. */
    startConcentration(spell: Spell, currentTurn: number): void;
    /** Encerra concentração sem teste. */
    breakConcentration(): void;
    isConcentrating(): boolean;
    getInfo(): ConcentrationInfo;
    /**
     * Teste de Constituição ao sofrer dano (PHB §5.2).
     * CD = max(10, floor(dano/2)). Retorna true se manteve concentração.
     */
    onDamage(damageAmount: number, caster: SpellCasterCharacter, roller?: DiceRoller): boolean;
}
//# sourceMappingURL=ConcentrationManager.d.ts.map