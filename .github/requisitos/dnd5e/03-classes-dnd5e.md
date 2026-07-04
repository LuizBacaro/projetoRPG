# FEATURE: Sistema de Classes D&D 5E

## Descrição Breve
Implementar 12 classes (Bárbaro, Bardo, Bruxo, Clérigo, Druida, Feiticeiro, Guerreiro, Ladino, Mago, Monge, Paladino, Patrulheiro) com dados de vida, progressão e habilidades por nível.

## Regra Principal
Cada classe define: d. de vida (d8, d10, d12), habilidade primária, proficiências, e ganhos de habilidades a cada nível. Progresso 1-20.

## Dados/Campos Necessários
- classe: enum — 12 opções acima
- nivel: number (1-20)
- experiencia: number (total XP)
- habilidades_de_classe: string[] (list de habilidades desbloqueadas)
- proficiencias: Proficiencia[] (escudos, armas, salvados, perícias)

## Dado de Vida e Habilidade Primária

| Classe | d. Vida | Primária |
|--------|---------|----------|
| Bárbaro | d12 | Força |
| Bardo | d8 | Carisma |
| Bruxo | d8 | Carisma |
| Clérigo | d8 | Sabedoria |
| Druida | d8 | Sabedoria |
| Feiticeiro | d6 | Carisma |
| Guerreiro | d10 | Força |
| Ladino | d8 | Destreza |
| Mago | d6 | Inteligência |
| Monge | d8 | Destreza |
| Paladino | d10 | Força |
| Patrulheiro | d10 | Destreza |

## Tabela de Experiência (requisito para nível)

**Fonte canônica no código:** `backend/app/games/dnd5e/data/classes_catalogo.py` → `TABELA_XP_POR_NIVEL` (exposta na API `/dnd5e/regras/classes`).

| Nível | XP | Nível | XP |
|-------|-----|-------|-----|
| 1 | 0 | 11 | 86.000 |
| 2 | 300 | 12 | 110.000 |
| 3 | 900 | 13 | 140.000 |
| 4 | 2.700 | 14 | 170.000 |
| 5 | 6.500 | 15 | 205.000 |
| 6 | 14.000 | 16 | 250.000 |
| 7 | 23.000 | 17 | 300.000 |
| 8 | 34.000 | 18 | 355.000 |
| 9 | 48.000 | 19 | 420.000 |
| 10 | 64.000 | 20 | 500.000 |

## Pontos de Vida por Nível

- **Nível 1**: d[vida] + CON mod (mínimo 1)
- **Nível 2+**: PV anterior + (1d[vida] + CON mod), mínimo 1

**Exemplo Bárbaro com CON +2:**
- Nível 1: 1d12 (rolou 8) + 2 = 10 PV
- Nível 2: 10 + (1d12 (rolou 6) + 2) = 18 PV

## Habilidades de Classe (Resumo)

- **Nível 1**: Subclasse, proficiências
- **Nível 2**: Característica especial
- **Nível 3**: Subclasse escolhida
- **Nível 5**: Ataque Extra (maioria)
- **Nível 11, 17, 20**: Aumentos superiores

## Validações
- Classe: 12 opções válidas
- Nível: 1-20
- XP: validar contra tabela de progressão
- PV: nunca <= 0 (inconsciente)
- Proficiências: aplicar conforme classe

## Cálculos
- **PV Total**: soma incremental d[vida] + CON cada nível
- **Ganho XP/Nível**: diferença entre nível atual e próximo
- **Proficiência**: adiciona bônus em perícias/salvados conforme classe

## Exemplo: Guerreiro Nível 5

- STR 16 (mod +3), CON 14 (mod +2)
- PV: ~30-45 (depende rolls de d10)
- BAB: múltiplo (Ataque Extra em nível 5)
- Proficiências: armas marciais, armadura pesada, salvados STR/CON

## Referência do Livro
Capítulo 3: Classes | Tabelas de progressão e habilidades por nível
