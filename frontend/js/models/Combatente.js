export class Combatente {
    constructor(data) {
        this.id           = data.id;
        this.nome         = data.nome;
        this.tipo         = data.tipo;
        this.classe       = data.classe;
        this.hp_atual     = data.hp_atual;
        this.hp_maximo    = data.hp_maximo;
        this.iniciativa   = data.iniciativa;
        this.foto_url     = data.foto_url;
        this.nivel        = data.nivel        || 1;
        this.pontos       = data.pontos       || 0;
        this.ca           = data.ca           !== undefined ? data.ca           : 10;
        this.toque        = data.toque        !== undefined ? data.toque        : 10;
        this.surpresa     = data.surpresa     !== undefined ? data.surpresa     : 10;
        this.fortitude    = data.fortitude    !== undefined ? data.fortitude    : 0;
        this.reflexos     = data.reflexos     !== undefined ? data.reflexos     : 0;
        this.vontade      = data.vontade      !== undefined ? data.vontade      : 0;
        this.forca        = data.forca        || 10;
        this.destreza     = data.destreza     || 10;
        this.constituicao = data.constituicao || 10;
        this.inteligencia = data.inteligencia || 10;
        this.sabedoria    = data.sabedoria    || 10;
        this.carisma      = data.carisma      || 10;
        this.ataques      = Array.isArray(data.ataques)      ? data.ataques      : [];
        this.magias_slots = Array.isArray(data.magias_slots) ? data.magias_slots : [];
    }

    estaVivo()   { return this.hp_atual > 0; }
    estaCritico(){ return this.hp_atual < this.hp_maximo * 0.25; }

    calcularModificador(atributo) {
        var valor = this[atributo] || 10;
        return Math.floor((valor - 10) / 2);
    }

    getModificadorFormatado(atributo) {
        var mod = this.calcularModificador(atributo);
        return mod >= 0 ? ('+' + mod) : ('' + mod);
    }

    getHPPercentual() { return (this.hp_atual / this.hp_maximo) * 100; }
    getBadgeClass()   { return 'badge-' + this.tipo; }
}