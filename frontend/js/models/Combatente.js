function _attr1a30(data, key, def = 10) {
    const v = Number(data[key]);
    if (!Number.isFinite(v)) return def;
    return Math.min(30, Math.max(1, Math.round(v)));
}

export class Combatente {
    constructor(data) {
        this.id                = data.id;
        this.nome              = data.nome;
        this.tipo              = data.tipo;
        this.classe            = data.classe;
        this.raca              = data.raca              || '';
        this.raca_slug         = data.raca_slug         || '';
        this.divindade         = data.divindade         || data.deidade || '';
        this.alinhamento       = data.alinhamento       || '';
        this.dominios          = data.dominios          || '';
        this.pagina_referencia = data.pagina_referencia || '';  // ✅ NOVO
        this.hp_atual          = data.hp_atual;
        this.hp_maximo         = data.hp_maximo;
        this.iniciativa        = data.iniciativa;
        this.foto_url          = data.foto_url;
        this.nivel             = data.nivel             || 1;
        this.pontos            = data.pontos            || 0;
        this.bonus_base_ataque = data.bonus_base_ataque || '';
        this.habilidades_especiais = data.habilidades_especiais || '';
        this.tamanho_racial = data.tamanho_racial || '';
        this.deslocamento_racial_metros = data.deslocamento_racial_metros ?? null;
        this.idiomas_raciais = Array.isArray(data.idiomas_raciais) ? data.idiomas_raciais : [];
        this.passivos_raciais = Array.isArray(data.passivos_raciais) ? data.passivos_raciais : [];
        this.ca                = data.ca                !== undefined ? data.ca                : 10;
        this.toque             = data.toque             !== undefined ? data.toque             : 10;
        this.surpresa          = data.surpresa          !== undefined ? data.surpresa          : 10;
        this.fortitude         = data.fortitude         !== undefined ? data.fortitude         : 0;
        this.reflexos          = data.reflexos          !== undefined ? data.reflexos          : 0;
        this.vontade           = data.vontade           !== undefined ? data.vontade           : 0;
        this.fortitude_base    = data.fortitude_base    !== undefined ? data.fortitude_base    : this.fortitude;
        this.reflexos_base     = data.reflexos_base     !== undefined ? data.reflexos_base     : this.reflexos;
        this.vontade_base      = data.vontade_base      !== undefined ? data.vontade_base      : this.vontade;
        this.forca             = _attr1a30(data, 'forca', 10);
        this.destreza          = _attr1a30(data, 'destreza', 10);
        this.constituicao      = _attr1a30(data, 'constituicao', 10);
        this.inteligencia      = _attr1a30(data, 'inteligencia', 10);
        this.sabedoria         = _attr1a30(data, 'sabedoria', 10);
        this.carisma           = _attr1a30(data, 'carisma', 10);
        this.ataques           = Array.isArray(data.ataques)           ? data.ataques           : [];
        this.magias_slots      = Array.isArray(data.magias_slots)      ? data.magias_slots      : [];
        this.magias_preparadas = Array.isArray(data.magias_preparadas) ? data.magias_preparadas : [];
    }

    estaVivo() {
        if (this.tipo === 'monstro') return this.hp_atual > 0;
        return this.hp_atual > -10;
    }
    estaCritico() { return this.hp_atual > 0 && this.hp_atual < this.hp_maximo * 0.25; }

    calcularModificador(atributo) {
        var valor = this[atributo] || 10;
        return Math.floor((valor - 10) / 2);
    }

    getModificadorFormatado(atributo) {
        var mod = this.calcularModificador(atributo);
        return mod >= 0 ? ('+' + mod) : ('' + mod);
    }

    getHPPercentual() { return (Math.max(0, this.hp_atual) / this.hp_maximo) * 100; }
    getBadgeClass()   { return 'badge-' + this.tipo; }
}