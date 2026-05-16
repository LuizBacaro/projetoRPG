"""Inventário — consumíveis vinculados ao personagem Tormenta 20."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.models.consumivel import (
    TormentaConsumivel,
    TormentaConsumivelPersonagem,
)
from app.games.tormenta.schemas.consumivel_personagem import (
    TormentaConsumivelPersonagemItem,
    TormentaConsumivelVinculoCreate,
    TormentaConsumivelVinculoPatch,
    TormentaMigrarConsumiveisJsonResponse,
)
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos


class TormentaPersonagemConsumiveisService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_item(row: TormentaConsumivelPersonagem) -> TormentaConsumivelPersonagemItem:
        c = row.consumivel
        return TormentaConsumivelPersonagemItem(
            id=row.id,
            consumivel_id=row.consumivel_id,
            nome=c.nome,
            categoria=c.categoria,
            quantidade=int(row.quantidade or 1),
            notas=row.notas,
            adicionado_em=row.adicionado_em,
        )

    def listar_por_personagem(
        self, personagem_id: int
    ) -> List[TormentaConsumivelPersonagemItem]:
        rows = (
            self.db.query(TormentaConsumivelPersonagem)
            .filter(TormentaConsumivelPersonagem.personagem_id == personagem_id)
            .order_by(TormentaConsumivelPersonagem.adicionado_em.asc())
            .all()
        )
        return [self._to_item(r) for r in rows]

    def _buscar_consum_por_nome_ci(self, nome: str) -> Optional[TormentaConsumivel]:
        n = nome.strip()
        if not n:
            return None
        return (
            self.db.query(TormentaConsumivel)
            .filter(func.lower(TormentaConsumivel.nome) == func.lower(n))
            .first()
        )

    def _buscar_ou_criar_por_nome(self, nome: str) -> TormentaConsumivel:
        n = str(nome or "").strip()[:200]
        if len(n) < 2:
            raise DadosInvalidos("Nome do consumivel deve ter pelo menos 2 caracteres")
        exist = self._buscar_consum_por_nome_ci(n)
        if exist:
            return exist
        c = TormentaConsumivel(nome=n, origem_catalogo_mb=False)
        self.db.add(c)
        self.db.flush()
        return c

    def adicionar_vinculo(
        self, personagem_id: int, payload: TormentaConsumivelVinculoCreate
    ) -> TormentaConsumivelPersonagemItem:
        if payload.consumivel_id is not None:
            c = self.db.get(TormentaConsumivel, payload.consumivel_id)
            if not c:
                raise DadosInvalidos("Consumivel nao encontrado no catalogo")
        else:
            c = self._buscar_ou_criar_por_nome(payload.nome or "")

        dup = (
            self.db.query(TormentaConsumivelPersonagem)
            .filter(
                TormentaConsumivelPersonagem.personagem_id == personagem_id,
                TormentaConsumivelPersonagem.consumivel_id == c.id,
            )
            .first()
        )
        if dup:
            raise ArenaBaseException(
                "Este consumivel ja esta no inventario do personagem",
                status_code=409,
            )

        v = TormentaConsumivelPersonagem(
            personagem_id=personagem_id,
            consumivel_id=c.id,
            quantidade=int(payload.quantidade or 1),
            notas=(payload.notas or "").strip() or None,
        )
        self.db.add(v)
        commit_with_rollback(self.db)
        self.db.refresh(v)
        return self._to_item(v)

    def atualizar_quantidade(
        self,
        personagem_id: int,
        vinculo_id: int,
        payload: TormentaConsumivelVinculoPatch,
    ) -> TormentaConsumivelPersonagemItem:
        row = self.db.get(TormentaConsumivelPersonagem, vinculo_id)
        if not row or row.personagem_id != personagem_id:
            raise ArenaBaseException("Vinculo nao encontrado", status_code=404)
        row.quantidade = int(payload.quantidade)
        commit_with_rollback(self.db)
        self.db.refresh(row)
        return self._to_item(row)

    def remover_vinculo(self, personagem_id: int, vinculo_id: int) -> None:
        row = self.db.get(TormentaConsumivelPersonagem, vinculo_id)
        if not row or row.personagem_id != personagem_id:
            raise ArenaBaseException("Vinculo nao encontrado", status_code=404)
        self.db.delete(row)
        commit_with_rollback(self.db)

    def migrar_consumiveis_do_json(
        self, personagem_id: int
    ) -> TormentaMigrarConsumiveisJsonResponse:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        fj = p.ficha_json or {}
        raw = fj.get("consumiveis")
        if raw is None:
            raw = fj.get("consumiveis_lista")
        if not isinstance(raw, list):
            return TormentaMigrarConsumiveisJsonResponse(
                vinculos_criados=0, ignorados_duplicados=0
            )

        criados = 0
        dup = 0
        vistos: set[int] = set()
        for item in raw:
            if isinstance(item, str):
                nome = item.strip()
                qtd = 1
            elif isinstance(item, dict):
                nome = str(item.get("nome", item.get("item", ""))).strip()
                try:
                    qtd = int(
                        str(item.get("qtd", item.get("quantidade", "1")))
                        .replace(",", ".")
                        .split(".")[0]
                    )
                except (TypeError, ValueError):
                    qtd = 1
            else:
                continue
            if len(nome) < 2:
                continue
            qtd = max(1, min(9999, qtd))
            c = self._buscar_ou_criar_por_nome(nome)
            if c.id in vistos:
                dup += 1
                continue
            exist = (
                self.db.query(TormentaConsumivelPersonagem)
                .filter(
                    TormentaConsumivelPersonagem.personagem_id == personagem_id,
                    TormentaConsumivelPersonagem.consumivel_id == c.id,
                )
                .first()
            )
            if exist:
                dup += 1
                continue
            self.db.add(
                TormentaConsumivelPersonagem(
                    personagem_id=personagem_id,
                    consumivel_id=c.id,
                    quantidade=qtd,
                    notas=None,
                )
            )
            vistos.add(c.id)
            criados += 1
            self.db.flush()
        if criados:
            commit_with_rollback(self.db)
        return TormentaMigrarConsumiveisJsonResponse(
            vinculos_criados=criados,
            ignorados_duplicados=dup,
        )
