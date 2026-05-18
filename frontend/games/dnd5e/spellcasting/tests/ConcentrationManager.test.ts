import { describe, expect, it } from 'vitest';
import { ConcentrationManager } from '../src/ConcentrationManager.js';
import { SpellCasterCharacter } from '../src/Character.js';
import { getSpellById } from '../src/SpellDatabase.js';
import { fixedRoller } from './fixtures.js';

describe('ConcentrationManager', () => {
  const bless = getSpellById('bless')!;

  function caster(conMod = 2) {
    return new SpellCasterCharacter({
      id: 'c1',
      name: 'Clérigo',
      level: 5,
      classSlug: 'clerigo',
      abilityScores: {
        strength: 10,
        dexterity: 10,
        constitution: 10 + conMod * 2,
        intelligence: 10,
        wisdom: 16,
        charisma: 10,
      },
      spellcastingAbility: 'wisdom',
      proficiencyBonus: 3,
      resolveSpell: getSpellById,
    });
  }

  it('inicia e quebra concentração', () => {
    const mgr = new ConcentrationManager();
    mgr.startConcentration(bless, 1);
    expect(mgr.isConcentrating()).toBe(true);
    mgr.breakConcentration();
    expect(mgr.isConcentrating()).toBe(false);
  });

  it('dano alto quebra com salvaguarda falha', () => {
    const mgr = new ConcentrationManager();
    const c = caster();
    mgr.startConcentration(bless, 1);
    const kept = mgr.onDamage(30, c, fixedRoller({ d20: [1] }));
    expect(kept).toBe(false);
    expect(mgr.isConcentrating()).toBe(false);
  });

  it('salvaguarda bem-sucedida mantém concentração', () => {
    const mgr = new ConcentrationManager();
    const c = caster(3);
    mgr.startConcentration(bless, 1);
    const kept = mgr.onDamage(12, c, fixedRoller({ d20: [18] }));
    expect(kept).toBe(true);
    expect(mgr.isConcentrating()).toBe(true);
  });
});
