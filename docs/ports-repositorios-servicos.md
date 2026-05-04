# Ports (`typing.Protocol`) — repositórios e serviços

Este documento fixa o padrão de **contratos estruturais** entre serviços e persistência no backend, para implementações futuras e sustentação.

## Objetivo

- Declarar, em um único lugar tipado, **quais operações de repositório** cada serviço realmente usa.
- Reduzir acoplamento a classes concretas: o repositório implementado **não precisa herdar** o `Protocol`; basta expor métodos compatíveis (subtipagem estrutural).
- Facilitar **testes** (fakes/mocks mínimos) e **análise estática** (mypy/Pyright), quando adotados.

## Onde colocar o código

| Área | Pacote | Observação |
|------|--------|------------|
| Hub global (usuários, catálogo de jogos, memberships) | `backend/app/shared/ports/` | Ex.: `usuario.py`, `games.py` |
| D&D 3.5 | `backend/app/games/dnd35/ports/` | Vários módulos por domínio (`repositories.py`, `magias.py`, `grimorio.py`, etc.) |
| GURPS | `backend/app/games/gurps/ports/` | Ex.: `repositories.py` |

Reexportar símbolos públicos no `__init__.py` do pacote `ports` com `__all__`.

## Convenções

1. **Nome:** sufixo `*Protocol` (ex.: `MagiaRepositoryProtocol`).
2. **Superfície:** incluir apenas métodos (e `db: Session` quando o serviço acessa `repo.db` ou o contrato espelha o repositório que expõe sessão).
3. **Serviço:** o `__init__` do serviço deve anotar dependências com o `Protocol`, não com a classe concreta do repositório.
4. **Factories FastAPI** (`Depends`): podem continuar retornando a **classe concreta**; o tipo de retorno concreto é compatível com o `Protocol`. Centralizar montagem em `app.core.deps.dnd35` (ex.: `get_pericia_service`, `get_consumivel_service`, `get_equipamento_service`, `get_armadura_protecao_service`, `get_talento_service`; `get_combatente_service` injeta `DivindadeCustomRepository` via `get_divindade_custom_repository`).
5. **Protocol estreito vs completo:** quando um serviço usa poucos métodos (ex.: combate só precisa de parte de `CombatenteRepository`), prefira um protocol dedicado (ex.: `CombatenteRepositoryForCombateProtocol`) em vez de forçar o protocol “completo” em todos os consumidores.

## Inventário atual (referência)

**`app.shared.ports`**

- `UsuarioRepositoryProtocol`
- `GameRepositoryProtocol`
- `UserGameMembershipRepositoryProtocol`

**`app.games.dnd35.ports`**

- `CombateRepositoryProtocol`, `CombatenteRepositoryForCombateProtocol`, `CombatenteRepositoryProtocol`
- `CombatenteGetByIdProtocol` (só `get_by_id`; usado por `AtaqueService` e `ConsumivelService`; `CombatenteRepositoryForAtaqueProtocol` é alias)
- `CondicaoRepositoryProtocol`
- `CampanhaRepositoryProtocol`, `SessaoCampanhaRepositoryProtocol`
- `MagiaRepositoryProtocol`, `MagiaCriacaoParaImportProtocol` (`MagiaImportService`), `GrimorioRepositoryProtocol`
- `ArmaduraProtecaoCatalogProtocol`, `ArmaduraProtecaoJogadorLinksProtocol`
- `TalentoCatalogProtocol`, `TalentoJogadorLinksProtocol`
- `EquipamentoCatalogProtocol`, `EquipamentoJogadorLinksProtocol`
- `PericiaCatalogRestoreProtocol`, `PericiaRepositoryProtocol`, `PericiaJogadorRepositoryProtocol` (`PericiaService`; o primeiro é subconjunto do segundo)
- `MagiaPreparadaRepositoryProtocol` (persistência usada em `api/v1/magias_preparadas`)
- `AtaqueRepositoryProtocol`, `CombatenteRepositoryForAtaqueProtocol` (alias de `CombatenteGetByIdProtocol`; `AtaqueService`)
- `DivindadeCustomRepositoryProtocol` (`DivindadeCustomService`; também injetável em `CombatenteService` para `_carregar_divindades_custom`)
- `ConsumivelCatalogProtocol`, `ConsumivelJogadorLinksProtocol` (`ConsumivelService`)

**`app.games.gurps.ports`**

- `GurpsPersonagemRepositoryProtocol` (inclui `get_by_ids` e `ordenar_para_turno_gurps` para campanha/combate)
- `GurpsCampanhaRepositoryProtocol`
- `GurpsCombateRepositoryProtocol`

## Como adicionar um novo protocol

1. Localizar todas as chamadas `self.<repo>.` (ou equivalente) no serviço.
2. Criar ou estender um módulo em `ports/` com um `class MeuRepositoryProtocol(Protocol):` contendo **exatamente** essa superfície (assinaturas alinhadas ao repositório concreto).
3. Atualizar o serviço para importar o `Protocol` e anotar o construtor.
4. Exportar no `__init__.py` do pacote `ports`.
5. Rodar testes do domínio afetado.

## O que isso não substitui

- Não melhora performance por si só.
- Não dispensa testes de integração onde o fluxo cruza SQL, transações ou migrações.
- `@runtime_checkable` só é necessário se houver `isinstance` em runtime; para injeção típica, não é obrigatório.

## Próximos passos naturais

1. **Cobrir serviços/repositórios ainda tipados só com classes concretas** — repetir o mesmo recorte por uso real no serviço (ex.: outros catálogos D&D 3.5 ainda sem port dedicado).
2. **Reduzir `repo.db` nos serviços:** mover queries ad-hoc para métodos do repositório (ou um port de consultas), mantendo o serviço alinhado ao contrato nomeado.
3. **Fakes em testes unitários:** onde hoje só há testes de API com SQLite, introduzir testes de serviço com implementações mínimas dos `Protocol`s.
4. **Tipagem estrita gradual:** habilitar mypy/Pyright nos pacotes `ports/` e serviços já anotados.
5. **Documentar exceções:** repositórios que permanecem só com métodos estáticos ou sem injeção devem ser normalizados (instância + `db`) quando forem tocados de novo — ver `ArmaduraProtecaoRepository` como referência de instância injetável.

---

Última orientação: ao alterar um repositório usado por um `Protocol`, atualize o `Protocol` **no mesmo PR** se o serviço passar a exigir novos métodos ou mudar assinaturas.
