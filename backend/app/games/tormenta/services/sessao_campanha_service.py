"""Regras de negócio — sessões de campanha Tormenta 20."""

from typing import List

from app.games.tormenta.models.campanha import TormentaCampanha, TormentaSessaoCampanha
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.repositories.campanha_repository import TormentaCampanhaRepository
from app.games.tormenta.repositories.sessao_campanha_repository import (
    TormentaSessaoCampanhaRepository,
)
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import PerfilUsuario


class TormentaSessaoCampanhaService:
    def __init__(
        self,
        sessao_repository: TormentaSessaoCampanhaRepository,
        campanha_repository: TormentaCampanhaRepository,
    ):
        self.sessao_repository = sessao_repository
        self.campanha_repository = campanha_repository

    def listar_para_mestre_ou_admin(
        self, perfil: PerfilUsuario, usuario_id: int
    ) -> List[TormentaSessaoCampanha]:
        if perfil == PerfilUsuario.ADMINISTRADOR:
            sessoes = self.sessao_repository.listar_todas()
        else:
            sessoes = self.sessao_repository.listar_por_mestre(usuario_id)
        for sessao in sessoes:
            sessao.campanha_nome = (
                getattr(getattr(sessao, "campanha", None), "nome", "") or ""
            )
        return sessoes

    def listar_visiveis_para_usuario(
        self, usuario_id: int
    ) -> List[TormentaSessaoCampanha]:
        db = self.sessao_repository.db
        campanha_ids = [
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
        if not campanha_ids:
            return []
        sessoes = (
            db.query(TormentaSessaoCampanha)
            .join(
                TormentaCampanha,
                TormentaSessaoCampanha.campanha_id == TormentaCampanha.id,
            )
            .filter(TormentaSessaoCampanha.campanha_id.in_(campanha_ids))
            .filter(TormentaSessaoCampanha.visivel_jogadores.is_(True))
            .order_by(
                TormentaSessaoCampanha.created_at.desc(),
                TormentaSessaoCampanha.id.desc(),
            )
            .all()
        )
        for sessao in sessoes:
            sessao.campanha_nome = (
                getattr(getattr(sessao, "campanha", None), "nome", "") or ""
            )
        return sessoes

    def _campanha_para_nova_sessao(
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

    def _sessao_gestao(
        self, sessao_id: int, usuario_id: int, perfil: PerfilUsuario
    ) -> TormentaSessaoCampanha:
        if perfil == PerfilUsuario.ADMINISTRADOR:
            sessao = self.sessao_repository.obter_por_id(sessao_id)
        else:
            sessao = self.sessao_repository.obter_por_id_e_mestre(
                sessao_id, usuario_id
            )
        if not sessao:
            raise ArenaBaseException("Sessao nao encontrada", status_code=404)
        return sessao

    def criar(
        self,
        usuario_id: int,
        perfil: PerfilUsuario,
        campanha_id: int,
        resumo: str,
        visivel_jogadores: bool = False,
    ) -> TormentaSessaoCampanha:
        self._campanha_para_nova_sessao(campanha_id, usuario_id, perfil)
        resumo_limpo = str(resumo or "").strip()
        if not resumo_limpo:
            raise DadosInvalidos("Resumo da sessao e obrigatorio")
        sessao = self.sessao_repository.create(
            TormentaSessaoCampanha(
                campanha_id=campanha_id,
                resumo=resumo_limpo,
                visivel_jogadores=bool(visivel_jogadores),
            )
        )
        sessao.campanha_nome = (
            getattr(getattr(sessao, "campanha", None), "nome", "") or ""
        )
        return sessao

    def atualizar(
        self,
        usuario_id: int,
        perfil: PerfilUsuario,
        sessao_id: int,
        resumo: str | None = None,
        visivel_jogadores: bool | None = None,
    ) -> TormentaSessaoCampanha:
        sessao = self._sessao_gestao(sessao_id, usuario_id, perfil)
        if resumo is not None:
            resumo_limpo = str(resumo).strip()
            if not resumo_limpo:
                raise DadosInvalidos("Resumo da sessao nao pode ser vazio")
            sessao.resumo = resumo_limpo
        if visivel_jogadores is not None:
            sessao.visivel_jogadores = bool(visivel_jogadores)
        atualizada = self.sessao_repository.update(sessao)
        atualizada.campanha_nome = (
            getattr(getattr(atualizada, "campanha", None), "nome", "") or ""
        )
        return atualizada

    def deletar(self, usuario_id: int, perfil: PerfilUsuario, sessao_id: int) -> None:
        sessao = self._sessao_gestao(sessao_id, usuario_id, perfil)
        self.sessao_repository.delete(sessao)
