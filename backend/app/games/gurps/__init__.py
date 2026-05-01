"""
backend/app/games/gurps/

Backend **GURPS** — mesma divisão conceitual do D&D 3.5 (`api/v1`, `models`,
`repositories`, `schemas`, `services`). Rotas sob `/api/v1/gurps/...` com
guard `requer_game_gurps` (claim JWT `game_slug=gurps` em modo estrito).
"""
