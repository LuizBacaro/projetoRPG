# Grimório MB — fechamento das fases G0–G2

Checklist de **entrega concluída** antes de investir em G5 (catálogo completo p.150–209) e polish de G4 (UI).

Referência épica: [07-requisitos-grimorio-mb-144-209.md](07-requisitos-grimorio-mb-144-209.md)

---

## G0 — Documentação e backlog

| Item | Estado |
|------|--------|
| Doc 07 + RFs RF-T40–T47 no backlog | ✅ |
| Skill [tormenta-20-arena-arquitetura-e-regras](../../.cursor/skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md) | ✅ |
| [grimorio-mb-mesa.md](grimorio-mb-mesa.md) | ✅ |

---

## G1 — Catálogo + API listagem

| Item | Estado | Onde |
|------|--------|------|
| `magias_mb_catalogo.json` (metadados; stubs substituíveis) | ✅ | `backend/app/games/tormenta/data/` |
| `GET /tormenta/regras/magias` (filtros, paginação) | ✅ | `api/v1/regras.py` |
| `check_magias_mb_catalogo.py` no CI | ✅ | `.github/workflows/ci.yml` |
| Pipeline listagem pp.307–317 | ✅ | `build_magias_mb_catalogo_from_listagem_txt.py` |

---

## G2 — Motor PM + habilidade-chave

| Item | Estado | Onde |
|------|--------|------|
| `conjuracao_classe_mb.json` | ✅ | `data/` |
| `rules/conjuracao_t20.py` | ✅ | testes `test_tormenta_conjuracao_t20.py` |
| `GET /tormenta/regras/conjuracao-mb` | ✅ | |
| `GET /tormenta/regras/conjuracao-preview` | ✅ | ficha + grimório |

---

## G3 — Vínculos por personagem (SQL)

| Item | Estado | Onde |
|------|--------|------|
| `tormenta_magias_personagem` + migration | ✅ | Alembic |
| CRUD `/personagens/{id}/magias` | ✅ | README backend Tormenta |
| `magias` no GET personagem enriquecido | ✅ | |

---

## G4 — UI (parcial, em uso)

| Item | Estado | Notas |
|------|--------|-------|
| `TormentaGrimorioService.js` | ✅ | |
| Modal / botão `btnT20Grimorio` na ficha | ✅ | `ficha-personagem.html` |
| Migrar só `magias_texto` → SQL | ✅ | `POST …/magias/migrar-do-json` + botão no modal grimório |
| Filtro escola no catálogo | ✅ | `grimorioTormentaFiltroEscola` |
| Troca magia bardo (RF-T42c) | ✅ | Catálogo em modo troca (sem prompt de slug) |
| Página dedicada `/grimorio-tormenta` | ✅ | Rewrite Vercel; modal na ficha cobre MVP |

**Conclusão G0–G2:** **fechadas** para desenvolvimento backend/regras. Produto pode marcar Tormenta `disponivel` no catálogo (já em `game_catalog.py`).

---

## G5 — Catálogo MB (metadados pp.150–209)

| Item | Estado | Notas |
|------|--------|-------|
| Listagem pp.307–317 (~706 magias) | ✅ | `build_magias_mb_catalogo_from_listagem_txt.py` |
| Enriquecimento escola/execução (PDF privado) | ✅ | `enrich_magias_mb_catalogo.py` + `magias_mb_nome_aliases.json`; `g5_estado: enriquecimento_completo` |
| Texto integral no repo público | ❌ | RF-T46 / licença — usar livro na mesa |
| 4 stubs de teste | ✅ | `escola: Geral` |

---

## G6 — Combate conjuração (próximo)

- Concentração: registo ao lançar; encerrar na ficha/arena (**MVP feito**).
- Resistência à magia ativa: lembrete na arena; motor completo → backlog.

---

## Testes de regressão sugeridos

```bash
cd backend
python3 -m pytest tests/test_tormenta_conjuracao_t20.py tests/test_tormenta_grimorio_elegibilidade.py tests/test_tormenta_personagens_api.py -q
python3 scripts/check_magias_mb_catalogo.py
```
