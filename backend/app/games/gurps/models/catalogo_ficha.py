"""Catálogo global da ficha (perícias / vantagens / desvantagens) — opcional; vazio = API usa JSON."""

from sqlalchemy import JSON, Boolean, Column, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from app.shared.core.database import Base

# JSONB no Postgres; JSON genérico em SQLite/testes.
_META_CUSTO_TYPE = JSON().with_variant(JSONB(), "postgresql")


class GurpsCatalogoFichaVantagem(Base):
    __tablename__ = "gurps_catalogo_ficha_vantagens"
    __table_args__ = (UniqueConstraint("nome", name="uq_gurps_cat_ficha_vant_nome"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(512), nullable=False)
    custo = Column(Integer, nullable=True)
    custo_texto = Column(String(255), nullable=True)
    ordem = Column(Integer, nullable=False, server_default="0")
    # Contrato enriquecido (cost_model, opcoes_custo, faixa, autocontrole, etc.).
    # Espelha o item bruto do JSON `gurps_personagens_sumario_catalogo.json`
    # (menos `nome`, `custo`, `custo_texto` que já estão em colunas dedicadas).
    meta_custo = Column(_META_CUSTO_TYPE, nullable=True)


class GurpsCatalogoFichaDesvantagem(Base):
    __tablename__ = "gurps_catalogo_ficha_desvantagens"
    __table_args__ = (UniqueConstraint("nome", name="uq_gurps_cat_ficha_desv_nome"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(512), nullable=False)
    custo = Column(Integer, nullable=True)
    custo_texto = Column(String(255), nullable=True)
    ordem = Column(Integer, nullable=False, server_default="0")
    meta_custo = Column(_META_CUSTO_TYPE, nullable=True)


class GurpsCatalogoFichaPericia(Base):
    __tablename__ = "gurps_catalogo_ficha_pericias"
    __table_args__ = (UniqueConstraint("nome", name="uq_gurps_cat_ficha_per_nome"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(512), nullable=False)
    atributo_base = Column(String(16), nullable=False, server_default="dx")
    dificuldade = Column(String(8), nullable=False, server_default="M")
    nt = Column(Boolean, nullable=False, server_default="false")
    ordem = Column(Integer, nullable=False, server_default="0")
