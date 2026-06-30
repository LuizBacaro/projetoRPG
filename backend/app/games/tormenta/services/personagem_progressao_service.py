"""Subir de nível MB — preview e aplicação na ficha."""

from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.repositories.personagem_repository import (
    TormentaPersonagemRepository,
)
from app.games.tormenta.rules.classes_t20 import classe_por_slug, lista_classes_mb
from app.games.tormenta.rules.progressao_subir_nivel_t20 import (
    preview_subir_nivel_mb,
    preview_subir_nivel_v13,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)
from app.games.tormenta.schemas.personagem import TormentaPersonagemResponse
from app.games.tormenta.schemas.progressao import (
    TormentaSubirNivelAplicarRequest,
    TormentaSubirNivelAplicarResponse,
    TormentaSubirNivelPreviewResponse,
)
from app.games.tormenta.services.personagem_service import TormentaPersonagemService
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos


class TormentaPersonagemProgressaoService:
    def __init__(self, db: Session):
        self.db = db
        self._personagem_svc = TormentaPersonagemService(
            TormentaPersonagemRepository(db)
        )

    def _personagem(self, personagem_id: int) -> TormentaPersonagem:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        return p

    def _classe_alvo(self, fj: Dict[str, Any], classe_slug: Optional[str]) -> str:
        slug = (
            str(classe_slug or fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        )
        return slug

    def _preview_dict(
        self,
        p: TormentaPersonagem,
        nivel_alvo: int,
        *,
        classe_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        fj = p.ficha_json if isinstance(p.ficha_json, dict) else {}
        rv = regra_versao_de_ficha(fj)
        attrs = dict(
            ficha_json=fj,
            for_valor=int(p.for_valor or 10),
            des_valor=int(p.des_valor or 10),
            con_valor=int(p.con_valor or 10),
            int_valor=int(p.int_valor or 10),
            sab_valor=int(p.sab_valor or 10),
            car_valor=int(p.car_valor or 10),
            pv_max_atual=int(p.pv_max) if p.pv_max is not None else None,
            pa_max_atual=int(p.pa_max) if p.pa_max is not None else None,
        )
        if rv == REGRA_VERSAO_V13:
            slug = self._classe_alvo(fj, classe_slug)
            return preview_subir_nivel_v13(
                nivel_personagem=int(p.nivel or 1),
                classe_alvo_slug=slug,
                **attrs,
            )
        slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        return preview_subir_nivel_mb(
            nivel_atual=int(p.nivel or 1),
            nivel_alvo=nivel_alvo,
            slug_classe=slug,
            **attrs,
        )

    def preview_subir_nivel(
        self,
        personagem_id: int,
        nivel_alvo: int,
        *,
        classe_slug: Optional[str] = None,
    ) -> TormentaSubirNivelPreviewResponse:
        p = self._personagem(personagem_id)
        if str(p.tipo or "").strip().lower() != "jogador":
            raise DadosInvalidos(
                "Subir nivel MB disponivel apenas para personagens jogador."
            )
        data = self._preview_dict(p, nivel_alvo, classe_slug=classe_slug)
        return TormentaSubirNivelPreviewResponse(**data)

    @staticmethod
    def _formatar_classe_nivel(linhas: list) -> str:
        partes: list[str] = []
        for item in linhas:
            if not isinstance(item, dict):
                continue
            slug = str(item.get("slug") or "").strip().lower()
            try:
                nv = int(item.get("nivel", 0))
            except (TypeError, ValueError):
                continue
            if not slug or nv < 1:
                continue
            nome = slug
            row = classe_por_slug(slug, REGRA_VERSAO_V13)
            if row:
                nome = str(row.get("nome", slug) or slug)
            partes.append(f"{nome} {nv}")
        return " / ".join(partes)

    def aplicar_subir_nivel(
        self,
        personagem_id: int,
        payload: TormentaSubirNivelAplicarRequest,
    ) -> TormentaSubirNivelAplicarResponse:
        p = self._personagem(personagem_id)
        if str(p.tipo or "").strip().lower() != "jogador":
            raise DadosInvalidos(
                "Subir nivel MB disponivel apenas para personagens jogador."
            )
        fj = dict(p.ficha_json or {})
        rv = regra_versao_de_ficha(fj)
        nv_alvo = int(p.nivel or 1) + 1
        data = self._preview_dict(p, nv_alvo, classe_slug=payload.classe_slug)
        prev = TormentaSubirNivelPreviewResponse(**data)
        if not prev.permitido:
            raise DadosInvalidos(prev.motivo or "Nao foi possivel subir de nivel.")

        p.nivel = int(prev.nivel_alvo)
        if prev.pv_max_novo is not None:
            p.pv_max = int(prev.pv_max_novo)
            cur_pv = int(p.pv_atual or 0)
            if payload.aplicar_ganhos_vida and prev.pv_ganho:
                p.pv_atual = min(cur_pv + int(prev.pv_ganho), int(prev.pv_max_novo))
            else:
                p.pv_atual = min(cur_pv, int(prev.pv_max_novo))

        if rv == REGRA_VERSAO_V13 and prev.multiclasse_v13_novo:
            fj["multiclasse_v13"] = prev.multiclasse_v13_novo
            p.classe_nivel = self._formatar_classe_nivel(prev.multiclasse_v13_novo)
        else:
            slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
            if slug:
                nome_cls = slug
                for row in lista_classes_mb():
                    if str(row.get("slug", "")).strip().lower() == slug:
                        nome_cls = str(row.get("nome", slug) or slug)
                        break
                p.classe_nivel = f"{nome_cls} {p.nivel}"

        if prev.habilidade_classe:
            fj["habilidade_classe_mb"] = prev.habilidade_classe
        p.ficha_json = fj

        self._personagem_svc._sincronizar_pontos_magia_mb(p)
        if p.pv_max is not None and p.pv_atual is not None:
            p.pv_atual = min(int(p.pv_atual), int(p.pv_max))
        if p.pa_max is not None and p.pa_atual is not None:
            p.pa_atual = min(int(p.pa_atual), int(p.pa_max))

        commit_with_rollback(self.db)
        self.db.refresh(p)
        return TormentaSubirNivelAplicarResponse(
            preview=prev,
            personagem=TormentaPersonagemResponse.model_validate(p),
        )
