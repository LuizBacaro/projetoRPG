/**
 * Personagem conjurador — integração com managers e inventário mínimo.
 */
import type { Ability, DiceRoller, InventoryItem, Spell, SpellBookState } from './types.js';
import { ConcentrationManager } from './ConcentrationManager.js';
import { SpellBook } from './SpellBook.js';
import { SpellSlotsManager } from './SpellSlotsManager.js';
/** Modificador de habilidade D&D 5e. */
export declare function abilityModifier(score: number): number;
export interface SpellCasterCharacterOptions {
    id: string;
    name: string;
    level: number;
    classSlug: string;
    abilityScores: Record<Ability, number>;
    spellcastingAbility: Ability;
    proficiencyBonus: number;
    isSilenced?: boolean;
    hasFreeHand?: boolean;
    warCaster?: boolean;
    isProficientWithArmor?: boolean;
    armorClass?: number;
    currentTurn?: number;
    inventory?: InventoryItem[];
    spellBookState?: Partial<SpellBookState>;
    slotsUsed?: number[];
    resolveSpell: (id: string) => Spell | undefined;
    roller?: DiceRoller;
}
/**
 * Personagem com suporte a conjuração — ponto de integração da ficha e da arena.
 */
export declare class SpellCasterCharacter {
    readonly id: string;
    readonly name: string;
    level: number;
    readonly classSlug: string;
    spellSlotsManager: SpellSlotsManager;
    concentrationManager: ConcentrationManager;
    spellBook: SpellBook;
    spellcastingAbility: Ability;
    proficiencyBonus: number;
    isSilenced: boolean;
    hasFreeHand: boolean;
    warCaster: boolean;
    isProficientWithArmor: boolean;
    armorClass: number;
    currentTurn: number;
    private inventory;
    private readonly abilityScores;
    readonly roller: DiceRoller;
    /** Regra de multicast: lançou magia como ação bônus neste turno. */
    castBonusActionSpellThisTurn: boolean;
    constructor(options: SpellCasterCharacterOptions);
    get spellcastingAbilityModifier(): number;
    get constitutionModifier(): number;
    /** Verifica se a magia está disponível (grimório). */
    canCastSpell(spell: Spell): boolean;
    rollD20(): number;
    /** Salvaguarda de Constituição (concentração e efeitos). */
    makeConstitutionSave(dc: number, roller?: DiceRoller): boolean;
    /** Salvaguarda genérica do alvo. */
    rollSave(ability: Ability, roller?: DiceRoller): number;
    /** Possui material no inventário (custo ou consumível). */
    hasMaterialComponent(spell: Spell): boolean;
    consumeMaterialComponent(spell: Spell): void;
    exportSpellBookState(): SpellBookState;
    exportSlotsUsed(): number[];
}
/** Alvo de magia em combate (simplificado). */
export declare class SpellTargetCharacter {
    name: string;
    armorClass: number;
    abilityScores: Record<Ability, number>;
    private roller;
    constructor(name: string, armorClass: number, abilityScores?: Partial<Record<Ability, number>>, roller?: DiceRoller);
    rollSave(ability: Ability): number;
}
//# sourceMappingURL=Character.d.ts.map