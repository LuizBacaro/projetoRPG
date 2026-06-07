---
description: "Regras para alteracoes no backend FastAPI/SQLAlchemy: arquitetura em camadas, dependencias, seguranca e compatibilidade de respostas."
applyTo: "backend/**/*.py"
---

# Backend Instructions

- Preserve a separacao `api/v1 -> services -> repositories -> models`.
- Routers devem permanecer finos; regras de negocio ficam em `backend/app/services`.
- Em rotas, use dependencias/factories de `backend/app/core/dependencies.py`; evite construir service manualmente.
- Rotas protegidas devem continuar com autenticacao real via `Depends(get_usuario_atual)` ou dependencias derivadas.
- Mantenha compatibilidade JWT no header `Authorization: Bearer <token>` para usuarios, combatentes e condicoes.

## Compatibilidade de API

- Em listagens antigas, preserve corpo de resposta.
- Quando aplicavel, mantenha headers de paginacao: `X-Total-Count`, `X-Skip`, `X-Limit`.
- Evite breaking changes em schema de request/response sem necessidade explicita.

## Repositorios e `Protocol` (DIP)

- Servicos devem depender de **contratos** (`typing.Protocol`) quando ja existirem em `app.shared.ports` ou `app.games.<jogo>.ports`, nao da classe concreta do repositorio no construtor.
- Ao criar fluxo novo ou estender persistencia: definir/atualizar o `Protocol` com a **superficie realmente usada** pelo servico; reexportar no `__init__.py` do pacote `ports`.
- Convencoes, inventario e proximos passos: [docs/ports-repositorios-servicos.md](../../docs/ports-repositorios-servicos.md).

## Qualidade e Testes

- **Antes de push/PR:** seguir [docs/normas-qualidade-backend-ci.md](../../docs/normas-qualidade-backend-ci.md) — `make install-hooks` (pre-commit com black/isort); validacao completa: `make ci-backend-lint` (black 24.10.0, isort 5.13.2 com `--profile black`, flake8).
- Preserve compatibilidade com testes FastAPI que usam SQLite em memoria com `StaticPool`.
- Ao tocar auth, cache, listagens ou startup, valide fluxos impactados e destaque risco residual quando nao houver teste.
- Novos models/routers: imports em ordem alfabética em `app/main.py`, `app/models/__init__.py` e `app/core/deps/dnd35.py` (ver normas CI).

## Especificacao minima (rotas e contratos)

- Nova rota ou mudanca de payload: manter **schemas** alinhados ao contrato real; preferir **pelo menos um teste** no caminho feliz (e erro esperado se for fluxo critico).
- Criterios de aceite e risco de breaking change: ver [docs/fluxo-spec-driven-leve.md](../../docs/fluxo-spec-driven-leve.md).

## Seguranca

- Nao introduza fallback permissivo para usuario atual.
- Nao remova verificacoes de perfil (`admin`, `mestre`, `jogador`) sem razao funcional clara.

## Catalogo de talentos (producao vs local)

- O startup `inicializar_talentos` so insere um **seed minimo** (~15 linhas) se a tabela estiver vazia; Neon em producao costuma ficar so com esse subconjunto.
- O catálogo completo do LdJ esta em `talentos_importacao_limpo.json` na raiz do repo; desenvolvimento local costuma ter sido preenchido via esse arquivo ou import manual.
- Para **alinhar producao** ao catálogo completo: `cd backend && DATABASE_URL=... python scripts/importar_talentos_catalogo_json.py` (upsert por nome + fase opcional que copia benefício/seção do JSON para linhas do **seed** com nome antigo, via `MAPEAMENTO_SEED_PARA_JSON` no script).
- Listagens de talentos devem usar **ordem estável** (ex.: `nome` ASC) para paginacao consistente entre SQLite e Postgres.
