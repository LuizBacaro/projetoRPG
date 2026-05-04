"""Catálogo global da ficha (perícias / vantagens / desvantagens) — opcional; vazio = API usa JSON."""

from sqlalchemy import Boolean, Column, Integer, String, UniqueConstraint

from app.shared.core.database import Base


class GurpsCatalogoFichaVantagem(Base):
    __tablename__ = "gurps_catalogo_ficha_vantagens"
    __table_args__ = (UniqueConstraint("nome", name="uq_gurps_cat_ficha_vant_nome"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(512), nullable=False)
    custo = Column(Integer, nullable=True)
    custo_texto = Column(String(255), nullable=True)
    ordem = Column(Integer, nullable=False, server_default="0")


class GurpsCatalogoFichaDesvantagem(Base):
    __tablename__ = "gurps_catalogo_ficha_desvantagens"
    __table_args__ = (UniqueConstraint("nome", name="uq_gurps_cat_ficha_desv_nome"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(512), nullable=False)
    custo = Column(Integer, nullable=True)
    custo_texto = Column(String(255), nullable=True)
    ordem = Column(Integer, nullable=False, server_default="0")


class GurpsCatalogoFichaPericia(Base):
    __tablename__ = "gurps_catalogo_ficha_pericias"
    __table_args__ = (UniqueConstraint("nome", name="uq_gurps_cat_ficha_per_nome"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(512), nullable=False)
    atributo_base = Column(String(16), nullable=False, server_default="dx")
    dificuldade = Column(String(8), nullable=False, server_default="M")
    nt = Column(Boolean, nullable=False, server_default="false")
    ordem = Column(Integer, nullable=False, server_default="0")
