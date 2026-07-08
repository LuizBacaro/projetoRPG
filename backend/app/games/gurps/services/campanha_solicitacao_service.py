"""Regras de negócio — solicitações de entrada em campanha GURPS."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from app.games.gurps.models.campanha import GurpsCampanha, GurpsCampanhaSolicitacao
from app.games.gurps.repositories.campanha_repository import GurpsCampanhaRepository
from app.games.gurps.repositories.campanha_solicitacao_repository import (
    GurpsCampanhaSolicitacaoRepository,
)
from app.games.gurps.repositories.personagem_repository import GurpsPersonagemRepository
from app.games.gurps.schemas.campanha_solicitacao import (
    GurpsCampanhaDisponivelResponse,
    GurpsCampanhaSolicitacaoResponse,
)
from app.repositories.base import commit_with_rollback
from app.shared.core.usuario_lookup import mapa_nomes_usuarios_por_ids
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import PerfilUsuario, Usuario


class GurpsCampanhaSolicitacaoService:
    def __init__(
        self,
        solicitacao_repository: GurpsCampanhaSolicitacaoRepository,
        campanha_repository: GurpsCampanhaRepository,
        personagem_repository: GurpsPersonagemRepository,
    ):
        self.solicitacao_repository = solicitacao_repository
        self.campanha_repository = campanha_repository
        self.personagem_repository = personagem_repository

    def listar_disponiveis(self) -> List[GurpsCampanhaDisponivelResponse]:
        campanhas = self.campanha_repository.listar_todas()
        mestre_ids = [c.mestre_id for c in campanhas]
        mapa_mestres = mapa_nomes_usuarios_por_ids(
            self.campanha_repository.db, mestre_ids
        )
        return [
            GurpsCampanhaDisponivelResponse(
                id=c.id,
                nome=c.nome,
                mestre_nome=mapa_mestres.get(c.mestre_id, ""),
            )
            for c in campanhas
        ]

    def _personagem_do_jogador(self, personagem_id: int, usuario_id: int):
        personagem = self.personagem_repository.get_by_id(personagem_id)
        if not personagem:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        if personagem.dono_id != usuario_id:
            raise ArenaBaseException(
                "Sem permissao para este personagem", status_code=403
            )
        if str(personagem.tipo or "").lower() != "jogador":
            raise DadosInvalidos("Apenas personagens jogador podem solicitar campanha")
        return personagem

    def _para_resposta(
        self, sol: GurpsCampanhaSolicitacao, *, vinculado_direto: bool = False
    ) -> GurpsCampanhaSolicitacaoResponse:
        campanha = sol.campanha or self.campanha_repository.obter_por_id(
            sol.campanha_id
        )
        personagem = sol.personagem or self.personagem_repository.get_by_id(
            sol.personagem_id
        )
        mapa = mapa_nomes_usuarios_por_ids(
            self.solicitacao_repository.db,
            [sol.solicitante_id, campanha.mestre_id if campanha else None],
        )
        return GurpsCampanhaSolicitacaoResponse(
            id=sol.id,
            campanha_id=sol.campanha_id,
            campanha_nome=campanha.nome if campanha else "",
            personagem_id=sol.personagem_id,
            personagem_nome=personagem.nome if personagem else "",
            solicitante_id=sol.solicitante_id,
            solicitante_nome=mapa.get(sol.solicitante_id, ""),
            status=sol.status,
            created_at=sol.created_at,
            updated_at=sol.updated_at,
            resolved_at=sol.resolved_at,
            vinculado_direto=vinculado_direto,
        )

    def _vincular_personagem_campanha(
        self, personagem, campanha: GurpsCampanha
    ) -> None:
        personagem.campanha_id = campanha.id
        commit_with_rollback(self.personagem_repository.db)

    def criar_solicitacao(
        self, usuario: Usuario, campanha_id: int, personagem_id: int
    ) -> GurpsCampanhaSolicitacaoResponse:
        personagem = self._personagem_do_jogador(personagem_id, usuario.id)
        campanha = self.campanha_repository.obter_por_id(campanha_id)
        if not campanha:
            raise ArenaBaseException("Campanha nao encontrada", status_code=404)

        if personagem.campanha_id is not None:
            if int(personagem.campanha_id) == int(campanha_id):
                raise DadosInvalidos("Personagem ja participa desta campanha")
            raise DadosInvalidos(
                "Personagem ja esta vinculado a outra campanha. O mestre deve remover o vinculo antes."
            )

        existente = self.solicitacao_repository.obter_pendente(
            personagem_id, campanha_id
        )
        if existente:
            return self._para_resposta(existente)

        if int(campanha.mestre_id) == int(usuario.id):
            self._vincular_personagem_campanha(personagem, campanha)
            sol = GurpsCampanhaSolicitacao(
                campanha_id=campanha_id,
                personagem_id=personagem_id,
                solicitante_id=usuario.id,
                status="aceita",
                resolved_at=datetime.now(timezone.utc),
            )
            sol = self.solicitacao_repository.criar(sol)
            return self._para_resposta(sol, vinculado_direto=True)

        outra_pendente = self.solicitacao_repository.obter_pendente_por_personagem(
            personagem_id
        )
        if outra_pendente and int(outra_pendente.campanha_id) != int(campanha_id):
            raise DadosInvalidos(
                "Ja existe uma solicitacao pendente para outra campanha. Cancele antes de solicitar outra."
            )

        sol = GurpsCampanhaSolicitacao(
            campanha_id=campanha_id,
            personagem_id=personagem_id,
            solicitante_id=usuario.id,
            status="pendente",
        )
        sol = self.solicitacao_repository.criar(sol)
        return self._para_resposta(sol)

    def obter_pendente_personagem(
        self, usuario: Usuario, personagem_id: int
    ) -> Optional[GurpsCampanhaSolicitacaoResponse]:
        self._personagem_do_jogador(personagem_id, usuario.id)
        sol = self.solicitacao_repository.obter_pendente_por_personagem(personagem_id)
        if not sol:
            return None
        return self._para_resposta(sol)

    def listar_pendentes_mestre(
        self, usuario: Usuario
    ) -> List[GurpsCampanhaSolicitacaoResponse]:
        if usuario.perfil == PerfilUsuario.ADMINISTRADOR:
            rows = self.solicitacao_repository.listar_pendentes_todas()
        else:
            rows = self.solicitacao_repository.listar_pendentes_para_mestre(usuario.id)
        return [self._para_resposta(r) for r in rows]

    def listar_historico_mestre(
        self, usuario: Usuario, limit: int = 100
    ) -> List[GurpsCampanhaSolicitacaoResponse]:
        if usuario.perfil == PerfilUsuario.ADMINISTRADOR:
            rows = self.solicitacao_repository.listar_historico_todas(limit)
        else:
            rows = self.solicitacao_repository.listar_historico_para_mestre(
                usuario.id, limit
            )
        return [self._para_resposta(r) for r in rows]

    def _assert_mestre_solicitacao(
        self, usuario: Usuario, sol: GurpsCampanhaSolicitacao
    ) -> GurpsCampanha:
        campanha = self.campanha_repository.obter_por_id(sol.campanha_id)
        if not campanha:
            raise ArenaBaseException("Campanha nao encontrada", status_code=404)
        if usuario.perfil == PerfilUsuario.ADMINISTRADOR:
            return campanha
        if int(campanha.mestre_id) != int(usuario.id):
            raise ArenaBaseException(
                "Sem permissao para gerir solicitacoes desta campanha", status_code=403
            )
        return campanha

    def aceitar(
        self, usuario: Usuario, solicitacao_id: int
    ) -> GurpsCampanhaSolicitacaoResponse:
        sol = self.solicitacao_repository.obter_por_id(solicitacao_id)
        if not sol:
            raise ArenaBaseException("Solicitacao nao encontrada", status_code=404)
        if sol.status != "pendente":
            raise DadosInvalidos("Solicitacao nao esta pendente")
        campanha = self._assert_mestre_solicitacao(usuario, sol)
        personagem = self.personagem_repository.get_by_id(sol.personagem_id)
        if not personagem:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        if personagem.campanha_id is not None and int(personagem.campanha_id) != int(
            campanha.id
        ):
            raise DadosInvalidos("Personagem ja esta em outra campanha")

        self._vincular_personagem_campanha(personagem, campanha)
        sol.status = "aceita"
        sol.resolved_at = datetime.now(timezone.utc)
        sol = self.solicitacao_repository.salvar(sol)
        return self._para_resposta(sol)

    def recusar(
        self, usuario: Usuario, solicitacao_id: int
    ) -> GurpsCampanhaSolicitacaoResponse:
        sol = self.solicitacao_repository.obter_por_id(solicitacao_id)
        if not sol:
            raise ArenaBaseException("Solicitacao nao encontrada", status_code=404)
        if sol.status != "pendente":
            raise DadosInvalidos("Solicitacao nao esta pendente")
        self._assert_mestre_solicitacao(usuario, sol)
        sol.status = "recusada"
        sol.resolved_at = datetime.now(timezone.utc)
        sol = self.solicitacao_repository.salvar(sol)
        return self._para_resposta(sol)

    def cancelar(self, usuario: Usuario, solicitacao_id: int) -> None:
        sol = self.solicitacao_repository.obter_por_id(solicitacao_id)
        if not sol:
            raise ArenaBaseException("Solicitacao nao encontrada", status_code=404)
        if int(sol.solicitante_id) != int(usuario.id):
            raise ArenaBaseException("Sem permissao", status_code=403)
        if sol.status != "pendente":
            raise DadosInvalidos("Solicitacao nao esta pendente")
        sol.status = "cancelada"
        sol.resolved_at = datetime.now(timezone.utc)
        self.solicitacao_repository.salvar(sol)
