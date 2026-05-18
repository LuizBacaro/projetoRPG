/**
 * Personagem conjurador — integração com managers e inventário mínimo.
 */
import { ConcentrationManager } from './ConcentrationManager.js';
import { SpellBook } from './SpellBook.js';
import { SpellSlotsManager } from './SpellSlotsManager.js';
import { defaultDiceRoller } from './dice.js';
/** Modificador de habilidade D&D 5e. */
export function abilityModifier(score) {
    return Math.floor((score - 10) / 2);
}
/**
 * Personagem com suporte a conjuração — ponto de integração da ficha e da arena.
 */
export class SpellCasterCharacter {
    constructor(options) {
        /** Regra de multicast: lançou magia como ação bônus neste turno. */
        this.castBonusActionSpellThisTurn = false;
        this.id = options.id;
        this.name = options.name;
        this.level = options.level;
        this.classSlug = options.classSlug;
        this.abilityScores = { ...options.abilityScores };
        this.spellcastingAbility = options.spellcastingAbility;
        this.proficiencyBonus = options.proficiencyBonus;
        this.isSilenced = options.isSilenced ?? false;
        this.hasFreeHand = options.hasFreeHand ?? true;
        this.warCaster = options.warCaster ?? false;
        this.isProficientWithArmor = options.isProficientWithArmor ?? true;
        this.armorClass = options.armorClass ?? 10;
        this.currentTurn = options.currentTurn ?? 0;
        this.inventory = [...(options.inventory ?? [])];
        this.roller = options.roller ?? defaultDiceRoller;
        this.spellSlotsManager = new SpellSlotsManager(this.level, this.classSlug, options.slotsUsed);
        this.concentrationManager = new ConcentrationManager();
        this.spellBook = new SpellBook(this.classSlug, options.resolveSpell, options.spellBookState);
    }
    get spellcastingAbilityModifier() {
        return abilityModifier(this.abilityScores[this.spellcastingAbility] ?? 10);
    }
    get constitutionModifier() {
        return abilityModifier(this.abilityScores.constitution ?? 10);
    }
    /** Verifica se a magia está disponível (grimório). */
    canCastSpell(spell) {
        return this.spellBook.knowsOrPrepared(spell.id);
    }
    rollD20() {
        return this.roller.d20();
    }
    /** Salvaguarda de Constituição (concentração e efeitos). */
    makeConstitutionSave(dc, roller) {
        const r = roller ?? this.roller;
        const roll = r.d20();
        const total = roll + this.constitutionModifier + this.proficiencyBonus;
        return total >= dc;
    }
    /** Salvaguarda genérica do alvo. */
    rollSave(ability, roller) {
        const r = roller ?? this.roller;
        return r.d20() + abilityModifier(this.abilityScores[ability] ?? 10);
    }
    /** Possui material no inventário (custo ou consumível). */
    hasMaterialComponent(spell) {
        const { material, materialConsumed, materialCost } = spell.components;
        if (!material)
            return true;
        if (materialCost > 0) {
            const gold = this.inventory.reduce((s, i) => s + (i.goldValue ?? 0) * i.quantity, 0);
            return gold >= materialCost;
        }
        if (materialConsumed) {
            return this.inventory.some((i) => i.name.toLowerCase().includes(material.toLowerCase().slice(0, 8)) && i.quantity > 0);
        }
        return true; // foco arcano / bolsa de componentes (MVP)
    }
    consumeMaterialComponent(spell) {
        const { material, materialConsumed } = spell.components;
        if (!material || !materialConsumed)
            return;
        const item = this.inventory.find((i) => i.name.toLowerCase().includes(material.toLowerCase().slice(0, 8)));
        if (item && item.quantity > 0)
            item.quantity -= 1;
    }
    exportSpellBookState() {
        return this.spellBook.getState();
    }
    exportSlotsUsed() {
        return this.spellSlotsManager.exportUsed();
    }
}
/** Alvo de magia em combate (simplificado). */
export class SpellTargetCharacter {
    constructor(name, armorClass, abilityScores = {}, roller = defaultDiceRoller) {
        this.name = name;
        this.armorClass = armorClass;
        this.abilityScores = {
            strength: 10,
            dexterity: 10,
            constitution: 10,
            intelligence: 10,
            wisdom: 10,
            charisma: 10,
            ...abilityScores,
        };
        this.roller = roller;
    }
    rollSave(ability) {
        return this.roller.d20() + abilityModifier(this.abilityScores[ability] ?? 10);
    }
}
//# sourceMappingURL=Character.js.map