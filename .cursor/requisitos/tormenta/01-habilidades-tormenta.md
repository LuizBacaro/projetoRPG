# FEATURE: Habilidades Tormenta 20 (MB)

> **Alinhamento:** Tormenta 20 — Módulo Básico. Não usar regras d20 3.5 (modificador `(valor-10)/2`, compra 15 pts). Backlog canônico: `docs/tormenta/`.

## Descrição
Seis atributos (FOR, DES, CON, INT, SAB, CAR) com modificadores por **faixas T20** e compra por pontos MB (20 pts, valores 8–18).

## Regra principal (MB)
- Modificador por tabela de faixas (`modificador_atributo_t20` em `backend/app/games/tormenta/rules/atributos_t20.py`).
- Compra por pontos: soma dos custos = **20** (jogador); valores-base 8–18 sem bônus racial.
- Dados: `data/atributos_compra_pontos.json`, API `GET /tormenta/regras/atributos`.

## Estado de implementação

| Item | Estado |
|------|--------|
| 6 atributos + modificadores T20 | **Feito** |
| Compra 20 pts + validação API/UI | **Feito** |
| Métodos aleatórios (4d6, 3d6, heroico…) | **Não feito** (fora do MB padrão da ficha) |
| Campo `generationMethod` | **Não aplicável** ao T20 MB |

## Referência
MB Cap. 1 — Habilidades; contrato `docs/tormenta/05-contrato-dados-ficha-json-e-api.md`.
