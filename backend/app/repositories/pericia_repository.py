"""
Repository de Perícia
Single Responsibility: Operações de banco de dados
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.pericia import Pericia, PericiaJogador, PericiaClasse
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
    def listar_pericias_por_classe(db: Session, classe_nome: str) -> list[Pericia]:
        """Lista perícias padrão de uma classe específica"""
        return db.query(Pericia).join(
            PericiaClasse,
            Pericia.id == PericiaClasse.pericia_id
        ).filter(
            PericiaClasse.classe_nome == classe_nome,
            PericiaClasse.is_default == 1
        ).all()

    @staticmethod
    def obter_custo_pericia(db: Session, pericia_id: int, classe_nome: str) -> int:
        """
        Obtém o custo de uma perícia para uma classe
        Retorna: 1 se é perícia de classe, 2 se é fora da classe
        """
        pericia_classe = db.query(PericiaClasse).filter(
            PericiaClasse.pericia_id == pericia_id,
            PericiaClasse.classe_nome == classe_nome,
            PericiaClasse.is_default == 1
        ).first()
        
        # Se encontrou, é perícia de classe (custo 1)
        # Se não encontrou, é perícia fora da classe (custo 2)
        return 1 if pericia_classe else 2

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
    def obter_pericia_jogador_por_ids(
        db: Session, 
        combatente_id: int, 
        pericia_id: int
    ) -> PericiaJogador:
        """Obtém perícia do jogador por combatente_id e pericia_id"""
        return db.query(PericiaJogador).filter(
            PericiaJogador.combatente_id == combatente_id,
            PericiaJogador.pericia_id == pericia_id
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
        """Conta os pontos totais gastos em perícias (incluindo penalidades)"""
        resultado = db.query(func.sum(PericiaJogador.custo_total)).filter(
            PericiaJogador.combatente_id == combatente_id
        ).scalar()
        return resultado or 0

    @staticmethod
    def contar_graduacoes(db: Session, combatente_id: int) -> int:
        """Conta os pontos de graduação (sem penalidades)"""
        resultado = db.query(func.sum(PericiaJogador.graduacao)).filter(
            PericiaJogador.combatente_id == combatente_id
        ).scalar()
        return resultado or 0