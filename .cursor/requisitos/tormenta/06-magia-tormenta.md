# FEATURE: Magia Tormenta 20 (MB)

> **Não usar slots 0–9 do d20.** T20 usa **PM**, **círculos** e modos **preparar** vs **espontâneo**.

## Descrição
Conjuração MB: PM por classe, habilidade-chave, grimório SQL, catálogo de magias, gasto de PM ao lançar.

## Dados
- `conjuracao_classe_mb.json` — `modo_conjuracao`: `preparar` | `espontaneo`
- Catálogo: `magias_mb_catalogo.json`, `GET /tormenta/regras/magias`
- Vínculos: `tormenta_magias_personagem`, `/personagens/{id}/magias`
- Lançar: `POST /personagens/{id}/magias/lancar` (debita `pa_atual`)

## Modos por classe (MB)
| Modo | Classes |
|------|---------|
| preparar | mago, clérigo, druida, paladino, ranger |
| espontaneo | bardo, feiticeiro |

Validação de papel (`grimorio` / `conhecida` / `preparada`): `grimorio_conjuracao_t20.py`.

## Estado de implementação

| Item | Estado |
|------|--------|
| Motor PM + CD preview | **Feito** (G2) |
| Grimório SQL + modal ficha | **Feito** (G3–G4) |
| Enforcement preparar vs espontâneo | **Feito** |
| Gasto PM automático ao lançar | **Feito** |
| Página `/tormenta/grimorio` | **Feito** |
| Catálogo completo p.150–209 (G5) | **Feito** (706 itens; metadados `escola`/execução via `enrich_magias_mb_catalogo.py`; sem `descricao_longa` no repo — RF-T46) |
| Repertório aprendido + prece de devoção (RF-T44d) | **Feito** |
| Progressão magias conhecidas por nível (RF-T42) | **Feito** (bardo/feiticeiro; troca bardo RF-T42c no backend + UI) |
| Migração `magias_texto` → SQL | **Feito** (automática ao abrir o grimório) |
| Concentração / resistência à magia | **Feito** (concentração ao lançar/encerrar; teste automático ao aplicar dano; `POST …/combate/testar-resistencia-magia`; RM +4/+8 MB) |

## Referência
`docs/tormenta/07-requisitos-grimorio-mb-144-209.md`, `08-grimorio-g0-g2-fechamento.md`.
