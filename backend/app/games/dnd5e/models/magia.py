"""Catálogo de magias D&D 5e (PHB) — tabelas `dnd5e_magias` e `dnd5e_magias_classes`."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class Dnd5eMagia(Base):
    """Magia do livro base 5e — metadados para grimório e conjuração."""

    __tablename__ = "dnd5e_magias"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(120), nullable=False, unique=True, index=True)
    nome = Column(String(160), nullable=False, index=True)
    nome_en = Column(String(160), nullable=True, index=True)
    nivel = Column(Integer, nullable=False, index=True)  # 0 = truque
    escola = Column(String(40), nullable=True, index=True)

    tempo_conjuracao = Column(String(60), nullable=True)
    alcance_texto = Column(String(80), nullable=True)
    alcance_metros = Column(Integer, nullable=True)
    duracao = Column(String(120), nullable=True)
    requer_concentracao = Column(Boolean, nullable=False, default=False)
    ritual = Column(Boolean, nullable=False, default=False)

    componentes_verbal = Column(Boolean, nullable=False, default=False)
    componentes_somatico = Column(Boolean, nullable=False, default=False)
    componentes_material = Column(Text, nullable=True)
    material_consumido = Column(Boolean, nullable=False, default=False)
    material_custo_gp = Column(Integer, nullable=False, default=0)

    dano = Column(String(80), nullable=True)
    teste_resistencia = Column(String(40), nullable=True)  # for/dex/con/int/wis/cha/nenhum
    ataque_magico = Column(String(20), nullable=True)  # ranged | melee | None
    descricao = Column(Text, nullable=True)
    descricao_en = Column(Text, nullable=True)
    descricao_nivel_superior = Column(Text, nullable=True)

    pagina_referencia = Column(Integer, nullable=True)
    ativo = Column(Boolean, nullable=False, default=True)
    criado_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    classes_niveis = relationship(
        "Dnd5eMagiaClasse",
        back_populates="magia",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Dnd5eMagiaClasse(Base):
    """Quais classes podem aprender a magia (lista por classe)."""

    __tablename__ = "dnd5e_magias_classes"
    __table_args__ = (
        UniqueConstraint(
            "magia_id", "classe_slug", name="uq_dnd5e_magias_classes_magia_classe"
        ),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    magia_id = Column(
        Integer,
        ForeignKey("dnd5e_magias.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    classe_slug = Column(String(40), nullable=False, index=True)
    nivel = Column(Integer, nullable=False)

    magia = relationship("Dnd5eMagia", back_populates="classes_niveis")
