"""
Catálogo global de jogos (`games` / `UserGameMembership`).

Sincronizado no startup da API; dados estáticos em `GAME_CATALOG_SEED`.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.shared.models.game import Game

logger = logging.getLogger(__name__)

GAME_CATALOG_SEED = [
    {
        "slug": "dnd35",
        "nome": "D&D 3.5 — Arena TTRPG",
        "descricao": (
            "Sistema completo da Arena TTRPG com regras de combate, magias, "
            "ficha por classe e gerenciamento de campanhas no D&D 3.5."
        ),
        "status": "disponivel",
        "icone": "🐉",
        "ordem": 10,
    },
    {
        "slug": "dnd5e",
        "nome": "D&D 5e",
        "descricao": (
            "Sistema D&D 5e com ficha simplificada e proficiências. "
            "Em breve: stack independente."
        ),
        "status": "em_breve",
        "icone": "🛡️",
        "ordem": 20,
    },
    {
        "slug": "tormenta",
        "nome": "Tormenta RPG",
        "descricao": (
            "Sistema d20 brasileiro (Jambo Editora): ficha digital do Módulo "
            "Básico, cadastro e evolução na Arena."
        ),
        "status": "disponivel",
        "icone": "🐉",
        "ordem": 25,
    },
    {
        "slug": "gurps",
        "nome": "GURPS",
        "descricao": (
            "Sistema genérico GURPS com pontos de personagem, vantagens, "
            "desvantagens e perícias — ficha e Arena na plataforma."
        ),
        "status": "disponivel",
        "icone": "⚙️",
        "ordem": 30,
    },
]


def inicializar_catalogo_jogos(db: Session) -> None:
    """
    Sincroniza o catálogo global de jogos suportados pela plataforma.

    Idempotente: insere jogos novos e atualiza metadados (nome, descrição,
    status, ícone, ordem) sem quebrar memberships já existentes.
    """
    try:
        existentes = {g.slug: g for g in db.query(Game).all()}
        criados = 0
        atualizados = 0

        for entrada in GAME_CATALOG_SEED:
            slug = entrada["slug"]
            game = existentes.get(slug)
            if game is None:
                db.add(
                    Game(
                        slug=slug,
                        nome=entrada["nome"],
                        descricao=entrada.get("descricao", ""),
                        status=entrada.get("status", "disponivel"),
                        icone=entrada.get("icone", ""),
                        ordem=int(entrada.get("ordem", 0)),
                    )
                )
                criados += 1
                continue

            mudou = False
            for campo in ("nome", "descricao", "status", "icone", "ordem"):
                novo = entrada.get(campo)
                if novo is not None and getattr(game, campo) != novo:
                    setattr(game, campo, novo)
                    mudou = True
            if mudou:
                atualizados += 1

        if criados or atualizados:
            db.commit()
            logger.info(
                "✅ games_catalog: %s criados, %s atualizados", criados, atualizados
            )
        else:
            logger.info("✅ games_catalog já sincronizado (%s jogos)", len(existentes))
    except Exception:
        db.rollback()
        raise
