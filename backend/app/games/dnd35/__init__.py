"""
backend/app/games/dnd35/

Backend específico do sistema **Dungeons & Dragons 3.5** dentro da
plataforma multi-jogo.

Estrutura-alvo:
  api/v1/        → routers HTTP (combatentes, campanhas, magias, ...)
  core/          → regras puras (parsers de tabela de classe, deps de jogo)
  models/        → entidades ORM (Combatente, Magia, Campanha, ...)
  repositories/  → persistência
  schemas/       → contratos Pydantic
  services/      → regras de negócio
  seeds/         → catálogos importados (Tabela 3-7, talentos manuais, ...)

Estado atual:
  Pacote criado como andaime. Apenas o domínio `divindades_custom` foi
  migrado fisicamente como POC; demais domínios continuam em
  backend/app/{api,models,...}/ e serão movidos em PRs separados.
"""
