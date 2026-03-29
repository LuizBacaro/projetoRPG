"""
Repository de Talento
Single Responsibility: Operações de banco de dados
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.talento import Talento, TalentoJogador
from app.schemas.talento import TalentoCreate, TalentoJogadorCreate
from app.repositories.base import commit_with_rollback


class TalentoRepository:
    """Operações de banco de dados para talentos"""

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
        return db.query(Talento).filter(Talento.id == talento_id).first()

    @staticmethod
    def obter_talento_por_nome(db: Session, nome: str) -> Talento:
        """Obtém um talento por nome"""
        return db.query(Talento).filter(Talento.nome == nome).first()

    @staticmethod
    def listar_talentos(db: Session, skip: int = 0, limit: int = 100) -> list[Talento]:
        """Lista todos os talentos com paginação"""
        return db.query(Talento).filter(Talento.ativo == True).offset(skip).limit(limit).all()

    @staticmethod
    def atualizar_talento(db: Session, talento_id: int, talento_data: dict) -> Talento:
        """Atualiza um talento"""
        db_talento = db.query(Talento).filter(Talento.id == talento_id).first()
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
        db_talento = db.query(Talento).filter(Talento.id == talento_id).first()
        if db_talento:
            db.delete(db_talento)
            commit_with_rollback(db)
            return True
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
