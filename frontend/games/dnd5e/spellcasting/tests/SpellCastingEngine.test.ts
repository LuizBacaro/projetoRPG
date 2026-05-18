import './fixtures.js';
import { describe, expect, it } from 'vitest';
import { SpellCasterCharacter, SpellTargetCharacter } from '../src/Character.js';
import { SpellCastingEngine } from '../src/SpellCastingEngine.js';
import { getSpellById } from '../src/SpellDatabase.js';
import { fixedRoller } from './fixtures.js';

describe('SpellCastingEngine', () => {
  const engine = new SpellCastingEngine();

  function wizard(partial: Partial<ConstructorParameters<typeof SpellCasterCharacter>[0]> = {}) {
    return new SpellCasterCharacter({
      id: 'w1',
      name: 'Mago',
      level: 5,
      classSlug: 'mago',
      abilityScores: {
        strength: 8,
        dexterity: 14,
        constitution: 12,
        intelligence: 18,
        wisdom: 10,
        charisma: 10,
      },
      spellcastingAbility: 'intelligence',
      proficiencyBonus: 3,
      spellBookState: {
        mode: 'prepared',
        preparedSpellIds: [
          'fire-bolt',
          'magic-missile',
          'fireball',
          'shield',
        ],
        knownSpellIds: ['fire-bolt', 'magic-missile', 'fireball', 'shield'],
      },
      resolveSpell: getSpellById,
      roller: fixedRoller({ d20: [15], dice: 24 }),
      ...partial,
    });
  }

  it('falha sem proficiência em armadura', () => {
    const c = wizard({ isProficientWithArmor: false });
    const res = engine.castSpell(getSpellById('fire-bolt')!, c, new SpellTargetCharacter('Goblin', 12));
    expect(res.success).toBe(false);
    expect(res.reason).toMatch(/armadura/i);
  });

  it('falha se silenciado com componente verbal', () => {
    const c = wizard({ isSilenced: true });
    const res = engine.castSpell(getSpellById('fire-bolt')!, c, new SpellTargetCharacter('Goblin', 12));
    expect(res.success).toBe(false);
    expect(res.reason).toMatch(/verbal/i);
  });

  it('falha sem mão livre em componente somático', () => {
    const c = wizard({ hasFreeHand: false, warCaster: false });
    const res = engine.castSpell(getSpellById('fire-bolt')!, c, new SpellTargetCharacter('Goblin', 12));
    expect(res.success).toBe(false);
    expect(res.reason).toMatch(/somático/i);
  });

  it('truque com ataque gasta slot zero', () => {
    const c = wizard();
    const before = c.spellSlotsManager.getAvailableSlots();
    const res = engine.castSpell(
      getSpellById('fire-bolt')!,
      c,
      new SpellTargetCharacter('Goblin', 10),
      {}
    );
    expect(res.success).toBe(true);
    expect(res.effect?.attackHit).toBe(true);
    expect(c.spellSlotsManager.getAvailableSlots()[1]).toBe(before[1]);
  });

  it('bola de fogo aplica metade do dano em save bem-sucedido', () => {
    const c = wizard();
    const target = new SpellTargetCharacter(
      'Grupo',
      14,
      { dexterity: 18 },
      fixedRoller({ d20: [20], dice: 24 })
    );
    const res = engine.castSpell(
      getSpellById('fireball')!,
      c,
      target,
      { slotLevel: 3 }
    );
    expect(res.success).toBe(true);
    expect(res.effect?.saveSucceeded).toBe(true);
    expect(res.effect?.damageDealt).toBe(12);
  });

  it('magia não preparada falha', () => {
    const c = wizard({ spellBookState: { mode: 'prepared', preparedSpellIds: [] } });
    const res = engine.castSpell(getSpellById('fireball')!, c);
    expect(res.success).toBe(false);
  });
});
