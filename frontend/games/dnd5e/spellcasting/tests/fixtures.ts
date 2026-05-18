import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import type { DiceRoller } from '../src/types.js';
import { loadSpellDatabaseFromData } from '../src/SpellDatabase.js';
import type { SpellDatabaseFile } from '../src/SpellDatabase.js';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const raw = readFileSync(join(root, 'data', 'SpellDatabase.json'), 'utf-8');
loadSpellDatabaseFromData(JSON.parse(raw) as SpellDatabaseFile);

export function fixedRoller(rolls: { d20?: number[]; dice?: number }): DiceRoller {
  const d20Queue = [...(rolls.d20 ?? [15])];
  return {
    d20() {
      return d20Queue.shift() ?? 10;
    },
    roll() {
      return rolls.dice ?? 10;
    },
  };
}
