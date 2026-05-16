"""Regras de negócio — magias MB vinculadas ao personagem (grimório / conhecidas / preparadas)."""

from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.games.tormenta.models.magia_personagem import TormentaMagiaPersonagem
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.rules.catalogo_t20 import (
    magia_mb_slug_no_catalogo,
    metadados_magia_mb_por_slug,
)
from app.games.tormenta.rules.grimorio_elegibilidade_t20 import (
    resumo_elegibilidade_grimorio_mb,
)
from app.games.tormenta.schemas.magia_personagem import (
    TormentaMagiaPersonagemItem,
    TormentaMagiaVinculoCreate,
)
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos

_PAPEIS = frozenset({"grimorio", "conhecida", "preparada"})


class TormentaPersonagemMagiasService:
    """Vínculos `tormenta_magias_personagem` + validação contra catálogo JSON MB."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_item(row: TormentaMagiaPersonagem) -> TormentaMagiaPersonagemItem:
        meta = metadados_magia_mb_por_slug(row.magia_slug)
        nome = str(meta["nome"]) if meta and meta.get("nome") else None
        circulo = (
            int(meta["circulo"]) if meta and meta.get("circulo") is not None else None
        )
        tipo = str(meta["tipo"]) if meta and meta.get("tipo") else None
        escola = str(meta["escola"]) if meta and meta.get("escola") else None
        return TormentaMagiaPersonagemItem(
            id=row.id,
            magia_slug=row.magia_slug,
            papel=row.papel,
            nome=nome,
            circulo=circulo,
            tipo=tipo,
            escola=escola,
            notas=row.notas,
            adicionado_em=row.adicionado_em,
        )

    def listar_por_personagem(
        self, personagem_id: int
    ) -> List[TormentaMagiaPersonagemItem]:
        rows = (
            self.db.query(TormentaMagiaPersonagem)
            .filter(TormentaMagiaPersonagem.personagem_id == personagem_id)
            .order_by(
                TormentaMagiaPersonagem.papel.asc(),
                TormentaMagiaPersonagem.adicionado_em.asc(),
            )
            .all()
        )
        return [self._to_item(r) for r in rows]

    def adicionar_vinculo(
        self, personagem_id: int, payload: TormentaMagiaVinculoCreate
    ) -> TormentaMagiaPersonagemItem:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)

        ok_g, motivo_g = resumo_elegibilidade_grimorio_mb(
            tipo=str(p.tipo or ""),
            nivel=int(p.nivel or 1),
            ficha_json=p.ficha_json if isinstance(p.ficha_json, dict) else {},
        )
        if not ok_g:
            raise DadosInvalidos(motivo_g)

        slug = str(payload.magia_slug or "").strip().lower()[:80]
        if len(slug) < 2:
            raise DadosInvalidos("magia_slug invalido")
        if not magia_mb_slug_no_catalogo(slug):
            raise DadosInvalidos(
                "Magia nao encontrada no catalogo MB (slug desconhecido)"
            )

        papel = str(payload.papel or "").strip().lower()
        if papel not in _PAPEIS:
            raise DadosInvalidos("papel deve ser grimorio, conhecida ou preparada")

        dup = (
            self.db.query(TormentaMagiaPersonagem)
            .filter(
                TormentaMagiaPersonagem.personagem_id == personagem_id,
                TormentaMagiaPersonagem.magia_slug == slug,
                TormentaMagiaPersonagem.papel == papel,
            )
            .first()
        )
        if dup:
            raise ArenaBaseException(
                "Esta magia ja esta vinculada ao personagem com o mesmo papel",
                status_code=409,
            )

        v = TormentaMagiaPersonagem(
            personagem_id=personagem_id,
            magia_slug=slug,
            papel=papel,
            notas=(payload.notas or "").strip() or None,
        )
        self.db.add(v)
        commit_with_rollback(self.db)
        self.db.refresh(v)
        return self._to_item(v)

    def remover_vinculo(self, personagem_id: int, vinculo_id: int) -> None:
        row = self.db.get(TormentaMagiaPersonagem, vinculo_id)
        if not row or row.personagem_id != personagem_id:
            raise ArenaBaseException("Vinculo nao encontrado", status_code=404)
        self.db.delete(row)
        commit_with_rollback(self.db)
