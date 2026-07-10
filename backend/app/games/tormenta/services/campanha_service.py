"""Regras de negócio — campanhas Tormenta 20."""

from __future__ import annotations

import secrets
from typing import List

from app.games.tormenta.models.campanha import TormentaCampanha
from app.games.tormenta.repositories.campanha_repository import (
    TormentaCampanhaRepository,
)
from app.games.tormenta.repositories.personagem_repository import (
    TormentaPersonagemRepository,
)
from app.games.tormenta.schemas.campanha_convite import (
    TormentaCampanhaConviteStatusResponse,
)
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import PerfilUsuario


class TormentaCampanhaService:
    def __init__(
        self,
        campanha_repository: TormentaCampanhaRepository,
        personagem_repository: TormentaPersonagemRepository,
    ):
        self.campanha_repository = campanha_repository
        self.personagem_repository = personagem_repository

    def listar_por_mestre(self, mestre_id: int) -> List[TormentaCampanha]:
        campanhas = self.campanha_repository.listar_por_mestre(mestre_id)
        for c in campanhas:
            c.total_personagens = len(c.personagens or [])
            c.personagem_ids = [p.id for p in (c.personagens or [])]
        return campanhas

    def listar_para_mestre_ou_admin(
        self, perfil: PerfilUsuario, usuario_id: int
    ) -> List[TormentaCampanha]:
        if perfil == PerfilUsuario.ADMINISTRADOR:
            campanhas = self.campanha_repository.listar_todas()
        else:
            campanhas = self.campanha_repository.listar_por_mestre(usuario_id)
        for c in campanhas:
            c.total_personagens = len(c.personagens or [])
            c.personagem_ids = [p.id for p in (c.personagens or [])]
        return campanhas

    def _campanha_gestao(
        self, campanha_id: int, usuario_id: int, perfil: PerfilUsuario
    ) -> TormentaCampanha:
        if perfil == PerfilUsuario.ADMINISTRADOR:
            campanha = self.campanha_repository.obter_por_id(campanha_id)
        else:
            campanha = self.campanha_repository.obter_por_id_e_mestre(
                campanha_id, usuario_id
            )
        if not campanha:
            raise ArenaBaseException("Campanha nao encontrada", status_code=404)
        return campanha

    def criar(
        self,
        mestre_id: int,
        nome: str,
        descricao: str = "",
        personagem_ids: List[int] | None = None,
    ) -> TormentaCampanha:
        nome_limpo = str(nome or "").strip()
        if not nome_limpo:
            raise DadosInvalidos("Nome da campanha e obrigatorio")

        entidade = TormentaCampanha(
            mestre_id=mestre_id,
            nome=nome_limpo,
            descricao=str(descricao or "").strip(),
        )
        criada = self.campanha_repository.create(entidade)
        if personagem_ids:
            self._associar_personagens(criada.id, personagem_ids)
            criada = self.obter_por_id_mestre(criada.id, mestre_id)
        criada.total_personagens = len(criada.personagens or [])
        criada.personagem_ids = [p.id for p in (criada.personagens or [])]
        return criada

    def obter_por_id_mestre(self, campanha_id: int, mestre_id: int) -> TormentaCampanha:
        campanha = self.campanha_repository.obter_por_id_e_mestre(
            campanha_id, mestre_id
        )
        if not campanha:
            raise ArenaBaseException("Campanha nao encontrada", status_code=404)
        return campanha

    def atualizar(
        self,
        campanha_id: int,
        usuario_id: int,
        perfil: PerfilUsuario,
        nome: str | None = None,
        descricao: str | None = None,
        personagem_ids: List[int] | None = None,
    ) -> TormentaCampanha:
        campanha = self._campanha_gestao(campanha_id, usuario_id, perfil)
        if nome is not None:
            nome_limpo = str(nome).strip()
            if not nome_limpo:
                raise DadosInvalidos("Nome da campanha nao pode ser vazio")
            campanha.nome = nome_limpo
        if descricao is not None:
            campanha.descricao = str(descricao).strip()

        if personagem_ids is not None:
            self._substituir_personagens(
                campanha.id, usuario_id, perfil, personagem_ids
            )

        atualizada = self.campanha_repository.update(campanha)
        atualizada.total_personagens = len(atualizada.personagens or [])
        atualizada.personagem_ids = [p.id for p in (atualizada.personagens or [])]
        return atualizada

    def deletar(self, campanha_id: int, usuario_id: int, perfil: PerfilUsuario) -> None:
        campanha = self._campanha_gestao(campanha_id, usuario_id, perfil)
        for personagem in campanha.personagens or []:
            personagem.campanha_id = None
        commit_with_rollback(self.campanha_repository.db)
        self.campanha_repository.delete_hard(campanha)

    def associar_personagens(
        self,
        campanha_id: int,
        usuario_id: int,
        perfil: PerfilUsuario,
        personagem_ids: List[int],
    ) -> TormentaCampanha:
        self._campanha_gestao(campanha_id, usuario_id, perfil)
        self._associar_personagens(campanha_id, personagem_ids)
        campanha = self._campanha_gestao(campanha_id, usuario_id, perfil)
        campanha.total_personagens = len(campanha.personagens or [])
        campanha.personagem_ids = [p.id for p in (campanha.personagens or [])]
        return campanha

    def _substituir_personagens(
        self,
        campanha_id: int,
        usuario_id: int,
        perfil: PerfilUsuario,
        personagem_ids: List[int],
    ) -> None:
        campanha = self._campanha_gestao(campanha_id, usuario_id, perfil)
        atuais = list(campanha.personagens or [])
        ids_novos = set(personagem_ids or [])
        for personagem in atuais:
            if personagem.id not in ids_novos:
                personagem.campanha_id = None
        self._associar_personagens(campanha_id, personagem_ids or [], commit=False)
        commit_with_rollback(self.campanha_repository.db)

    def _associar_personagens(
        self,
        campanha_id: int,
        personagem_ids: List[int],
        commit: bool = True,
    ) -> None:
        ids = list(
            dict.fromkeys([int(pid) for pid in (personagem_ids or []) if int(pid) > 0])
        )
        if not ids:
            if commit:
                commit_with_rollback(self.campanha_repository.db)
            return

        personagens = self.personagem_repository.get_by_ids(ids)
        if len(personagens) != len(ids):
            raise ArenaBaseException(
                "Alguns personagens nao foram encontrados", status_code=404
            )
        tipos_permitidos = {"jogador", "monstro", "npc"}
        invalidos = [
            p.nome
            for p in personagens
            if str((p.tipo or "")).lower() not in tipos_permitidos
        ]
        if invalidos:
            raise ArenaBaseException(
                "Tipos de personagem invalidos para campanha",
                status_code=422,
            )

        for personagem in personagens:
            personagem.campanha_id = campanha_id
        if commit:
            commit_with_rollback(self.campanha_repository.db)

    @staticmethod
    def _url_path_convite(token: str) -> str:
        return f"dashboard.html?convite={token}"

    def obter_status_convite(
        self, campanha_id: int, usuario_id: int, perfil: PerfilUsuario
    ) -> TormentaCampanhaConviteStatusResponse:
        campanha = self._campanha_gestao(campanha_id, usuario_id, perfil)
        token = campanha.convite_token if campanha.convite_ativo else None
        return TormentaCampanhaConviteStatusResponse(
            campanha_id=campanha.id,
            ativo=bool(campanha.convite_ativo and campanha.convite_token),
            token=token,
            url_path=self._url_path_convite(token) if token else None,
        )

    def gerar_convite(
        self, campanha_id: int, usuario_id: int, perfil: PerfilUsuario
    ) -> TormentaCampanhaConviteStatusResponse:
        campanha = self._campanha_gestao(campanha_id, usuario_id, perfil)
        for _ in range(8):
            token = secrets.token_urlsafe(32)
            existente = self.campanha_repository.obter_por_convite_token(token)
            if existente and existente.id != campanha.id:
                continue
            campanha.convite_token = token
            campanha.convite_ativo = True
            self.campanha_repository.update(campanha)
            return TormentaCampanhaConviteStatusResponse(
                campanha_id=campanha.id,
                ativo=True,
                token=token,
                url_path=self._url_path_convite(token),
            )
        raise ArenaBaseException(
            "Nao foi possivel gerar token de convite", status_code=500
        )

    def revogar_convite(
        self, campanha_id: int, usuario_id: int, perfil: PerfilUsuario
    ) -> TormentaCampanhaConviteStatusResponse:
        campanha = self._campanha_gestao(campanha_id, usuario_id, perfil)
        campanha.convite_ativo = False
        self.campanha_repository.update(campanha)
        return TormentaCampanhaConviteStatusResponse(
            campanha_id=campanha.id,
            ativo=False,
            token=None,
            url_path=None,
        )
