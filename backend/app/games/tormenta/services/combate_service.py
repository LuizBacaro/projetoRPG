"""Regras de negócio — combate Tormenta 20 (Arena)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.tormenta.models.combate import TormentaCombate
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.repositories.combate_repository import TormentaCombateRepository
from app.games.tormenta.repositories.personagem_repository import (
    TormentaPersonagemRepository,
)
from app.games.tormenta.schemas.combate import TormentaCombateCondicaoMbItem
from app.games.tormenta.schemas.personagem import TormentaPersonagemResponse
from app.shared.exceptions.custom_exceptions import (
    ArenaBaseException,
    CombateJaAtivoError,
    CombateNotFoundError,
    DadosInvalidos,
)


class TormentaCombateService:
    def __init__(
        self,
        combate_repo: TormentaCombateRepository,
        personagem_repo: TormentaPersonagemRepository,
        usuario_id: int,
    ):
        self.combate_repo = combate_repo
        self.personagem_repo = personagem_repo
        self.usuario_id = usuario_id

    @staticmethod
    def _ordenar_para_arena(
        personagens: List[TormentaPersonagem],
    ) -> List[TormentaPersonagem]:
        def chave(p: TormentaPersonagem) -> tuple:
            ini = int(p.iniciativa) if p.iniciativa is not None else 0
            nome = (p.nome or "").lower()
            return (-ini, nome)

        return sorted(personagens, key=chave)

    def obter_combate_ativo(self) -> Optional[TormentaCombate]:
        return self.combate_repo.get_ativo_por_usuario(self.usuario_id)

    def montar_status(
        self, combate: Optional[TormentaCombate], incluir_personagens: bool = True
    ) -> Dict[str, Any]:
        if not combate or not combate.ativo:
            return {
                "ativo": False,
                "message": "Nenhum combate Tormenta ativo",
                "resumido": not incluir_personagens,
            }

        raw_cond = combate.condicoes_mb_json
        cond_map: Dict[str, Any] = raw_cond if isinstance(raw_cond, dict) else {}

        payload: Dict[str, Any] = {
            "id": combate.id,
            "usuario_id": combate.usuario_id,
            "personagens_ids": combate.personagens_ids,
            "turno_atual": combate.turno_atual,
            "rodada_atual": combate.rodada_atual,
            "ativo": combate.ativo,
            "personagem_ativo_id": combate.obter_personagem_ativo_id(),
            "resumido": not incluir_personagens,
            "condicoes_mb": cond_map,
        }

        if incluir_personagens:
            pers = self.personagem_repo.get_by_ids(list(combate.personagens_ids or []))
            by_id = {p.id: p for p in pers}
            ordenados = [by_id[i] for i in combate.personagens_ids if i in by_id]
            payload["personagens"] = [
                TormentaPersonagemResponse.model_validate(p).model_dump()
                for p in ordenados
            ]

        return payload

    def obter_status_combate(self, incluir_personagens: bool = True) -> Dict[str, Any]:
        combate = self.obter_combate_ativo()
        return self.montar_status(combate, incluir_personagens=incluir_personagens)

    def iniciar_combate(self, personagem_ids: List[int]) -> TormentaCombate:
        if self.combate_repo.existe_combate_ativo_por_usuario(self.usuario_id):
            raise CombateJaAtivoError(
                "Ja existe um combate Tormenta ativo para sua conta. Encerre-o antes de iniciar outro."
            )

        ids_unicos = list(dict.fromkeys(personagem_ids))
        personagens = self.personagem_repo.get_by_ids(ids_unicos)
        if len(personagens) != len(ids_unicos):
            raise ArenaBaseException(
                "Alguns personagens nao foram encontrados", status_code=404
            )

        ordenados = self._ordenar_para_arena(personagens)
        ids_ordenados = [p.id for p in ordenados]

        combate = TormentaCombate(
            usuario_id=self.usuario_id,
            personagens_ids=ids_ordenados,
            turno_atual=0,
            rodada_atual=1,
            ativo=True,
            condicoes_mb_json={},
        )
        return self.combate_repo.create(combate)

    def avancar_turno(self) -> TormentaCombate:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate Tormenta ativo")
        combate.avancar_turno()
        return self.combate_repo.update(combate)

    def finalizar_combate(self) -> bool:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate Tormenta ativo")
        combate.finalizar()
        self.combate_repo.update(combate)
        return True

    def aplicar_condicoes_mb(
        self, por_personagem: Dict[str, TormentaCombateCondicaoMbItem]
    ) -> TormentaCombate:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate Tormenta ativo")
        permitidos = {int(x) for x in (combate.personagens_ids or [])}
        atual: Dict[str, Any] = {}
        raw = combate.condicoes_mb_json
        if isinstance(raw, dict):
            atual = {str(k): v for k, v in raw.items()}

        for k, item in por_personagem.items():
            try:
                pid = int(str(k).strip())
            except (TypeError, ValueError) as exc:
                raise DadosInvalidos(f"Id de personagem invalido: {k}") from exc
            if pid not in permitidos:
                raise DadosInvalidos("Personagem nao participa deste combate")
            rotulos = list(item.rotulos)
            tips = list(item.tips)
            if not rotulos and not tips:
                atual.pop(str(pid), None)
            else:
                atual[str(pid)] = {"rotulos": rotulos, "tips": tips}

        combate.condicoes_mb_json = atual
        return self.combate_repo.update(combate)
