"""
CondicaoRepository
Princípio SOLID: DIP - Abstração para acesso a dados de Condições
SRP - Apenas lógica de persistência
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session, aliased

from app.games.dnd35.models.combatente_condicao import CombatenteCondicao
from app.games.dnd35.models.condicao import Condicao
from app.repositories.base import commit_with_rollback


class CondicaoRepository:
    """
    Repository padrão para operações de Condição.
    Sem ORM relationship — queries manuais para máximo controle.
    """

    def __init__(self, db: Session):
        self.db = db

    def commit(self) -> None:
        """Executa commit explícito para fluxos em lote."""
        commit_with_rollback(self.db)

    # ── Catálogo ────────────────────────────────────────────────────────────

    def get_all(self) -> List[Dict]:
        """Retorna todas as condições"""
        condicoes = self.db.query(Condicao).all()
        return [
            {
                "id": c.id,
                "nome": c.nome,
                "efeito": c.efeito,
            }
            for c in condicoes
        ]

    def get_by_id(
        self, condicao_id: int
    ) -> Optional[Condicao]:  # ✅ Usar Optional em vez de |
        """Retorna uma condição por ID"""
        return self.db.query(Condicao).filter(Condicao.id == condicao_id).first()

    def get_by_nome(self, nome: str) -> Optional[Condicao]:
        """Retorna uma condição pelo nome exato."""
        return self.db.query(Condicao).filter(Condicao.nome == nome).first()

    def seed(self, condicoes_data: List[Dict]) -> None:
        """Popula a tabela com as 25 condições padrão D&D"""
        for data in condicoes_data:
            existente = (
                self.db.query(Condicao).filter(Condicao.nome == data["nome"]).first()
            )
            if not existente:
                novo = Condicao(nome=data["nome"], efeito=data["efeito"])
                self.db.add(novo)
        commit_with_rollback(self.db)

    # ── Por combatente ──────────────────────────────────────────────────────

    def get_condicoes_do_combatente(self, combatente_id: int) -> list:
        """Retorna condições ativas com duração"""
        cc_alias = aliased(CombatenteCondicao, name="cc")
        cond_alias = aliased(Condicao, name="cond")

        registros = (
            self.db.query(
                cc_alias.id.label("relacao_id"),
                cc_alias.condicao_id.label("condicao_id"),
                cc_alias.duracao_turnos.label("duracao_turnos"),
                cond_alias.nome.label("condicao_nome"),
                cond_alias.efeito.label("condicao_efeito"),
            )
            .join(cond_alias, cc_alias.condicao_id == cond_alias.id)
            .filter(cc_alias.combatente_id == combatente_id)
            .all()
        )

        return [
            {
                "id": row.relacao_id,
                "condicao_id": row.condicao_id,
                "nome": row.condicao_nome,
                "efeito": row.condicao_efeito,
                "duracao_turnos": row.duracao_turnos,
            }
            for row in registros
        ]

    def aplicar(
        self,
        combatente_id: int,
        condicao_id: int,
        duracao_turnos: int = -1,
        commit: bool = True,
    ) -> None:
        """
        Aplica uma condição a um combatente com duração.
        ✅ Idempotente — atualiza duração se já existe
        """
        existente = (
            self.db.query(CombatenteCondicao)
            .filter(
                CombatenteCondicao.combatente_id == combatente_id,
                CombatenteCondicao.condicao_id == condicao_id,
            )
            .first()
        )

        if existente:
            # Atualiza duração se já existe
            existente.duracao_turnos = duracao_turnos
        else:
            # Cria nova associação
            cc = CombatenteCondicao(
                combatente_id=combatente_id,
                condicao_id=condicao_id,
                duracao_turnos=duracao_turnos,
            )
            self.db.add(cc)

        if commit:
            commit_with_rollback(self.db)

    def remover(
        self, combatente_id: int, condicao_id: int, commit: bool = True
    ) -> None:
        """Remove uma condição específica de um combatente"""
        self.db.query(CombatenteCondicao).filter(
            CombatenteCondicao.combatente_id == combatente_id,
            CombatenteCondicao.condicao_id == condicao_id,
        ).delete()
        if commit:
            commit_with_rollback(self.db)

    def remover_todas(self, combatente_id: int, commit: bool = True) -> None:
        """Remove todas as condições de um combatente"""
        self.db.query(CombatenteCondicao).filter(
            CombatenteCondicao.combatente_id == combatente_id
        ).delete()
        if commit:
            commit_with_rollback(self.db)

    def atualizar_duracao(
        self,
        combatente_id: int,
        condicao_id: int,
        nova_duracao: int,
        commit: bool = True,
    ) -> bool:
        """Atualiza a duração em turnos de uma condição específica

        Returns:
            True se atualizado, False se condição não encontrada
        """
        cc = (
            self.db.query(CombatenteCondicao)
            .filter(
                CombatenteCondicao.combatente_id == combatente_id,
                CombatenteCondicao.condicao_id == condicao_id,
            )
            .first()
        )

        if not cc:
            return False

        cc.duracao_turnos = nova_duracao
        if commit:
            commit_with_rollback(self.db)
        return True
