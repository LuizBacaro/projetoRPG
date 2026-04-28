"""
Compatibilidade com usuários legados: membership automático no jogo `dnd35`.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.shared.models.game import Game, UserGameMembership
from app.shared.models.usuario import Usuario

logger = logging.getLogger(__name__)


def garantir_membership_dnd35_para_usuarios_legados(db: Session) -> None:
    """
    Para todos os usuários ativos sem nenhum membership, cria automaticamente o
    membership do jogo `dnd35` com o perfil global do usuário. Garante que a
    base legada continue acessando o D&D 3.5 sem precisar passar por seleção
    explícita de jogo.
    """
    try:
        dnd35 = db.query(Game).filter(Game.slug == "dnd35").first()
        if dnd35 is None:
            logger.warning(
                "garantir_membership_dnd35_para_usuarios_legados: jogo dnd35 ausente; "
                "pulando enrolamento."
            )
            return

        ja_com_membership = {
            uid for (uid,) in db.query(UserGameMembership.usuario_id).distinct()
        }

        usuarios = db.query(Usuario).filter(Usuario.ativo == True).all()  # noqa: E712
        criados = 0
        for usuario in usuarios:
            if usuario.id in ja_com_membership:
                continue
            perfil_valor = (
                usuario.perfil.value
                if hasattr(usuario.perfil, "value")
                else str(usuario.perfil)
            )
            db.add(
                UserGameMembership(
                    usuario_id=usuario.id,
                    game_id=dnd35.id,
                    perfil_no_jogo=perfil_valor,
                    ativo=True,
                )
            )
            criados += 1

        if criados:
            db.commit()
            logger.info(
                "✅ Auto-enroll dnd35: %s usuário(s) legados vinculados", criados
            )
        else:
            logger.info("✅ Auto-enroll dnd35: nenhum usuário legado pendente")
    except Exception:
        db.rollback()
        raise
