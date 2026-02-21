"""
Model do Combatente (Entity)
"""
from sqlalchemy import Column, Integer, String
from ..core.database import Base


class Combatente(Base):
    """
    Entidade que representa um combatente no sistema
    """
    __tablename__ = "combatentes"
    __table_args__ = {'extend_existing': True}

    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # jogador, monstro, npc
    classe = Column(String, nullable=False)

    # Combate
    hp_atual = Column(Integer, nullable=False)
    hp_maximo = Column(Integer, nullable=False)
    iniciativa = Column(Integer, nullable=False, default=0)

    # Defesa
    ca = Column(Integer, default=10)
    toque = Column(Integer, default=10)
    surpresa = Column(Integer, default=10)

    # Visual
    foto_url = Column(String, nullable=True)

    # Atributos D&D
    forca = Column(Integer, default=10)
    destreza = Column(Integer, default=10)
    constituicao = Column(Integer, default=10)
    inteligencia = Column(Integer, default=10)
    sabedoria = Column(Integer, default=10)
    carisma = Column(Integer, default=10)

    # Resistências
    fortitude = Column(Integer, default=0)
    reflexos = Column(Integer, default=0)
    vontade = Column(Integer, default=0)

    # Progressão
    nivel = Column(Integer, default=1)
    pontos = Column(Integer, default=0)

    def __repr__(self):
        return f"<Combatente(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"

    def esta_vivo(self) -> bool:
        """Verifica se o combatente está vivo"""
        return self.hp_atual > 0

    def esta_critico(self) -> bool:
        """Verifica se o HP está crítico (< 25%)"""
        return self.hp_atual < self.hp_maximo * 0.25

    def aplicar_dano(self, dano: int) -> int:
        """Aplica dano ao combatente. Retorna o HP atual após o dano"""
        self.hp_atual = max(0, self.hp_atual - dano)
        return self.hp_atual

    def curar(self, cura: int) -> int:
        """Cura o combatente. Retorna o HP atual após a cura"""
        self.hp_atual = min(self.hp_maximo, self.hp_atual + cura)
        return self.hp_atual

    def resetar_hp(self) -> None:
        """Reseta HP para o máximo"""
        self.hp_atual = self.hp_maximo

    def calcular_modificador(self, atributo: str) -> int:
        """
        Calcula o modificador de um atributo (D&D 5e)
        Fórmula: (Atributo - 10) / 2 (arredondado para baixo)
        """
        valor = getattr(self, atributo.lower(), 10)
        return (valor - 10) // 2