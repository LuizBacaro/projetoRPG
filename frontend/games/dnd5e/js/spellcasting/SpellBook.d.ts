/**
 * Grimório / lista de magias — conhecidas vs preparadas (PHB §10.3).
 * Persistência via SpellBookState na ficha JSON.
 */
import type { Spell, SpellBookState, SpellListMode } from './types.js';
/** Resolve modo de lista pela classe. */
export declare function spellListModeForClass(classSlug: string): SpellListMode;
export declare class SpellBook {
    private state;
    private readonly resolveSpell;
    constructor(classSlug: string, resolveSpell: (id: string) => Spell | undefined, initial?: Partial<SpellBookState>);
    getState(): SpellBookState;
    /** Magias que o personagem pode lançar hoje (preparadas ou conhecidas). */
    getCastableSpells(): Spell[];
    /** Grimório do Mago: todas as magias aprendidas no livro. */
    getSpellbookSpells(): Spell[];
    knowsOrPrepared(spellId: string): boolean;
    addToSpellbook(spellId: string): void;
    addKnown(spellId: string): void;
    removeKnown(spellId: string): void;
    prepare(spellId: string, maxPrepared: number): boolean;
    unprepare(spellId: string): void;
    /** Após descanso longo: Mago/Clérigo re-preparam (mantém lista ou limpa — MVP mantém). */
    afterLongRest(): void;
    toggleFavorite(spellId: string): boolean;
    setAnnotation(spellId: string, text: string): void;
    /** Páginas do grimório de Mago: soma dos níveis das magias no livro. */
    totalWizardPages(): number;
    /**
     * Limite de magias preparadas: INT + nível de mago (Mago) ou WIS/CHA + nível (Clérigo/Paladino).
     */
    static maxPreparedCount(mode: SpellListMode, abilityMod: number, casterLevel: number): number;
}
//# sourceMappingURL=SpellBook.d.ts.map