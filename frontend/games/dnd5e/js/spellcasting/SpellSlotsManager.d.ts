/**
 * Gerencia espaços de magia: gasto, recuperação e upcast.
 * Regras: repouso longo (maioria), repouso curto (Bruxo), truques não gastam slot.
 */
import type { SpellSlots } from './types.js';
export declare class SpellSlotsManager {
    /** Slots máximos por índice de nível (0 = truque, sem gasto). */
    private readonly maxByLevel;
    /** Slots já gastos por nível. */
    private usedByLevel;
    private readonly classSlug;
    constructor(characterLevel: number, classSlug: string, usedByLevel?: number[]);
    /** Slots ainda disponíveis no nível informado (truques sempre true). */
    canCast(spellLevel: number): boolean;
    /** Gasta um slot do nível indicado; lança erro se indisponível. */
    useSlot(spellLevel: number): void;
    /**
     * Recupera slots conforme tipo de descanso.
     * Longo: zera gastos (PHB). Curto: Bruxo recupera tudo.
     */
    recoverSlots(restType: 'short' | 'long'): void;
    /** Mapa nível → quantidade disponível (apenas níveis 1–9 com valor > 0). */
    getAvailableSlots(): SpellSlots;
    /** Slots máximos (útil para UI do grimório). */
    getMaxSlots(): SpellSlots;
    /**
     * Valida upcast: slot usado deve ser >= nível base da magia.
     * Não gasta slot — apenas validação antes do lançamento.
     */
    upcastToSlot(spellLevel: number, slotLevel: number): void;
    /** Serialização para ficha JSON. */
    exportUsed(): number[];
    /** Atualiza nível do personagem (sobe de nível). */
    refreshForLevel(characterLevel: number): void;
}
//# sourceMappingURL=SpellSlotsManager.d.ts.map