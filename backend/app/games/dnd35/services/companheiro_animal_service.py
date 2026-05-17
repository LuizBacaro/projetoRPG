from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.games.dnd35.catalogs.companheiros_especies import (
    especie_por_slug,
    listar_especies,
)
from app.games.dnd35.models.companheiro_animal import CompanheiroAnimal
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.repositories.companheiro_animal_repository import (
    CompanheiroAnimalRepository,
)
from app.games.dnd35.repositories.familiar_repository import FamiliarRepository
from app.games.dnd35.rules.companheiro_animal import (
    calcular_estatisticas,
    elegibilidade_companheiro,
)
from app.games.dnd35.rules.vinculo_animal import MSG_TEM_FAMILIAR
from app.games.dnd35.schemas.companheiro_animal import (
    CHAVES_ATRIBUTO,
    CompanheiroAnimalResponse,
    CompanheiroAnimalUpsert,
    CompanheiroCalcularRequest,
    CompanheiroCalcularResponse,
    CompanheiroElegibilidadeResponse,
    CompanheiroEspecieItem,
    CompanheiroEstatisticasDerivadas,
)
from app.games.dnd35.services.vinculo_arena_service import VinculoArenaService
from app.shared.exceptions.custom_exceptions import CombatenteNaoEncontrado


class CompanheiroAnimalService:
    def __init__(
        self,
        db: Session,
        *,
        repo: CompanheiroAnimalRepository,
        combatente_repo: CombatenteRepository,
        familiar_repo: FamiliarRepository | None = None,
        vinculo_arena: VinculoArenaService | None = None,
    ):
        self.db = db
        self._repo = repo
        self._combatente_repo = combatente_repo
        self._familiar_repo = familiar_repo
        self._vinculo_arena = vinculo_arena

    def _combatente_or_raise(self, combatente_id: int):
        c = self._combatente_repo.get_by_id(combatente_id)
        if not c:
            raise CombatenteNaoEncontrado(combatente_id)
        return c

    def _assert_sem_familiar(self, combatente_id: int) -> None:
        if self._familiar_repo and self._familiar_repo.obter_por_combatente(
            combatente_id
        ):
            raise ValueError(MSG_TEM_FAMILIAR)

    def _elegibilidade(self, combatente) -> CompanheiroElegibilidadeResponse:
        ok, motivo, nivel_ef = elegibilidade_companheiro(
            combatente.classe, combatente.nivel or 1
        )
        return CompanheiroElegibilidadeResponse(
            elegivel=ok,
            motivo=motivo,
            nivel_efetivo=nivel_ef,
            classe=str(combatente.classe or ""),
            nivel_personagem=int(combatente.nivel or 1),
        )

    def listar_especies(self) -> List[CompanheiroEspecieItem]:
        return [CompanheiroEspecieItem(**e) for e in listar_especies()]

    def calcular(
        self, combatente_id: int, payload: CompanheiroCalcularRequest
    ) -> CompanheiroCalcularResponse:
        combatente = self._combatente_or_raise(combatente_id)
        eleg = self._elegibilidade(combatente)
        if not eleg.elegivel:
            raise ValueError(
                eleg.motivo or "Personagem não elegível para companheiro animal."
            )

        especie_raw = especie_por_slug(payload.especie_slug)
        if not especie_raw:
            raise ValueError(f"Espécie inválida: {payload.especie_slug}")

        deriv = calcular_estatisticas(
            nivel_efetivo=eleg.nivel_efetivo,
            hd_base=especie_raw["hd_base"],
            atributos_base=especie_raw["atributos_base"],
            bonus_atributos=payload.bonus_atributos,
            armadura_natural_base=especie_raw["armadura_natural_base"],
        )
        return CompanheiroCalcularResponse(
            especie=CompanheiroEspecieItem(**especie_raw),
            elegibilidade=eleg,
            derivadas=CompanheiroEstatisticasDerivadas(**deriv),
        )

    def _aplicar_payload(
        self, entidade: CompanheiroAnimal, payload: CompanheiroAnimalUpsert
    ) -> None:
        entidade.especie_slug = payload.especie_slug
        entidade.nome = payload.nome.strip()
        entidade.forca = payload.forca
        entidade.destreza = payload.destreza
        entidade.constituicao = payload.constituicao
        entidade.inteligencia = payload.inteligencia
        entidade.sabedoria = payload.sabedoria
        entidade.carisma = payload.carisma
        entidade.bonus_atributos = dict(payload.bonus_atributos or {})
        entidade.hp_atual = payload.hp_atual
        entidade.hp_maximo = payload.hp_maximo
        entidade.ca = payload.ca
        entidade.iniciativa = payload.iniciativa
        entidade.deslocamento = payload.deslocamento
        entidade.truques = list(payload.truques or [])
        entidade.talentos = list(payload.talentos or [])
        entidade.pericias = list(payload.pericias or [])
        entidade.ataques = list(payload.ataques or [])
        entidade.anotacoes = payload.anotacoes

    def _to_response(
        self, entidade: CompanheiroAnimal, combatente
    ) -> CompanheiroAnimalResponse:
        especie_raw = especie_por_slug(entidade.especie_slug) or {}
        eleg = self._elegibilidade(combatente)
        deriv = None
        if eleg.elegivel and especie_raw:
            deriv_map = calcular_estatisticas(
                nivel_efetivo=eleg.nivel_efetivo,
                hd_base=especie_raw.get("hd_base", 1),
                atributos_base=especie_raw.get("atributos_base", {}),
                bonus_atributos=entidade.bonus_atributos or {},
                armadura_natural_base=especie_raw.get("armadura_natural_base", 0),
            )
            deriv = CompanheiroEstatisticasDerivadas(**deriv_map)

        return CompanheiroAnimalResponse(
            id=entidade.id,
            combatente_id=entidade.combatente_id,
            especie_slug=entidade.especie_slug,
            especie_nome=especie_raw.get("nome", entidade.especie_slug),
            nome=entidade.nome,
            forca=entidade.forca,
            destreza=entidade.destreza,
            constituicao=entidade.constituicao,
            inteligencia=entidade.inteligencia,
            sabedoria=entidade.sabedoria,
            carisma=entidade.carisma,
            bonus_atributos=entidade.bonus_atributos or {},
            hp_atual=entidade.hp_atual,
            hp_maximo=entidade.hp_maximo,
            ca=entidade.ca,
            iniciativa=entidade.iniciativa,
            deslocamento=entidade.deslocamento,
            truques=entidade.truques or [],
            talentos=entidade.talentos or [],
            pericias=entidade.pericias or [],
            ataques=entidade.ataques or [],
            anotacoes=entidade.anotacoes,
            derivadas=deriv,
            elegibilidade=eleg,
        )

    def obter(self, combatente_id: int) -> Optional[CompanheiroAnimalResponse]:
        try:
            combatente = self._combatente_or_raise(combatente_id)
            ent = self._repo.obter_por_combatente(combatente_id)
            if not ent:
                return None
            return self._to_response(ent, combatente)
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def elegibilidade(self, combatente_id: int) -> CompanheiroElegibilidadeResponse:
        combatente = self._combatente_or_raise(combatente_id)
        return self._elegibilidade(combatente)

    def salvar(
        self, combatente_id: int, payload: CompanheiroAnimalUpsert
    ) -> CompanheiroAnimalResponse:
        combatente = self._combatente_or_raise(combatente_id)
        eleg = self._elegibilidade(combatente)
        if not eleg.elegivel:
            raise ValueError(eleg.motivo or "Personagem não elegível.")

        if not especie_por_slug(payload.especie_slug):
            raise ValueError(f"Espécie inválida: {payload.especie_slug}")

        self._assert_sem_familiar(combatente_id)

        ent = self._repo.obter_por_combatente(combatente_id)
        if ent is None:
            ent = CompanheiroAnimal(combatente_id=combatente_id)
            self._aplicar_payload(ent, payload)
            ent = self._repo.criar(ent)
        else:
            self._aplicar_payload(ent, payload)
            ent = self._repo.atualizar(ent)
        if self._vinculo_arena:
            self._vinculo_arena.sync_companheiro(ent, combatente)
        return self._to_response(ent, combatente)

    def criar_a_partir_calculo(
        self, combatente_id: int, payload: CompanheiroCalcularRequest, nome: str
    ) -> CompanheiroAnimalResponse:
        calc = self.calcular(combatente_id, payload)
        d = calc.derivadas
        a = d.atributos_efetivos
        especie = calc.especie
        upsert = CompanheiroAnimalUpsert(
            especie_slug=payload.especie_slug,
            nome=nome.strip() or especie.nome,
            forca=a["forca"],
            destreza=a["destreza"],
            constituicao=a["constituicao"],
            inteligencia=a["inteligencia"],
            sabedoria=a["sabedoria"],
            carisma=a["carisma"],
            bonus_atributos=payload.bonus_atributos,
            hp_atual=d.hp_max_sugerido,
            hp_maximo=d.hp_max_sugerido,
            ca=d.ca,
            deslocamento=especie.deslocamento,
            truques=[],
            talentos=[],
            pericias=[],
            ataques=[{"nome": "Padrão", "descricao": especie.ataque_padrao}],
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
