"""[SHIM DE COMPATIBILIDADE] app.seeds.pericias_seed

Re-exporta `seed_pericias` de `app.games.dnd35.seeds.pericias_seed`.
"""

from app.games.dnd35.seeds.pericias_seed import seed_pericias

__all__ = ["seed_pericias"]
