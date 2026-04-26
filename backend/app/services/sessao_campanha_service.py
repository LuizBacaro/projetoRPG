"""
Service de Sessao de Campanha.
"""
from typing import List

from ..exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from ..models.sessao_campanha import SessaoCampanha
from ..repositories.campanha_repository import CampanhaRepository
from ..repositories.sessao_campanha_repository import SessaoCampanhaRepository


class SessaoCampanhaService:
    def __init__(
        self,
        sessao_repository: SessaoCampanhaRepository,
        campanha_repository: CampanhaRepository,
    ):
        self.sessao_repository = sessao_repository
        self.campanha_repository = campanha_repository

    def listar_por_mestre(self, mestre_id: int) -> List[SessaoCampanha]:
        sessoes = self.sessao_repository.listar_por_mestre(mestre_id)
        for sessao in sessoes:
            sessao.campanha_nome = getattr(getattr(sessao, "campanha", None), "nome", "")
        return sessoes

    def criar(self, mestre_id: int, campanha_id: int, resumo: str, visivel_jogadores: bool = False) -> SessaoCampanha:
        campanha = self.campanha_repository.obter_por_id_e_mestre(campanha_id, mestre_id)
        if not campanha:
            raise ArenaBaseException("Campanha não encontrada para este mestre", status_code=404)
        resumo_limpo = str(resumo or "").strip()
        if not resumo_limpo:
            raise DadosInvalidos("Resumo da sessão é obrigatório")
        sessao = self.sessao_repository.create(
            SessaoCampanha(
                campanha_id=campanha_id,
                resumo=resumo_limpo,
                visivel_jogadores=bool(visivel_jogadores),
            )
        )
        sessao.campanha_nome = getattr(getattr(sessao, "campanha", None), "nome", "")
        return sessao

    def atualizar(
        self,
        mestre_id: int,
        sessao_id: int,
        resumo: str | None = None,
        visivel_jogadores: bool | None = None,
    ) -> SessaoCampanha:
        sessao = self.sessao_repository.obter_por_id_e_mestre(sessao_id, mestre_id)
        if not sessao:
            raise ArenaBaseException("Sessão não encontrada", status_code=404)
        if resumo is not None:
            resumo_limpo = str(resumo).strip()
            if not resumo_limpo:
                raise DadosInvalidos("Resumo da sessão não pode ser vazio")
            sessao.resumo = resumo_limpo
        if visivel_jogadores is not None:
            sessao.visivel_jogadores = bool(visivel_jogadores)
        atualizada = self.sessao_repository.update(sessao)
        atualizada.campanha_nome = getattr(getattr(atualizada, "campanha", None), "nome", "")
        return atualizada

    def deletar(self, mestre_id: int, sessao_id: int) -> None:
        sessao = self.sessao_repository.obter_por_id_e_mestre(sessao_id, mestre_id)
        if not sessao:
            raise ArenaBaseException("Sessão não encontrada", status_code=404)
        self.sessao_repository.delete(sessao_id)
