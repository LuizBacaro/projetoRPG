# `backend/app/games/dnd5e/` — D&D 5ª edição

Motor de regras **5E** (PHB) isolado do pacote `dnd35` (3.5). Sem API persistida ainda — fase 1 = domínio puro em `rules/` + testes (ver camadas em [AGENTS.md](../../../AGENTS.md) e [docs/arquitetura-camadas-solid.md](../../../../docs/arquitetura-camadas-solid.md) §1–3).

## Estrutura

```
dnd5e/
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

## Próximos passos (plataforma)

1. `requer_game_dnd5e` + routers `api/v1/`
2. Models SQLAlchemy + Alembic (`dnd5e_*`)
3. `game_slug=dnd5e` disponível no catálogo
4. Frontend `frontend/games/dnd5e/`

Ver também [.cursor/requisitos/dnd5e/README.md](../../../.cursor/requisitos/dnd5e/README.md) e [AGENTS.md](../../../AGENTS.md).

## Testes

```bash
cd backend && pytest tests/test_dnd5e_*.py -q
```
