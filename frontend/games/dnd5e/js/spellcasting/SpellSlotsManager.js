/**
 * Gerencia espaços de magia: gasto, recuperação e upcast.
 * Regras: repouso longo (maioria), repouso curto (Bruxo), truques não gastam slot.
 */
import { SHORT_REST_RECOVER_ALL, slotsForCharacterLevel, } from './spellSlotsTable.js';
export class SpellSlotsManager {
    constructor(characterLevel, classSlug, usedByLevel) {
        this.maxByLevel = slotsForCharacterLevel(characterLevel);
        this.classSlug = (classSlug || '').toLowerCase();
        this.usedByLevel = usedByLevel
            ? [...usedByLevel]
            : new Array(this.maxByLevel.length).fill(0);
        if (this.usedByLevel.length < this.maxByLevel.length) {
            this.usedByLevel = [
                ...this.usedByLevel,
                ...new Array(this.maxByLevel.length - this.usedByLevel.length).fill(0),
            ];
        }
    }
    /** Slots ainda disponíveis no nível informado (truques sempre true). */
    canCast(spellLevel) {
        if (spellLevel <= 0)
            return true;
        return this.getAvailableSlots()[spellLevel] > 0;
    }
    /** Gasta um slot do nível indicado; lança erro se indisponível. */
    useSlot(spellLevel) {
        if (spellLevel <= 0)
            return;
        if (!this.canCast(spellLevel)) {
            throw new Error(`Sem slot de magia de ${spellLevel}º nível disponível.`);
        }
        this.usedByLevel[spellLevel] = (this.usedByLevel[spellLevel] ?? 0) + 1;
    }
    /**
     * Recupera slots conforme tipo de descanso.
     * Longo: zera gastos (PHB). Curto: Bruxo recupera tudo.
     */
    recoverSlots(restType) {
        if (restType === 'long') {
            this.usedByLevel = this.usedByLevel.map(() => 0);
            return;
        }
        if (SHORT_REST_RECOVER_ALL.has(this.classSlug)) {
            this.usedByLevel = this.usedByLevel.map(() => 0);
        }
    }
    /** Mapa nível → quantidade disponível (apenas níveis 1–9 com valor > 0). */
    getAvailableSlots() {
        const out = {};
        for (let lvl = 1; lvl < this.maxByLevel.length; lvl += 1) {
            const max = this.maxByLevel[lvl] ?? 0;
            const used = this.usedByLevel[lvl] ?? 0;
            const left = Math.max(0, max - used);
            if (left > 0)
                out[lvl] = left;
        }
        return out;
    }
    /** Slots máximos (útil para UI do grimório). */
    getMaxSlots() {
        const out = {};
        for (let lvl = 1; lvl < this.maxByLevel.length; lvl += 1) {
            const max = this.maxByLevel[lvl] ?? 0;
            if (max > 0)
                out[lvl] = max;
        }
        return out;
    }
    /**
     * Valida upcast: slot usado deve ser >= nível base da magia.
     * Não gasta slot — apenas validação antes do lançamento.
     */
    upcastToSlot(spellLevel, slotLevel) {
        if (spellLevel <= 0)
            return;
        if (slotLevel < spellLevel) {
            throw new Error(`Slot de ${slotLevel}º nível é inferior ao nível da magia (${spellLevel}º).`);
        }
        if (!this.canCast(slotLevel)) {
            throw new Error(`Sem slot de ${slotLevel}º nível para upcast.`);
        }
    }
    /** Serialização para ficha JSON. */
    exportUsed() {
        return [...this.usedByLevel];
    }
    /** Atualiza nível do personagem (sobe de nível). */
    refreshForLevel(characterLevel) {
        const next = slotsForCharacterLevel(characterLevel);
        const prevUsed = [...this.usedByLevel];
        this.maxByLevel.length = 0;
        this.maxByLevel.push(...next);
        this.usedByLevel = next.map((_, i) => prevUsed[i] ?? 0);
    }
}
//# sourceMappingURL=SpellSlotsManager.js.map