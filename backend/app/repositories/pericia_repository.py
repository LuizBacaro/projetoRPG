"""
Repository de Perícia
Single Responsibility: Operações de banco de dados
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.pericia import Pericia, PericiaJogador
from app.schemas.pericia import PericiaCreate, PericiaUpdate, PericiaJogadorCreate, PericiaJogadorUpdate


class PericiaRepository:
    """Operações de banco de dados para perícias"""

    @staticmethod
    def criar_pericia(db: Session, pericia: PericiaCreate) -> Pericia:
        """Cria uma nova perícia"""
        db_pericia = Pericia(**pericia.dict())
        db.add(db_pericia)
        db.commit()
        db.refresh(db_pericia)
        return db_pericia

    @staticmethod
    def obter_pericia(db: Session, pericia_id: int) -> Pericia:
        """Obtém uma perícia por ID"""
        return db.query(Pericia).filter(Pericia.id == pericia_id).first()

    @staticmethod
    def obter_pericia_por_nome(db: Session, nome: str) -> Pericia:
        """Obtém uma perícia por nome"""
        return db.query(Pericia).filter(Pericia.nome == nome).first()

    @staticmethod
    def listar_pericias(db: Session, skip: int = 0, limit: int = 100) -> list[Pericia]:
        """Lista todas as perícias com paginação"""
        return db.query(Pericia).offset(skip).limit(limit).all()

    @staticmethod
    def listar_pericias_por_atributo(db: Session, atributo: str) -> list[Pericia]:
        """Lista perícias filtradas por atributo"""
        return db.query(Pericia).filter(Pericia.atributo == atributo).all()

    @staticmethod
    def listar_pericias_por_tipo(db: Session, tipo: str) -> list[Pericia]:
        """Lista perícias filtradas por tipo"""
        return db.query(Pericia).filter(Pericia.tipo == tipo).all()

    @staticmethod
    def atualizar_pericia(db: Session, pericia_id: int, pericia: PericiaUpdate) -> Pericia:
        """Atualiza uma perícia"""
        db_pericia = db.query(Pericia).filter(Pericia.id == pericia_id).first()
        if db_pericia:
            for key, value in pericia.dict(exclude_unset=True).items():
                setattr(db_pericia, key, value)
            db.commit()
            db.refresh(db_pericia)
        return db_pericia

    @staticmethod
    def deletar_pericia(db: Session, pericia_id: int) -> bool:
        """Deleta uma perícia"""
        db_pericia = db.query(Pericia).filter(Pericia.id == pericia_id).first()
        if db_pericia:
            db.delete(db_pericia)
            db.commit()
            return True
        return False


class PericiaJogadorRepository:
    """Operações de banco de dados para perícias do jogador"""

    @staticmethod
    def adicionar_pericia(db: Session, pericia_jogador: PericiaJogadorCreate) -> PericiaJogador:
        """Adiciona uma perícia ao jogador"""
        db_pericia_jogador = PericiaJogador(**pericia_jogador.dict())
        db.add(db_pericia_jogador)
        db.commit()
        db.refresh(db_pericia_jogador)
        return db_pericia_jogador

    @staticmethod
    def obter_pericia_jogador(db: Session, pericia_jogador_id: int) -> PericiaJogador:
        """Obtém uma perícia específica do jogador"""
        return db.query(PericiaJogador).filter(PericiaJogador.id == pericia_jogador_id).first()

    @staticmethod
    def listar_pericias_jogador(db: Session, combatente_id: int) -> list[PericiaJogador]:
        """Lista todas as perícias de um combatente"""
        return db.query(PericiaJogador).filter(
            PericiaJogador.combatente_id == combatente_id
        ).all()

    @staticmethod
    def obter_pericia_jogador_por_nome(db: Session, combatente_id: int, nome_pericia: str) -> PericiaJogador:
        """Obtém uma perícia específica do jogador por nome"""
        return db.query(PericiaJogador).join(Pericia).filter(
            PericiaJogador.combatente_id == combatente_id,
            Pericia.nome == nome_pericia
        ).first()

    @staticmethod
    def atualizar_pericia_jogador(
        db: Session,
        pericia_jogador_id: int,
        pericia: PericiaJogadorUpdate
    ) -> PericiaJogador:
        """Atualiza uma perícia do jogador"""
        db_pericia_jogador = db.query(PericiaJogador).filter(
            PericiaJogador.id == pericia_jogador_id
        ).first()
        if db_pericia_jogador:
            for key, value in pericia.dict(exclude_unset=True).items():
                setattr(db_pericia_jogador, key, value)
            db.commit()
            db.refresh(db_pericia_jogador)
        return db_pericia_jogador

    @staticmethod
    def deletar_pericia_jogador(db: Session, pericia_jogador_id: int) -> bool:
        """Deleta uma perícia do jogador"""
        db_pericia_jogador = db.query(PericiaJogador).filter(
            PericiaJogador.id == pericia_jogador_id
        ).first()
        if db_pericia_jogador:
            db.delete(db_pericia_jogador)
            db.commit()
            return True
        return False

    @staticmethod
    def contar_pontos_gastos(db: Session, combatente_id: int) -> int:
        """Conta os pontos gastos em perícias"""
        resultado = db.query(func.sum(PericiaJogador.graduacao)).filter(
            PericiaJogador.combatente_id == combatente_id
        ).scalar()
        return resultado or 0