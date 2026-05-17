"""Detecção de colunas/tabelas no Postgres (compatibilidade pré-migration)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import inspect

_cache: dict[tuple[int, str, str], bool] = {}


def _engine(bind: Any):
    return bind.engine if hasattr(bind, "engine") else bind


def table_exists(bind, table: str) -> bool:
    engine = _engine(bind)
    key = (id(engine), table, "__table__")
    if key not in _cache:
        _cache[key] = table in inspect(engine).get_table_names()
    return _cache[key]


def column_exists(bind, table: str, column: str) -> bool:
    engine = _engine(bind)
    key = (id(engine), table, column)
    if key not in _cache:
        if not table_exists(bind, table):
            _cache[key] = False
        else:
            cols = [c["name"] for c in inspect(engine).get_columns(table)]
            _cache[key] = column in cols
    return _cache[key]


def has_arena_combatente_id(bind) -> bool:
    return column_exists(bind, "companheiros_animais", "arena_combatente_id")


def has_familiares_table(bind) -> bool:
    return table_exists(bind, "familiares")
