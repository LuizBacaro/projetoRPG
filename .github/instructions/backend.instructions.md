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
