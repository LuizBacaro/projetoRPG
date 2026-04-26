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
  Esta pasta é um ANDAIME. Os arquivos ainda vivem em backend/app/{core,
  models, schemas, repositories, services, api/v1, exceptions}/. A
  reorganização será feita em PRs pequenos por domínio para não quebrar
  imports em massa. Veja docs/arquitetura-multi-jogo.md (Fase 5) para o
  plano completo.

Convenção de imports (após a reorganização):
  from ...shared.core.deps import get_usuario_atual
  from ...shared.models.usuario import Usuario
"""
