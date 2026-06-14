"""Preview de subir de nível MB — PV, PM, benefícios globais e conjuração."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.classes_t20 import lista_classes_mb
from app.games.tormenta.rules.conjuracao_t20 import (
    classe_conjuracao_mb_registrada,
    pontos_magia_maximos_conjuracao,
)
from app.games.tormenta.rules.grimorio_elegibilidade_t20 import (
    nivel_efetivo_conjuracao_mb,
)
from app.games.tormenta.rules.magias_conhecidas_progressao_t20 import (
    bardo_pode_trocar_magia_mb,
    classe_usa_limite_conhecidas_mb,
    total_magias_conhecidas_max_mb,
)
from app.games.tormenta.rules.magias_grimorio_aprendizado_t20 import (
    classe_usa_limite_grimorio_mb,
    orcamento_magias_grimorio_mb,
)
from app.games.tormenta.rules.magias_preparadas_t20 import (
    classe_usa_limite_preparadas_mb,
    teto_preparadas_mb,
)
from app.games.tormenta.rules.pericias_criacao_t20 import beneficio_nivel_mb
from app.games.tormenta.rules.progressao_pv_t20 import pv_maximos_mb


def _habilidade_classe_mb(slug_classe: str, nivel: int) -> Optional[str]:
    s = str(slug_classe or "").strip().lower()
    for row in lista_classes_mb():
        if str(row.get("slug", "")).strip().lower() != s:
            continue
        hab = row.get("habilidades_por_nivel") or {}
        if not isinstance(hab, dict):
            return None
        return str(hab.get(str(int(nivel)), "") or "").strip() or None
    return None


def preview_subir_nivel_mb(
    *,
    nivel_atual: int,
    nivel_alvo: int,
    slug_classe: str,
    ficha_json: Optional[Dict[str, Any]],
    for_valor: int,
    des_valor: int,
    con_valor: int,
    int_valor: int,
    sab_valor: int,
    car_valor: int,
    pv_max_atual: Optional[int] = None,
    pa_max_atual: Optional[int] = None,
) -> Dict[str, Any]:
    """Compara nível atual vs alvo; retorna ganhos e textos para UI."""
    try:
        nv0 = int(nivel_atual)
    except (TypeError, ValueError):
        nv0 = 1
    try:
        nv1 = int(nivel_alvo)
    except (TypeError, ValueError):
        nv1 = nv0 + 1
    nv0 = max(1, min(40, nv0))
    nv1 = max(1, min(40, nv1))
    slug = str(slug_classe or "").strip().lower()
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    avisos: List[str] = []

    if nv1 <= nv0:
        return {
            "permitido": False,
            "motivo": "O nível alvo deve ser maior que o nível atual.",
            "nivel_atual": nv0,
            "nivel_alvo": nv1,
            "avisos": avisos,
        }
    if nv1 != nv0 + 1:
        avisos.append(
            "O app aplica um nível de cada vez (MB). Para saltar níveis, repita ou ajuste manualmente."
        )
        return {
            "permitido": False,
            "motivo": "Use apenas o próximo nível (atual + 1).",
            "nivel_atual": nv0,
            "nivel_alvo": nv1,
            "avisos": avisos,
        }
    if not slug:
        return {
            "permitido": False,
            "motivo": "Selecione a classe MB na ficha antes de subir de nível.",
            "nivel_atual": nv0,
            "nivel_alvo": nv1,
            "avisos": avisos,
        }

    pv_ant = pv_maximos_mb(slug, nv0, con_valor)
    pv_nov = pv_maximos_mb(slug, nv1, con_valor)
    pv_ganho = None
    if pv_ant is not None and pv_nov is not None:
        pv_ganho = max(0, pv_nov - pv_ant)

    nv_conj0 = nivel_efetivo_conjuracao_mb(fj, nv0)
    nv_conj1 = nivel_efetivo_conjuracao_mb(fj, nv1)
    pa_ant = None
    pa_nov = None
    pa_ganho = None
    if classe_conjuracao_mb_registrada(slug):
        pa_ant = pontos_magia_maximos_conjuracao(
            slug,
            nv_conj0,
            for_valor,
            des_valor,
            con_valor,
            int_valor,
            sab_valor,
            car_valor,
        )
        pa_nov = pontos_magia_maximos_conjuracao(
            slug,
            nv_conj1,
            for_valor,
            des_valor,
            con_valor,
            int_valor,
            sab_valor,
            car_valor,
        )
        if pa_ant is not None and pa_nov is not None:
            pa_ganho = max(0, pa_nov - pa_ant)

    ben_ant = beneficio_nivel_mb(nv0) or {}
    ben_nov = beneficio_nivel_mb(nv1) or {}
    if nv1 > 20:
        avisos.append(
            "Tabela de benefícios MB cobre níveis 1–20; acima disso use campos manuais."
        )

    talentos_ant = int(ben_ant.get("talentos_totais", 0) or 0)
    talentos_nov = int(ben_nov.get("talentos_totais", 0) or 0)
    talentos_ganho = max(0, talentos_nov - talentos_ant)

    magias_livro_ganho = None
    magias_livro_max_novo = None
    if classe_usa_limite_grimorio_mb(slug):
        o0 = orcamento_magias_grimorio_mb(
            slug,
            nv_conj0,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
        )
        o1 = orcamento_magias_grimorio_mb(
            slug,
            nv_conj1,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
        )
        if o0 is not None and o1 is not None:
            magias_livro_ganho = max(0, o1 - o0)
            magias_livro_max_novo = o1

    conhecidas_max_novo = None
    if classe_usa_limite_conhecidas_mb(slug):
        conhecidas_max_novo = total_magias_conhecidas_max_mb(slug, nv_conj1)

    preparadas_teto_novo = None
    if classe_usa_limite_preparadas_mb(slug):
        preparadas_teto_novo = teto_preparadas_mb(
            slug,
            nv_conj1,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
        )

    hab_txt = _habilidade_classe_mb(slug, nv1)

    return {
        "permitido": True,
        "motivo": "",
        "nivel_atual": nv0,
        "nivel_alvo": nv1,
        "classe_slug": slug,
        "nivel_conjuracao_atual": nv_conj0,
        "nivel_conjuracao_novo": nv_conj1,
        "pv_max_atual": pv_ant if pv_ant is not None else pv_max_atual,
        "pv_max_novo": pv_nov,
        "pv_ganho": pv_ganho,
        "pa_max_atual": pa_ant if pa_ant is not None else pa_max_atual,
        "pa_max_novo": pa_nov,
        "pa_ganho": pa_ganho,
        "beneficio_nivel": ben_nov if ben_nov else None,
        "graduacao_pericias_nova": str(ben_nov.get("graduacao_pericias", "") or ""),
        "talentos_totais_novo": talentos_nov,
        "talentos_ganho": talentos_ganho,
        "pontos_habilidade_acumulados": int(
            ben_nov.get("pontos_habilidade_acumulados", 0) or 0
        ),
        "bonus_meio_nivel": int(ben_nov.get("bonus_meio_nivel", 0) or 0),
        "habilidade_classe": hab_txt,
        "magias_livro_ganho": magias_livro_ganho,
        "magias_livro_max_novo": magias_livro_max_novo,
        "magias_conhecidas_max_novo": conhecidas_max_novo,
        "magias_preparadas_teto_novo": preparadas_teto_novo,
        "bardo_pode_trocar_magia": (
            bardo_pode_trocar_magia_mb(nv_conj1) if slug == "bardo" else False
        ),
        "avisos": avisos,
    }
