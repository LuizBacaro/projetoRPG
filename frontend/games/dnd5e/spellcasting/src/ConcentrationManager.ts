/**
 * Concentração D&D 5e — uma magia ativa; quebra por dano, nova magia ou incapacitação.
 */

import type { ConcentrationInfo, DiceRoller, Spell } from './types.js';
import type { SpellCasterCharacter } from './Character.js';
import { defaultDiceRoller } from './dice.js';

export class ConcentrationManager {
  private info: ConcentrationInfo = { activeSpell: null, startTurn: 0 };

  /** Registra magia em concentração no turno atual. */
  startConcentration(spell: Spell, currentTurn: number): void {
    if (!spell.concentration) return;
    this.info = { activeSpell: spell, startTurn: currentTurn };
  }

  /** Encerra concentração sem teste. */
  breakConcentration(): void {
    this.info = { activeSpell: null, startTurn: 0 };
  }

  isConcentrating(): boolean {
    return this.info.activeSpell !== null;
  }

  getInfo(): ConcentrationInfo {
    return { ...this.info, activeSpell: this.info.activeSpell };
  }

  /**
   * Teste de Constituição ao sofrer dano (PHB §5.2).
   * CD = max(10, floor(dano/2)). Retorna true se manteve concentração.
   */
  onDamage(
    damageAmount: number,
    caster: SpellCasterCharacter,
    roller: DiceRoller = defaultDiceRoller
  ): boolean {
    if (!this.isConcentrating()) return true;

    const dc = Math.max(10, Math.floor(damageAmount / 2));
    const passed = caster.makeConstitutionSave(dc, roller);
    if (!passed) {
      this.breakConcentration();
      return false;
    }
    return true;
  }
}
