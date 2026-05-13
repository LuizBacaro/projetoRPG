"""Rotas HTTP v1 — Tormenta."""

from app.games.tormenta.api.v1 import combate, personagens, regras

__all__ = ["combate", "personagens", "regras"]
