"""
CondicaoRepository
Princípio SOLID: DIP - Abstração para acesso a dados de Condições
SRP - Apenas lógica de persistência
"""
from typing import List, Dict, Optional  # ✅ Adicionar Optional
from sqlalchemy.orm import Session

from ..models.condicao import Condicao
from ..models.combatente_condicao import CombatenteCondicao


class CondicaoRepository:
    """
    Repository padrão para operações de Condição.
    Sem ORM relationship — queries manuais para máximo controle.
    """

    def __init__(self, db: Session):
        self.db = db

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

    def get_by_id(self, condicao_id: int) -> Optional[Condicao]:  # ✅ Usar Optional em vez de |
        """Retorna uma condição por ID"""
        return self.db.query(Condicao).filter(Condicao.id == condicao_id).first()

    def seed(self, condicoes_data: List[Dict]) -> None:
        """Popula a tabela com as 25 condições padrão D&D"""
        for data in condicoes_data:
            existente = self.db.query(Condicao).filter(
                Condicao.nome == data["nome"]
            ).first()
            if not existente:
                novo = Condicao(nome=data["nome"], efeito=data["efeito"])
                self.db.add(novo)
        self.db.commit()

    # ── Por combatente ──────────────────────────────────────────────────────

    def get_condicoes_do_combatente(self, combatente_id: int) -> List[Dict]:
        """
        Retorna condições ativas de um combatente com duração.
        ✅ Garante que duracao_turnos é sempre um inteiro (default -1)
        """
        query = (
            self.db.query(CombatenteCondicao, Condicao)
            .join(Condicao, CombatenteCondicao.condicao_id == Condicao.id)
            .filter(CombatenteCondicao.combatente_id == combatente_id)
            .all()
        )

        result = []
        for cc, cond in query:
            # ✅ Garantir que duracao_turnos é sempre um inteiro (nunca None/undefined)
            duracao = cc.duracao_turnos if cc.duracao_turnos is not None else -1

            result.append({
                "id": cc.id,
                "condicao_id": cond.id,
                "combatente_id": cc.combatente_id,
                "nome": cond.nome,
                "efeito": cond.efeito,
                "duracao_turnos": int(duracao),  # ✅ Force integer type
            })

        return result

    def aplicar(self, combatente_id: int, condicao_id: int, duracao_turnos: int = -1) -> None:
        """
        Aplica uma condição a um combatente com duração.
        ✅ Idempotente — atualiza duração se já existe
        """
        existente = self.db.query(CombatenteCondicao).filter(
            CombatenteCondicao.combatente_id == combatente_id,
            CombatenteCondicao.condicao_id == condicao_id,
        ).first()

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

        self.db.commit()

    def remover(self, combatente_id: int, condicao_id: int) -> None:
        """Remove uma condição específica de um combatente"""
        self.db.query(CombatenteCondicao).filter(
            CombatenteCondicao.combatente_id == combatente_id,
            CombatenteCondicao.condicao_id == condicao_id,
        ).delete()
        self.db.commit()

    def remover_todas(self, combatente_id: int) -> None:
        """Remove todas as condições de um combatente"""
        self.db.query(CombatenteCondicao).filter(
            CombatenteCondicao.combatente_id == combatente_id
        ).delete()
        self.db.commit()

    def atualizar_duracao(self, combatente_id: int, condicao_id: int, nova_duracao: int) -> None:
        """Atualiza a duração em turnos de uma condição específica"""
        cc = self.db.query(CombatenteCondicao).filter(
            CombatenteCondicao.combatente_id == combatente_id,
            CombatenteCondicao.condicao_id == condicao_id,
        ).first()

        if cc:
            cc.duracao_turnos = nova_duracao
            self.db.commit()