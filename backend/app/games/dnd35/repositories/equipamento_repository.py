"""
Repository de Equipamento (D&D 3.5)
SRP: operações de banco de dados para equipamentos.

Localização: este módulo pertence ao pacote
`app.games.dnd35.repositories` por ser dependente exclusivamente das
regras de equipamentos do D&D 3.5. Existe um shim em
`app.repositories.equipamento_repository` que re-exporta as classes
durante a reorganização multi-jogo.
"""

from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased

from app.games.dnd35.models.equipamento import Equipamento, EquipamentoJogador
from app.games.dnd35.schemas.equipamento import (
    EquipamentoCreate,
    EquipamentoJogadorCreate,
)
from app.repositories.base import (
    apply_not_deleted,
    commit_with_rollback,
    soft_delete_entity,
)


class EquipamentoRepository:
    """Operações de banco de dados para equipamentos"""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _payload_data(payload, exclude_unset: bool = False) -> dict:
        if hasattr(payload, "model_dump"):
            return payload.model_dump(exclude_unset=exclude_unset)
        if exclude_unset:
            return payload.dict(exclude_unset=True)
        return payload.dict()

    def restaurar_equipamento(
        self,
        db_equipamento: Equipamento,
        equipamento: EquipamentoCreate,
    ) -> Equipamento:
        db_equipamento.deleted_at = None
        db_equipamento.ativo = True
        for key, value in self._payload_data(equipamento).items():
            setattr(db_equipamento, key, value)
        commit_with_rollback(self.db)
        self.db.refresh(db_equipamento)
        return db_equipamento

    def criar_equipamento(self, equipamento: EquipamentoCreate) -> Equipamento:
        """Cria um novo equipamento"""
        db_equipamento = Equipamento(**self._payload_data(equipamento))
        self.db.add(db_equipamento)
        commit_with_rollback(self.db)
        self.db.refresh(db_equipamento)
        return db_equipamento

    def obter_equipamento(self, equipamento_id: int) -> Optional[Equipamento]:
        """Obtém um equipamento por ID"""
        return (
            apply_not_deleted(self.db.query(Equipamento), Equipamento)
            .filter(Equipamento.id == equipamento_id)
            .first()
        )

    def obter_equipamento_por_nome(self, nome: str) -> Optional[Equipamento]:
        """Obtém um equipamento por nome"""
        return self.db.query(Equipamento).filter(Equipamento.nome == nome).first()

    def listar_equipamentos(self, skip: int = 0, limit: int = 100) -> list[Equipamento]:
        """Lista todos os equipamentos com paginação"""
        return (
            apply_not_deleted(self.db.query(Equipamento), Equipamento)
            .filter(Equipamento.ativo == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def atualizar_equipamento(
        self, equipamento_id: int, equipamento_data: dict
    ) -> Optional[Equipamento]:
        """Atualiza um equipamento"""
        db_equipamento = (
            apply_not_deleted(self.db.query(Equipamento), Equipamento)
            .filter(Equipamento.id == equipamento_id)
            .first()
        )
        if db_equipamento:
            for key, value in equipamento_data.items():
                if value is not None:
                    setattr(db_equipamento, key, value)
            commit_with_rollback(self.db)
            self.db.refresh(db_equipamento)
        return db_equipamento

    def deletar_equipamento(self, equipamento_id: int) -> bool:
        """Deleta um equipamento"""
        db_equipamento = (
            apply_not_deleted(self.db.query(Equipamento), Equipamento)
            .filter(Equipamento.id == equipamento_id)
            .first()
        )
        if db_equipamento:
            return soft_delete_entity(self.db, db_equipamento)
        return False


class EquipamentoJogadorRepository:
    """Operações de banco de dados para equipamentos do jogador"""

    def __init__(self, db: Session):
        self.db = db

    def adicionar_equipamento(
        self,
        combatente_id: int,
        equipamento_jogador: EquipamentoJogadorCreate,
    ) -> EquipamentoJogador:
        """Adiciona um equipamento ao combatente"""
        db_existente = (
            self.db.query(EquipamentoJogador)
            .filter(
                and_(
                    EquipamentoJogador.combatente_id == combatente_id,
                    EquipamentoJogador.equipamento_id
                    == equipamento_jogador.equipamento_id,
                )
            )
            .first()
        )

        if db_existente:
            db_existente.quantidade += equipamento_jogador.quantidade
            commit_with_rollback(self.db)
            self.db.refresh(db_existente)
            return db_existente

        db_equipamento_jogador = EquipamentoJogador(
            combatente_id=combatente_id,
            equipamento_id=equipamento_jogador.equipamento_id,
            quantidade=equipamento_jogador.quantidade,
        )
        self.db.add(db_equipamento_jogador)
        commit_with_rollback(self.db)
        self.db.refresh(db_equipamento_jogador)
        return db_equipamento_jogador

    def obter_equipamentos_jogador(self, combatente_id: int) -> list[EquipamentoJogador]:
        """Obtém todos os equipamentos de um combatente"""
        return (
            self.db.query(EquipamentoJogador)
            .filter(EquipamentoJogador.combatente_id == combatente_id)
            .all()
        )

    def obter_equipamentos_jogador_detalhado(self, combatente_id: int) -> list[dict]:
        """Obtém equipamentos do jogador com aliases explícitos para evitar ambiguidade em joins."""
        eq_jogador = aliased(EquipamentoJogador, name="eq_jogador")
        eq_catalogo = aliased(Equipamento, name="eq_catalogo")

        rows = (
            self.db.query(
                eq_jogador.equipamento_id.label("equipamento_id"),
                eq_jogador.quantidade.label("jogador_quantidade"),
                eq_catalogo.nome.label("equipamento_nome"),
                eq_catalogo.descricao.label("equipamento_descricao"),
                eq_catalogo.pagina_referencia.label("equipamento_pagina_referencia"),
                eq_catalogo.categoria.label("equipamento_categoria"),
                eq_catalogo.subcategoria.label("equipamento_subcategoria"),
                eq_catalogo.custo.label("equipamento_custo"),
                eq_catalogo.dano_pequeno.label("equipamento_dano_pequeno"),
                eq_catalogo.dano_medio.label("equipamento_dano_medio"),
                eq_catalogo.critico.label("equipamento_critico"),
                eq_catalogo.alcance_incremento.label("equipamento_alcance_incremento"),
                eq_catalogo.peso.label("equipamento_peso"),
                eq_catalogo.tipo_dano.label("equipamento_tipo_dano"),
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

    def remover_equipamento(self, combatente_id: int, equipamento_id: int) -> bool:
        """Remove um equipamento do combatente"""
        db_equipamento_jogador = (
            self.db.query(EquipamentoJogador)
            .filter(
                and_(
                    EquipamentoJogador.combatente_id == combatente_id,
                    EquipamentoJogador.equipamento_id == equipamento_id,
                )
            )
            .first()
        )

        if db_equipamento_jogador:
            self.db.delete(db_equipamento_jogador)
            commit_with_rollback(self.db)
            return True
        return False

    def atualizar_quantidade(
        self,
        combatente_id: int,
        equipamento_id: int,
        quantidade: int,
    ) -> Optional[EquipamentoJogador]:
        """Atualiza a quantidade de um equipamento"""
        db_equipamento_jogador = (
            self.db.query(EquipamentoJogador)
            .filter(
                and_(
                    EquipamentoJogador.combatente_id == combatente_id,
                    EquipamentoJogador.equipamento_id == equipamento_id,
                )
            )
            .first()
        )

        if db_equipamento_jogador:
            db_equipamento_jogador.quantidade = quantidade
            commit_with_rollback(self.db)
            self.db.refresh(db_equipamento_jogador)
        return db_equipamento_jogador
