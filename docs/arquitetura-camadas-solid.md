# Arquitetura de código — camadas e SOLID (Arena TTRPG)

> **Norma:** [AGENTS.md](../AGENTS.md) (secao **Arquitetura de codigo**). Este documento **detalha** camadas, SOLID, modularidade e roteiro pragmatico. Em conflito, prevalece `AGENTS.md`.

Para o **projetoRPG / Arena**, arquitetura mais limpa (SOLID + manutencao + modularidade + reuso) e **onde poes fronteiras** e **como dependes** (direcao das setas). Alinha com `shared/`, `games/<slug>/` (`dnd35`, `dnd5e`, `tormenta`, `gurps`, …), `core/deps` e evolucoes em `ports/`.

**Leitura minima antes de codar backend:** secoes **1–3** deste ficheiro + secao **Arquitetura de codigo** em [AGENTS.md](../AGENTS.md).

Deploy e Auth Hub: [arquitetura-multi-jogo.md](arquitetura-multi-jogo.md). Contratos `Protocol`: [ports-repositorios-servicos.md](ports-repositorios-servicos.md).

Roadmaps e checklists por jogo: [roadmap-gurps-melhorias.md](roadmap-gurps-melhorias.md).

---

## 1. Camadas e responsabilidades (SRP + “quem pode chamar quem”)

| Camada | Papel | Regra de ouro |
|--------|--------|----------------|
| **API (routers)** | HTTP, status, deps, validacao de entrada | Nao contem regras de jogo nem SQL; chama **services** ou **casos de uso**. |
| **Services / use cases** | Orquestra repositorios, transacoes, politicas | Unico sitio para “fluxo” (ex.: criar combatente + side effects). |
| **Repositories** | Persistencia, queries, `commit`/`rollback` onde fizer sentido | Nao conhecem FastAPI; podem usar helpers partilhados (`commit_with_rollback`, soft delete). |
| **Models (ORM)** | Tabelas e invariantes de BD | Sem regras de negocio pesadas (evita “modelo gordo” dificil de testar). |
| **Dominio puro (`rules/`)** | Entidades/regras sem SQLAlchemy | Testavel sem BD; preferir `app.games.<slug>.rules` antes de logica pesada no service. |

**Multi-jogo:** plataforma (user, game, JWT, membership) em **`app.shared.*`**. Cada sistema em **`app.games.<slug>.*`**. O `shared` **nao** importa de `app.games.*`. Regras puras em **`games/<slug>/rules/`** (ex.: `dnd5e/rules/`).

---

## 2. SOLID no teu contexto (curto e aplicavel)

- **S — Responsabilidade unica:** um ficheiro = um motivo para mudar (ex.: `CombatenteService` nao mistura parsing de Excel).
- **O — Aberto/fechado:** extensoes por **novo jogo** (`games/dnd5e`) ou **nova estrategia** (`Protocol`), nao `if slug == "dnd35"` espalhado.
- **L — Substituicao de Liskov:** contratos estaveis em **schemas Pydantic** e interfaces de servico; testes com `dependency_overrides`.
- **I — Interfaces pequenas:** preferir `GrimorioReader` + `GrimorioWriter` a uma “God interface”.
- **D — Inversao de dependencias:** rotas e services dependem de **abstracoes**; `app.core.deps` afunila factories — ver [ports-repositorios-servicos.md](ports-repositorios-servicos.md).

---

## 3. Modularidade maxima (o que “fechar” no pacote do jogo)

Trata cada jogo como **plugin**:

- `games/<slug>/api`, `services`, `repositories`, `models`, `schemas`, `catalogs`, `rules/`, `seeds`
- **Contrato minimo** com a plataforma: slug, rotas no `main`, guards (`requer_game_<slug>`), eventualmente `GameModule.register_routes(app)`.

D&D 5e, Tormenta ou GURPS **reutilizam** o hub; nao reescrevem auth nem `Game`.

---

## 4. Reuso real (evitar reescrever codigo)

1. **Kernel partilhado** — `shared/core`, `shared/exceptions`, `repositories/base.py`; subir utilitarios agnosticos (paginacao, soft-delete, erros HTTP).
2. **Porta + adaptador** — Cloudinary, ficheiros, caches: interface no `shared`, implementacao injetavel.
3. **Catalogos e seeds** — JSON/Python + sync idempotente, sem duplicar em scripts e API.
4. **Evitar copia entre jogos** — sobe para `shared` se agnostico de sistema; senao `games/<slug>/` ou futuro `games/common`.

---

## 5. O `app/models/__init__.py` no meio disto tudo

Infra de **registo de metadata** (Alembic/testes), nao “modelo de dominio”. SRP: *este modulo so carrega mapeamentos no `Base.metadata`*.

---

## 6. Roteiro pragmatico (por ordem de ROI)

1. **Manter** fronteira `shared` ↔ `games/*` sem imports cruzados errados.
2. **Afinar** `dependencies.py` por dominio (hub vs jogo), sem mudar URLs.
3. **Introduzir protocols** onde ha mais mocks (`CombatenteRepositoryProtocol`, etc.).
4. **Extrair casos de uso** de services grandes (> ~400 linhas).
5. **ADR curto** em `docs/adr/` para estrutura de pacotes + regra de imports.

---

## Resumo em uma frase

**Hub estavel em `shared`, cada jogo em `games/<slug>/`, routers finos, services orquestram, repositories persistem, dependencias injetadas — reuso sobe codigo agnostico, nao copia entre jogos.**
