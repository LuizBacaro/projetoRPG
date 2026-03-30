"""
Repository de Equipamento
Single Responsibility: Operações de banco de dados
"""

from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased
from sqlalchemy import func, and_
from app.models.equipamento import Equipamento, EquipamentoJogador
from app.schemas.equipamento import EquipamentoCreate, EquipamentoJogadorCreate
from app.repositories.base import apply_not_deleted, commit_with_rollback, soft_delete_entity


class EquipamentoRepository:
    """Operações de banco de dados para equipamentos"""

    @staticmethod
    def restaurar_equipamento(db: Session, db_equipamento: Equipamento, equipamento: EquipamentoCreate) -> Equipamento:
        db_equipamento.deleted_at = None
        db_equipamento.ativo = True
        for key, value in equipamento.dict().items():
            setattr(db_equipamento, key, value)
        commit_with_rollback(db)
        db.refresh(db_equipamento)
        return db_equipamento

    @staticmethod
    def criar_equipamento(db: Session, equipamento: EquipamentoCreate) -> Equipamento:
        """Cria um novo equipamento"""
        db_equipamento = Equipamento(**equipamento.dict())
        db.add(db_equipamento)
        commit_with_rollback(db)
        db.refresh(db_equipamento)
        return db_equipamento

    @staticmethod
    def obter_equipamento(db: Session, equipamento_id: int) -> Equipamento:
        """Obtém um equipamento por ID"""
        return apply_not_deleted(db.query(Equipamento), Equipamento).filter(Equipamento.id == equipamento_id).first()

    @staticmethod
    def obter_equipamento_por_nome(db: Session, nome: str) -> Equipamento:
        """Obtém um equipamento por nome"""
        return db.query(Equipamento).filter(Equipamento.nome == nome).first()

    @staticmethod
    def listar_equipamentos(db: Session, skip: int = 0, limit: int = 100) -> list[Equipamento]:
        """Lista todos os equipamentos com paginação"""
        return (
            apply_not_deleted(db.query(Equipamento), Equipamento)
            .filter(Equipamento.ativo == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def atualizar_equipamento(db: Session, equipamento_id: int, equipamento_data: dict) -> Equipamento:
        """Atualiza um equipamento"""
        db_equipamento = apply_not_deleted(db.query(Equipamento), Equipamento).filter(Equipamento.id == equipamento_id).first()
        if db_equipamento:
            for key, value in equipamento_data.items():
                if value is not None:
                    setattr(db_equipamento, key, value)
            commit_with_rollback(db)
            db.refresh(db_equipamento)
        return db_equipamento

    @staticmethod
    def deletar_equipamento(db: Session, equipamento_id: int) -> bool:
        """Deleta um equipamento"""
        db_equipamento = apply_not_deleted(db.query(Equipamento), Equipamento).filter(Equipamento.id == equipamento_id).first()
        if db_equipamento:
            return soft_delete_entity(db, db_equipamento)
        return False


class EquipamentoJogadorRepository:
    """Operações de banco de dados para equipamentos do jogador"""

    @staticmethod
    def adicionar_equipamento(db: Session, combatente_id: int, equipamento_jogador: EquipamentoJogadorCreate) -> EquipamentoJogador:
        """Adiciona um equipamento ao combatente"""
        # Verifica se já existe
        db_existente = db.query(EquipamentoJogador).filter(
            and_(
                EquipamentoJogador.combatente_id == combatente_id,
                EquipamentoJogador.equipamento_id == equipamento_jogador.equipamento_id
            )
        ).first()
        
        if db_existente:
            # Se já existe, apenas incrementa quantidade
            db_existente.quantidade += equipamento_jogador.quantidade
            commit_with_rollback(db)
            db.refresh(db_existente)
            return db_existente
        
        # Se não existe, cria novo
        db_equipamento_jogador = EquipamentoJogador(
            combatente_id=combatente_id,
            equipamento_id=equipamento_jogador.equipamento_id,
            quantidade=equipamento_jogador.quantidade
        )
        db.add(db_equipamento_jogador)
        commit_with_rollback(db)
        db.refresh(db_equipamento_jogador)
        return db_equipamento_jogador

    @staticmethod
    def obter_equipamentos_jogador(db: Session, combatente_id: int) -> list[EquipamentoJogador]:
        """Obtém todos os equipamentos de um combatente"""
        return db.query(EquipamentoJogador).filter(
            EquipamentoJogador.combatente_id == combatente_id
        ).all()

    @staticmethod
    def obter_equipamentos_jogador_detalhado(db: Session, combatente_id: int) -> list[dict]:
        """Obtém equipamentos do jogador com aliases explícitos para evitar ambiguidade em joins."""
        eq_jogador = aliased(EquipamentoJogador, name="eq_jogador")
        eq_catalogo = aliased(Equipamento, name="eq_catalogo")

        rows = (
            db.query(
                eq_jogador.equipamento_id.label("equipamento_id"),
                eq_jogador.quantidade.label("jogador_quantidade"),
                eq_catalogo.nome.label("equipamento_nome"),
                eq_catalogo.descricao.label("equipamento_descricao"),
                eq_catalogo.pagina_referencia.label("equipamento_pagina_referencia"),
            )
            .join(eq_catalogo, eq_catalogo.id == eq_jogador.equipamento_id)
            .filter(
                eq_jogador.combatente_id == combatente_id,
                eq_catalogo.deleted_at.is_(None),
            )
            .order_by(eq_catalogo.nome.asc())
            .all()
        )

        return [dict(row._mapping) for row in rows]

    @staticmethod
    def remover_equipamento(db: Session, combatente_id: int, equipamento_id: int) -> bool:
        """Remove um equipamento do combatente"""
        db_equipamento_jogador = db.query(EquipamentoJogador).filter(
            and_(
                EquipamentoJogador.combatente_id == combatente_id,
                EquipamentoJogador.equipamento_id == equipamento_id
            )
        ).first()
        
        if db_equipamento_jogador:
            db.delete(db_equipamento_jogador)
            commit_with_rollback(db)
            return True
        return False

    @staticmethod
    def atualizar_quantidade(db: Session, combatente_id: int, equipamento_id: int, quantidade: int) -> EquipamentoJogador:
        """Atualiza a quantidade de um equipamento"""
        db_equipamento_jogador = db.query(EquipamentoJogador).filter(
            and_(
                EquipamentoJogador.combatente_id == combatente_id,
                EquipamentoJogador.equipamento_id == equipamento_id
            )
        ).first()
        
        if db_equipamento_jogador:
            db_equipamento_jogador.quantidade = quantidade
            commit_with_rollback(db)
            db.refresh(db_equipamento_jogador)
        return db_equipamento_jogador
