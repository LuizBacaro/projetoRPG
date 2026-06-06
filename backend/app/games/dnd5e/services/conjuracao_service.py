"""Resolução de conjuração na arena — catálogo, grimório, slots, CD e concentração."""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException

from app.games.dnd5e.data.spell_tables import PREPARED_CLASSES
from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.rules.combate import (
    ataque_atinge_ca,
    calcular_dano,
    resumo_modificadores_ataque,
    rolar_d20_ataque,
)
from app.games.dnd5e.rules.habilidades import calcular_bonus_proficiencia
from app.games.dnd5e.rules.magia import (
    Conjurador,
    Magia,
    calcular_dc_magia,
    componentes_resumo,
    escalar_dano_upcast,
    escalar_expressao_dano_truque,
    save_causa_metade_dano,
    habilidade_primaria_classe,
    lancar_magia,
    salvaguarda_atinge_dc,
    teste_concentracao,
)
from app.games.dnd5e.schemas.combate import (
    Dnd5eConcentracaoTesteRequest,
    Dnd5eConcentracaoTesteResponse,
    Dnd5eConjurarRequest,
    Dnd5eConjurarResponse,
)


def _mod_por_habilidade(payload: Dnd5eConjurarRequest) -> int:
    mapa = {
        "int": payload.mod_inteligencia,
        "wis": payload.mod_sabedoria,
        "cha": payload.mod_carisma,
        "dex": payload.mod_destreza,
    }
    hab = habilidade_primaria_classe(payload.classe)
    return mapa.get(hab, payload.mod_inteligencia)


def _normalizar_save(slug: Optional[str]) -> str:
    s = (slug or "nenhum").strip().lower()
    mapa = {
        "dex": "reflexos",
        "destreza": "reflexos",
        "con": "fortitude",
        "constituicao": "fortitude",
        "wis": "vontade",
        "sabedoria": "vontade",
        "int": "vontade",
        "inteligencia": "vontade",
        "cha": "vontade",
        "carisma": "vontade",
        "for": "fortitude",
        "str": "fortitude",
        "forca": "fortitude",
        "nenhum": "nenhum",
    }
    return mapa.get(s, "nenhum")


class Dnd5eConjuracaoService:
    def __init__(
        self,
        magia_repo: Dnd5eMagiaRepository,
        grimorio_repo: Optional[Dnd5eGrimorioRepository] = None,
    ):
        self.magia_repo = magia_repo
        self.grimorio_repo = grimorio_repo

    def teste_concentracao(
        self, payload: Dnd5eConcentracaoTesteRequest
    ) -> Dnd5eConcentracaoTesteResponse:
        if not payload.magia_concentracao_id:
            return Dnd5eConcentracaoTesteResponse(
                manteve_concentracao=True,
                dc=0,
                rolagem=0,
                total=0,
                magia_concentracao_id=None,
                mensagem="Sem magia em concentração.",
            )

        conj = Conjurador(
            conjurador_id=payload.conjurador_id,
            nome="",
            classe="mago",
            nivel=1,
            mod_habilidade=payload.mod_constituicao,
            bonus_proficiencia=payload.bonus_proficiencia,
            magia_concentracao=str(payload.magia_concentracao_id),
        )
        from app.games.dnd5e.rules.dados import rolar_d20

        roll = payload.rolagem_d20 if payload.rolagem_d20 is not None else rolar_d20()
        dc = max(10, payload.dano_recebido // 2)
        prof = payload.bonus_proficiencia
        total = roll + payload.mod_constituicao + prof
        manteve = teste_concentracao(
            conj,
            payload.dano_recebido,
            payload.mod_constituicao,
            rolagem_d20=roll,
            bonus_proficiencia=prof,
        )
        conc_id = (
            int(conj.magia_concentracao)
            if conj.magia_concentracao and conj.magia_concentracao.isdigit()
            else payload.magia_concentracao_id if manteve else None
        )
        msg = (
            "Concentração mantida."
            if manteve
            else "Concentração perdida — a magia termina."
        )
        return Dnd5eConcentracaoTesteResponse(
            manteve_concentracao=manteve,
            dc=dc,
            rolagem=roll,
            total=total,
            magia_concentracao_id=conc_id,
            mensagem=msg,
        )

    def conjurar(self, payload: Dnd5eConjurarRequest) -> Dnd5eConjurarResponse:
        magia_row = self.magia_repo.obter(payload.magia_id)
        if not magia_row:
            raise HTTPException(status_code=404, detail="Magia não encontrada")

        classe_norm = (payload.classe or "").strip().lower()
        if payload.validar_preparacao and classe_norm in PREPARED_CLASSES:
            prep = set(payload.magias_preparadas_ids or [])
            if payload.magia_id not in prep:
                raise HTTPException(
                    status_code=422,
                    detail="Magia não está preparada para hoje",
                )

        if payload.personagem_id and self.grimorio_repo:
            from app.games.dnd5e.services.grimorio_service import _classe_lista_magias

            classe_grim = _classe_lista_magias(payload.classe)
            item = self.grimorio_repo.obter_item(
                payload.personagem_id, payload.magia_id, classe_grim
            )
            if not item:
                raise HTTPException(
                    status_code=422, detail="Magia não está no grimório do personagem"
                )

        nivel = magia_row.nivel
        prof = payload.bonus_proficiencia or calcular_bonus_proficiencia(
            payload.nivel_personagem
        )
        mod_hab = _mod_por_habilidade(payload)
        dc = calcular_dc_magia(prof, mod_hab)

        slots_total = list(payload.espacos_por_nivel or [])
        slots_usados = list(payload.espacos_usados_por_nivel or [])
        if not slots_total:
            from app.games.dnd5e.rules.magia import espacos_por_classe_nivel

            slots_total = espacos_por_classe_nivel(
                payload.classe, payload.nivel_personagem
            )
        if len(slots_usados) < len(slots_total):
            slots_usados = slots_usados + [0] * (len(slots_total) - len(slots_usados))

        como_ritual = bool(payload.como_ritual)
        if como_ritual:
            if not magia_row.ritual:
                raise HTTPException(
                    status_code=422,
                    detail="Esta magia não possui a tag Ritual",
                )
            if nivel <= 0:
                raise HTTPException(
                    status_code=422,
                    detail="Truques não são conjurados como ritual",
                )

        if magia_row.material_consumido and not payload.confirmar_material_consumido:
            mat = (magia_row.componentes_material or "componente").strip()
            raise HTTPException(
                status_code=422,
                detail=f"Confirme o consumo do material: {mat}",
            )

        nivel_slot = payload.nivel_slot_usado
        if nivel > 0 and not como_ritual:
            if nivel_slot is None:
                nivel_slot = nivel
            if nivel_slot < nivel:
                raise HTTPException(
                    status_code=422,
                    detail="O espaço gasto deve ser de nível igual ou superior ao da magia",
                )
        elif como_ritual:
            nivel_slot = None

        conj = Conjurador(
            conjurador_id=payload.conjurador_id,
            nome=payload.nome,
            classe=payload.classe,
            nivel=payload.nivel_personagem,
            mod_habilidade=mod_hab,
            bonus_proficiencia=prof,
            espacos_por_nivel=slots_total,
            espacos_usados_por_nivel=slots_usados,
            magia_concentracao=(
                str(payload.magia_concentracao_id)
                if payload.magia_concentracao_id
                else None
            ),
        )

        save_tipo = _normalizar_save(magia_row.teste_resistencia)
        magia = Magia(
            magia_id=str(magia_row.id),
            nome=magia_row.nome,
            nivel=nivel,
            escola=magia_row.escola or "",
            tempo_execucao=magia_row.tempo_conjuracao or "ação",
            alcance=magia_row.alcance_texto or "",
            duracao=magia_row.duracao or "instantâneo",
            teste_resistencia=save_tipo,  # type: ignore[arg-type]
            descricao=magia_row.descricao or "",
            requer_concentracao=bool(magia_row.requer_concentracao),
        )

        comps = componentes_resumo(
            bool(magia_row.componentes_verbal),
            bool(magia_row.componentes_somatico),
            magia_row.componentes_material,
        )

        ataque_tipo = (getattr(magia_row, "ataque_magico", None) or "").strip().lower()
        requer_ataque = ataque_tipo in ("ranged", "melee")

        ok = lancar_magia(
            conj,
            magia,
            nivel_slot=nivel_slot,
            ignorar_slot=como_ritual,
        )
        if not ok:
            return Dnd5eConjurarResponse(
                sucesso=False,
                mensagem="Sem espaço de magia disponível para este nível.",
                dc=dc,
                espacos_usados_por_nivel=conj.espacos_usados_por_nivel,
                teste_resistencia=save_tipo if save_tipo != "nenhum" else None,
                componentes=comps,
                requer_concentracao=magia.requer_concentracao,
                ritual=bool(magia_row.ritual),
                requer_ataque_magico=requer_ataque,
            )

        ataque_roll: Optional[int] = None
        ataque_total: Optional[int] = None
        ataque_acertou: Optional[bool] = None
        critico = False

        if requer_ataque:
            if payload.ac_alvo is None:
                raise HTTPException(
                    status_code=422,
                    detail="Esta magia exige rolagem de ataque mágico (informe a CA do alvo)",
                )
            mods = resumo_modificadores_ataque(
                payload.condicoes_atacante,
                payload.condicoes_alvo,
                corpo_a_corpo=ataque_tipo == "melee",
            )
            vant, desv = mods.rolagem_efetiva()
            ataque_roll = payload.rolagem_ataque_d20
            if ataque_roll is None:
                ataque_roll, _ = rolar_d20_ataque(vantagem=vant, desvantagem=desv)
            ataque_total = (
                ataque_roll + mod_hab + prof + (payload.bonus_ataque_extra or 0)
            )
            ataque_acertou = ataque_atinge_ca(
                mod_hab,
                prof,
                payload.ac_alvo,
                rolagem_d20=ataque_roll,
                bonus_extra=payload.bonus_ataque_extra or 0,
                vantagem=vant,
                desvantagem=desv,
                acerto_automatico=mods.acerto_automatico,
            )
            critico = ataque_roll == 20 or mods.critico_automatico

        dano_total = None
        if magia_row.dano and (not requer_ataque or ataque_acertou):
            expressao_dano = magia_row.dano
            if nivel <= 0:
                expressao_dano = escalar_expressao_dano_truque(
                    magia_row.dano, payload.nivel_personagem
                )
            dano_total = calcular_dano(expressao_dano, mod_hab, is_critico=critico)

        salv_passou: Optional[bool] = None
        salv_roll: Optional[int] = None
        if save_tipo != "nenhum" and payload.teste_resistencia_mod_alvo is not None:
            from app.games.dnd5e.rules.dados import rolar_d20

            salv_roll = (
                payload.rolagem_salvaguarda_alvo
                if payload.rolagem_salvaguarda_alvo is not None
                else rolar_d20()
            )
            salv_passou = salvaguarda_atinge_dc(
                payload.teste_resistencia_mod_alvo,
                dc,
                rolagem_d20=salv_roll,
            )

        metade_no_save = save_causa_metade_dano(
            dano=magia_row.dano,
            save_tipo=save_tipo,
            slug=str(magia_row.slug or ""),
        )
        dano_aplicar: Optional[int] = None
        if dano_total is not None:
            if salv_passou is True:
                dano_aplicar = (
                    max(0, int(dano_total) // 2)
                    if metade_no_save
                    else 0
                )
            else:
                dano_aplicar = int(dano_total)

        concentracao_id = (
            int(conj.magia_concentracao)
            if conj.magia_concentracao and conj.magia_concentracao.isdigit()
            else payload.magia_id if magia.requer_concentracao else None
        )

        msg = f"{magia_row.nome} conjurada."
        if como_ritual:
            msg += " (ritual — sem gastar espaço)"
        elif nivel_slot and nivel_slot > nivel:
            msg += f" (espaço de {nivel_slot}º nível)"
        if magia_row.material_consumido and payload.confirmar_material_consumido:
            msg += " · Material consumido"
        if requer_ataque and ataque_roll is not None:
            if ataque_acertou:
                msg += f" · Ataque {ataque_total} vs CA {payload.ac_alvo} (acerto)"
                if critico:
                    msg += ", crítico"
            else:
                msg += f" · Ataque {ataque_total} vs CA {payload.ac_alvo} (erro)"
        if salv_passou is True:
            msg += " · Alvo passou na resistência."
            if dano_aplicar is not None:
                if dano_aplicar == 0 and not metade_no_save:
                    msg += " · Sem dano (save bem-sucedido)."
                elif metade_no_save and dano_total is not None:
                    msg += f" · Dano reduzido para {dano_aplicar}."
        elif salv_passou is False:
            msg += " · Alvo falhou na resistência."

        return Dnd5eConjurarResponse(
            sucesso=True,
            mensagem=msg,
            dc=dc,
            espacos_usados_por_nivel=conj.espacos_usados_por_nivel,
            magia_concentracao_id=(
                concentracao_id if magia.requer_concentracao else None
            ),
            dano_total=dano_total,
            dano_aplicar=dano_aplicar,
            magia_nome=magia_row.nome,
            magia_nivel=nivel,
            nivel_slot_gasto=nivel_slot if nivel > 0 and not como_ritual else None,
            teste_resistencia=save_tipo if save_tipo != "nenhum" else None,
            salvaguarda_passou=salv_passou,
            salvaguarda_rolagem=salv_roll,
            componentes=comps,
            requer_concentracao=magia.requer_concentracao,
            ritual=bool(magia_row.ritual),
            requer_ataque_magico=requer_ataque,
            ataque_rolagem=ataque_roll,
            ataque_total=ataque_total,
            ataque_acertou=ataque_acertou,
            ataque_critico=critico,
            conjurada_como_ritual=como_ritual,
            material_consumido_confirmado=bool(
                magia_row.material_consumido and payload.confirmar_material_consumido
            ),
        )
