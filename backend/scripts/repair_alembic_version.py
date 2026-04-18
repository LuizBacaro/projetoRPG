#!/usr/bin/env python3
"""Repair Alembic version state.

Detecta e corrige estados multi-head na tabela alembic_version de um banco.
Use este script manualmente em produção quando o startup falhar com erro
similar a "Requested revision ... overlaps with other requested revisions".
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Permite importar o backend local quando o script é executado de dentro de backend/scripts.
backend_root = Path(__file__).resolve().parent
project_root = backend_root.parent
sys.path.insert(0, str(project_root))

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./rpg_arena.db")


def get_alembic_config() -> "Config":
    from alembic.config import Config

    ini_path = project_root / "alembic.ini"
    if not ini_path.exists():
        raise FileNotFoundError(f"alembic.ini não encontrado em {ini_path}")

    cfg = Config(str(ini_path))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    return cfg


def build_engine(url: str):
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(url, connect_args=connect_args)


def read_alembic_revisions(engine) -> list[str]:
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            return [row[0] for row in result.fetchall()]
    except OperationalError as exc:
        if "no such table" in str(exc).lower() or "does not exist" in str(exc).lower():
            return []
        raise


def is_ancestor(script, ancestor: str, descendant: str) -> bool:
    if ancestor == descendant:
        return True

    visited: set[str] = set()
    stack: list[str] = [descendant]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        rev_obj = script.get_revision(current)
        if not rev_obj:
            continue

        down_rev = rev_obj.down_revision
        if down_rev is None:
            continue

        if isinstance(down_rev, tuple):
            stack.extend([rev for rev in down_rev if rev is not None])
        else:
            stack.append(down_rev)

        if ancestor in visited:
            return True

    return False


def normalize_alembic_version(engine):
    from alembic import command
    from alembic.script import ScriptDirectory

    cfg = get_alembic_config()
    revisions = read_alembic_revisions(engine)
    if len(revisions) <= 1:
        print("✅ estado Alembic já está normalizado. Nenhuma ação necessária.")
        return

    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    if len(heads) != 1:
        raise RuntimeError(
            "O repositório Alembic possui múltiplos heads no código. "
            f"Heads detectados: {heads}."
        )

    head = heads[0]
    print(f"⚠️  estado Alembic multi-head detectado: {revisions}")
    if not all(is_ancestor(script, rev, head) for rev in revisions):
        raise RuntimeError(
            "Não foi possível normalizar o estado atual de alembic_version porque "
            "nem todas as revisões são ancestrais do head único. "
            f"Revisões atuais: {revisions}. Head esperado: {head}."
        )

    print(f"🔧 Normalizando alembic_version para o head único: {head}")
    command.stamp(cfg, head)
    print("✅ Normalização concluída. O estado Alembic agora aponta para head.")


def main() -> None:
    engine = build_engine(DATABASE_URL)
    normalize_alembic_version(engine)


if __name__ == "__main__":
    main()
