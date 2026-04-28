"""
backend/app/shared/

Pacote que abriga código GLOBAL da plataforma — não pertence a nenhum
sistema de RPG específico. É o "Auth Hub" embutido + utilitários comuns.

O que entra aqui (alvo da reorganização):
  - Auth Hub:
      models: Usuario, Game, UserGameMembership, mixins
      schemas: usuario, game, auth tokens
      repositories: usuario_repository, game_repository
      services: usuario_service, game_service
      api/v1: auth.py, usuarios.py, games.py
  - Core de plataforma: config, database, deps, security, security_audit,
    rate_limit, request_size, catalog_cache, logging
  - Exceções genéricas (custom_exceptions, http_errors)

O que NÃO entra aqui:
  - Regras de cada jogo (combate, magia, ficha, campanha) — vão para
    backend/app/games/<slug>/.

Estado atual da migração:
  O Auth Hub e a infra partilhada (config, BD, deps, segurança, routers
  /auth /games /usuarios) estão consolidados em `app/shared/`. Código de jogo
  (D&D 3.5) vive em `app/games/dnd35/`. `app/core/` concentra DI
  (`dependencies.py`); o arranque de BD importa-se em `main.py` a partir de
  `app.shared.startup.*` e `app.games.dnd35.*`. Ver docs/arquitetura-multi-jogo.md
  e `backend/app/shared/README.md`.

Convenção de imports (após a reorganização):
  from ...shared.core.deps import get_usuario_atual
  from ...shared.models.usuario import Usuario
"""
