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

## Qualidade e Testes

- Preserve compatibilidade com testes FastAPI que usam SQLite em memoria com `StaticPool`.
- Ao tocar auth, cache, listagens ou startup, valide fluxos impactados e destaque risco residual quando nao houver teste.

## Seguranca

- Nao introduza fallback permissivo para usuario atual.
- Nao remova verificacoes de perfil (`admin`, `mestre`, `jogador`) sem razao funcional clara.

## Catalogo de talentos (producao vs local)

- O startup `inicializar_talentos` so insere um **seed minimo** (~15 linhas) se a tabela estiver vazia; Neon em producao costuma ficar so com esse subconjunto.
- O catálogo completo do LdJ esta em `talentos_importacao_limpo.json` na raiz do repo; desenvolvimento local costuma ter sido preenchido via esse arquivo ou import manual.
- Para **alinhar producao** ao catálogo completo: `cd backend && DATABASE_URL=... python scripts/importar_talentos_catalogo_json.py` (upsert por nome + fase opcional que copia benefício/seção do JSON para linhas do **seed** com nome antigo, via `MAPEAMENTO_SEED_PARA_JSON` no script).
- Listagens de talentos devem usar **ordem estável** (ex.: `nome` ASC) para paginacao consistente entre SQLite e Postgres.
