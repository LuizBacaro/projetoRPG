# `backend/app/games/dnd5e/` — D&D 5ª edição

Motor de regras **5E** (PHB) isolado do pacote `dnd35` (3.5). Fase 1 = domínio puro em `rules/`; fase 2 = API mínima com guard multi-jogo (ver [AGENTS.md](../../../AGENTS.md) e [docs/arquitetura-camadas-solid.md](../../../../docs/arquitetura-camadas-solid.md) §1–3).

## Estrutura

```
dnd5e/
  api/v1/          Rotas HTTP (regras estáticas; personagens em breve)
  schemas/         Pydantic de resposta
  rules/           Lógica de jogo (habilidades, combate, magia, feats, equipamento, antecedentes)
  data/            Tabelas e catálogos (spell slots, feats, equipamento, antecedentes)
  README.md
```

## Módulos implementados

| RF | Módulo | Testes |
|----|--------|--------|
| 01-habilidades | `rules/habilidades.py` | `tests/test_dnd5e_habilidades.py` |
| 04-combate | `rules/combate.py` | `tests/test_dnd5e_combate.py` |
| 05-magia | `rules/magia.py` | `tests/test_dnd5e_magia.py` |
| 06-talentos-feitos | `rules/talentos.py` | `tests/test_dnd5e_talentos.py` |
| 07-equipamento | `rules/equipamento.py` | `tests/test_dnd5e_equipamento.py` |
| 08-antecedentes | `rules/antecedentes.py` | `tests/test_dnd5e_antecedentes.py` |

## API (fase 2)

| Método | Rota | Guard |
|--------|------|-------|
| GET | `/api/v1/dnd5e/regras/atributos` | `requer_game_dnd5e` |
| GET/POST | `/api/v1/dnd5e/personagens` | `requer_game_dnd5e` |
| GET/PATCH | `/api/v1/dnd5e/personagens/{id}` | `requer_game_dnd5e` + dono/admin |
| POST | `/api/v1/dnd5e/personagens/{id}/foto` | idem |

Migration: `alembic_migrations/versions/d5e6f7a8b9c0_dnd5e_personagens.py`

## API de regras (catálogos)

| Método | Rota |
|--------|------|
| GET | `/api/v1/dnd5e/regras/atributos` |
| GET | `/api/v1/dnd5e/regras/racas` |
| GET | `/api/v1/dnd5e/regras/classes` |
| GET | `/api/v1/dnd5e/regras/combate` |
| GET | `/api/v1/dnd5e/regras/magias` |
| GET | `/api/v1/dnd5e/regras/talentos` |
| GET | `/api/v1/dnd5e/regras/equipamento` |
| GET | `/api/v1/dnd5e/regras/antecedentes` |

## Ficha web

- `frontend/games/dnd5e/pages/ficha-personagem.html` — raça, classe, antecedente, matriz padrão (15–8), bônus meio-elfo, preview via `POST /regras/calcular-atributos`.
- Rewrite Vercel: `/dnd5e/ficha` → ficha HTML.

## Plataforma

- Catálogo global: `dnd5e` com status `disponivel` (`game_catalog.py`).
- Frontend: `frontend/games/dnd5e/pages/dashboard.html` (rewrite `/dnd5e/dashboard`).

Ver também [.cursor/requisitos/dnd5e/README.md](../../../.cursor/requisitos/dnd5e/README.md) e [AGENTS.md](../../../AGENTS.md).

## Testes

```bash
cd backend && pytest tests/test_dnd5e_*.py -q

Inclui `tests/test_dnd5e_regras_api.py` (HTTP + guard).
```
