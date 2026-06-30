"""Inventário — equipamentos vinculados ao personagem Tormenta 20."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.games.tormenta.models.equipamento import (
    TormentaEquipamento,
    TormentaEquipamentoPersonagem,
)
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.schemas.equipamento_personagem import (
    TormentaEquipamentoPersonagemItem,
    TormentaEquipamentoVinculoCreate,
    TormentaEquipamentoVinculoPatch,
    TormentaMigrarEquipJsonResponse,
)
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos


class TormentaPersonagemEquipamentosService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_item(
        row: TormentaEquipamentoPersonagem,
    ) -> TormentaEquipamentoPersonagemItem:
        e = row.equipamento
        return TormentaEquipamentoPersonagemItem(
            id=row.id,
            equipamento_id=row.equipamento_id,
            nome=e.nome,
            categoria=e.categoria,
            quantidade=int(row.quantidade or 1),
            notas=row.notas,
            adicionado_em=row.adicionado_em,
        )

    def listar_por_personagem(
        self, personagem_id: int
    ) -> List[TormentaEquipamentoPersonagemItem]:
        rows = (
            self.db.query(TormentaEquipamentoPersonagem)
            .filter(TormentaEquipamentoPersonagem.personagem_id == personagem_id)
            .order_by(TormentaEquipamentoPersonagem.adicionado_em.asc())
            .all()
        )
        return [self._to_item(r) for r in rows]

    def _buscar_equip_por_nome_ci(self, nome: str) -> Optional[TormentaEquipamento]:
        n = nome.strip()
        if not n:
            return None
        return (
            self.db.query(TormentaEquipamento)
            .filter(func.lower(TormentaEquipamento.nome) == func.lower(n))
            .first()
        )

    def _buscar_ou_criar_equip_por_nome(self, nome_bruto: str) -> TormentaEquipamento:
        base = str(nome_bruto or "").strip()
        if " — " in base:
            base = base.split(" — ", 1)[0].strip()
        n = base[:200]
        if len(n) < 1:
            raise DadosInvalidos("Nome do equipamento invalido")
        exist = self._buscar_equip_por_nome_ci(n)
        if exist:
            return exist
        e = TormentaEquipamento(
            nome=n,
            origem_catalogo_mb=False,
        )
        self.db.add(e)
        self.db.flush()
        return e

    def adicionar_vinculo(
        self, personagem_id: int, payload: TormentaEquipamentoVinculoCreate
    ) -> TormentaEquipamentoPersonagemItem:
        if payload.equipamento_id is not None:
            e = self.db.get(TormentaEquipamento, payload.equipamento_id)
            if not e:
                raise DadosInvalidos("Equipamento nao encontrado no catalogo")
        else:
            e = self._buscar_ou_criar_equip_por_nome(payload.nome or "")

        dup = (
            self.db.query(TormentaEquipamentoPersonagem)
            .filter(
                TormentaEquipamentoPersonagem.personagem_id == personagem_id,
                TormentaEquipamentoPersonagem.equipamento_id == e.id,
            )
            .first()
        )
        if dup:
            raise ArenaBaseException(
                "Este equipamento ja esta no inventario do personagem",
                status_code=409,
            )

        v = TormentaEquipamentoPersonagem(
            personagem_id=personagem_id,
            equipamento_id=e.id,
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
        payload: TormentaEquipamentoVinculoPatch,
    ) -> TormentaEquipamentoPersonagemItem:
        row = self.db.get(TormentaEquipamentoPersonagem, vinculo_id)
        if not row or row.personagem_id != personagem_id:
            raise ArenaBaseException("Vinculo nao encontrado", status_code=404)
        row.quantidade = int(payload.quantidade)
        commit_with_rollback(self.db)
        self.db.refresh(row)
        return self._to_item(row)

    def remover_vinculo(self, personagem_id: int, vinculo_id: int) -> None:
        row = self.db.get(TormentaEquipamentoPersonagem, vinculo_id)
        if not row or row.personagem_id != personagem_id:
            raise ArenaBaseException("Vinculo nao encontrado", status_code=404)
        self.db.delete(row)
        commit_with_rollback(self.db)

    def migrar_equipamentos_do_json(
        self, personagem_id: int
    ) -> TormentaMigrarEquipJsonResponse:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        raw = (p.ficha_json or {}).get("equipamentos")
        if not isinstance(raw, list):
            return TormentaMigrarEquipJsonResponse(
                vinculos_criados=0, ignorados_duplicados=0
            )

        criados = 0
        dup = 0
        vistos: set[int] = set()
        for item in raw:
            if not isinstance(item, dict):
                continue
            nome_bruto = str(item.get("item", "")).strip()
            if not nome_bruto:
                continue
            try:
                qtd = int(str(item.get("qtd", "1")).replace(",", ".").split(".")[0])
            except (TypeError, ValueError):
                qtd = 1
            qtd = max(1, min(9999, qtd))
            e = self._buscar_ou_criar_equip_por_nome(nome_bruto)
            if e.id in vistos:
                dup += 1
                continue
            exist = (
                self.db.query(TormentaEquipamentoPersonagem)
                .filter(
                    TormentaEquipamentoPersonagem.personagem_id == personagem_id,
                    TormentaEquipamentoPersonagem.equipamento_id == e.id,
                )
                .first()
            )
            if exist:
                dup += 1
                continue
            self.db.add(
                TormentaEquipamentoPersonagem(
                    personagem_id=personagem_id,
                    equipamento_id=e.id,
                    quantidade=qtd,
                    notas=None,
                )
            )
            vistos.add(e.id)
            criados += 1
            self.db.flush()
        if criados:
            commit_with_rollback(self.db)
        return TormentaMigrarEquipJsonResponse(
            vinculos_criados=criados,
            ignorados_duplicados=dup,
        )

    def sincronizar_equipamentos_automaticos_v13(
        self, personagem_id: int, ficha_json: dict
    ) -> dict:
        """Garante vínculos SQL para itens de origem e kit inicial v1.3."""
        from app.games.tormenta.rules.equipamentos_ficha_v13_t20 import (
            AUTO_EQUIP_NOTA_PREFIX,
            listar_equipamentos_sync_v13,
        )

        desejados = listar_equipamentos_sync_v13(ficha_json)
        desejados_notas = {e["notas"] for e in desejados}

        rows = (
            self.db.query(TormentaEquipamentoPersonagem)
            .filter(TormentaEquipamentoPersonagem.personagem_id == personagem_id)
            .all()
        )

        removidos = 0
        for row in rows:
            nota = (row.notas or "").strip()
            if nota.startswith(AUTO_EQUIP_NOTA_PREFIX) and nota not in desejados_notas:
                self.db.delete(row)
                removidos += 1

        if removidos:
            self.db.flush()

        existentes = (
            self.db.query(TormentaEquipamentoPersonagem)
            .filter(TormentaEquipamentoPersonagem.personagem_id == personagem_id)
            .all()
        )
        vinculados_equip_ids = {r.equipamento_id for r in existentes}
        notas_existentes = {
            (r.notas or "").strip() for r in existentes if (r.notas or "").strip()
        }

        criados = 0
        for item in desejados:
            nota = item["notas"]
            if nota in notas_existentes:
                continue
            nome = str(item.get("nome") or "").strip()
            if not nome:
                continue
            e = self._buscar_ou_criar_equip_por_nome(nome)
            if e.id in vinculados_equip_ids:
                continue
            qtd = int(item.get("quantidade") or 1)
            self.db.add(
                TormentaEquipamentoPersonagem(
                    personagem_id=personagem_id,
                    equipamento_id=e.id,
                    quantidade=max(1, min(9999, qtd)),
                    notas=nota,
                )
            )
            vinculados_equip_ids.add(e.id)
            criados += 1

        if criados or removidos:
            commit_with_rollback(self.db)

        return {"vinculos_criados": criados, "vinculos_removidos": removidos}
