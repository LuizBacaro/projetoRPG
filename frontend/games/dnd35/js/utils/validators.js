/**
 * Validadores genéricos
 */

export const validators = {
    
    /**
     * Valida se string não está vazia
     */
    isNotEmpty(value) {
        return value && value.trim().length > 0;
    },
    
    /**
     * Valida se é número positivo
     */
    isPositiveNumber(value) {
        const num = parseInt(value);
        return !isNaN(num) && num > 0;
    },
    
    /**
     * Valida se é número não-negativo
     */
    isNonNegativeNumber(value) {
        const num = parseInt(value);
        return !isNaN(num) && num >= 0;
    },
    
    /**
     * Valida se tipo é válido
     */
    isTipoValido(tipo) {
        return ['jogador', 'monstro', 'npc'].includes(tipo);
    }
};