/**
 * Model de Combatente (Entidade de Domínio)
 * Princípio SOLID: Single Responsibility - apenas representação de dados e comportamentos da entidade
 */
export class Combatente {
    constructor(data) {
        this.id = data.id;
        this.nome = data.nome;
        this.tipo = data.tipo;
        this.classe = data.classe;
        this.hp_atual = data.hp_atual;
        this.hp_maximo = data.hp_maximo;
        this.iniciativa = data.iniciativa;
        this.foto_url = data.foto_url;
        
        // Atributos D&D
        this.forca = data.forca || 10;
        this.destreza = data.destreza || 10;
        this.constituicao = data.constituicao || 10;
        this.inteligencia = data.inteligencia || 10;
        this.sabedoria = data.sabedoria || 10;
        this.carisma = data.carisma || 10;

        this.fortitude = data.fortitude || 0;
        this.reflexos = data.reflexos || 0;
        this.vontade = data.vontade || 0;
        
        // Progressão
        this.nivel = data.nivel || 1;
        this.pontos = data.pontos || 0;
    }
    
    /**
     * Verifica se o combatente está vivo
     */
    estaVivo() {
        return this.hp_atual > 0;
    }
    
    /**
     * Verifica se o HP está crítico (< 25%)
     */
    estaCritico() {
        return this.hp_atual < this.hp_maximo * 0.25;
    }
    
    /**
     * Calcula modificador de um atributo (D&D 5e)
     */
    calcularModificador(atributo) {
        const valor = this[atributo] || 10;
        return Math.floor((valor - 10) / 2);
    }
    
    /**
     * Retorna modificador formatado com sinal (+/-)
     */
    getModificadorFormatado(atributo) {
        const mod = this.calcularModificador(atributo);
        return mod >= 0 ? `+${mod}` : `${mod}`;
    }
    
    /**
     * Calcula percentual de HP
     */
    getHPPercentual() {
        return (this.hp_atual / this.hp_maximo) * 100;
    }
    
    /**
     * Retorna classe CSS baseada no tipo
     */
    getBadgeClass() {
        return `badge-${this.tipo}`;
    }
}