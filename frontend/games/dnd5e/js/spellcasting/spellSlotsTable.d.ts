/**
 * Tabela de progressão de slots — conjurador completo (PHB).
 * Índice do array: [0]=truques, [1]=1º nível, … [9]=9º nível.
 */
/** Slots máximos por nível de personagem (1–20). */
export declare const FULL_CASTER_SLOTS_BY_LEVEL: Record<number, number[]>;
/** Classes que recuperam slots em repouso curto (Bruxo). */
export declare const SHORT_REST_RECOVER_ALL: ReadonlySet<string>;
/** Classes com preparação diária de magias. */
export declare const PREPARED_CASTERS: ReadonlySet<string>;
export declare function slotsForCharacterLevel(characterLevel: number): number[];
//# sourceMappingURL=spellSlotsTable.d.ts.map