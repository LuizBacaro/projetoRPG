"""
Constantes do hub multi-jogo (Auth + catálogo).
Evita strings mágicas duplicadas entre `deps`, `game_service` e testes.
"""

GAME_SLUG_DND35 = "dnd35"
GAME_SLUG_DND5E = "dnd5e"
GAME_SLUG_GURPS = "gurps"
GAME_SLUG_TORMENTA = "tormenta"

# Jogos em que o usuario ganha membership automaticamente ao selecionar
# (espelha a politica em `GameService.selecionar_jogo`).
AUTO_ENROLL_MEMBERSHIP_GAME_SLUGS = frozenset(
    {GAME_SLUG_DND35, GAME_SLUG_DND5E, GAME_SLUG_GURPS, GAME_SLUG_TORMENTA}
)
