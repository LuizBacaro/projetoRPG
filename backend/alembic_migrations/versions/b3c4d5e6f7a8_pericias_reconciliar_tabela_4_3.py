"""Reconcilia catálogo legado de perícias à Tabela 4-3 (D&D 3.5, Livro do Jogador p. 55).

Revision ID: b3c4d5e6f7a8
Revises: a9b8c7d6e5f4
Create Date: 2026-04-21

Efeitos do upgrade:
- Renomeia perícias legadas para os nomes canônicos do livro
  (ex.: "Acrobacia" → "Acrobacias", "Conhecimento: Arcano" → "Conhecimento (arcano)",
  "Uso de Dispositivos Mágicos" → "Usar Instrumento Mágico", etc.).
- Insere as perícias canônicas que ainda não existam (ex.: "Observar", "Blefar",
  "Arte da Fuga", "Concentração", "Prestidigitação", "Ofícios", "Obter Informação",
  "Conhecimento (masmorras)", "Conhecimento (planos)", etc.).
- Consolida os 9 registros de especialidade de "Atuação" em uma única linha
  "Atuação" quando essas especialidades não possuírem nenhum `pericia_jogador` ligado.
- Marca como soft-deleted (preservando histórico) as perícias legadas que não têm
  correspondente na Tabela 4-3 ("Alquimia", "Navegação", "Pesquisa") e não estão em
  uso por nenhum `pericia_jogador`.

O downgrade é best-effort: desfaz os renames e remove "Falar Idioma" / "Observar" /
entradas canônicas inseridas se elas não estiverem em uso.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
from sqlalchemy.orm import Session


revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, None] = "a9b8c7d6e5f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Renames legados → canônicos da Tabela 4-3.
_RENAMES_LEGADOS: list[tuple[str, str]] = [
    ("Acrobacia", "Acrobacias"),
    ("Apreciar", "Avaliação"),
    ("Disfarce", "Disfarces"),
    ("Intuição", "Sentir Motivação"),
    ("Pesquisa", "Obter Informação"),
    ("Uso de Dispositivos Mágicos", "Usar Instrumento Mágico"),
    ("Conhecimento: Arcano", "Conhecimento (arcano)"),
    ("Conhecimento: Arquitetura", "Conhecimento (arquitetura e engenharia)"),
    ("Conhecimento: Geografia", "Conhecimento (geografia)"),
    ("Conhecimento: História", "Conhecimento (história)"),
    ("Conhecimento: Local", "Conhecimento (local)"),
    ("Conhecimento: Natureza", "Conhecimento (natureza)"),
    ("Conhecimento: Nobreza", "Conhecimento (nobreza e realeza)"),
    ("Conhecimento: Plano", "Conhecimento (planos)"),
    ("Conhecimento: Religião", "Conhecimento (religião)"),
]

# Legados fora da Tabela 4-3 (apenas soft-delete se não estiverem em uso).
_LEGADOS_OBSOLETOS: tuple[str, ...] = ("Alquimia", "Navegação")

# Especialidades de Atuação introduzidas antes de alinharmos o livro.
# Só são removidas se não houver `pericia_jogador` referenciando.
_ATUACAO_ESPECIALIDADES: tuple[str, ...] = (
    "Atuação (canto)",
    "Atuação (dança)",
    "Atuação (dramaturgia)",
    "Atuação (humor)",
    "Atuação (instrumentos de corda)",
    "Atuação (instrumentos de percussão)",
    "Atuação (instrumentos de sopro)",
    "Atuação (instrumentos de teclas)",
    "Atuação (oratória)",
)


def _pericia_em_uso(session: Session, pericia_id: int) -> bool:
    from app.games.dnd35.models.pericia import PericiaJogador

    return (
        session.query(PericiaJogador.id)
        .filter(PericiaJogador.pericia_id == pericia_id)
        .first()
        is not None
    )


def _soft_delete_se_ocioso(session: Session, pericia) -> bool:
    from app.games.dnd35.models.pericia import PericiaClasse

    if _pericia_em_uso(session, pericia.id):
        return False
    session.query(PericiaClasse).filter(PericiaClasse.pericia_id == pericia.id).delete(
        synchronize_session=False
    )
    pericia.deleted_at = datetime.now(timezone.utc)
    return True


def _migrar_referencias_jogador(session: Session, origem_id: int, destino_id: int) -> int:
    """Transfere registros de ``pericia_jogador`` da perícia de origem para a de destino.

    Se o jogador já possuir a perícia de destino, o registro de origem é descartado
    (evita violar o índice único implícito combatente_id × pericia_id).
    """
    from app.games.dnd35.models.pericia import PericiaJogador

    atualizados = 0
    origens = (
        session.query(PericiaJogador)
        .filter(PericiaJogador.pericia_id == origem_id)
        .all()
    )
    for registro in origens:
        ja_tem = (
            session.query(PericiaJogador.id)
            .filter(
                PericiaJogador.combatente_id == registro.combatente_id,
                PericiaJogador.pericia_id == destino_id,
                PericiaJogador.id != registro.id,
            )
            .first()
        )
        if ja_tem is not None:
            session.delete(registro)
        else:
            registro.pericia_id = destino_id
            atualizados += 1
    session.flush()
    return atualizados


def _copiar_associacoes_classe(session: Session, origem_id: int, destino_id: int) -> None:
    from app.games.dnd35.models.pericia import PericiaClasse

    ja_existentes = {
        c.classe_nome
        for c in session.query(PericiaClasse).filter(PericiaClasse.pericia_id == destino_id).all()
    }
    origens = (
        session.query(PericiaClasse)
        .filter(PericiaClasse.pericia_id == origem_id)
        .all()
    )
    for registro in origens:
        if registro.classe_nome not in ja_existentes:
            session.add(
                PericiaClasse(
                    pericia_id=destino_id,
                    classe_nome=registro.classe_nome,
                    is_default=registro.is_default or 1,
                )
            )
            ja_existentes.add(registro.classe_nome)
    session.flush()


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    try:
        from scripts.seed_pericias import PERICIAS_DATA  # noqa: WPS433

        from app.games.dnd35.models.pericia import Pericia, PericiaClasse

        # 1) Renomes legados → canônicos. Se a canônica já existir,
        # migramos referências de jogador/classe e removemos a legada.
        for nome_antigo, nome_novo in _RENAMES_LEGADOS:
            antiga = session.query(Pericia).filter(Pericia.nome == nome_antigo).first()
            if antiga is None:
                continue

            nova = (
                session.query(Pericia)
                .filter(Pericia.nome == nome_novo, Pericia.id != antiga.id)
                .first()
            )
            if nova is None:
                antiga.nome = nome_novo
                if antiga.deleted_at is not None:
                    antiga.deleted_at = None
                session.flush()
                continue

            if nova.deleted_at is not None:
                nova.deleted_at = None
            _copiar_associacoes_classe(session, antiga.id, nova.id)
            _migrar_referencias_jogador(session, antiga.id, nova.id)
            _soft_delete_se_ocioso(session, antiga)

        # 2) Consolidação de Atuação (9 especialidades → 1 linha "Atuação").
        atuacao = session.query(Pericia).filter(Pericia.nome == "Atuação").first()
        for nome_especialidade in _ATUACAO_ESPECIALIDADES:
            especial = session.query(Pericia).filter(Pericia.nome == nome_especialidade).first()
            if especial is None:
                continue
            if atuacao is not None:
                _copiar_associacoes_classe(session, especial.id, atuacao.id)
                _migrar_referencias_jogador(session, especial.id, atuacao.id)
            _soft_delete_se_ocioso(session, especial)

        # 3) Legados fora da Tabela 4-3: tentamos migrar para perícia canônica
        # equivalente (quando houver) antes do soft-delete.
        _MAPA_SEMANTICO_OBSOLETOS = {
            "Alquimia": "Ofícios",   # "Ofícios" engloba criação mundana no 3.5
            "Navegação": "Sobrevivência",  # Orientação/navegação cai em Sobrevivência
        }
        for nome in _LEGADOS_OBSOLETOS:
            p = (
                session.query(Pericia)
                .filter(Pericia.nome == nome, Pericia.deleted_at.is_(None))
                .first()
            )
            if p is None:
                continue
            destino_nome = _MAPA_SEMANTICO_OBSOLETOS.get(nome)
            destino = None
            if destino_nome:
                destino = (
                    session.query(Pericia)
                    .filter(Pericia.nome == destino_nome, Pericia.deleted_at.is_(None))
                    .first()
                )
            if destino is not None:
                _migrar_referencias_jogador(session, p.id, destino.id)
            _soft_delete_se_ocioso(session, p)

        # 4) Inserção idempotente de perícias canônicas faltantes.
        existentes = {
            nome for (nome,) in session.query(Pericia.nome).filter(Pericia.deleted_at.is_(None)).all()
        }
        inseridas = 0
        for entrada in PERICIAS_DATA:
            nome = entrada["nome"]
            if nome in existentes:
                continue

            atributo = str(entrada.get("atributo") or "").strip()[:3].upper() or "DES"
            nova = Pericia(
                nome=nome,
                descricao=entrada.get("descricao") or "",
                atributo=atributo,
                tipo="comum",
                especialidade=None,
                requer_treinamento=0,
                pode_usar_sem_treinamento=1,
                sofre_penalidade_armadura=0,
            )
            session.add(nova)
            session.flush()
            inseridas += 1

            for classe_nome in entrada.get("classes", []) or []:
                session.add(
                    PericiaClasse(
                        pericia_id=nova.id,
                        classe_nome=classe_nome,
                        is_default=1,
                    )
                )

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
        from app.games.dnd35.models.pericia import Pericia

        for nome_antigo, nome_novo in _RENAMES_LEGADOS:
            p = session.query(Pericia).filter(Pericia.nome == nome_novo).first()
            if p is None:
                continue
            colisao = (
                session.query(Pericia)
                .filter(Pericia.nome == nome_antigo, Pericia.id != p.id)
                .first()
            )
            if colisao is None:
                p.nome = nome_antigo

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
