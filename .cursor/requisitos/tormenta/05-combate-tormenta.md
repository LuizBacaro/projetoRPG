# FEATURE: Combate Tormenta 20 (MB) — Arena

> **Escopo Arena:** tracker de mesa + rolagens assistidas. Motor completo de economia de ações permanece backlog P3.

## Descrição
Rodadas, iniciativa, turnos, dano/cura PV, condições MB (~p.220) e rolagens via API.

## API
- `POST /tormenta/combate/iniciar`, `/avancar-turno`, `/finalizar`
- `POST /tormenta/combate/condicoes-mb`
- `POST /tormenta/combate/rolar-iniciativa` — 1d20 + DES, reordena combate
- `POST /tormenta/combate/rolar-ataque` — 1d20 + BAB + mod vs CA (+ mods condição)
- `POST /tormenta/combate/rolar-dano` — fórmula NdM + mod; opcional aplicar PV

## Motor
- `rules/combate_t20.py` — rolagens e modificadores automáticos de condições
- UI: aba Arena no dashboard + `t20-combate-rolagens.js`

## Estado de implementação

| Item | Estado |
|------|--------|
| Iniciativa ordenada (valor gravado) | **Feito** |
| Rolagem iniciativa 1d20+DES | **Feito** |
| Rolagem ataque/dano | **Feito** (MVP prompts) |
| Modificadores automáticos de condições | **Feito** (ataque/CA parcial) |
| Economia de ações / surpresa / oportunidade | **Não feito** |
| Regras de morte (0 PV, -10) | **Não feito** |

## Referência
MB Cap. 9 — Combate; RF-T30–T31 em `docs/tormenta/03-requisitos-funcionais-backlog.md`.
