import { describe, expect, it } from 'vitest';
import { SpellSlotsManager } from '../src/SpellSlotsManager.js';

describe('SpellSlotsManager', () => {
  it('truques não consomem slot', () => {
    const mgr = new SpellSlotsManager(5, 'mago');
    expect(mgr.canCast(0)).toBe(true);
    mgr.useSlot(0);
    expect(mgr.getAvailableSlots()[1]).toBe(4);
  });

  it('gasta e recupera no repouso longo', () => {
    const mgr = new SpellSlotsManager(7, 'mago');
    expect(mgr.canCast(3)).toBe(true);
    mgr.useSlot(3);
    mgr.useSlot(3);
    mgr.useSlot(3);
    expect(mgr.canCast(3)).toBe(false);
    mgr.recoverSlots('long');
    expect(mgr.canCast(3)).toBe(true);
  });

  it('bruxo recupera slots no repouso curto', () => {
    const mgr = new SpellSlotsManager(5, 'bruxo');
    mgr.useSlot(2);
    mgr.recoverSlots('short');
    expect(mgr.canCast(2)).toBe(true);
  });

  it('mago não recupera no repouso curto', () => {
    const mgr = new SpellSlotsManager(5, 'mago');
    const antes = mgr.getAvailableSlots()[1];
    for (let i = 0; i < antes; i += 1) mgr.useSlot(1);
    expect(mgr.canCast(1)).toBe(false);
    mgr.recoverSlots('short');
    expect(mgr.canCast(1)).toBe(false);
  });

  it('upcast exige slot >= nível da magia', () => {
    const mgr = new SpellSlotsManager(17, 'mago');
    expect(() => mgr.upcastToSlot(3, 2)).toThrow(/inferior/i);
    mgr.upcastToSlot(3, 5);
    const total5 = mgr.getMaxSlots()[5] ?? 0;
    for (let i = 0; i < total5; i += 1) mgr.useSlot(5);
    expect(mgr.canCast(5)).toBe(false);
  });
});
