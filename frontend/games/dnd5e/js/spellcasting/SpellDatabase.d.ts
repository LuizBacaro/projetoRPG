/**
 * Carrega e indexa SpellDatabase.json em tempo de execução.
 */
import type { Spell } from './types.js';
export interface SpellDatabaseFile {
    version: number;
    spells: Spell[];
}
/** Carrega magias a partir de objeto já parseado (testes / bundler). */
export declare function loadSpellDatabaseFromData(data: SpellDatabaseFile): Spell[];
/** Busca magia por id no cache. */
export declare function getSpellById(id: string): Spell | undefined;
/** Lista completa do catálogo em memória. */
export declare function getAllSpells(): Spell[];
/**
 * Fetch do JSON no browser (caminho relativo à página da ficha).
 * Em Node/testes, use loadSpellDatabaseFromData com import do JSON.
 */
export declare function fetchSpellDatabase(url?: string): Promise<Spell[]>;
/** Habilidade de conjuração por classe (slug). */
export declare function spellcastingAbilityForClass(classSlug: string): import('./types.js').Ability;
/** Classe é conjuradora (tem slots ou truques). */
export declare function isSpellcastingClass(classSlug: string): boolean;
//# sourceMappingURL=SpellDatabase.d.ts.map