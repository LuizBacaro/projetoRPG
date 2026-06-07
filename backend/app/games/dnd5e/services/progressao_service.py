"""Regras de negócio — progressão D&D 5e (HP, marcos, pendências)."""

from __future__ import annotations

from typing import Any, Dict, List

from app.games.dnd5e.models.personagem import Dnd5ePersonagem
from app.games.dnd5e.ports import Dnd5ePersonagemRepositoryProtocol
from app.games.dnd5e.rules.ficha import calcular_atributos_efetivos, montar_resumo_ficha
from app.games.dnd5e.rules.progressao import (
    ORCAMENTO_COMPRA_PONTOS,
    aplicar_marco_na_ficha,
    calcular_hp_max_total,
    montar_hp_resumo,
    gerar_scores_4d6,
    listar_pendencias,
    marcos_pendentes,
    matriz_padrao_scores,
    migrar_ficha_para_v2,
    niveis_hp_pendentes,
    normalizar_hp_rolls,
    normalizar_marcos,
    registrar_hp_roll_na_ficha,
    total_pontos_gastos,
    validar_marco,
    validar_nivel_vs_experiencia,
    validar_scores_base_por_metodo,
)
from app.games.dnd5e.schemas.personagem import (
    ficha_json_para_resposta,
    normalizar_ficha_para_gravacao,
)
from app.games.dnd5e.schemas.progressao import (
    Dnd5eGerarAtributosResponse,
    Dnd5eHpRollEntry,
    Dnd5eHpRollResponse,
    Dnd5eMarcoResponse,
    Dnd5ePendenciasProgressaoResponse,
)
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos


class Dnd5eProgressaoService:
    def __init__(self, repo: Dnd5ePersonagemRepositoryProtocol):
        self.repo = repo

    def obter_ent(self, personagem_id: int) -> Dnd5ePersonagem:
        ent = self.repo.get_by_id(personagem_id)
        if not ent:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        return ent

    @staticmethod
    def gerar_atributos(
        metodo: str, *, seed: int | None = None
    ) -> Dnd5eGerarAtributosResponse:
        met = (metodo or "padrao").strip().lower()
        if met == "4d6":
            scores = gerar_scores_4d6(seed=seed)
        elif met == "pontos":
            scores = {k: 8 for k in matriz_padrao_scores()}
            validar_scores_base_por_metodo(scores, "pontos")
            return Dnd5eGerarAtributosResponse(
                metodo=met,
                scores_base=scores,
                pontos_gastos=0,
                orcamento_pontos=ORCAMENTO_COMPRA_PONTOS,
            )
        else:
            scores = matriz_padrao_scores()
            met = "padrao"
        validar_scores_base_por_metodo(scores, met)
        return Dnd5eGerarAtributosResponse(
            metodo=met,
            scores_base=scores,
            pontos_gastos=total_pontos_gastos(scores) if met == "pontos" else None,
            orcamento_pontos=ORCAMENTO_COMPRA_PONTOS if met == "pontos" else None,
        )

    def _ficha_atual(self, ent: Dnd5ePersonagem) -> Dict[str, Any]:
        return migrar_ficha_para_v2(ficha_json_para_resposta(ent.ficha_json))

    def _scores_efetivos(
        self, ent: Dnd5ePersonagem, ficha: Dict[str, Any]
    ) -> Dict[str, int]:
        scores_base = dict(ficha.get("scores_base") or {})
        if not scores_base:
            scores_base = {
                "strength": ent.strength,
                "dexterity": ent.dexterity,
                "constitution": ent.constitution,
                "intelligence": ent.intelligence,
                "wisdom": ent.wisdom,
                "charisma": ent.charisma,
            }
        raca_slug = (ficha.get("raca_slug") or "").strip()
        if not raca_slug:
            return scores_base
        efetivos = calcular_atributos_efetivos(
            scores_base,
            raca_slug,
            bonus_habilidade_extra=ficha.get("bonus_habilidade_extra"),
        )
        bonus_feat = dict(ficha.get("bonus_atributo_feat") or {})
        for chave, delta in bonus_feat.items():
            if chave in efetivos:
                efetivos[chave] = int(efetivos[chave]) + int(delta)
        return efetivos

    def _classe_slug(self, ficha: Dict[str, Any]) -> str:
        return (ficha.get("classe_slug") or "").strip().lower()

    def _con_mod(self, ent: Dnd5ePersonagem, ficha: Dict[str, Any]) -> int:
        scores = self._scores_efetivos(ent, ficha)
        return (int(scores.get("constitution", ent.constitution)) - 10) // 2

    def pendencias(self, personagem_id: int) -> Dnd5ePendenciasProgressaoResponse:
        ent = self.obter_ent(personagem_id)
        ficha = self._ficha_atual(ent)
        classe_slug = self._classe_slug(ficha)
        con_mod = self._con_mod(ent, ficha)
        prog = ficha.get("progressao") or {}
        hp_rolls = normalizar_hp_rolls(prog.get("hp_rolls") or [])
        marcos = normalizar_marcos(prog.get("marcos") or [])
        hp1 = (
            montar_resumo_ficha(
                raca_slug=ficha.get("raca_slug") or "humano",
                classe_slug=classe_slug or "guerreiro",
                scores_base=ficha.get("scores_base")
                or {
                    "strength": ent.strength,
                    "dexterity": ent.dexterity,
                    "constitution": ent.constitution,
                    "intelligence": ent.intelligence,
                    "wisdom": ent.wisdom,
                    "charisma": ent.charisma,
                },
                nivel=ent.nivel,
                ficha_progressao=ficha,
                feats=ficha.get("feats"),
            )["hp_max_nivel_1"]
            if classe_slug
            else max(1, ent.hp_max)
        )
        raca_slug = (ficha.get("raca_slug") or "").strip()
        feats = list(ficha.get("feats") or [])
        hp_max = (
            calcular_hp_max_total(
                classe_slug,
                con_mod,
                ent.nivel,
                hp_rolls,
                raca_slug=raca_slug,
                feats=feats,
            )
            if classe_slug
            else max(1, ent.hp_max)
        )
        hp_resumo = (
            montar_hp_resumo(
                classe_slug,
                con_mod,
                ent.nivel,
                hp_rolls,
                raca_slug=raca_slug,
                feats=feats,
            )
            if classe_slug
            else None
        )
        return Dnd5ePendenciasProgressaoResponse(
            pendencias=listar_pendencias(
                nivel=ent.nivel,
                classe_slug=classe_slug,
                con_mod=con_mod,
                ficha=ficha,
            ),
            hp_max=hp_max,
            hp_max_nivel_1=hp1,
            hp_resumo=hp_resumo,
            marcos_pendentes=marcos_pendentes(ent.nivel, marcos),
            niveis_hp_pendentes=niveis_hp_pendentes(ent.nivel, hp_rolls),
        )

    def registrar_hp_roll(
        self,
        personagem_id: int,
        *,
        nivel: int,
        roll: int | None = None,
        usar_media: bool = False,
    ) -> Dnd5eHpRollResponse:
        ent = self.obter_ent(personagem_id)
        ficha = self._ficha_atual(ent)
        classe_slug = self._classe_slug(ficha)
        if not classe_slug:
            raise DadosInvalidos("Defina a classe na ficha antes de rolar PV")
        if nivel > ent.nivel:
            raise DadosInvalidos(
                f"Nível de rolagem ({nivel}) excede nível do personagem ({ent.nivel})"
            )
        try:
            validar_nivel_vs_experiencia(ent.nivel, ent.experiencia)
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e

        con_mod = self._con_mod(ent, ficha)
        try:
            ficha_nova, entrada = registrar_hp_roll_na_ficha(
                ficha,
                nivel=nivel,
                classe_slug=classe_slug,
                con_mod=con_mod,
                roll=roll,
                usar_media=usar_media,
            )
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e

        raca_slug = (ficha_nova.get("raca_slug") or "").strip()
        feats = list(ficha_nova.get("feats") or [])
        hp_max = calcular_hp_max_total(
            classe_slug,
            con_mod,
            ent.nivel,
            ficha_nova["progressao"]["hp_rolls"],
            raca_slug=raca_slug,
            feats=feats,
        )
        ent.ficha_json = normalizar_ficha_para_gravacao(ficha_nova)
        ent.hp_max = hp_max
        if (ent.hp_atual or 0) > hp_max:
            ent.hp_atual = hp_max
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        return Dnd5eHpRollResponse(
            entrada=Dnd5eHpRollEntry(**entrada),
            hp_max=hp_max,
            ficha=ficha_json_para_resposta(ent.ficha_json),
        )

    def registrar_marco(
        self,
        personagem_id: int,
        *,
        nivel: int,
        tipo: str,
        slug: str | None = None,
        distribuicao: Dict[str, int] | None = None,
    ) -> Dnd5eMarcoResponse:
        ent = self.obter_ent(personagem_id)
        ficha = self._ficha_atual(ent)
        classe_slug = self._classe_slug(ficha)
        scores_efetivos = self._scores_efetivos(ent, ficha)
        marco: Dict[str, Any] = {
            "nivel": nivel,
            "tipo": (tipo or "").strip().lower(),
        }
        if marco["tipo"] == "feat":
            marco["slug"] = (slug or "").strip().lower()
        elif marco["tipo"] == "asi":
            marco["distribuicao"] = dict(distribuicao or {})
        else:
            raise DadosInvalidos("Marco deve ser tipo feat ou asi")

        try:
            validar_marco(
                marco,
                ficha=ficha,
                nivel=ent.nivel,
                scores_efetivos=scores_efetivos,
            )
            ficha_nova = aplicar_marco_na_ficha(ficha, marco)
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e

        con_mod = self._con_mod(ent, ficha_nova)
        hp_rolls = (ficha_nova.get("progressao") or {}).get("hp_rolls") or []
        raca_slug = (ficha_nova.get("raca_slug") or "").strip()
        feats = list(ficha_nova.get("feats") or [])
        hp_max = (
            calcular_hp_max_total(
                classe_slug,
                con_mod,
                ent.nivel,
                hp_rolls,
                raca_slug=raca_slug,
                feats=feats,
            )
            if classe_slug
            else max(1, ent.hp_max)
        )
        ent.ficha_json = normalizar_ficha_para_gravacao(ficha_nova)
        ent.hp_max = hp_max
        if (ent.hp_atual or 0) > hp_max:
            ent.hp_atual = hp_max
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)

        pendencias: List[str] = listar_pendencias(
            nivel=ent.nivel,
            classe_slug=classe_slug,
            con_mod=con_mod,
            ficha=ficha_nova,
        )
        return Dnd5eMarcoResponse(
            marco=marco,
            hp_max=hp_max,
            ficha=ficha_json_para_resposta(ent.ficha_json),
            pendencias=pendencias,
        )
