"""Estado de conjuração persistido em ficha_json.conjuracao."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from fastapi import HTTPException

from app.games.dnd5e.data.spell_tables import SHORT_REST_RECOVER_ALL
from app.games.dnd5e.models.grimorio import Dnd5eGrimorioMagia
from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.repositories.personagem_repository import Dnd5ePersonagemRepository
from app.games.dnd5e.rules.magia import (
    custo_ponto_feiticaria_criar_slot,
    espacos_por_classe_nivel,
    habilidade_primaria_classe,
    max_nivel_magia_conjuravel,
    pontos_feiticaria_max,
    recuperacao_arcana_max_niveis_slot,
    truque_multiplicador_dados,
)
from app.games.dnd5e.schemas.conjuracao import (
    Dnd5eConjuracaoEstadoResponse,
    Dnd5eSlotNivelItem,
)
from app.games.dnd5e.services.conjuracao_shared import (
    FULL_SPELL_LIST_PREPARED_CLASSES,
    classe_prepara_magias,
    classe_slug_ficha,
    contar_magias_conhecidas_grimorio,
    contar_magias_preparadas_com_nivel,
    magias_conhecidas_max,
    magias_preparadas_max,
    modo_lista_conjuracao,
    normalizar_magias_preparadas_qty,
    somar_qty_preparadas_por_nivel,
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
    pf_max = pontos_feiticaria_max(classe, nivel)
    return {
        "classe": classe,
        "espacos_usados": [0] * len(totais),
        "slots_bonus_pf": [0] * len(totais),
        "magias_preparadas_ids": [],
        "magias_preparadas_qty": {},
        "magias_lancadas_ids": [],
        "magia_concentracao_id": None,
        "pontos_feiticaria_atual": pf_max if pf_max else None,
        "recuperacao_arcana_usada": False,
    }


def _normalizar_slots_bonus(conj: dict, tamanho: int) -> list[int]:
    bonus = list(conj.get("slots_bonus_pf") or [])
    if len(bonus) < tamanho:
        bonus.extend([0] * (tamanho - len(bonus)))
    return bonus[:tamanho]


def _pontos_feiticaria_atual(conj: dict, classe: str, nivel: int) -> Optional[int]:
    maximo = pontos_feiticaria_max(classe, nivel)
    if maximo <= 0:
        return None
    atual = conj.get("pontos_feiticaria_atual")
    if atual is None:
        return maximo
    return max(0, min(maximo, int(atual)))


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
    lancadas = base.get("magias_lancadas_ids")
    if not isinstance(lancadas, list):
        base["magias_lancadas_ids"] = []
    base["magias_preparadas_qty"] = normalizar_magias_preparadas_qty(
        base.get("magias_preparadas_qty")
    )
    base["slots_bonus_pf"] = _normalizar_slots_bonus(base, len(totais))
    pf_max = pontos_feiticaria_max(classe, nivel)
    if pf_max > 0 and base.get("pontos_feiticaria_atual") is None:
        base["pontos_feiticaria_atual"] = pf_max
    return base


def _magias_preparadas_max(personagem, classe: str, nivel: int) -> Optional[int]:
    mod = _mod_habilidade(personagem, classe)
    return magias_preparadas_max(classe, nivel, mod)


class Dnd5eConjuracaoFichaService:
    def __init__(
        self,
        personagem_repo: Dnd5ePersonagemRepository,
        grimorio_repo: Dnd5eGrimorioRepository,
        magia_repo: Dnd5eMagiaRepository,
    ):
        self.personagem_repo = personagem_repo
        self.grimorio_repo = grimorio_repo
        self.magia_repo = magia_repo

    def _nivel_magia(self, magia_id: int) -> int:
        row = self.magia_repo.obter(magia_id)
        return int(row.nivel or 0) if row else 0

    def _magia_na_lista_classe(self, magia_id: int, classe_grim: str) -> bool:
        row = self.magia_repo.obter(magia_id)
        if not row:
            return False
        return any(
            (link.classe_slug or "").strip().lower() == classe_grim
            for link in (row.classes_niveis or [])
        )

    def _garantir_magia_no_grimorio(
        self,
        personagem_id: int,
        magia_id: int,
        classe: str,
        classe_grim: str,
    ) -> None:
        if self.grimorio_repo.obter_item(personagem_id, magia_id, classe_grim):
            return
        if classe not in FULL_SPELL_LIST_PREPARED_CLASSES:
            raise HTTPException(
                status_code=422,
                detail=f"Magia {magia_id} não está no grimório",
            )
        if not self._magia_na_lista_classe(magia_id, classe_grim):
            raise HTTPException(
                status_code=422,
                detail="Magia não pertence à lista da classe",
            )
        self.grimorio_repo.adicionar(
            Dnd5eGrimorioMagia(
                personagem_id=personagem_id,
                magia_id=magia_id,
                classe=classe_grim,
                origem="PREPARACAO_CATALOGO",
            )
        )

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
            raise HTTPException(
                status_code=422, detail="Personagem sem classe conjuradora"
            )
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        usados = conj["espacos_usados"]
        bonus = _normalizar_slots_bonus(conj, len(totais))
        slots = []
        for nivel, total in enumerate(totais):
            if nivel == 0 or total <= 0:
                continue
            u = usados[nivel] if nivel < len(usados) else 0
            b = bonus[nivel] if nivel < len(bonus) else 0
            slots.append(
                Dnd5eSlotNivelItem(
                    nivel=nivel,
                    total=total + b,
                    usados=u,
                    disponiveis=max(0, total + b - u),
                )
            )
        pf_max = pontos_feiticaria_max(classe, p.nivel)
        pf_atual = _pontos_feiticaria_atual(conj, classe, p.nivel)
        arcana_max = (
            recuperacao_arcana_max_niveis_slot(p.nivel) if classe == "mago" else None
        )
        classe_grim = _classe_lista_magias(classe)
        _, itens = self.grimorio_repo.listar_paginado(
            personagem_id, classe=classe_grim, limit=500
        )
        prep_ids = [int(x) for x in (conj.get("magias_preparadas_ids") or [])]
        prep_qty = normalizar_magias_preparadas_qty(conj.get("magias_preparadas_qty"))
        lancadas_ids = [int(x) for x in (conj.get("magias_lancadas_ids") or [])]
        return Dnd5eConjuracaoEstadoResponse(
            classe=classe,
            nivel_personagem=p.nivel,
            habilidade_primaria=habilidade_primaria_classe(classe),
            modo_lista=modo_lista_conjuracao(classe),
            max_nivel_magia=max_nivel_magia_conjuravel(classe, p.nivel),
            prepara_magias=classe_prepara_magias(classe),
            magias_conhecidas_max=magias_conhecidas_max(classe, p.nivel),
            magias_conhecidas_atual=contar_magias_conhecidas_grimorio(itens),
            magias_preparadas_max=_magias_preparadas_max(p, classe, p.nivel),
            magias_preparadas_ids=prep_ids,
            magias_preparadas_qty=prep_qty,
            magias_lancadas_ids=lancadas_ids,
            slots=slots,
            magia_concentracao_id=conj.get("magia_concentracao_id"),
            recupera_slots_repouso_curto=classe in SHORT_REST_RECOVER_ALL,
            truque_multiplicador_dados=truque_multiplicador_dados(p.nivel),
            pontos_feiticaria_atual=pf_atual,
            pontos_feiticaria_max=pf_max if pf_max > 0 else None,
            recuperacao_arcana_disponivel=classe == "mago"
            and not bool(conj.get("recuperacao_arcana_usada")),
            recuperacao_arcana_max_niveis=arcana_max,
        )

    def _salvar_conjuracao(self, personagem, ficha: dict, conj: dict) -> None:
        ficha = deepcopy(ficha)
        ficha["conjuracao"] = conj
        personagem.ficha_json = ficha
        commit_with_rollback(self.personagem_repo.db)
        self.personagem_repo.db.refresh(personagem)

    def gastar_slot(
        self,
        personagem_id: int,
        nivel_magia: int,
        quantidade: int = 1,
        magia_id: Optional[int] = None,
    ) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        if nivel_magia < 0 or nivel_magia >= len(totais):
            raise HTTPException(status_code=422, detail="Nível de magia inválido")
        if nivel_magia >= 1:
            usados = conj["espacos_usados"]
            bonus = _normalizar_slots_bonus(conj, len(totais))
            disp = totais[nivel_magia] + bonus[nivel_magia] - usados[nivel_magia]
            if disp < quantidade:
                raise HTTPException(status_code=422, detail="Sem espaços disponíveis")
            usados[nivel_magia] += quantidade
            conj["slots_bonus_pf"] = bonus
        if magia_id is not None:
            lancadas = list(conj.get("magias_lancadas_ids") or [])
            if int(magia_id) not in lancadas:
                lancadas.append(int(magia_id))
            conj["magias_lancadas_ids"] = lancadas
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def devolver_slot(
        self,
        personagem_id: int,
        nivel_magia: int,
        quantidade: int = 1,
        magia_id: Optional[int] = None,
    ) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        if nivel_magia < 0 or nivel_magia >= len(totais):
            raise HTTPException(status_code=422, detail="Nível de magia inválido")
        if nivel_magia >= 1:
            usados = conj["espacos_usados"]
            if usados[nivel_magia] < quantidade:
                raise HTTPException(
                    status_code=422, detail="Nenhum espaço usado neste nível"
                )
            usados[nivel_magia] -= quantidade
        if magia_id is not None:
            lancadas = [
                int(x)
                for x in (conj.get("magias_lancadas_ids") or [])
                if int(x) != int(magia_id)
            ]
            conj["magias_lancadas_ids"] = lancadas
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def preparar_magias(
        self,
        personagem_id: int,
        magia_ids: list[int],
        magias_quantidade: Optional[dict] = None,
    ) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        if not classe_prepara_magias(classe):
            raise HTTPException(
                status_code=400, detail="Esta classe não prepara magias diariamente"
            )
        max_prep = _magias_preparadas_max(p, classe, p.nivel) or 1
        classe_grim = _classe_lista_magias(classe)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        conj = _get_conjuracao(ficha, classe, p.nivel)
        qty_map = normalizar_magias_preparadas_qty(
            magias_quantidade
            if magias_quantidade is not None
            else conj.get("magias_preparadas_qty")
        )

        for mid in magia_ids:
            chave = str(int(mid))
            if chave not in qty_map:
                qty_map[chave] = 1

        ids_ativos = sorted({int(chave) for chave, qtd in qty_map.items() if qtd > 0})
        niveis = {int(mid): self._nivel_magia(int(mid)) for mid in ids_ativos}

        if contar_magias_preparadas_com_nivel(ids_ativos, niveis) > max_prep:
            raise HTTPException(
                status_code=422,
                detail=f"Máximo de {max_prep} magias preparadas (truques não contam)",
            )

        soma_por_nivel = somar_qty_preparadas_por_nivel(qty_map, niveis)
        for nivel_slot, soma in soma_por_nivel.items():
            limite = totais[nivel_slot] if nivel_slot < len(totais) else 0
            if soma > limite:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Preparação excede os {limite} espaço(s) de magia "
                        f"do nível {nivel_slot}"
                    ),
                )

        for mid in ids_ativos:
            self._garantir_magia_no_grimorio(
                personagem_id, int(mid), classe, classe_grim
            )

        conj["magias_preparadas_ids"] = ids_ativos
        conj["magias_preparadas_qty"] = {
            chave: qtd for chave, qtd in qty_map.items() if qtd > 0
        }
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def descanso_longo(self, personagem_id: int) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        conj["espacos_usados"] = [0] * len(totais)
        conj["slots_bonus_pf"] = [0] * len(totais)
        conj["magia_concentracao_id"] = None
        conj["magias_lancadas_ids"] = []
        conj["recuperacao_arcana_usada"] = False
        pf_max = pontos_feiticaria_max(classe, p.nivel)
        if pf_max > 0:
            conj["pontos_feiticaria_atual"] = pf_max
        if classe_prepara_magias(classe):
            conj["magias_preparadas_ids"] = []
            conj["magias_preparadas_qty"] = {}
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def descanso_curto(self, personagem_id: int) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        conj = _get_conjuracao(ficha, classe, p.nivel)
        if classe in SHORT_REST_RECOVER_ALL:
            totais = espacos_por_classe_nivel(classe, p.nivel)
            conj["espacos_usados"] = [0] * len(totais)
            conj["magias_lancadas_ids"] = []
            self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def criar_slot_pontos_feiticaria(
        self, personagem_id: int, nivel_slot: int
    ) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        if classe not in ("feiticeiro", "sorcerer"):
            raise HTTPException(
                status_code=400, detail="Pontos de feitiçaria só para Feiticeiro"
            )
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        try:
            custo = custo_ponto_feiticaria_criar_slot(nivel_slot)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        atual = _pontos_feiticaria_atual(conj, classe, p.nivel) or 0
        if atual < custo:
            raise HTTPException(
                status_code=422,
                detail=f"Pontos insuficientes (precisa {custo}, tem {atual})",
            )
        bonus = _normalizar_slots_bonus(conj, len(totais))
        bonus[nivel_slot] += 1
        conj["pontos_feiticaria_atual"] = atual - custo
        conj["slots_bonus_pf"] = bonus
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def converter_slot_pontos_feiticaria(
        self, personagem_id: int, nivel_slot: int
    ) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        if classe not in ("feiticeiro", "sorcerer"):
            raise HTTPException(
                status_code=400, detail="Pontos de feitiçaria só para Feiticeiro"
            )
        conj = _get_conjuracao(ficha, classe, p.nivel)
        totais = espacos_por_classe_nivel(classe, p.nivel)
        usados = conj["espacos_usados"]
        bonus = _normalizar_slots_bonus(conj, len(totais))
        disp = totais[nivel_slot] + bonus[nivel_slot] - usados[nivel_slot]
        if disp < 1:
            raise HTTPException(
                status_code=422, detail="Sem espaço disponível para converter"
            )
        pf_max = pontos_feiticaria_max(classe, p.nivel)
        atual = _pontos_feiticaria_atual(conj, classe, p.nivel) or 0
        if atual + nivel_slot > pf_max:
            raise HTTPException(
                status_code=422,
                detail=f"Excede o máximo de {pf_max} pontos de feitiçaria",
            )
        usados[nivel_slot] += 1
        conj["pontos_feiticaria_atual"] = atual + nivel_slot
        conj["slots_bonus_pf"] = bonus
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def recuperacao_arcana(
        self, personagem_id: int, slots: dict[int, int]
    ) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        if classe != "mago":
            raise HTTPException(
                status_code=400, detail="Recuperação arcana só para Mago"
            )
        conj = _get_conjuracao(ficha, classe, p.nivel)
        if conj.get("recuperacao_arcana_usada"):
            raise HTTPException(
                status_code=400,
                detail="Recuperação arcana já usada desde o último descanso longo",
            )
        max_niveis = recuperacao_arcana_max_niveis_slot(p.nivel)
        gasto = sum(int(n) * int(q) for n, q in slots.items())
        if gasto <= 0:
            raise HTTPException(status_code=422, detail="Informe slots a recuperar")
        if gasto > max_niveis:
            raise HTTPException(
                status_code=422,
                detail=f"Máximo de {max_niveis} níveis de slot recuperáveis",
            )
        usados = conj["espacos_usados"]
        for nivel, qtd in slots.items():
            if usados[nivel] < qtd:
                raise HTTPException(
                    status_code=422,
                    detail=f"Sem {qtd} espaço(s) usado(s) no nível {nivel}",
                )
        for nivel, qtd in slots.items():
            usados[nivel] -= qtd
        conj["recuperacao_arcana_usada"] = True
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)

    def definir_concentracao(
        self, personagem_id: int, magia_id: Optional[int]
    ) -> Dnd5eConjuracaoEstadoResponse:
        p = self._personagem(personagem_id)
        ficha = deepcopy(dict(p.ficha_json or {}))
        classe = classe_slug_ficha(ficha)
        conj = _get_conjuracao(ficha, classe, p.nivel)
        conj["magia_concentracao_id"] = int(magia_id) if magia_id else None
        self._salvar_conjuracao(p, ficha, conj)
        return self.obter_estado(personagem_id)
