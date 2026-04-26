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

/** IDs dos spans de modificador na coluna esquerda da ficha (mesmos valores que “Atributos”). */
export const FICHA_PERICIA_MOD_DOM_IDS = {
    FOR: 'fichaForModResumo',
    DES: 'fichaDesModResumo',
    CON: 'fichaConModResumo',
    INT: 'fichaIntModResumo',
    SAB: 'fichaSabModResumo',
    CAR: 'fichaCarModResumo',
};

/**
 * Normaliza o código de atributo vindo da API/seed (ex.: "Int", "INT", " int ").
 * @returns {string} FOR|DES|CON|INT|SAB|CAR ou '' se não reconhecer
 */
export function normalizarCodigoAtributoPericia(raw) {
    if (raw == null) return '';
    let s = String(raw).trim();
    if (!s) return '';
    s = s.toUpperCase();
    if (['FOR', 'DES', 'CON', 'INT', 'SAB', 'CAR'].includes(s)) return s;
    const c = s.replace(/\s+/g, '').replace(/Ç/g, 'C');
    if (c.startsWith('FOR') || c.startsWith('FORCA')) return 'FOR';
    if (c.startsWith('DES') || c.startsWith('DEST')) return 'DES';
    if (c.startsWith('CON') || c.startsWith('CONS')) return 'CON';
    if (c.startsWith('INT')) return 'INT';
    if (c.startsWith('SAB')) return 'SAB';
    if (c.startsWith('CAR')) return 'CAR';
    return s.length >= 3 ? s.slice(0, 3) : s;
}

function _valorAtributoCombatente(combatente, campo) {
    const raw = combatente[campo];
    const n = typeof raw === 'number' ? raw : parseInt(String(raw).trim(), 10);
    return Number.isFinite(n) ? Math.min(30, Math.max(1, n)) : 10;
}

/**
 * Lê texto exibido na ficha (+2, -1, −1 unicode) como inteiro.
 */
export function parseTextoModificadorFicha(texto) {
    if (texto == null) return null;
    const t = String(texto).trim().replace(/\u2212/g, '-');
    if (t === '' || t === '—') return null;
    const n = parseInt(t.replace(/^\+/, ''), 10);
    return Number.isFinite(n) ? n : null;
}

/**
 * Modificador já renderizado na ficha (círculos de atributos), se o elemento existir.
 * @param {string} codigo FOR|DES|…
 * @returns {number|null} null se não houver DOM ou texto inválido
 */
export function modificadorPericiaLendoDomFicha(codigo) {
    if (typeof document === 'undefined' || !codigo) return null;
    const id = FICHA_PERICIA_MOD_DOM_IDS[codigo];
    if (!id) return null;
    const el = document.getElementById(id);
    if (!el) return null;
    return parseTextoModificadorFicha(el.textContent);
}

/**
 * Modificador de perícia a partir do atributo associado (FOR/DES/…) e da ficha atual.
 * Não usar o valor persistido em pericia_jogador — pode ficar defasado se os atributos mudarem.
 */
export function modificadorPericiaPorAtributo(combatente, atributoCodigo) {
    if (!combatente) return 0;
    const key = normalizarCodigoAtributoPericia(atributoCodigo);
    const campo = ATRIBUTO_PERICIA_PARA_CAMPO[key];
    if (!campo) return 0;
    const valor = _valorAtributoCombatente(combatente, campo);
    return Math.floor((valor - 10) / 2);
}

/**
 * Na página da ficha do personagem, prefere o Mod. já exibido nos atributos (DOM);
 * caso contrário calcula a partir do combatente.
 */
export function modificadorPericiaPreferindoDomFicha(combatente, atributoCodigo) {
    const key = normalizarCodigoAtributoPericia(atributoCodigo);
    if (!key) return 0;
    const dom = modificadorPericiaLendoDomFicha(key);
    if (dom !== null) return dom;
    return modificadorPericiaPorAtributo(combatente, key);
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