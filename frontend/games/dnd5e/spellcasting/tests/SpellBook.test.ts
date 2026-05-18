import './fixtures.js';
import { describe, expect, it } from 'vitest';
import { SpellBook } from '../src/SpellBook.js';
import { getSpellById } from '../src/SpellDatabase.js';

describe('SpellBook', () => {
  it('mago prepara até INT + nível', () => {
    const book = new SpellBook('mago', getSpellById, {
      mode: 'prepared',
      spellbookIds: ['fire-bolt', 'magic-missile', 'fireball'],
    });
    const max = SpellBook.maxPreparedCount('prepared', 4, 5);
    expect(max).toBe(9);
    expect(book.prepare('fire-bolt', max)).toBe(true);
    expect(book.prepare('magic-missile', max)).toBe(true);
    expect(book.knowsOrPrepared('fire-bolt')).toBe(true);
  });

  it('feiticeiro usa lista conhecida', () => {
    const book = new SpellBook('feiticeiro', getSpellById, {
      mode: 'known',
      knownSpellIds: ['fire-bolt', 'shield'],
    });
    expect(book.knowsOrPrepared('fire-bolt')).toBe(true);
    expect(book.knowsOrPrepared('fireball')).toBe(false);
  });

  it('calcula páginas do grimório de mago', () => {
    const book = new SpellBook('mago', getSpellById, {
      spellbookIds: ['magic-missile', 'fireball'],
    });
    expect(book.totalWizardPages()).toBe(4);
  });
});
