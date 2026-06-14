# FEATURE: Perícias Tormenta 20 (MB)

> **Alinhamento:** **32 perícias** MB (não 19 do doc legado d20). Lista em `pericias_atributo_chave.json`.

## Regra principal (MB)
Bônus = mod. atributo + ½ nível + graduações + **+2 se treinado** + outros − penalidade armadura + bônus racial.

## Dados
- Metadados: `GET /tormenta/regras/atributos` → `pericias[]`
- DCs padrão: `data/pericias_dc_mb.json`, `GET /tormenta/regras/pericias`
- Cálculo: `POST /tormenta/regras/pericias/calcular-bonus`
- Rolagem: `POST /tormenta/regras/pericias/rolar`

## Estado de implementação

| Item | Estado |
|------|--------|
| Tabela 32 perícias na ficha | **Feito** |
| Somente treinado / penalidade armadura (flags) | **Feito** |
| Percepção passiva (API) | **Feito** |
| Rolador na ficha (`t20-pericias-rolador.js`) | **Feito** |
| Bônus racial automático no teste | **Feito** (via traços raciais) |
| Tabela SQL `tormenta_pericias` (RF-T20) | **Não feito** (JSON + API) |

## Referência
MB Cap. 4 — Perícias; inventário `docs/tormenta/02-inventario-tabelas-regras-por-secao.md` (T04, T05).
