"""
Model de Condição (Entity)
Princípio SOLID: SRP - Entidade responsável apenas por representar uma Condição D&D
"""
from sqlalchemy import Column, Integer, String, Text

from app.core.database import Base


class Condicao(Base):
    """
    Entidade que representa uma condição de D&D 3.5
    Seed com as 25 condições da planilha Condies-D&D.xlsx
    """
    __tablename__ = "condicoes"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    efeito = Column(Text, nullable=False)

    def __repr__(self):
        return f"<Condicao(id={self.id}, nome='{self.nome}')>"
