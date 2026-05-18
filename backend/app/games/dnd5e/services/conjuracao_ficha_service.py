"""Estado de conjuração persistido em ficha_json.conjuracao."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from fastapi import HTTPException

from app.games.dnd5e.data.spell_tables import PREPARED_CLASSES, SHORT_REST_RECOVER_ALL
from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.personagem_repository import Dnd5ePersonagemRepository
from app.games.dnd5e.rules.magia import espacos_por_classe_nivel
from app.games.dnd5e.schemas.conjuracao import (
    Dnd5eConjuracaoEstadoResponse,
    Dnd5eSlotNivelItem,
)
from app.games.dnd5e.services.conjuracao_shared import (
    classe_slug_ficha,
    magias_conhecidas_max,
)
from app.games.dnd5e.services.grimorio_service import _classe_lista_magias
from app.repositories.base import commit_with_rollback

_HAB_MOD = {
    "mago": "intelligence",
    "feiticeiro": "charisma",
    "bruxo": "charisma",
    "bardo": "charisma",
    "clerigo": "wisdom",
    "druida": "wisdom",
    "paladino": "charisma",
    "patrulheiro": "wisdom",
}


def _mod_habilidade(personagem, classe: str) -> int:
    attr = _HAB_MOD.get(classe, "intelligence")
    val = getattr(personagem, attr, 10) or 10
    return (int(val) - 10) // 2


def _estado_default(classe: str, nivel: int) -> dict[str, Any]:
    totais = espacos_por_classe_nivel(classe, nivel)
    return {
        "classe": classe,
        "espacos_usados": [0] * len(totais),
        "magias_preparadas_ids": [],
        "magia_concentracao_id": None,
    }


def _get_conjuracao(ficha: dict, classe: str, nivel: int) -> dict[str, Any]:
    base = ficha.get("conjuracao")
    if not isinstance(base, dict):
        base = _estado_default(classe, nivel)
    totais = espacos_por_classe_nivel(classe, nivel)
    usados = list(base.get("espacos_usados") or [])
    if len(usados) < len(totais):
        usados.extend([0] * (len(totais) - len(usados)))
    base["espacos_usados"] = usados[: len(totais)]
    base["classe"] = classe
    return base


def _magias_preparadas_max(personagem, classe: str, nivel: int) -> Optional[int]:
    if classe not in PREPARED_CLASSES:
        return None
    mod = _mod_habilidade(personagem, classe)
    return max(1, mod + nivel)


class Dnd5eConjuracaoFichaService:
    def __init__(
        self,
        personagem_repo: Dnd5ePersonagemRepository,
        grimorio_repo: Dnd5eGrimorioRepository,
    ):
        self.personagem_repo = personagem_repo
        self.grimorio_repo = grimorio_repo

    def _personagem(self, personagem_id: int):
        p = self.personagem_repo.get_by_id(personagem_id)
        if not p:
            raise HTTPException(status_code=404, detail="Personagem não encontrado")
        return p

    def obter_estado(self, personagem_id: int) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        if not classe:
            raise HTTPException(status_code=422, detail="Personagem sem classe conjuradora")
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        usados = conj["espacos_usados"]
        slots = []
        for nivel, total in enumerate(totais):
            if nivel == 0 or total <= 0:
                continue
            u = usados[nivel] if nivel < len(usados) else 0
            slots.append(
                Dnd5eSlotNivelItem(
                    nivel=nivel,
                    total=total,
                    usados=u,
                    disponiveis=max(0, total - u),
                )
            )
        classe_grim = _classe_lista_magias(classe)
        _, itens = self.grimorio_repo.listar_paginado(
            personagem_id, classe=classe_grim, limit=500
        )
        prep_ids = [int(x) for x in (conj.get("magias_preparadas_ids") or [])]
        return Dnd5eConjuracaoEstadoResponse(
            classe=classe,
            nivel_personagem=p.nivel,
            prepara_magias=classe in PREPARED_CLASSES,
            magias_conhecidas_max=magias_conhecidas_max(classe, p.nivel),
            magias_conhecidas_atual=len(itens),
            magias_preparadas_max=_magias_preparadas_max(p, classe, p.nivel),
            magias_preparadas_ids=prep_ids,
            slots=slots,
            magia_concentracao_id=conj.get("magia_concentracao_id"),
            recupera_slots_repouso_curto=classe in SHORT_REST_RECOVER_ALL,
        )

    def _salvar_conjuracao(self, personagem, ficha: dict, conj: dict) -> None:
        ficha = deepcopy(ficha)
        ficha["conjuracao"] = conj
        personagem.ficha_json = ficha
        commit_with_rollback(self.personagem_repo.db)
        self.personagem_repo.db.refresh(personagem)

    def gastar_slot(
        self, personagem_id: int, nivel_magia: int, quantidade: int = 1
    ) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        if nivel_magia <= 0 or nivel_magia >= len(totais):
            raise HTTPException(status_code=422, detail="Nível de magia inválido")
        usados = conj["espacos_usados"]
        disp = totais[nivel_magia] - usados[nivel_magia]
        if disp < quantidade:
            raise HTTPException(status_code=422, detail="Sem espaços disponíveis")
        usados[nivel_magia] += quantidade
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def preparar_magias(
        self, personagem_id: int, magia_ids: list[int]
    ) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        if classe not in PREPARED_CLASSES:
            raise HTTPException(
                status_code=400, detail="Esta classe não prepara magias diariamente"
            )
        max_prep = _magias_preparadas_max(p, classe, p.nivel) or 1
        if len(magia_ids) > max_prep:
            raise HTTPException(
                status_code=422,
                detail=f"Máximo de {max_prep} magias preparadas",
            )
        classe_grim = _classe_lista_magias(classe)
        for mid in magia_ids:
            if not self.grimorio_repo.obter_item(personagem_id, mid, classe_grim):
                raise HTTPException(
                    status_code=422,
                    detail=f"Magia {mid} não está no grimório",
                )
        conj = _get_conjuracao(ficha, classe, p.nivel)
        conj["magias_preparadas_ids"] = magia_ids
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def descanso_longo(self, personagem_id: int) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        conj["espacos_usados"] = [0] * len(totais)
        conj["magia_concentracao_id"] = None
        if classe in PREPARED_CLASSES:
            conj["magias_preparadas_ids"] = []
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def descanso_curto(self, personagem_id: int) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        if classe not in SHORT_REST_RECOVER_ALL:
            raise HTTPException(
                status_code=400,
                detail="Repouso curto não recupera slots desta classe",
            )
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        conj["espacos_usados"] = [0] * len(totais)
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)
