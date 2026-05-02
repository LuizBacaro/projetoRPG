"""Regras de negócio — combate GURPS (Arena)."""

from typing import Any, Dict, List, Optional

from app.games.gurps.models.combate import GurpsCombate
from app.games.gurps.ports import (
    GurpsCombateRepositoryProtocol,
    GurpsPersonagemRepositoryProtocol,
)
from app.games.gurps.schemas.personagem import GurpsPersonagemResponse
from app.shared.exceptions.custom_exceptions import (
    ArenaBaseException,
    CombateJaAtivoError,
    CombateNotFoundError,
)


class GurpsCombateService:
    def __init__(
        self,
        combate_repo: GurpsCombateRepositoryProtocol,
        personagem_repo: GurpsPersonagemRepositoryProtocol,
    ):
        self.combate_repo = combate_repo
        self.personagem_repo = personagem_repo

    def iniciar_combate(self, personagem_ids: List[int]) -> GurpsCombate:
        if self.combate_repo.existe_combate_ativo():
            raise CombateJaAtivoError(
                "Ja existe um combate GURPS ativo. Finalize-o antes de iniciar outro."
            )

        personagens = self.personagem_repo.get_by_ids(personagem_ids)
        if len(personagens) != len(set(personagem_ids)):
            raise ArenaBaseException(
                "Alguns personagens nao foram encontrados", status_code=404
            )

        ordenados = self.personagem_repo.ordenar_por_iniciativa(personagens)
        ids_ordenados = [p.id for p in ordenados]

        combate = GurpsCombate(
            personagens_ids=ids_ordenados,
            turno_atual=0,
            rodada_atual=1,
            ativo=True,
        )
        return self.combate_repo.create(combate)

    def obter_combate_ativo(self) -> Optional[GurpsCombate]:
        return self.combate_repo.get_ativo()

    def montar_status(
        self, combate: Optional[GurpsCombate], incluir_personagens: bool = True
    ) -> Dict[str, Any]:
        if not combate:
            return {
                "ativo": False,
                "message": "Nenhum combate GURPS ativo",
                "resumido": not incluir_personagens,
            }

        payload: Dict[str, Any] = {
            "id": combate.id,
            "personagens_ids": combate.personagens_ids,
            "turno_atual": combate.turno_atual,
            "rodada_atual": combate.rodada_atual,
            "ativo": combate.ativo,
            "personagem_ativo_id": combate.obter_personagem_ativo_id(),
            "resumido": not incluir_personagens,
        }

        if incluir_personagens:
            pers = self.personagem_repo.get_by_ids(list(combate.personagens_ids or []))
            by_id = {p.id: p for p in pers}
            ordenados = [by_id[i] for i in combate.personagens_ids if i in by_id]
            payload["personagens"] = [
                GurpsPersonagemResponse.model_validate(p) for p in ordenados
            ]

        return payload

    def obter_status_combate(self, incluir_personagens: bool = True) -> Dict[str, Any]:
        combate = self.obter_combate_ativo()
        return self.montar_status(combate, incluir_personagens=incluir_personagens)

    def avancar_turno(self) -> GurpsCombate:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate GURPS ativo")
        combate.avancar_turno()
        return self.combate_repo.update(combate)

    def finalizar_combate(self) -> bool:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate GURPS ativo")
        combate.finalizar()
        self.combate_repo.update(combate)
        return True
