/**
 * Tabela de progressão de slots — conjurador completo (PHB).
 * Índice do array: [0]=truques, [1]=1º nível, … [9]=9º nível.
 */

/** Slots máximos por nível de personagem (1–20). */
export const FULL_CASTER_SLOTS_BY_LEVEL: Record<number, number[]> = {
  1: [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
  2: [0, 3, 0, 0, 0, 0, 0, 0, 0, 0],
  3: [0, 4, 2, 0, 0, 0, 0, 0, 0, 0],
  4: [0, 4, 3, 0, 0, 0, 0, 0, 0, 0],
  5: [0, 4, 3, 2, 0, 0, 0, 0, 0, 0],
  6: [0, 4, 3, 3, 0, 0, 0, 0, 0, 0],
  7: [0, 4, 4, 3, 2, 0, 0, 0, 0, 0],
  8: [0, 4, 4, 3, 3, 0, 0, 0, 0, 0],
  9: [0, 4, 4, 4, 3, 2, 0, 0, 0, 0],
  10: [0, 4, 4, 4, 3, 3, 0, 0, 0, 0],
  11: [0, 4, 4, 4, 4, 3, 2, 0, 0, 0],
  12: [0, 4, 4, 4, 4, 3, 3, 0, 0, 0],
  13: [0, 4, 4, 4, 4, 4, 3, 2, 0, 0],
  14: [0, 4, 4, 4, 4, 4, 3, 3, 0, 0],
  15: [0, 4, 4, 4, 4, 4, 4, 3, 2, 0],
  16: [0, 4, 4, 4, 4, 4, 4, 3, 3, 0],
  17: [0, 4, 4, 4, 4, 4, 4, 4, 3, 2],
  18: [0, 4, 4, 4, 4, 4, 4, 4, 3, 3],
  19: [0, 4, 4, 4, 4, 4, 4, 4, 4, 3],
  20: [0, 4, 4, 4, 4, 4, 4, 4, 4, 4],
};

/** Classes que recuperam slots em repouso curto (Bruxo). */
export const SHORT_REST_RECOVER_ALL: ReadonlySet<string> = new Set([
  'bruxo',
  'warlock',
]);

/** Classes com preparação diária de magias. */
export const PREPARED_CASTERS: ReadonlySet<string> = new Set([
  'mago',
  'wizard',
  'clerigo',
  'cleric',
  'druida',
  'druid',
  'paladino',
  'paladin',
]);

export function slotsForCharacterLevel(characterLevel: number): number[] {
  const lvl = Math.max(1, Math.min(20, characterLevel));
  return [...(FULL_CASTER_SLOTS_BY_LEVEL[lvl] ?? FULL_CASTER_SLOTS_BY_LEVEL[1])];
}
