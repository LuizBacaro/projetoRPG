/**
 * Utilitários de dados — parsing e rolagem de expressões simples (ex.: "3d6+2").
 */
/** Rolagem padrão com Math.random (produção / UI). */
export const defaultDiceRoller = {
    d20() {
        return Math.floor(Math.random() * 20) + 1;
    },
    roll(expression) {
        return rollDiceExpression(expression, defaultDiceRoller);
    },
};
/**
 * Interpreta "NdM" ou "NdM+X" e soma os dados.
 * Não cobre expressões complexas; suficiente para magias do MVP.
 */
export function rollDiceExpression(expression, roller = defaultDiceRoller) {
    const trimmed = expression.trim().toLowerCase();
    const match = trimmed.match(/^(\d+)d(\d+)([+-]\d+)?$/);
    if (!match) {
        return roller.d20();
    }
    const count = parseInt(match[1], 10);
    const sides = parseInt(match[2], 10);
    const mod = match[3] ? parseInt(match[3], 10) : 0;
    if (roller !== defaultDiceRoller) {
        return roller.roll(expression);
    }
    let total = mod;
    for (let i = 0; i < count; i += 1) {
        total += Math.floor(Math.random() * sides) + 1;
    }
    return total;
}
/** Quantidade de dados de truque conforme nível total do personagem (PHB §1.4). */
export function cantripDamageDiceCount(characterLevel) {
    const lvl = Math.max(1, Math.min(20, characterLevel));
    if (lvl >= 17)
        return 4;
    if (lvl >= 11)
        return 3;
    if (lvl >= 5)
        return 2;
    return 1;
}
/** Extrai faces do primeiro dado em "1d8" → 8. */
export function parseDieFaces(dice) {
    const m = dice.match(/\d+d(\d+)/i);
    return m ? parseInt(m[1], 10) : 6;
}
/** Monta expressão NdM a partir de contagem e faces. */
export function buildDiceExpression(count, faces, mod = 0) {
    const base = `${count}d${faces}`;
    if (mod > 0)
        return `${base}+${mod}`;
    if (mod < 0)
        return `${base}${mod}`;
    return base;
}
//# sourceMappingURL=dice.js.map