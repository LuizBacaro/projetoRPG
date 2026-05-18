"""Service — catálogo de magias D&D 5e."""

from __future__ import annotations

from typing import Optional

from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.schemas.magia import Dnd5eMagiaClasseItem, Dnd5eMagiaResponse


def _componentes_str(magia) -> str:
    parts = []
    if magia.componentes_verbal:
        parts.append("V")
    if magia.componentes_somatico:
        parts.append("S")
    if magia.componentes_material:
        parts.append("M")
    return ", ".join(parts) if parts else ""


def magia_para_response(magia) -> Dnd5eMagiaResponse:
    classes = [
        Dnd5eMagiaClasseItem(classe_slug=row.classe_slug, nivel=row.nivel)
        for row in (magia.classes_niveis or [])
    ]
    return Dnd5eMagiaResponse(
        id=magia.id,
        slug=magia.slug,
        nome=magia.nome,
        nivel=magia.nivel,
        escola=magia.escola,
        tempo_conjuracao=magia.tempo_conjuracao,
        alcance_texto=magia.alcance_texto,
        duracao=magia.duracao,
        requer_concentracao=bool(magia.requer_concentracao),
        ritual=bool(magia.ritual),
        componentes=_componentes_str(magia),
        dano=magia.dano,
        teste_resistencia=magia.teste_resistencia,
        descricao=magia.descricao,
        descricao_nivel_superior=magia.descricao_nivel_superior,
        classes=classes,
    )


class Dnd5eMagiaService:
    def __init__(self, repository: Dnd5eMagiaRepository):
        self.repository = repository

    def listar(
        self,
        *,
        nome: Optional[str] = None,
        nivel: Optional[int] = None,
        escola: Optional[str] = None,
        classe_slug: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[int, list[Dnd5eMagiaResponse]]:
        total, rows = self.repository.listar_paginado(
            nome=nome,
            nivel=nivel,
            escola=escola,
            classe_slug=classe_slug,
            skip=skip,
            limit=limit,
        )
        return total, [magia_para_response(row) for row in rows]

    def obter(self, magia_id: int) -> Optional[Dnd5eMagiaResponse]:
        row = self.repository.obter(magia_id)
        return magia_para_response(row) if row else None
