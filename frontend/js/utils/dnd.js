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