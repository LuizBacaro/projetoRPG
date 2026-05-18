/**
 * Grimório / lista de magias — conhecidas vs preparadas (PHB §10.3).
 * Persistência via SpellBookState na ficha JSON.
 */
import { PREPARED_CASTERS } from './spellSlotsTable.js';
const EMPTY_STATE = {
    mode: 'known',
    spellbookIds: [],
    knownSpellIds: [],
    preparedSpellIds: [],
    favorites: [],
    annotations: {},
};
/** Resolve modo de lista pela classe. */
export function spellListModeForClass(classSlug) {
    return PREPARED_CASTERS.has((classSlug || '').toLowerCase()) ? 'prepared' : 'known';
}
export class SpellBook {
    constructor(classSlug, resolveSpell, initial) {
        this.resolveSpell = resolveSpell;
        const mode = initial?.mode ?? spellListModeForClass(classSlug);
        this.state = {
            ...EMPTY_STATE,
            mode,
            ...initial,
            favorites: [...(initial?.favorites ?? [])],
            spellbookIds: [...(initial?.spellbookIds ?? [])],
            knownSpellIds: [...(initial?.knownSpellIds ?? [])],
            preparedSpellIds: [...(initial?.preparedSpellIds ?? [])],
            annotations: { ...(initial?.annotations ?? {}) },
        };
    }
    getState() {
        return {
            ...this.state,
            favorites: [...this.state.favorites],
            spellbookIds: [...this.state.spellbookIds],
            knownSpellIds: [...this.state.knownSpellIds],
            preparedSpellIds: [...this.state.preparedSpellIds],
            annotations: { ...this.state.annotations },
        };
    }
    /** Magias que o personagem pode lançar hoje (preparadas ou conhecidas). */
    getCastableSpells() {
        const ids = this.state.mode === 'prepared'
            ? this.state.preparedSpellIds
            : this.state.knownSpellIds;
        return ids
            .map((id) => this.resolveSpell(id))
            .filter((s) => Boolean(s));
    }
    /** Grimório do Mago: todas as magias aprendidas no livro. */
    getSpellbookSpells() {
        return this.state.spellbookIds
            .map((id) => this.resolveSpell(id))
            .filter((s) => Boolean(s));
    }
    knowsOrPrepared(spellId) {
        if (this.state.mode === 'prepared') {
            return this.state.preparedSpellIds.includes(spellId);
        }
        return this.state.knownSpellIds.includes(spellId);
    }
    addToSpellbook(spellId) {
        if (!this.state.spellbookIds.includes(spellId)) {
            this.state.spellbookIds.push(spellId);
        }
        if (!this.state.knownSpellIds.includes(spellId)) {
            this.state.knownSpellIds.push(spellId);
        }
    }
    addKnown(spellId) {
        if (!this.state.knownSpellIds.includes(spellId)) {
            this.state.knownSpellIds.push(spellId);
        }
    }
    removeKnown(spellId) {
        this.state.knownSpellIds = this.state.knownSpellIds.filter((id) => id !== spellId);
        this.state.preparedSpellIds = this.state.preparedSpellIds.filter((id) => id !== spellId);
        this.state.favorites = this.state.favorites.filter((id) => id !== spellId);
    }
    prepare(spellId, maxPrepared) {
        if (this.state.preparedSpellIds.includes(spellId))
            return true;
        if (this.state.preparedSpellIds.length >= maxPrepared)
            return false;
        const inBook = this.state.spellbookIds.includes(spellId) ||
            this.state.knownSpellIds.includes(spellId);
        if (!inBook && this.state.mode === 'prepared') {
            this.state.spellbookIds.push(spellId);
        }
        this.state.preparedSpellIds.push(spellId);
        return true;
    }
    unprepare(spellId) {
        this.state.preparedSpellIds = this.state.preparedSpellIds.filter((id) => id !== spellId);
    }
    /** Após descanso longo: Mago/Clérigo re-preparam (mantém lista ou limpa — MVP mantém). */
    afterLongRest() {
        // Extensão futura: limpar preparadas se a UI exigir re-seleção manual.
    }
    toggleFavorite(spellId) {
        const idx = this.state.favorites.indexOf(spellId);
        if (idx >= 0) {
            this.state.favorites.splice(idx, 1);
            return false;
        }
        this.state.favorites.push(spellId);
        return true;
    }
    setAnnotation(spellId, text) {
        if (!text.trim()) {
            delete this.state.annotations[spellId];
            return;
        }
        this.state.annotations[spellId] = text.trim();
    }
    /** Páginas do grimório de Mago: soma dos níveis das magias no livro. */
    totalWizardPages() {
        return this.state.spellbookIds.reduce((sum, id) => {
            const s = this.resolveSpell(id);
            return sum + (s && s.level > 0 ? s.level : 0);
        }, 0);
    }
    /**
     * Limite de magias preparadas: INT + nível de mago (Mago) ou WIS/CHA + nível (Clérigo/Paladino).
     */
    static maxPreparedCount(mode, abilityMod, casterLevel) {
        if (mode !== 'prepared')
            return 0;
        return Math.max(1, abilityMod + casterLevel);
    }
}
//# sourceMappingURL=SpellBook.js.map