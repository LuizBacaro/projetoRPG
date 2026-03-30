"""
Repository de Talento
Single Responsibility: Operações de banco de dados
"""

from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased
from sqlalchemy import func, and_
from app.models.talento import Talento, TalentoJogador
from app.schemas.talento import TalentoCreate, TalentoJogadorCreate
from app.repositories.base import apply_not_deleted, commit_with_rollback, soft_delete_entity


class TalentoRepository:
    """Operações de banco de dados para talentos"""

    @staticmethod
    def restaurar_talento(db: Session, db_talento: Talento, talento: TalentoCreate) -> Talento:
        db_talento.deleted_at = None
        db_talento.ativo = True
        for key, value in talento.dict().items():
            setattr(db_talento, key, value)
        commit_with_rollback(db)
        db.refresh(db_talento)
        return db_talento

    @staticmethod
    def criar_talento(db: Session, talento: TalentoCreate) -> Talento:
        """Cria um novo talento"""
        db_talento = Talento(**talento.dict())
        db.add(db_talento)
        commit_with_rollback(db)
        db.refresh(db_talento)
        return db_talento

    @staticmethod
    def obter_talento(db: Session, talento_id: int) -> Talento:
        """Obtém um talento por ID"""
        return apply_not_deleted(db.query(Talento), Talento).filter(Talento.id == talento_id).first()

    @staticmethod
    def obter_talento_por_nome(db: Session, nome: str) -> Talento:
        """Obtém um talento por nome"""
        return db.query(Talento).filter(Talento.nome == nome).first()

    @staticmethod
    def listar_talentos(db: Session, skip: int = 0, limit: int = 100) -> list[Talento]:
        """Lista todos os talentos com paginação"""
        return (
            apply_not_deleted(db.query(Talento), Talento)
            .filter(Talento.ativo == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def atualizar_talento(db: Session, talento_id: int, talento_data: dict) -> Talento:
        """Atualiza um talento"""
        db_talento = apply_not_deleted(db.query(Talento), Talento).filter(Talento.id == talento_id).first()
        if db_talento:
            for key, value in talento_data.items():
                if value is not None:
                    setattr(db_talento, key, value)
            commit_with_rollback(db)
            db.refresh(db_talento)
        return db_talento

    @staticmethod
    def deletar_talento(db: Session, talento_id: int) -> bool:
        """Deleta um talento"""
        db_talento = apply_not_deleted(db.query(Talento), Talento).filter(Talento.id == talento_id).first()
        if db_talento:
            return soft_delete_entity(db, db_talento)
        return False


class TalentoJogadorRepository:
    """Operações de banco de dados para talentos do jogador"""

    @staticmethod
    def adicionar_talento(db: Session, combatente_id: int, talento_jogador: TalentoJogadorCreate) -> TalentoJogador:
        """Adiciona um talento ao combatente"""
        # Verifica se já existe
        db_existente = db.query(TalentoJogador).filter(
            and_(
                TalentoJogador.combatente_id == combatente_id,
                TalentoJogador.talento_id == talento_jogador.talento_id
            )
        ).first()
        
        if db_existente:
            # Se já existe, apenas retorna
            return db_existente
        
        # Se não existe, cria novo
        db_talento_jogador = TalentoJogador(
            combatente_id=combatente_id,
            talento_id=talento_jogador.talento_id
        )
        db.add(db_talento_jogador)
        commit_with_rollback(db)
        db.refresh(db_talento_jogador)
        return db_talento_jogador

    @staticmethod
    def obter_talentos_jogador(db: Session, combatente_id: int) -> list[TalentoJogador]:
        """Obtém todos os talentos de um combatente"""
        return db.query(TalentoJogador).filter(
            TalentoJogador.combatente_id == combatente_id
        ).all()

    @staticmethod
    def obter_talentos_jogador_detalhado(db: Session, combatente_id: int) -> list[dict]:
        """Obtém talentos do jogador com aliases explícitos para evitar ambiguidade em joins."""
        tal_jogador = aliased(TalentoJogador, name="tal_jogador")
        tal_catalogo = aliased(Talento, name="tal_catalogo")

        rows = (
            db.query(
                tal_jogador.talento_id.label("talento_id"),
                tal_catalogo.nome.label("talento_nome"),
                tal_catalogo.descricao.label("talento_descricao"),
                tal_catalogo.pagina_referencia.label("talento_pagina_referencia"),
            )
            .join(tal_catalogo, tal_catalogo.id == tal_jogador.talento_id)
            .filter(
                tal_jogador.combatente_id == combatente_id,
                tal_catalogo.deleted_at.is_(None),
            )
            .order_by(tal_catalogo.nome.asc())
            .all()
        )

        return [dict(row._mapping) for row in rows]

    @staticmethod
    def remover_talento(db: Session, combatente_id: int, talento_id: int) -> bool:
        """Remove um talento do combatente"""
        db_talento_jogador = db.query(TalentoJogador).filter(
            and_(
                TalentoJogador.combatente_id == combatente_id,
                TalentoJogador.talento_id == talento_id
            )
        ).first()
        
        if db_talento_jogador:
            db.delete(db_talento_jogador)
            commit_with_rollback(db)
            return True
        return False
