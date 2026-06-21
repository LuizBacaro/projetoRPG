"""Regras de negócio — progressão D&D 5e (HP, marcos, pendências)."""

from __future__ import annotations

from typing import Any, Dict, List

from app.games.dnd5e.models.personagem import Dnd5ePersonagem
from app.games.dnd5e.ports import Dnd5ePersonagemRepositoryProtocol
from app.games.dnd5e.rules.ficha import calcular_atributos_efetivos, montar_resumo_ficha
from app.games.dnd5e.rules.pericias import (
    aplicar_pericias_override,
    calcular_slots_expertise_classe,
    montar_expertise_efetiva,
    montar_proficiencias_automaticas,
    validar_expertise_pericias_classe,
    validar_pericias_override,
)
from app.games.dnd5e.rules.progressao import (
    ORCAMENTO_COMPRA_PONTOS,
    aplicar_marco_na_ficha,
    aplicar_retroativo_con_hp_na_ficha,
    calcular_cura_repouso_longo,
    calcular_hp_max_total,
    gerar_scores_4d6,
    listar_pendencias,
    marcos_pendentes,
    matriz_padrao_scores,
    mesclar_feat_escolhas,
    migrar_ficha_para_v2,
    montar_hp_resumo,
    niveis_hp_pendentes,
    normalizar_hp_rolls,
    normalizar_marcos,
    registrar_hp_roll_na_ficha,
    total_pontos_gastos,
    validar_feat_escolhas_ficha,
    validar_marco,
    validar_nivel_vs_experiencia,
    validar_scores_base_por_metodo,
)
from app.games.dnd5e.schemas.personagem import (
    ficha_json_para_resposta,
    normalizar_ficha_para_gravacao,
)
from app.games.dnd5e.schemas.progressao import (
    Dnd5eExpertisePericiasResponse,
    Dnd5eFeatEscolhasRequest,
    Dnd5eFeatEscolhasResponse,
    Dnd5eGerarAtributosResponse,
    Dnd5eHpRollEntry,
    Dnd5eHpRollResponse,
    Dnd5eMarcoResponse,
    Dnd5ePendenciasProgressaoResponse,
    Dnd5ePericiasOverrideRequest,
    Dnd5ePericiasOverrideResponse,
    Dnd5eRepousoLongoCuraItem,
    Dnd5eRepousoLongoResponse,
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
        f = migrar_ficha_para_v2(ficha)
        return (f.get("classe_slug") or f.get("classe") or "").strip().lower()

    def _raca_slug(self, ficha: Dict[str, Any]) -> str:
        f = migrar_ficha_para_v2(ficha)
        return (f.get("raca_slug") or f.get("raca") or "").strip().lower()

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
            marcos_pendentes=marcos_pendentes(ent.nivel, marcos, raca_slug=raca_slug),
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
        feat_escolhas: Dict[str, Any] | None = None,
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
            if feat_escolhas:
                marco["feat_escolhas"] = dict(feat_escolhas)
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
            con_mod_antes = self._con_mod(ent, ficha)
            hp_rolls_antes = normalizar_hp_rolls(
                (ficha.get("progressao") or {}).get("hp_rolls") or []
            )
            raca_slug = (ficha.get("raca_slug") or "").strip()
            feats_antes = list(ficha.get("feats") or [])
            hp_max_antes = (
                calcular_hp_max_total(
                    classe_slug,
                    con_mod_antes,
                    ent.nivel,
                    hp_rolls_antes,
                    raca_slug=raca_slug,
                    feats=feats_antes,
                )
                if classe_slug
                else max(1, ent.hp_max)
            )

            ficha_nova = aplicar_marco_na_ficha(ficha, marco)
            con_mod_depois = self._con_mod(ent, ficha_nova)
            if con_mod_depois > con_mod_antes:
                ficha_nova = aplicar_retroativo_con_hp_na_ficha(
                    ficha_nova,
                    con_mod_novo=con_mod_depois,
                    nivel=ent.nivel,
                )
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e

        hp_rolls = (ficha_nova.get("progressao") or {}).get("hp_rolls") or []
        raca_slug = (ficha_nova.get("raca_slug") or "").strip()
        feats = list(ficha_nova.get("feats") or [])
        hp_max = (
            calcular_hp_max_total(
                classe_slug,
                con_mod_depois,
                ent.nivel,
                hp_rolls,
                raca_slug=raca_slug,
                feats=feats,
            )
            if classe_slug
            else max(1, ent.hp_max)
        )
        hp_retroativo = 0
        if con_mod_depois > con_mod_antes:
            hp_retroativo = max(0, hp_max - hp_max_antes)
            ent.hp_atual = min(hp_max, (ent.hp_atual or 0) + hp_retroativo)
        elif (ent.hp_atual or 0) > hp_max:
            ent.hp_atual = hp_max
        ent.ficha_json = normalizar_ficha_para_gravacao(ficha_nova)
        ent.hp_max = hp_max
        self.repo.db.refresh(ent)

        pendencias: List[str] = listar_pendencias(
            nivel=ent.nivel,
            classe_slug=classe_slug,
            con_mod=con_mod_depois,
            ficha=ficha_nova,
        )
        return Dnd5eMarcoResponse(
            marco=marco,
            hp_max=hp_max,
            hp_atual=ent.hp_atual or hp_max,
            hp_retroativo_con=hp_retroativo,
            ficha=ficha_json_para_resposta(ent.ficha_json),
            pendencias=pendencias,
        )

    def salvar_feat_escolhas(
        self,
        personagem_id: int,
        feat_escolhas: Dict[str, Any],
    ) -> Dnd5eFeatEscolhasResponse:
        ent = self.obter_ent(personagem_id)
        ficha = self._ficha_atual(ent)
        try:
            ficha_nova = mesclar_feat_escolhas(ficha, feat_escolhas)
            validar_feat_escolhas_ficha(ficha_nova)
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e
        ent.ficha_json = normalizar_ficha_para_gravacao(ficha_nova)
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        classe_slug = self._classe_slug(ficha_nova)
        con_mod = self._con_mod(ent, ficha_nova)
        pendencias = listar_pendencias(
            nivel=ent.nivel,
            classe_slug=classe_slug,
            con_mod=con_mod,
            ficha=ficha_nova,
        )
        ficha_resp = ficha_json_para_resposta(ent.ficha_json)
        return Dnd5eFeatEscolhasResponse(
            feat_escolhas=dict(ficha_resp.get("feat_escolhas") or {}),
            ficha=ficha_resp,
            pendencias=pendencias,
        )

    def salvar_pericias_override(
        self,
        personagem_id: int,
        pericias_override: Dict[str, Any],
    ) -> Dnd5ePericiasOverrideResponse:
        ent = self.obter_ent(personagem_id)
        ficha = self._ficha_atual(ent)
        try:
            norm = validar_pericias_override(pericias_override)
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e
        ficha_nova = dict(migrar_ficha_para_v2(ficha))
        ficha_nova["pericias_override"] = norm
        ent.ficha_json = normalizar_ficha_para_gravacao(ficha_nova)
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)

        classe_slug = self._classe_slug(ficha_nova)
        raca_slug = self._raca_slug(ficha_nova)
        if not classe_slug:
            raise DadosInvalidos(
                "Ficha sem classe definida — salve raça e classe antes de editar perícias."
            )
        con_mod = self._con_mod(ent, ficha_nova)
        try:
            prof_auto = montar_proficiencias_automaticas(
                classe_slug=classe_slug,
                raca_slug=raca_slug or "humano",
                antecedente_slug=ficha_nova.get("antecedente_slug"),
                pericias_classe_escolhidas=ficha_nova.get("pericias_classe_escolhidas")
                or [],
                pericia_racial_extra=ficha_nova.get("pericia_racial_extra"),
                feats=ficha_nova.get("feats") or [],
                feat_escolhas=ficha_nova.get("feat_escolhas"),
            )
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e
        prof_final = aplicar_pericias_override(prof_auto, norm)
        pendencias = listar_pendencias(
            nivel=ent.nivel,
            classe_slug=classe_slug,
            con_mod=con_mod,
            ficha=ficha_nova,
        )
        ficha_resp = ficha_json_para_resposta(ent.ficha_json)
        return Dnd5ePericiasOverrideResponse(
            pericias_override=norm,
            pericias_proficientes=prof_final,
            pericias_automaticas=prof_auto,
            ficha=ficha_resp,
            pendencias=pendencias,
        )

    def salvar_expertise_pericias(
        self,
        personagem_id: int,
        expertise_pericias: List[str],
    ) -> Dnd5eExpertisePericiasResponse:
        ent = self.obter_ent(personagem_id)
        ficha = self._ficha_atual(ent)
        classe_slug = self._classe_slug(ficha)
        raca_slug = self._raca_slug(ficha)
        if not classe_slug:
            raise DadosInvalidos(
                "Ficha sem classe definida — salve raça e classe antes de expertise."
            )
        try:
            prof_auto = montar_proficiencias_automaticas(
                classe_slug=classe_slug,
                raca_slug=raca_slug or "humano",
                antecedente_slug=ficha.get("antecedente_slug"),
                pericias_classe_escolhidas=ficha.get("pericias_classe_escolhidas")
                or [],
                pericia_racial_extra=ficha.get("pericia_racial_extra"),
                feats=ficha.get("feats") or [],
                feat_escolhas=ficha.get("feat_escolhas"),
            )
            prof_final = aplicar_pericias_override(
                prof_auto, ficha.get("pericias_override")
            )
            norm = validar_expertise_pericias_classe(
                expertise_pericias,
                classe_slug=classe_slug,
                nivel=ent.nivel,
                proficientes=prof_final,
            )
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e
        ficha_nova = dict(ficha)
        ficha_nova["expertise_pericias"] = norm
        ent.ficha_json = normalizar_ficha_para_gravacao(ficha_nova)
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        con_mod = self._con_mod(ent, ficha_nova)
        pendencias = listar_pendencias(
            nivel=ent.nivel,
            classe_slug=classe_slug,
            con_mod=con_mod,
            ficha=ficha_nova,
        )
        ficha_resp = ficha_json_para_resposta(ent.ficha_json)
        expertise_efetiva = montar_expertise_efetiva(
            norm,
            feats=ficha_nova.get("feats") or [],
            feat_escolhas=ficha_nova.get("feat_escolhas"),
        )
        return Dnd5eExpertisePericiasResponse(
            expertise_pericias=norm,
            expertise_efetiva=expertise_efetiva,
            expertise_slots_classe=calcular_slots_expertise_classe(
                classe_slug, ent.nivel
            ),
            ficha=ficha_resp,
            pendencias=pendencias,
        )

    def aplicar_repouso_longo(self, personagem_id: int) -> Dnd5eRepousoLongoResponse:
        ent = self.obter_ent(personagem_id)
        ficha = self._ficha_atual(ent)
        con_mod = self._con_mod(ent, ficha)
        cura_total, detalhes = calcular_cura_repouso_longo(ent.nivel, con_mod)
        hp_max = max(1, int(ent.hp_max or 1))
        hp_antes = max(0, int(ent.hp_atual or 0))
        hp_depois = min(hp_max, hp_antes + cura_total)
        ent.hp_atual = hp_depois
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        partes = []
        if cura_total > 0:
            partes.append(f"+{hp_depois - hp_antes} PV")
        elif ent.nivel <= 1:
            partes.append("Nível 1 — sem rolagens de repouso")
        else:
            partes.append("PV já no máximo")
        return Dnd5eRepousoLongoResponse(
            hp_atual=hp_depois,
            hp_max=hp_max,
            cura_total=hp_depois - hp_antes,
            cura_niveis=[Dnd5eRepousoLongoCuraItem(**item) for item in detalhes],
            mensagem="Repouso longo: " + ", ".join(partes),
        )
