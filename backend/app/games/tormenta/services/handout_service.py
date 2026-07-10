"""Regras de negócio — handouts de campanha Tormenta 20 (RF-T12f)."""

from __future__ import annotations

import json
from typing import List, Optional

from app.games.tormenta.models.campanha import TormentaCampanha, TormentaHandout
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.repositories.campanha_repository import (
    TormentaCampanhaRepository,
)
from app.games.tormenta.repositories.handout_repository import TormentaHandoutRepository
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import PerfilUsuario


class TormentaHandoutService:
    def __init__(
        self,
        handout_repository: TormentaHandoutRepository,
        campanha_repository: TormentaCampanhaRepository,
    ):
        self.handout_repository = handout_repository
        self.campanha_repository = campanha_repository

    @staticmethod
    def _anexar_campanha_nome(handout: TormentaHandout) -> None:
        handout.campanha_nome = (
            getattr(getattr(handout, "campanha", None), "nome", "") or ""
        )

    def _campanha_ids_do_usuario(self, usuario_id: int) -> List[int]:
        db = self.handout_repository.db
        return [
            row[0]
            for row in (
                db.query(TormentaPersonagem.campanha_id)
                .filter(TormentaPersonagem.dono_id == usuario_id)
                .filter(TormentaPersonagem.campanha_id.isnot(None))
                .distinct()
                .all()
            )
            if row[0] is not None
        ]

    @staticmethod
    def _usuario_pode_ver(handout: TormentaHandout, usuario_id: int) -> bool:
        ids = handout.visivel_para_user_ids
        if ids is None:
            return False
        if isinstance(ids, str):
            try:
                ids = json.loads(ids)
            except json.JSONDecodeError:
                return False
        if not isinstance(ids, list) or not ids:
            return False
        try:
            alvo = {int(x) for x in ids if int(x) > 0}
        except (TypeError, ValueError):
            return False
        return int(usuario_id) in alvo

    def listar_para_mestre_ou_admin(
        self,
        perfil: PerfilUsuario,
        usuario_id: int,
        campanha_id: Optional[int] = None,
    ) -> List[TormentaHandout]:
        if perfil == PerfilUsuario.ADMINISTRADOR:
            rows = self.handout_repository.listar_todas(campanha_id=campanha_id)
        else:
            rows = self.handout_repository.listar_por_mestre(
                usuario_id, campanha_id=campanha_id
            )
        for row in rows:
            self._anexar_campanha_nome(row)
        return rows

    def listar_visiveis_para_usuario(
        self, usuario_id: int, campanha_id: Optional[int] = None
    ) -> List[TormentaHandout]:
        campanha_ids = self._campanha_ids_do_usuario(usuario_id)
        if not campanha_ids:
            return []
        if campanha_id is not None:
            cid = int(campanha_id)
            if cid not in campanha_ids:
                return []
            campanha_ids = [cid]
        db = self.handout_repository.db
        rows = (
            db.query(TormentaHandout)
            .join(TormentaCampanha, TormentaHandout.campanha_id == TormentaCampanha.id)
            .filter(TormentaHandout.campanha_id.in_(campanha_ids))
            .order_by(
                TormentaHandout.created_at.desc(),
                TormentaHandout.id.desc(),
            )
            .all()
        )
        visiveis = [h for h in rows if self._usuario_pode_ver(h, usuario_id)]
        for row in visiveis:
            self._anexar_campanha_nome(row)
        return visiveis

    def _campanha_para_novo_handout(
        self, campanha_id: int, usuario_id: int, perfil: PerfilUsuario
    ) -> TormentaCampanha:
        if perfil == PerfilUsuario.ADMINISTRADOR:
            campanha = self.campanha_repository.obter_por_id(campanha_id)
        else:
            campanha = self.campanha_repository.obter_por_id_e_mestre(
                campanha_id, usuario_id
            )
        if not campanha:
            raise ArenaBaseException(
                "Campanha nao encontrada para este mestre", status_code=404
            )
        return campanha

    def _handout_gestao(
        self, handout_id: int, usuario_id: int, perfil: PerfilUsuario
    ) -> TormentaHandout:
        if perfil == PerfilUsuario.ADMINISTRADOR:
            handout = self.handout_repository.obter_por_id(handout_id)
        else:
            handout = self.handout_repository.obter_por_id_e_mestre(
                handout_id, usuario_id
            )
        if not handout:
            raise ArenaBaseException("Handout nao encontrado", status_code=404)
        return handout

    def criar(
        self,
        usuario_id: int,
        perfil: PerfilUsuario,
        campanha_id: int,
        titulo: str,
        corpo_md: str = "",
        imagem_url: str | None = None,
        visivel_para_user_ids: Optional[List[int]] = None,
    ) -> TormentaHandout:
        self._campanha_para_novo_handout(campanha_id, usuario_id, perfil)
        titulo_limpo = str(titulo or "").strip()
        if not titulo_limpo:
            raise DadosInvalidos("Titulo do handout e obrigatorio")
        corpo = str(corpo_md or "").strip()
        img = str(imagem_url).strip() if imagem_url else None
        if not corpo and not img:
            raise DadosInvalidos("Informe texto ou URL de imagem para o handout")
        vis = list(visivel_para_user_ids or [])
        handout = self.handout_repository.create(
            TormentaHandout(
                campanha_id=campanha_id,
                titulo=titulo_limpo,
                corpo_md=corpo,
                imagem_url=img or None,
                visivel_para_user_ids=vis,
            )
        )
        self._anexar_campanha_nome(handout)
        return handout

    def atualizar(
        self,
        usuario_id: int,
        perfil: PerfilUsuario,
        handout_id: int,
        titulo: str | None = None,
        corpo_md: str | None = None,
        imagem_url: str | None = None,
        visivel_para_user_ids: List[int] | None = None,
    ) -> TormentaHandout:
        handout = self._handout_gestao(handout_id, usuario_id, perfil)
        if titulo is not None:
            titulo_limpo = str(titulo).strip()
            if not titulo_limpo:
                raise DadosInvalidos("Titulo do handout nao pode ser vazio")
            handout.titulo = titulo_limpo
        if corpo_md is not None:
            handout.corpo_md = str(corpo_md).strip()
        if imagem_url is not None:
            img = str(imagem_url).strip()
            handout.imagem_url = img or None
        if visivel_para_user_ids is not None:
            handout.visivel_para_user_ids = list(visivel_para_user_ids)
        corpo_final = str(handout.corpo_md or "").strip()
        img_final = str(handout.imagem_url or "").strip()
        if not corpo_final and not img_final:
            raise DadosInvalidos("Handout precisa de texto ou imagem")
        atualizado = self.handout_repository.update(handout)
        self._anexar_campanha_nome(atualizado)
        return atualizado

    def deletar(self, usuario_id: int, perfil: PerfilUsuario, handout_id: int) -> None:
        handout = self._handout_gestao(handout_id, usuario_id, perfil)
        self.handout_repository.delete(handout)
