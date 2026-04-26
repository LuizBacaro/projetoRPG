"""
backend/app/games/

Cada subpasta aqui dentro é um sistema de RPG suportado pela plataforma,
com sua própria stack vertical: models, schemas, repositories, services,
api/v1 e core específico.

Convenção de slugs (deve casar com `games_catalog.slug`):
  - dnd35  → Dungeons & Dragons 3.5 (já em produção)
  - dnd5e  → Dungeons & Dragons 5e (em breve)
  - gurps  → GURPS (em breve)

Cada pacote de jogo expõe seus routers via `app/main.py`. O Auth Hub
(em backend/app/shared/) decide quem entra em cada jogo via JWT claim
`game_slug` e o guard `requer_game_<slug>` em deps.
"""
