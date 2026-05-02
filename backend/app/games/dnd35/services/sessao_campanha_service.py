"""
Service de Sessão de Campanha (D&D 3.5)

Localização: este módulo pertence ao pacote `app.games.dnd35.services`.
Existe um shim em `app.services.sessao_campanha_service` que re-exporta
a classe durante a reorganização multi-jogo.
"""

from typing import List

from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.games.dnd35.models.sessao_campanha import SessaoCampanha
from app.games.dnd35.ports import CampanhaRepositoryProtocol, SessaoCampanhaRepositoryProtocol


class SessaoCampanhaService:
    def __init__(
        self,
        sessao_repository: SessaoCampanhaRepositoryProtocol,
        campanha_repository: CampanhaRepositoryProtocol,
    ):
        self.sessao_repository = sessao_repository
        self.campanha_repository = campanha_repository

    def listar_por_mestre(self, mestre_id: int) -> List[SessaoCampanha]:
        sessoes = self.sessao_repository.listar_por_mestre(mestre_id)
        for sessao in sessoes:
            sessao.campanha_nome = getattr(
                getattr(sessao, "campanha", None), "nome", ""
            )
        return sessoes

    def criar(
        self,
        mestre_id: int,
        campanha_id: int,
        resumo: str,
        visivel_jogadores: bool = False,
    ) -> SessaoCampanha:
        campanha = self.campanha_repository.obter_por_id_e_mestre(
            campanha_id, mestre_id
        )
        if not campanha:
            raise ArenaBaseException(
                "Campanha não encontrada para este mestre", status_code=404
            )
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
        sessao.campanha_nome = getattr(
            getattr(sessao, "campanha", None), "nome", ""
        )
        return sessao

    def atualizar(
        self,
        mestre_id: int,
        sessao_id: int,
        resumo: str | None = None,
        visivel_jogadores: bool | None = None,
    ) -> SessaoCampanha:
        sessao = self.sessao_repository.obter_por_id_e_mestre(
            sessao_id, mestre_id
        )
        if not sessao:
            raise ArenaBaseException("Sessão não encontrada", status_code=404)
        if resumo is not None:
            resumo_limpo = str(resumo).strip()
            if not resumo_limpo:
                raise DadosInvalidos(
                    "Resumo da sessão não pode ser vazio"
                )
            sessao.resumo = resumo_limpo
        if visivel_jogadores is not None:
            sessao.visivel_jogadores = bool(visivel_jogadores)
        atualizada = self.sessao_repository.update(sessao)
        atualizada.campanha_nome = getattr(
            getattr(atualizada, "campanha", None), "nome", ""
        )
        return atualizada

    def deletar(self, mestre_id: int, sessao_id: int) -> None:
        sessao = self.sessao_repository.obter_por_id_e_mestre(
            sessao_id, mestre_id
        )
        if not sessao:
            raise ArenaBaseException("Sessão não encontrada", status_code=404)
        self.sessao_repository.delete(sessao)
