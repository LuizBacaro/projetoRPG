/**
 * Contratos de dados do sistema de magia D&D 5e (PHB).
 * Alinhados a `.cursor/requisitos/dnd5e/09-regra-lista-magias.md`.
 */

/** Habilidades usadas em salvaguardas e conjuração. */
export type Ability =
  | 'strength'
  | 'dexterity'
  | 'constitution'
  | 'intelligence'
  | 'wisdom'
  | 'charisma';

/** Efeito quando o alvo passa na salvaguarda. */
export type SaveEffect = 'half' | 'none' | 'negate';

/** Escalonamento de dano conforme regras 5e. */
export type DamageScaling = 'none' | 'per_slot_level' | 'per_character_level';

/** Tipo de ataque de magia. */
export type SpellAttackType = 'melee_spell' | 'ranged_spell';

/** Unidade de tempo de lançamento (simplificado para validação). */
export type CastingTimeUnit = 'action' | 'bonus_action' | 'reaction' | 'minute' | 'hour';

/**
 * Magia — unidade atômica do catálogo e do grimório.
 * Campos espelham a estrutura do documento de requisitos.
 */
export interface Spell {
  id: string;
  name: string;
  level: number; // 0 = truque, 1–9 = círculos
  school?: string;
  classes?: string[];
  castingTime: {
    value: number;
    unit: CastingTimeUnit;
    ritual: boolean;
  };
  range: {
    value?: number; // pés; omitido = pessoal/toque conforme rangeKind
    kind?: 'self' | 'touch' | 'feet' | 'sight' | 'unlimited';
  };
  components: {
    verbal: boolean;
    somatic: boolean;
    material: string | null;
    materialConsumed: boolean;
    materialCost: number; // ouro
  };
  duration: {
    value?: number;
    unit?: 'round' | 'minute' | 'hour' | 'day';
    instantaneous: boolean;
    untilDispelled: boolean;
  };
  concentration: boolean;
  description: string;
  damageInfo?: {
    dice: string; // ex.: "1d8"
    type?: string; // fogo, frio, etc.
    scaling: DamageScaling;
    /** Dados extras por nível de slot acima do nível base (upcast). */
    dicePerSlotLevel?: string;
  };
  healingInfo?: {
    dice: string;
    scaling: DamageScaling;
    dicePerSlotLevel?: string;
  };
  saveInfo?: {
    ability: Ability;
    effect: SaveEffect;
  };
  attackInfo?: {
    type: SpellAttackType;
  };
  areaOfEffect?: {
    size: number;
    shape?: 'sphere' | 'cube' | 'cone' | 'line' | 'cylinder';
  };
  higherLevelDescription?: string;
}

/** Slots disponíveis por nível de magia (chave = nível 1–9). */
export interface SpellSlots {
  [spellLevel: number]: number;
}

/** Estado de concentração ativa no personagem. */
export interface ConcentrationInfo {
  activeSpell: Spell | null;
  startTurn: number;
}

/** Ponto no mapa (magias de área sem alvo único). */
export interface Point {
  x: number;
  y: number;
}

/** Inventário mínimo para componentes materiais. */
export interface InventoryItem {
  id: string;
  name: string;
  quantity: number;
  goldValue?: number;
}

/** Resultado numérico de dano/cura aplicado. */
export interface EffectResult {
  damageDealt?: number;
  healingDone?: number;
  saveSucceeded?: boolean;
  attackHit?: boolean;
  attackRoll?: number;
  saveRoll?: number;
  dc?: number;
  diceRolled?: string;
  conditionsApplied?: string[];
}

/** Resultado completo de um lançamento. */
export interface CastResult {
  success: boolean;
  reason?: string;
  spell?: Spell;
  slotLevelUsed?: number;
  effect?: EffectResult;
  concentrationStarted?: boolean;
  concentrationBroken?: boolean;
}

/** Modo de lista de magias da classe (PHB §10.3). */
export type SpellListMode = 'known' | 'prepared';

/** Estado persistido do grimório na ficha JSON. */
export interface SpellBookState {
  mode: SpellListMode;
  /** Magias no grimório do Mago (todas que aprendeu). */
  spellbookIds: string[];
  /** Magias conhecidas (Bardo, Feiticeiro, Bruxo, etc.). */
  knownSpellIds: string[];
  /** Magias preparadas hoje (Mago, Clérigo, Druida, Paladino). */
  preparedSpellIds: string[];
  favorites: string[];
  annotations: Record<string, string>;
  /** Slots gastos (índice = nível de magia); persistido na ficha. */
  slotsUsed?: number[];
}

/** Callbacks de rolagem injetáveis (testes usam valores fixos). */
export interface DiceRoller {
  d20(): number;
  roll(expression: string): number;
}
