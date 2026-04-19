/**
 * Utilitários para cálculos de D&D
 * Princípio SOLID: Single Responsibility - apenas cálculos D&D
 */

/**
 * Calcula modificador de atributo D&D 5e
 */
export function calcularModificador(valor) {
    return Math.floor((valor - 10) / 2);
}

/**
 * CA base (sem armadura): 10 + modificador de Destreza.
 * @param {number} valorDestreza valor do atributo DES (1–30)
 */
export function caBasePorDestreza(valorDestreza) {
    const d = parseInt(valorDestreza, 10);
    const des = Number.isFinite(d) ? Math.min(30, Math.max(1, d)) : 10;
    return 10 + Math.floor((des - 10) / 2);
}

/** Código da perícia (coluna Atr.) → campo no combatente */
const ATRIBUTO_PERICIA_PARA_CAMPO = {
    FOR: 'forca',
    DES: 'destreza',
    CON: 'constituicao',
    INT: 'inteligencia',
    SAB: 'sabedoria',
    CAR: 'carisma',
};

/**
 * Modificador de perícia a partir do atributo associado (FOR/DES/…) e da ficha atual.
 * Não usar o valor persistido em pericia_jogador — pode ficar defasado se os atributos mudarem.
 */
export function modificadorPericiaPorAtributo(combatente, atributoCodigo) {
    if (!combatente) return 0;
    const key = String(atributoCodigo ?? '').trim().toUpperCase();
    const campo = ATRIBUTO_PERICIA_PARA_CAMPO[key];
    if (!campo) return 0;
    const raw = combatente[campo];
    const n = parseInt(raw, 10);
    const valor = Number.isFinite(n) ? Math.min(30, Math.max(1, n)) : 10;
    return Math.floor((valor - 10) / 2);
}

/**
 * Formata modificador com sinal (+/-)
 */
export function formatarModificador(valor) {
    const mod = calcularModificador(valor);
    return mod >= 0 ? `+${mod}` : `${mod}`;
}

/**
 * Atualiza o modificador no DOM
 */
export function atualizarModificadorDOM(input) {
    const valor = parseInt(input.value) || 10;
    const modificadorTexto = formatarModificador(valor);
    
    const modificadorSpan = input.parentElement.querySelector('.atributo-modificador');
    if (modificadorSpan) {
        modificadorSpan.textContent = modificadorTexto;
    }
}

/**
 * Valida valor de HP
 */
export function validarHP(valor, hpMaximo) {
    let hp = parseInt(valor);
    
    if (isNaN(hp) || hp < 0) {
        hp = 0;
    } else if (hp > hpMaximo) {
        hp = hpMaximo;
    }
    
    return hp;
}

/**
 * Valida valor de iniciativa
 */
export function validarIniciativa(valor) {
    let ini = parseInt(valor);
    
    if (isNaN(ini) || ini < 0) {
        ini = 0;
    }
    
    return ini;
}

/**
 * Valida atributo D&D (1-30)
 */
export function validarAtributo(valor) {
    let atributo = parseInt(valor);
    
    if (isNaN(atributo) || atributo < 1) {
        atributo = 1;
    } else if (atributo > 30) {
        atributo = 30;
    }
    
    return atributo;
}