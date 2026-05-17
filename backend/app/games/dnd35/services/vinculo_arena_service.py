"""Sincroniza companheiro animal / familiar como NPC na tabela combatentes (arena)."""

from __future__ import annotations

from typing import List, Optional, Sequence

from sqlalchemy.orm import Session

from app.games.dnd35.catalogs.companheiros_especies import (
    especie_por_slug as especie_companheiro,
)
from app.games.dnd35.catalogs.familiares_especies import (
    especie_por_slug as especie_familiar,
)
from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.companheiro_animal import CompanheiroAnimal
from app.games.dnd35.models.familiar import Familiar
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.repositories.companheiro_animal_repository import (
    CompanheiroAnimalRepository,
)
from app.games.dnd35.repositories.familiar_repository import FamiliarRepository
from app.repositories.base import soft_delete_entity


def _mod_atributo(valor: int) -> int:
    return (int(valor) - 10) // 2


def _iniciativa_companheiro(ca: CompanheiroAnimal, mestre: Combatente) -> int:
    if ca.iniciativa is not None:
        return max(0, int(ca.iniciativa))
    return max(0, _mod_atributo(int(ca.destreza or 10)), int(mestre.iniciativa or 0))


def _iniciativa_familiar(fam: Familiar, mestre: Combatente, destreza: int) -> int:
    return max(0, _mod_atributo(destreza), int(mestre.iniciativa or 0))


class VinculoArenaService:
    def __init__(
        self,
        db: Session,
        *,
        combatente_repo: CombatenteRepository,
        companheiro_repo: CompanheiroAnimalRepository,
        familiar_repo: FamiliarRepository,
    ):
        self.db = db
        self._combatente_repo = combatente_repo
        self._companheiro_repo = companheiro_repo
        self._familiar_repo = familiar_repo

    def _persistir_combatente_arena(
        self,
        *,
        arena_id: Optional[int],
        mestre: Combatente,
        nome: str,
        classe: str,
        raca: str,
        hp_atual: int,
        hp_maximo: int,
        ca: int,
        iniciativa: int,
        forca: int = 10,
        destreza: int = 10,
        constituicao: int = 10,
        inteligencia: int = 10,
        sabedoria: int = 10,
        carisma: int = 10,
    ) -> Combatente:
        hp_max = max(1, int(hp_maximo))
        hp_cur = max(0, min(int(hp_atual), hp_max))
        dados = {
            "nome": nome[:100],
            "tipo": "npc",
            "classe": classe[:50],
            "raca": raca[:50],
            "hp_maximo": hp_max,
            "hp_atual": hp_cur,
            "ca": int(ca),
            "iniciativa": max(0, int(iniciativa)),
            "forca": forca,
            "destreza": destreza,
            "constituicao": constituicao,
            "inteligencia": inteligencia,
            "sabedoria": sabedoria,
            "carisma": carisma,
            "dono_id": mestre.dono_id,
            "campanha_id": mestre.campanha_id,
            "nivel": 1,
        }
        if arena_id:
            existente = self._combatente_repo.get_by_id(arena_id)
            if existente:
                for k, v in dados.items():
                    setattr(existente, k, v)
                return self._combatente_repo.update(existente)
        ent = Combatente(**dados)
        return self._combatente_repo.create(ent)

    def sync_companheiro(self, ca: CompanheiroAnimal, mestre: Combatente) -> int:
        especie = especie_companheiro(ca.especie_slug) or {}
        especie_nome = especie.get("nome", ca.especie_slug)
        npc = self._persistir_combatente_arena(
            arena_id=ca.arena_combatente_id,
            mestre=mestre,
            nome=f"{ca.nome}",
            classe="Companheiro animal",
            raca=f"{especie_nome} · {mestre.nome}"[:50],
            hp_atual=ca.hp_atual,
            hp_maximo=ca.hp_maximo,
            ca=ca.ca,
            iniciativa=_iniciativa_companheiro(ca, mestre),
            forca=ca.forca,
            destreza=ca.destreza,
            constituicao=ca.constituicao,
            inteligencia=ca.inteligencia,
            sabedoria=ca.sabedoria,
            carisma=ca.carisma,
        )
        ca.arena_combatente_id = npc.id
        self._companheiro_repo.atualizar(ca)
        return npc.id

    def sync_familiar(self, fam: Familiar, mestre: Combatente) -> int:
        especie = especie_familiar(fam.especie_slug) or {}
        especie_nome = especie.get("nome", fam.especie_slug)
        attrs = especie.get("atributos_base", {})
        des = int(attrs.get("destreza", 10))
        npc = self._persistir_combatente_arena(
            arena_id=fam.arena_combatente_id,
            mestre=mestre,
            nome=fam.nome,
            classe="Familiar",
            raca=f"{especie_nome} · {mestre.nome}"[:50],
            hp_atual=fam.hp_atual,
            hp_maximo=fam.hp_maximo,
            ca=fam.ca,
            iniciativa=_iniciativa_familiar(fam, mestre, des),
            forca=int(attrs.get("forca", 10)),
            destreza=des,
            constituicao=int(attrs.get("constituicao", 10)),
            inteligencia=fam.inteligencia,
            sabedoria=int(attrs.get("sabedoria", 10)),
            carisma=int(attrs.get("carisma", 10)),
        )
        fam.arena_combatente_id = npc.id
        self._familiar_repo.atualizar(fam)
        return npc.id

    def remover_combatente_arena(self, arena_combatente_id: Optional[int]) -> None:
        if not arena_combatente_id:
            return
        ent = self._combatente_repo.get_by_id(arena_combatente_id)
        if ent:
            soft_delete_entity(self.db, ent)

    def expandir_combatente_ids(
        self,
        combatente_ids: Sequence[int],
        *,
        incluir_vinculos: bool = True,
    ) -> List[int]:
        ids = list(dict.fromkeys(int(i) for i in combatente_ids))
        if not incluir_vinculos:
            return ids

        extras: List[int] = []
        for cid in combatente_ids:
            mestre = self._combatente_repo.get_by_id(cid)
            if not mestre:
                continue
            ca = self._companheiro_repo.obter_por_combatente(cid)
            if ca:
                arena_id = ca.arena_combatente_id
                if not arena_id:
                    arena_id = self.sync_companheiro(ca, mestre)
                if arena_id and arena_id not in ids and arena_id not in extras:
                    extras.append(arena_id)
                continue
            fam = self._familiar_repo.obter_por_combatente(cid)
            if fam:
                arena_id = fam.arena_combatente_id
                if not arena_id:
                    arena_id = self.sync_familiar(fam, mestre)
                if arena_id and arena_id not in ids and arena_id not in extras:
                    extras.append(arena_id)

        return ids + extras
