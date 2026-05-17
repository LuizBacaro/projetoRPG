from __future__ import annotations

from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.games.dnd35.catalogs.familiares_especies import (
    especie_por_slug,
    listar_especies,
)
from app.games.dnd35.models.familiar import Familiar
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.repositories.companheiro_animal_repository import (
    CompanheiroAnimalRepository,
)
from app.games.dnd35.repositories.familiar_repository import FamiliarRepository
from app.games.dnd35.rules.familiar import (
    calcular_derivadas_familiar,
    elegibilidade_familiar,
)
from app.games.dnd35.rules.vinculo_animal import MSG_TEM_COMPANHEIRO
from app.games.dnd35.schemas.familiar import (
    FamiliarCalcularRequest,
    FamiliarCalcularResponse,
    FamiliarElegibilidadeResponse,
    FamiliarEspecieItem,
    FamiliarEstatisticasDerivadas,
    FamiliarResponse,
    FamiliarUpsert,
)
from app.games.dnd35.services.vinculo_arena_service import VinculoArenaService
from app.shared.exceptions.custom_exceptions import CombatenteNaoEncontrado


class FamiliarService:
    def __init__(
        self,
        db: Session,
        *,
        repo: FamiliarRepository,
        combatente_repo: CombatenteRepository,
        companheiro_repo: CompanheiroAnimalRepository,
        vinculo_arena: VinculoArenaService | None = None,
    ):
        self.db = db
        self._repo = repo
        self._combatente_repo = combatente_repo
        self._companheiro_repo = companheiro_repo
        self._vinculo_arena = vinculo_arena

    def _combatente_or_raise(self, combatente_id: int):
        c = self._combatente_repo.get_by_id(combatente_id)
        if not c:
            raise CombatenteNaoEncontrado(combatente_id)
        return c

    def _assert_sem_companheiro(self, combatente_id: int) -> None:
        if self._companheiro_repo.obter_por_combatente(combatente_id):
            raise ValueError(MSG_TEM_COMPANHEIRO)

    def _elegibilidade(self, combatente) -> FamiliarElegibilidadeResponse:
        ok, motivo, nivel_m = elegibilidade_familiar(
            combatente.classe, combatente.nivel or 1
        )
        return FamiliarElegibilidadeResponse(
            elegivel=ok,
            motivo=motivo,
            nivel_mestre=nivel_m,
            classe=str(combatente.classe or ""),
            nivel_personagem=int(combatente.nivel or 1),
        )

    def listar_especies(self) -> List[FamiliarEspecieItem]:
        return [FamiliarEspecieItem(**e) for e in listar_especies()]

    def calcular(
        self, combatente_id: int, payload: FamiliarCalcularRequest
    ) -> FamiliarCalcularResponse:
        combatente = self._combatente_or_raise(combatente_id)
        eleg = self._elegibilidade(combatente)
        if not eleg.elegivel:
            raise ValueError(eleg.motivo or "Personagem não elegível para familiar.")

        especie_raw = especie_por_slug(payload.especie_slug)
        if not especie_raw:
            raise ValueError(f"Espécie inválida: {payload.especie_slug}")

        deriv = calcular_derivadas_familiar(
            nivel_mestre=eleg.nivel_mestre,
            hp_maximo_mestre=int(combatente.hp_maximo or 1),
            atributos_base=especie_raw["atributos_base"],
            armadura_natural_base=especie_raw.get("armadura_natural_base", 0),
            hp_extra_mestre=int(especie_raw.get("hp_extra_mestre", 0)),
        )
        deriv["bonus_mestre_especie"] = especie_raw.get("bonus_mestre", "")
        return FamiliarCalcularResponse(
            especie=FamiliarEspecieItem(**especie_raw),
            elegibilidade=eleg,
            derivadas=FamiliarEstatisticasDerivadas(**deriv),
        )

    def _aplicar_payload(self, entidade: Familiar, payload: FamiliarUpsert) -> None:
        entidade.especie_slug = payload.especie_slug
        entidade.nome = payload.nome.strip()
        entidade.nivel_mestre = payload.nivel_mestre
        entidade.inteligencia = payload.inteligencia
        entidade.armadura_natural_bonus = payload.armadura_natural_bonus
        entidade.hp_atual = payload.hp_atual
        entidade.hp_maximo = payload.hp_maximo
        entidade.ca = payload.ca
        entidade.bonus_mestre = payload.bonus_mestre
        entidade.habilidades_especiais = list(payload.habilidades_especiais or [])
        entidade.anotacoes = payload.anotacoes

    def _to_response(self, entidade: Familiar, combatente) -> FamiliarResponse:
        especie_raw = especie_por_slug(entidade.especie_slug) or {}
        eleg = self._elegibilidade(combatente)
        deriv = None
        if eleg.elegivel and especie_raw:
            deriv_map = calcular_derivadas_familiar(
                nivel_mestre=eleg.nivel_mestre,
                hp_maximo_mestre=int(combatente.hp_maximo or 1),
                atributos_base=especie_raw.get("atributos_base", {}),
                armadura_natural_base=especie_raw.get("armadura_natural_base", 0),
                hp_extra_mestre=int(especie_raw.get("hp_extra_mestre", 0)),
            )
            deriv_map["bonus_mestre_especie"] = especie_raw.get("bonus_mestre", "")
            deriv = FamiliarEstatisticasDerivadas(**deriv_map)

        return FamiliarResponse(
            id=entidade.id,
            combatente_id=entidade.combatente_id,
            especie_slug=entidade.especie_slug,
            especie_nome=especie_raw.get("nome", entidade.especie_slug),
            nome=entidade.nome,
            nivel_mestre=entidade.nivel_mestre,
            inteligencia=entidade.inteligencia,
            armadura_natural_bonus=entidade.armadura_natural_bonus,
            hp_atual=entidade.hp_atual,
            hp_maximo=entidade.hp_maximo,
            ca=entidade.ca,
            bonus_mestre=entidade.bonus_mestre,
            habilidades_especiais=entidade.habilidades_especiais or [],
            anotacoes=entidade.anotacoes,
            derivadas=deriv,
            elegibilidade=eleg,
        )

    def obter(self, combatente_id: int) -> Optional[FamiliarResponse]:
        try:
            combatente = self._combatente_or_raise(combatente_id)
            ent = self._repo.obter_por_combatente(combatente_id)
            if not ent:
                return None
            return self._to_response(ent, combatente)
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def elegibilidade(self, combatente_id: int) -> FamiliarElegibilidadeResponse:
        combatente = self._combatente_or_raise(combatente_id)
        return self._elegibilidade(combatente)

    def salvar(self, combatente_id: int, payload: FamiliarUpsert) -> FamiliarResponse:
        combatente = self._combatente_or_raise(combatente_id)
        eleg = self._elegibilidade(combatente)
        if not eleg.elegivel:
            raise ValueError(eleg.motivo or "Personagem não elegível.")

        if not especie_por_slug(payload.especie_slug):
            raise ValueError(f"Espécie inválida: {payload.especie_slug}")

        self._assert_sem_companheiro(combatente_id)

        ent = self._repo.obter_por_combatente(combatente_id)
        if ent is None:
            ent = Familiar(combatente_id=combatente_id)
            self._aplicar_payload(ent, payload)
            ent = self._repo.criar(ent)
        else:
            self._aplicar_payload(ent, payload)
            ent = self._repo.atualizar(ent)
        if self._vinculo_arena:
            self._vinculo_arena.sync_familiar(ent, combatente)
        return self._to_response(ent, combatente)

    def criar_a_partir_calculo(
        self, combatente_id: int, payload: FamiliarCalcularRequest
    ) -> FamiliarResponse:
        calc = self.calcular(combatente_id, payload)
        d = calc.derivadas
        especie = calc.especie
        upsert = FamiliarUpsert(
            especie_slug=payload.especie_slug,
            nome=payload.nome.strip() or especie.nome,
            nivel_mestre=d.nivel_mestre,
            inteligencia=d.inteligencia,
            armadura_natural_bonus=d.armadura_natural_bonus,
            hp_atual=d.hp_max_sugerido,
            hp_maximo=d.hp_max_sugerido,
            ca=d.ca,
            bonus_mestre=d.bonus_mestre_especie or especie.bonus_mestre,
            habilidades_especiais=list(d.habilidades_especiais or []),
        )
        return self.salvar(combatente_id, upsert)

    def remover(self, combatente_id: int) -> bool:
        self._combatente_or_raise(combatente_id)
        ent = self._repo.obter_por_combatente(combatente_id)
        if not ent:
            return False
        if self._vinculo_arena:
            self._vinculo_arena.remover_combatente_arena(ent.arena_combatente_id)
        self._repo.remover(ent)
        return True
