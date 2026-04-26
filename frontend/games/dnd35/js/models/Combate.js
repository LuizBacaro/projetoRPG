/**
 * Model de Combate (Entidade de Domínio)
 */
export class Combate {
    constructor(data) {
        this.id = data.id;
        this.combatentes_ids = data.combatentes_ids || [];
        this.turno_atual = data.turno_atual || 0;
        this.ativo = data.ativo || false;
        this.combatente_ativo_id = data.combatente_ativo_id;
        this.combatentes = data.combatentes || [];
    }
    
    /**
     * Obtém o combatente cujo turno está ativo
     */
    getCombatenteAtivo() {
        return this.combatentes.find(c => c.id === this.combatente_ativo_id);
    }
    
    /**
     * Verifica se o combate está ativo
     */
    estaAtivo() {
        return this.ativo === true;
    }
    
    /**
     * Conta combatentes vivos
     */
    contarVivos() {
        return this.combatentes.filter(c => c.estaVivo()).length;
    }
    
    /**
     * Verifica se o combate acabou (todos mortos ou só um vivo)
     */
    acabou() {
        return this.contarVivos() <= 1;
    }
}