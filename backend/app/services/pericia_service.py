"""
Service de Perícia
Single Responsibility: Lógica de negócio das perícias
SOLID: Dependency Injection via repository
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.pericia import Pericia, PericiaJogador
from app.models.combatente import Combatente
from app.schemas.pericia import (
    PericiaCreate, PericiaUpdate, PericiaJogadorCreate, PericiaJogadorUpdate
)


class PericiaService:
    """Serviço de lógica de negócio para perícias"""

    def __init__(self, db: Session):
        self.db = db

    # ========== PERÍCIAS DISPONÍVEIS ==========

    def criar_pericia(self, pericia: PericiaCreate) -> Pericia:
        """Cria uma nova perícia"""
        # Verificar duplicata
        pericia_existente = self.db.query(Pericia).filter(
            Pericia.nome == pericia.nome
        ).first()
        
        if pericia_existente:
            raise ValueError(f"Perícia '{pericia.nome}' já existe")
        
        db_pericia = Pericia(**pericia.dict())
        self.db.add(db_pericia)
        self.db.commit()
        self.db.refresh(db_pericia)
        return db_pericia

    def obter_pericia(self, pericia_id: int) -> Optional[Pericia]:
        """Obtém uma perícia por ID"""
        return self.db.query(Pericia).filter(Pericia.id == pericia_id).first()

    def listar_todas_pericias(self, skip: int = 0, limit: int = 100) -> List[Pericia]:
        """Lista todas as perícias disponíveis"""
        return self.db.query(Pericia).offset(skip).limit(limit).all()

    def listar_pericias_por_atributo(self, atributo: str) -> List[Pericia]:
        """Lista perícias filtradas por atributo"""
        atributos_validos = ["FOR", "DES", "CON", "INT", "SAB", "CAR"]
        if atributo.upper() not in atributos_validos:
            raise ValueError(f"Atributo '{atributo}' inválido")
        
        return self.db.query(Pericia).filter(Pericia.atributo == atributo.upper()).all()

    def atualizar_pericia(self, pericia_id: int, pericia: PericiaUpdate) -> Optional[Pericia]:
        """Atualiza uma perícia"""
        db_pericia = self.db.query(Pericia).filter(Pericia.id == pericia_id).first()
        
        if not db_pericia:
            return None
        
        for key, value in pericia.dict(exclude_unset=True).items():
            setattr(db_pericia, key, value)
        
        self.db.commit()
        self.db.refresh(db_pericia)
        return db_pericia

    def deletar_pericia(self, pericia_id: int) -> bool:
        """Deleta uma perícia"""
        db_pericia = self.db.query(Pericia).filter(Pericia.id == pericia_id).first()
        
        if not db_pericia:
            return False
        
        self.db.delete(db_pericia)
        self.db.commit()
        return True

    # ========== PERÍCIAS DO JOGADOR ==========

    def adicionar_pericia_jogador(
        self,
        combatente_id: int,
        pericia_jogador: PericiaJogadorCreate
    ) -> PericiaJogador:
        """Adiciona uma perícia ao jogador"""
        # Validar combatente
        combatente = self.db.query(Combatente).filter(
            Combatente.id == combatente_id
        ).first()
        
        if not combatente:
            raise ValueError(f"Combatente com ID {combatente_id} não existe")

        # Validar perícia
        pericia = self.db.query(Pericia).filter(
            Pericia.id == pericia_jogador.pericia_id
        ).first()
        
        if not pericia:
            raise ValueError(f"Perícia com ID {pericia_jogador.pericia_id} não existe")

        # Verificar duplicata
        pericia_existente = self.db.query(PericiaJogador).filter(
            PericiaJogador.combatente_id == combatente_id,
            PericiaJogador.pericia_id == pericia_jogador.pericia_id
        ).first()
        
        if pericia_existente:
            raise ValueError("Jogador já possui essa perícia")

        # ✅ CORRIGIDO: Obter modificador do atributo direto do Combatente
        atributo_map = {
            "FOR": "forca",
            "DES": "destreza",
            "CON": "constituicao",
            "INT": "inteligencia",
            "SAB": "sabedoria",
            "CAR": "carisma"
        }

        atributo_nome = atributo_map.get(pericia.atributo, "forca")
        
        # ✅ CORRIGIDO: Calcular modificador usando método do Combatente
        modificador = combatente.calcular_modificador(atributo_nome)

        # Criar perícia do jogador
        db_pericia_jogador = PericiaJogador(
            combatente_id=combatente_id,
            pericia_id=pericia_jogador.pericia_id,
            graduacao=pericia_jogador.graduacao,
            modificador_atributo=float(modificador),
            bonus_outros=pericia_jogador.bonus_outros or 0
        )
        
        self.db.add(db_pericia_jogador)
        self.db.commit()
        self.db.refresh(db_pericia_jogador)
        
        return db_pericia_jogador

    def obter_pericia_jogador(self, pericia_jogador_id: int) -> Optional[PericiaJogador]:
        """Obtém uma perícia específica do jogador"""
        return self.db.query(PericiaJogador).filter(
            PericiaJogador.id == pericia_jogador_id
        ).first()

    def listar_pericias_combatente(self, combatente_id: int) -> List[PericiaJogador]:
        """Lista todas as perícias de um combatente"""
        return self.db.query(PericiaJogador).filter(
            PericiaJogador.combatente_id == combatente_id
        ).all()

    def atualizar_pericia_jogador(
        self,
        pericia_jogador_id: int,
        pericia: PericiaJogadorUpdate
    ) -> Optional[PericiaJogador]:
        """Atualiza uma perícia do jogador"""
        db_pericia_jogador = self.db.query(PericiaJogador).filter(
            PericiaJogador.id == pericia_jogador_id
        ).first()
        
        if not db_pericia_jogador:
            return None
        
        for key, value in pericia.dict(exclude_unset=True).items():
            setattr(db_pericia_jogador, key, value)
        
        self.db.commit()
        self.db.refresh(db_pericia_jogador)
        return db_pericia_jogador

    def deletar_pericia_jogador(self, pericia_jogador_id: int) -> bool:
        """Deleta uma perícia do jogador"""
        db_pericia_jogador = self.db.query(PericiaJogador).filter(
            PericiaJogador.id == pericia_jogador_id
        ).first()
        
        if not db_pericia_jogador:
            return False
        
        self.db.delete(db_pericia_jogador)
        self.db.commit()
        return True

    def obter_estatisticas_pericias(self, combatente_id: int) -> dict:
        """Obtém estatísticas de perícias do combatente"""
        pericias = self.listar_pericias_combatente(combatente_id)
        
        pontos_gastos = sum(p.graduacao for p in pericias)
        
        # Obter combatente para calcular pontos disponíveis
        combatente = self.db.query(Combatente).filter(
            Combatente.id == combatente_id
        ).first()
        
        if not combatente:
            raise ValueError(f"Combatente {combatente_id} não encontrado")
        
        # Regra D&D 3.5: Máximo de (3 * nível) pontos em perícias
        nivel = combatente.nivel
        pontos_disponiveis = max(0, (3 * nivel) - pontos_gastos)

        return {
            "total_pericias": len(pericias),
            "pontos_gastos": pontos_gastos,
            "pontos_disponiveis": pontos_disponiveis,
            "pericias": pericias
        }