"""
Sincronização em lote de progressão base nos combatentes (D&D 3.5).

BBA, habilidades especiais serializadas, resistências de salvamento base,
totais de save e CA/toque/surpresa — alinhado a `bonus_base_ataque` e ao
comportamento esperado da ficha. Usado no startup (`app.main`) e pode ser
reutilizado por scripts de manutenção.
"""

from __future__ import annotations

import json
import logging

from sqlalchemy.orm import Session

from app.games.dnd35.bonus_base_ataque import (
    calcular_bonus_base_ataque,
    calcular_habilidades_especiais,
    calcular_habilidades_especiais_por_nivel,
    calcular_resistencias_base,
)
from app.games.dnd35.models.combatente import Combatente

logger = logging.getLogger(__name__)


def _modificador_atributo(valor: int | None) -> int:
    try:
        return (int(valor) - 10) // 2
    except (TypeError, ValueError):
        return 0


def sincronizar_bonus_base_ataque_combatentes(db: Session) -> None:
    """
    Recalcula e persiste BBA de combatentes existentes.

    Mantém consistência para registros antigos criados antes da introdução
    do campo `bonus_base_ataque`.
    """
    combatentes = db.query(Combatente).filter(Combatente.deleted_at.is_(None)).all()
    atualizados = 0

    for combatente in combatentes:
        novo_bba = calcular_bonus_base_ataque(combatente.classe, combatente.nivel) or ""
        habilidades_grouped = calcular_habilidades_especiais_por_nivel(
            combatente.classe, combatente.nivel
        )
        if habilidades_grouped:
            habilidades_txt = json.dumps(habilidades_grouped, ensure_ascii=False)
        else:
            habilidades = calcular_habilidades_especiais(combatente.classe, combatente.nivel)
            habilidades_txt = " | ".join(habilidades) if habilidades else ""
        novas_resistencias = calcular_resistencias_base(combatente.classe, combatente.nivel)
        mudou = False

        if (combatente.bonus_base_ataque or "") != novo_bba:
            combatente.bonus_base_ataque = novo_bba
            mudou = True
        if (combatente.habilidades_especiais or "") != habilidades_txt:
            combatente.habilidades_especiais = habilidades_txt
            mudou = True

        if novas_resistencias is not None:
            nova_fortitude, novo_reflexos, nova_vontade = novas_resistencias
            if combatente.fortitude_base != nova_fortitude:
                combatente.fortitude_base = nova_fortitude
                mudou = True
            if combatente.reflexos_base != novo_reflexos:
                combatente.reflexos_base = novo_reflexos
                mudou = True
            if combatente.vontade_base != nova_vontade:
                combatente.vontade_base = nova_vontade
                mudou = True

            fort_total = nova_fortitude + _modificador_atributo(combatente.constituicao)
            reflex_total = novo_reflexos + _modificador_atributo(combatente.destreza)
            vontade_total = nova_vontade + _modificador_atributo(combatente.sabedoria)

            if combatente.fortitude != fort_total:
                combatente.fortitude = fort_total
                mudou = True
            if combatente.reflexos != reflex_total:
                combatente.reflexos = reflex_total
                mudou = True
            if combatente.vontade != vontade_total:
                combatente.vontade = vontade_total
                mudou = True

        else:
            # Classes sem mapeamento no catálogo/fallback: preservar totais legados
            # e preencher base de forma derivada para evitar nulls em responses.
            base_fort = (combatente.fortitude or 0) - _modificador_atributo(combatente.constituicao)
            base_ref = (combatente.reflexos or 0) - _modificador_atributo(combatente.destreza)
            base_vont = (combatente.vontade or 0) - _modificador_atributo(combatente.sabedoria)

            if combatente.fortitude_base is None:
                combatente.fortitude_base = base_fort
                mudou = True
            if combatente.reflexos_base is None:
                combatente.reflexos_base = base_ref
                mudou = True
            if combatente.vontade_base is None:
                combatente.vontade_base = base_vont
                mudou = True

        # Defesa automática: Toque/Surpresa/CA
        mod_des = _modificador_atributo(combatente.destreza)
        bonus_armadura = max(0, int(combatente.ca or 10) - (10 + mod_des))
        novo_toque = 10 + mod_des
        nova_surpresa = 10 + bonus_armadura
        nova_ca = 10 + mod_des + bonus_armadura
        if combatente.toque != novo_toque:
            combatente.toque = novo_toque
            mudou = True
        if combatente.surpresa != nova_surpresa:
            combatente.surpresa = nova_surpresa
            mudou = True
        if combatente.ca != nova_ca:
            combatente.ca = nova_ca
            mudou = True

        if mudou:
            atualizados += 1

    if atualizados:
        db.commit()
        logger.info("✅ Progressão base (BBA/TRs) sincronizada para %s combatente(s).", atualizados)
