"""Alinhar catálogo de perícias à Tabela 4-3 (Livro do Jogador D&D 3.5).

Revision ID: a9b8c7d6e5f4
Revises: 0bab69d07dc1
Create Date: 2026-04-21

"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session


revision: str = "a9b8c7d6e5f4"
down_revision: Union[str, None] = "0bab69d07dc1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TODAS_CLASSES_PHB = (
    "Bárbaro",
    "Bardo",
    "Clérigo",
    "Druida",
    "Feiticeiro",
    "Guerreiro",
    "Ladino",
    "Mago",
    "Monge",
    "Paladino",
    "Ranger",
)

_DESCR_FALAR_IDIOMA = (
    "Aprende idiomas adicionais: cada graduação representa um idioma que você fala e entende fluentemente. "
    "No livro não há teste de perícia padrão para falar; o atributo (INT) na ficha segue a convenção SRD."
)

# Restauração no downgrade (removidos do seed alinhado à Tabela 4-3).
_RESTORE_OBSOLETAS = {
    "Conhecimento": {
        "descricao": (
            "Saber acadêmico e erudito em uma área específica a ser escolhida. Serve para lembrar fatos, "
            "identificar criaturas/assuntos, e interpretar pistas históricas ou místicas sobre o tema escolhido."
        ),
        "classes": ("Bardo", "Mago"),
    },
    "Conhecimento (monstros)": {
        "descricao": (
            "Saber acadêmico e erudito sobre monstros. Serve para lembrar fatos, identificar características, "
            "e interpretar pistas sobre monstros e suas características."
        ),
        "classes": ("Mago",),
    },
}


def _garantir_falar_idioma(session: Session) -> None:
    from app.games.dnd35.models.pericia import Pericia, PericiaClasse

    row = session.query(Pericia).filter(Pericia.nome == "Falar Idioma").first()
    if row is None:
        row = Pericia(
            nome="Falar Idioma",
            descricao=_DESCR_FALAR_IDIOMA,
            atributo="Int",
            tipo="comum",
            especialidade=None,
            requer_treinamento=1,
            pode_usar_sem_treinamento=0,
            sofre_penalidade_armadura=0,
            pagina_livro=None,
        )
        session.add(row)
        session.flush()
    else:
        if row.deleted_at is not None:
            row.deleted_at = None
        row.descricao = _DESCR_FALAR_IDIOMA
        row.atributo = "Int"
        row.requer_treinamento = 1
        row.pode_usar_sem_treinamento = 0

    existentes = {c.classe_nome for c in row.pericias_classes}
    for classe in _TODAS_CLASSES_PHB:
        if classe not in existentes:
            session.add(
                PericiaClasse(pericia_id=row.id, classe_nome=classe, is_default=1)
            )


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.games.dnd35.models.pericia import Pericia, PericiaClasse, PericiaJogador

        p_inst = session.query(Pericia).filter(Pericia.nome == "Usar Intrumento Mágico").first()
        if p_inst is not None:
            p_inst.nome = "Usar Instrumento Mágico"

        _garantir_falar_idioma(session)

        for nome in ("Conhecimento", "Conhecimento (monstros)"):
            p = session.query(Pericia).filter(Pericia.nome == nome, Pericia.deleted_at.is_(None)).first()
            if p is None:
                continue
            if session.query(PericiaJogador).filter(PericiaJogador.pericia_id == p.id).count() > 0:
                continue
            session.query(PericiaClasse).filter(PericiaClasse.pericia_id == p.id).delete(
                synchronize_session=False
            )
            p.deleted_at = datetime.now(timezone.utc)

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from app.games.dnd35.models.pericia import Pericia, PericiaClasse, PericiaJogador

        p_inst = session.query(Pericia).filter(Pericia.nome == "Usar Instrumento Mágico").first()
        if p_inst is not None:
            p_inst.nome = "Usar Intrumento Mágico"

        falar = session.query(Pericia).filter(Pericia.nome == "Falar Idioma").first()
        if falar is not None:
            if session.query(PericiaJogador).filter(PericiaJogador.pericia_id == falar.id).count() == 0:
                session.query(PericiaClasse).filter(PericiaClasse.pericia_id == falar.id).delete(
                    synchronize_session=False
                )
                session.delete(falar)

        for nome, meta in _RESTORE_OBSOLETAS.items():
            p = session.query(Pericia).filter(Pericia.nome == nome).first()
            if p is None:
                continue
            p.deleted_at = None
            p.descricao = meta["descricao"]
            for classe in meta["classes"]:
                existe = (
                    session.query(PericiaClasse)
                    .filter(
                        PericiaClasse.pericia_id == p.id,
                        PericiaClasse.classe_nome == classe,
                    )
                    .first()
                )
                if existe is None:
                    session.add(
                        PericiaClasse(pericia_id=p.id, classe_nome=classe, is_default=1)
                    )

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
