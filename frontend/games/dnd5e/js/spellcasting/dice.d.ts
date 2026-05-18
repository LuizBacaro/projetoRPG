/**
 * Utilitários de dados — parsing e rolagem de expressões simples (ex.: "3d6+2").
 */
import type { DiceRoller } from './types.js';
/** Rolagem padrão com Math.random (produção / UI). */
export declare const defaultDiceRoller: DiceRoller;
/**
 * Interpreta "NdM" ou "NdM+X" e soma os dados.
 * Não cobre expressões complexas; suficiente para magias do MVP.
 */
export declare function rollDiceExpression(expression: string, roller?: DiceRoller): number;
/** Quantidade de dados de truque conforme nível total do personagem (PHB §1.4). */
export declare function cantripDamageDiceCount(characterLevel: number): number;
/** Extrai faces do primeiro dado em "1d8" → 8. */
export declare function parseDieFaces(dice: string): number;
/** Monta expressão NdM a partir de contagem e faces. */
export declare function buildDiceExpression(count: number, faces: number, mod?: number): string;
//# sourceMappingURL=dice.d.ts.map