# `backend/app/games/dnd35/`

Backend do sistema **Dungeons & Dragons 3.5**.

> Pacote em construção. A reorganização do código já existente acontece
> em PRs pequenos por domínio. Veja `docs/arquitetura-multi-jogo.md`.

## Domínios planejados

| Domínio         | Escopo (models / routers)                                                  |
|-----------------|----------------------------------------------------------------------------|
| **ficha**       | Combatente, Raca, Talento, HabilidadesEspeciais, TabelasClasses, Pericia   |
| **combate**     | Combate, CombatenteCondicao, Condicao, Ataque, ArmaduraProtecao           |
| **magia**       | Magia, Grimório, API preparadas (`MagiaSlot`/`MagiaPreparada` em `ataque`) |
| **campanha**    | Campanha, SessaoCampanha                                                   |
| **divindades**  | DivindadeCustom (POC já migrada) + catálogo oficial Tabela 3-7             |
| **equipamento** | Equipamento                                                                |

## Migrado fisicamente até agora

- `divindades/` (1ª onda — POC):
  - `models/divindade_custom.py`
  - `schemas/divindade_custom.py`
  - `repositories/divindade_custom_repository.py`
  - `services/divindade_custom_service.py`
  - `api/v1/divindades_custom.py`

- `equipamento/` (2ª onda):
  - `models/equipamento.py` (`Equipamento`, `EquipamentoJogador`)
  - `schemas/equipamento.py`
  - `repositories/equipamento_repository.py`
    (`EquipamentoRepository`, `EquipamentoJogadorRepository`)
  - `services/equipamento_service.py` (`EquipamentoService`)
  - `api/v1/equipamentos.py` (router `/equipamentos`)

  Observação: o router de equipamentos ainda **não** declara
  `requer_game_dnd35`. Avaliar adicioná-lo numa onda futura para
  alinhar com os demais routers de D&D 3.5.

- `campanha/` (3ª onda):
  - `models/campanha.py` (`Campanha`)
  - `models/sessao_campanha.py` (`SessaoCampanha`)
  - `schemas/campanha.py`, `schemas/sessao_campanha.py`
  - `repositories/campanha_repository.py` (`CampanhaRepository`)
  - `repositories/sessao_campanha_repository.py`
    (`SessaoCampanhaRepository`)
  - `services/campanha_service.py` (`CampanhaService`)
  - `services/sessao_campanha_service.py` (`SessaoCampanhaService`)
  - `api/v1/campanhas.py` (router `/campanhas` — já declarava
    `requer_game_dnd35`, mantido na migração)

- `habilidade_especial/` (4ª onda):
  - `catalogs/habilidades_especiais_catalog.py` (loader do JSON
    canônico; substitui o antigo `app.core.habilidades_especiais_catalog`)
  - `schemas/habilidade_especial.py`
  - `api/v1/habilidades_especiais.py` (router
    `/habilidades-especiais`)

  Esta onda introduziu a subpasta `catalogs/`, destinada a loaders de
  catálogos canônicos do PHB/Tomos (raças, classes, divindades
  oficiais, talentos…) que antes ficavam misturados em `app.core/`.
  O router ainda **não** declara `requer_game_dnd35` (paridade com o
  original); avaliar adicionar em onda futura.

- `raca/` (5ª onda):
  - `catalogs/racas_catalog.py` (loader do JSON
    `racas_caracteristicas_catalogo.json`; substitui o antigo
    `app.core.racas_catalog`)
  - `schemas/raca.py`
  - `api/v1/racas.py` (router `/racas`)

  O router ainda **não** declara `requer_game_dnd35` (paridade com o
  original).

- `talento/` (6ª onda):
  - `models/talento.py` (`Talento`, `TalentoJogador`)
  - `schemas/talento.py`
  - `repositories/talento_repository.py` (`TalentoRepository`,
    `TalentoJogadorRepository`)
  - `services/talento_service.py` (`TalentoService`)
  - `api/v1/talentos.py` (router `/talentos`)
  - `catalogs/talentos_catalog_seed.py` (seed/sincronização LdJ a
    partir de `talentos_importacao_limpo.json`; substitui o antigo
    `app.core.talentos_catalog_seed`)

  O router ainda **não** declara `requer_game_dnd35` (paridade com o
  original).

- `pericia/` (7ª onda):
  - `models/pericia.py` (`Pericia`, `PericiaClasse`, `PericiaJogador`)
  - `schemas/pericia.py`
  - `repositories/pericia_repository.py` (`PericiaRepository`,
    `PericiaJogadorRepository`)
  - `services/pericia_service.py` (`PericiaService`)
  - `api/v1/pericias.py` (router `/pericias`)
  - `seeds/pericias_seed.py` (`seed_pericias` a partir de `Perícias.xlsx`)

  O router ainda **não** declara `requer_game_dnd35` (paridade com o
  original).

- `tabelas_classes/` (8ª onda):
  - `catalogs/classes_tables_catalog.py` (loader do JSON
    `docs/dados/tabelas_classes_catalogo.json`; substitui o antigo
    `app.core.classes_tables_catalog`)
  - `schemas/tabelas_classes.py`
  - `services/tabelas_classes_service.py` (`TabelasClassesService`)
  - `api/v1/tabelas_classes.py` (router `/tabelas-classes`, opt-in por
    `CLASSES_TABLES_CATALOG_ENABLED`)

  O router ainda **não** declara `requer_game_dnd35` (paridade com o
  original).

- `magia/` (9ª onda — catálogo + grimório + preparadas):
  - `models/magia.py` (`Magia`, `MagiaClasse`, `MagiaHistorico`)
  - `models/grimorio.py` (`GrimorioMagia`, `GrimorioHistoricoTroca`,
    `GrimorioNotificacao`)
  - `schemas/magia.py`, `schemas/grimorio.py`
  - `repositories/magia_repository.py`, `repositories/grimorio_repository.py`
  - `services/magia_service.py`, `magia_import_service.py`,
    `grimorio_service.py` (caminho do CSV `restricoes_clerigo_completo.csv`
    ajustado para a profundidade de `games/dnd35/services/`)
  - `api/v1/magias.py`, `api/v1/grimorio.py`, `api/v1/magias_preparadas.py`

  `MagiaSlot` e `MagiaPreparada` vivem em `games/dnd35/models/ataque.py`
  (onda **combate**). O router `/magias-preparadas` importa esses models
  desse pacote; `app.models.ataque` permanece como shim.

  O router `/magias` ainda **não** declara `requer_game_dnd35` (paridade
  com o original). `/grimorio` e `/magias-preparadas` mantêm o guard.

- `combate/` (10ª onda):
  - `models/ataque.py` (`Ataque`, `MagiaSlot`, `MagiaPreparada`)
  - `models/combate.py` (`Combate`, `CombateHistorico`)
  - `models/condicao.py`, `models/combatente_condicao.py`
  - `models/armadura_protecao.py` (`ArmaduraProtecao`, `ArmaduraProtecaoJogador`)
  - schemas, repositórios, services e routers `/combate`, `/condicoes`,
    rotas de ataques/slots (`/combatentes/.../ataques`, `.../magias`,
    `/magias_slots/...`) e `/armaduras_protecao`
  - Shims em `app.models`, `app.schemas`, `app.repositories`, `app.services`,
    `app.api.v1` para imports legados

Os demais arquivos D&D 3.5 relevantes à **ficha** (`combatente`, etc.)
continuam em `backend/app/{models,api/v1,...}/` até a próxima onda.

## Convenção de imports (regras D&D 3.5)

```python
# Dentro do próprio pacote dnd35:
from ..models.divindade_custom import DivindadeCustom

# Cruzando para o Auth Hub (shared):
from ....shared.core.deps import get_usuario_atual, requer_game_dnd35
```

## Guard de jogo

Todos os routers deste pacote devem declarar:

```python
router = APIRouter(
    prefix="/...",
    tags=["..."],
    dependencies=[Depends(requer_game_dnd35)],
)
```

para que o backend recuse tokens com `game_slug != "dnd35"` em modo
estrito (`MULTI_GAME_STRICT_MODE=true`).
