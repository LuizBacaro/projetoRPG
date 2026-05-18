import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(fileURLToPath(import.meta.url), '..', '..');
const destDir = join(root, '..', 'js', 'spellcasting', 'data');
mkdirSync(destDir, { recursive: true });
copyFileSync(
  join(root, 'data', 'SpellDatabase.json'),
  join(destDir, 'SpellDatabase.json')
);
