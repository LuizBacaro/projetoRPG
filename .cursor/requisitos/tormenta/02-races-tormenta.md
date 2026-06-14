# FEATURE: Raças Tormenta 20 (MB)

> **Alinhamento:** 11 raças em `racas_mb.json` (+ gnomo, meio-elfo, meio-orc). Ajustes MB (+4/+2/-2), não +2/-2 do d20 antigo.

## Descrição
Raças jogáveis com ajustes de atributo, traços textuais e **efeitos mecânicos** resumidos.

## Dados
- Catálogo: `backend/app/games/tormenta/data/racas_mb.json`
- Efeitos mecânicos: `data/tracos_mecanicos_mb.json`
- API: `GET /tormenta/regras/racas`, `GET /tormenta/regras/tracos-raciais-preview?slug=`

## Estado de implementação

| Item | Estado |
|------|--------|
| 11 raças MB + API | **Feito** |
| Ajustes + humano/lefou +2 escolha | **Feito** (UI ficha) |
| Texto `tracos_resumo` na ficha | **Feito** |
| Motor mecânico (CA Pequeno, resistências, perícias) | **Feito** (`tracos_raciais_t20.py` + `t20-tracos-raciais.js`) |
| Deformidade lefou / domínio qareen (escolhas UI) | **Parcial** (texto; flags futuras) |
| Deslocamento/tamanho automático por raça | **Feito** (preview + tags ficha) |

## Referência
MB Cap. 2 — Raças (p.30–42).
