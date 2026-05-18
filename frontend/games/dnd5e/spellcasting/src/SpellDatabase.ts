/**
 * Carrega e indexa SpellDatabase.json em tempo de execução.
 */

import type { Spell } from './types.js';

export interface SpellDatabaseFile {
  version: number;
  spells: Spell[];
}

let cachedSpells: Spell[] | null = null;
let cachedById: Map<string, Spell> | null = null;

/** Carrega magias a partir de objeto já parseado (testes / bundler). */
export function loadSpellDatabaseFromData(data: SpellDatabaseFile): Spell[] {
  cachedSpells = data.spells;
  cachedById = new Map(data.spells.map((s) => [s.id, s]));
  return cachedSpells;
}

/** Busca magia por id no cache. */
export function getSpellById(id: string): Spell | undefined {
  return cachedById?.get(id);
}

/** Lista completa do catálogo em memória. */
export function getAllSpells(): Spell[] {
  return cachedSpells ? [...cachedSpells] : [];
}

/**
 * Fetch do JSON no browser (caminho relativo à página da ficha).
 * Em Node/testes, use loadSpellDatabaseFromData com import do JSON.
 */
export async function fetchSpellDatabase(
  url = '/games/dnd5e/js/spellcasting/data/SpellDatabase.json'
): Promise<Spell[]> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Falha ao carregar catálogo de magias: ${res.status}`);
  }
  const data = (await res.json()) as SpellDatabaseFile;
  return loadSpellDatabaseFromData(data);
}

/** Habilidade de conjuração por classe (slug). */
export function spellcastingAbilityForClass(classSlug: string): import('./types.js').Ability {
  const slug = (classSlug || '').toLowerCase();
  const map: Record<string, import('./types.js').Ability> = {
    mago: 'intelligence',
    wizard: 'intelligence',
    clerigo: 'wisdom',
    cleric: 'wisdom',
    druida: 'wisdom',
    druid: 'wisdom',
    bardo: 'charisma',
    bard: 'charisma',
    feiticeiro: 'charisma',
    sorcerer: 'charisma',
    bruxo: 'charisma',
    warlock: 'charisma',
    paladino: 'charisma',
    paladin: 'charisma',
    patrulheiro: 'wisdom',
    ranger: 'wisdom',
  };
  return map[slug] ?? 'intelligence';
}

/** Classe é conjuradora (tem slots ou truques). */
export function isSpellcastingClass(classSlug: string): boolean {
  const slug = (classSlug || '').toLowerCase();
  return [
    'mago',
    'wizard',
    'clerigo',
    'cleric',
    'druida',
    'druid',
    'bardo',
    'bard',
    'feiticeiro',
    'sorcerer',
    'bruxo',
    'warlock',
    'paladino',
    'paladin',
    'patrulheiro',
    'ranger',
  ].includes(slug);
}
