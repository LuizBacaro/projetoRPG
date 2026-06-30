"""Preview de subir de nível MB — PV, PM, benefícios globais e conjuração."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.beneficios_nivel_t20 import beneficio_nivel
from app.games.tormenta.rules.classes_t20 import classe_por_slug, lista_classes
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
from app.games.tormenta.rules.progressao_pv_t20 import (
    niveis_multiclasse_v13_de_ficha,
    preview_pm_multiclasse_v13,
    pv_maximos_mb,
    pv_maximos_v13_multiclasse,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)


def _habilidade_classe_por_nivel(
    slug_classe: str,
    nivel: int,
    regra_versao: Optional[str] = None,
) -> Optional[str]:
    s = str(slug_classe or "").strip().lower()
    for row in lista_classes(regra_versao):
        if str(row.get("slug", "")).strip().lower() != s:
            continue
        hab = row.get("habilidades_por_nivel") or {}
        if not isinstance(hab, dict):
            return None
        return str(hab.get(str(int(nivel)), "") or "").strip() or None
    return None


def _nivel_na_classe(linhas: List[Dict[str, Any]], slug: str) -> int:
    s = str(slug or "").strip().lower()
    for item in linhas:
        if str(item.get("slug", "")).strip().lower() == s:
            try:
                return int(item.get("nivel", 0))
            except (TypeError, ValueError):
                return 0
    return 0


def _incrementar_classe_multiclasse(
    linhas: List[Dict[str, Any]], slug_alvo: str
) -> tuple[List[Dict[str, Any]], bool]:
    """Soma +1 na classe alvo; se ausente, adiciona 1º nível (nova multiclasse)."""
    slug = str(slug_alvo or "").strip().lower()
    out: List[Dict[str, Any]] = []
    nova = True
    for item in linhas:
        sl = str(item.get("slug", "")).strip().lower()
        nv = int(item.get("nivel", 1))
        if sl == slug:
            out.append({"slug": sl, "nivel": min(40, nv + 1)})
            nova = False
        else:
            out.append({"slug": sl, "nivel": nv})
    if nova:
        out.append({"slug": slug, "nivel": 1})
    return out, nova


def preview_subir_nivel_v13(
    *,
    nivel_personagem: int,
    classe_alvo_slug: str,
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
    """Preview subir nível v1.3 — multiclasse (p.34): escolhe classe que sobe."""
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    avisos: List[str] = []
    slug_pri = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
    slug = str(classe_alvo_slug or slug_pri or "").strip().lower()
    linhas_atual = niveis_multiclasse_v13_de_ficha(fj, nivel_personagem)
    nv_total0 = sum(int(x.get("nivel", 0)) for x in linhas_atual)
    nv_total1 = nv_total0 + 1

    if nv_total1 > 40:
        return {
            "permitido": False,
            "motivo": "Nível total máximo é 40.",
            "nivel_atual": max(1, nv_total0),
            "nivel_alvo": nv_total1,
            "avisos": avisos,
        }
    if not slug:
        return {
            "permitido": False,
            "motivo": "Selecione a classe na ficha antes de subir de nível.",
            "nivel_atual": max(1, nv_total0),
            "nivel_alvo": nv_total1,
            "avisos": avisos,
        }
    if not classe_por_slug(slug, REGRA_VERSAO_V13):
        return {
            "permitido": False,
            "motivo": f"Classe «{slug}» não encontrada na v1.3.",
            "nivel_atual": max(1, nv_total0),
            "nivel_alvo": nv_total1,
            "avisos": avisos,
        }

    linhas_novo, classe_nova = _incrementar_classe_multiclasse(linhas_atual, slug)
    nv_classe0 = _nivel_na_classe(linhas_atual, slug)
    nv_classe1 = nv_classe0 + 1

    pri = slug_pri or slug
    pv_ant = pv_maximos_v13_multiclasse(linhas_atual, con_valor, pri)
    pv_nov = pv_maximos_v13_multiclasse(linhas_novo, con_valor, pri)
    pv_ganho = None
    if pv_ant is not None and pv_nov is not None:
        pv_ganho = max(1, pv_nov - pv_ant)

    pm_ant = preview_pm_multiclasse_v13(linhas_atual).get("pm_max")
    pm_nov = preview_pm_multiclasse_v13(linhas_novo).get("pm_max")
    pa_ganho = None
    if pm_ant is not None and pm_nov is not None:
        pa_ganho = max(0, pm_nov - pm_ant)

    rv = REGRA_VERSAO_V13
    arcanista = str(fj.get("arcanista_caminho") or "").strip().lower() or None
    nv_conj0 = max(1, nv_classe0)
    nv_conj1 = max(1, nv_classe1)

    ben_ant = beneficio_nivel(nv_total0, rv) or {}
    ben_nov = beneficio_nivel(nv_total1, rv) or {}
    if nv_total1 > 20:
        avisos.append(
            "Tabela de benefícios cobre níveis 1–20; acima disso use campos manuais."
        )
    if classe_nova:
        avisos.append(
            "1º nível em nova classe: PV = ganho de nível subsequente (p.34); "
            "sem perícias/proficiências da nova classe neste nível."
        )

    talentos_ant = int(ben_ant.get("talentos_totais", 0) or 0)
    talentos_nov = int(ben_nov.get("talentos_totais", 0) or 0)
    talentos_ganho = max(0, talentos_nov - talentos_ant)

    magias_livro_ganho = None
    magias_livro_max_novo = None
    if classe_usa_limite_grimorio_mb(
        slug,
        regra_versao=rv,
        arcanista_caminho=arcanista,
    ):
        o0 = orcamento_magias_grimorio_mb(
            slug,
            nv_conj0,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
            regra_versao=rv,
            arcanista_caminho=arcanista,
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
            regra_versao=rv,
            arcanista_caminho=arcanista,
        )
        if o0 is not None and o1 is not None:
            magias_livro_ganho = max(0, o1 - o0)
            magias_livro_max_novo = o1

    conhecidas_max_novo = None
    if classe_usa_limite_conhecidas_mb(
        slug,
        regra_versao=rv,
        arcanista_caminho=arcanista,
    ):
        conhecidas_max_novo = total_magias_conhecidas_max_mb(
            slug,
            nv_conj1,
            regra_versao=rv,
            arcanista_caminho=arcanista,
        )

    preparadas_teto_novo = None
    if classe_usa_limite_preparadas_mb(
        slug,
        regra_versao=rv,
        arcanista_caminho=arcanista,
    ):
        preparadas_teto_novo = teto_preparadas_mb(
            slug,
            nv_conj1,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
            regra_versao=rv,
            arcanista_caminho=arcanista,
        )

    hab_txt = _habilidade_classe_por_nivel(slug, nv_classe1, regra_versao=rv)

    return {
        "permitido": True,
        "motivo": "",
        "nivel_atual": max(1, nv_total0),
        "nivel_alvo": nv_total1,
        "classe_slug": slug,
        "classe_nivel_atual": nv_classe0 if nv_classe0 else None,
        "classe_nivel_novo": nv_classe1,
        "classe_nova_multiclasse": classe_nova,
        "multiclasse_v13_novo": linhas_novo,
        "nivel_conjuracao_atual": nv_conj0,
        "nivel_conjuracao_novo": nv_conj1,
        "pv_max_atual": pv_ant if pv_ant is not None else pv_max_atual,
        "pv_max_novo": pv_nov,
        "pv_ganho": pv_ganho,
        "pa_max_atual": pm_ant if pm_ant is not None else pa_max_atual,
        "pa_max_novo": pm_nov,
        "pa_ganho": pa_ganho,
        "beneficio_nivel": ben_nov if ben_nov else None,
        "graduacao_pericias_nova": str(ben_nov.get("graduacao_pericias", "") or ""),
        "talentos_totais_novo": talentos_nov,
        "talentos_ganho": talentos_ganho,
        "poderes_gerais_totais_novo": talentos_nov,
        "poderes_gerais_ganho": talentos_ganho,
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

    pv_ant = pv_maximos_mb(slug, nv0, con_valor, regra_versao=regra_versao_de_ficha(fj))
    pv_nov = pv_maximos_mb(slug, nv1, con_valor, regra_versao=regra_versao_de_ficha(fj))
    pv_ganho = None
    if pv_ant is not None and pv_nov is not None:
        pv_ganho = max(0, pv_nov - pv_ant)

    rv = regra_versao_de_ficha(fj)
    arcanista = str(fj.get("arcanista_caminho") or "").strip().lower() or None
    nv_conj0 = nivel_efetivo_conjuracao_mb(fj, nv0)
    nv_conj1 = nivel_efetivo_conjuracao_mb(fj, nv1)
    pa_ant = None
    pa_nov = None
    pa_ganho = None
    sinc_pm = rv == REGRA_VERSAO_V13 or classe_conjuracao_mb_registrada(slug)
    if sinc_pm:
        nv_pm0 = nv0 if rv == REGRA_VERSAO_V13 else nv_conj0
        nv_pm1 = nv1 if rv == REGRA_VERSAO_V13 else nv_conj1
        pa_ant = pontos_magia_maximos_conjuracao(
            slug,
            nv_pm0,
            for_valor,
            des_valor,
            con_valor,
            int_valor,
            sab_valor,
            car_valor,
            regra_versao=rv,
            arcanista_caminho=arcanista,
        )
        pa_nov = pontos_magia_maximos_conjuracao(
            slug,
            nv_pm1,
            for_valor,
            des_valor,
            con_valor,
            int_valor,
            sab_valor,
            car_valor,
            regra_versao=rv,
            arcanista_caminho=arcanista,
        )
        if pa_ant is not None and pa_nov is not None:
            pa_ganho = max(0, pa_nov - pa_ant)

    ben_ant = beneficio_nivel(nv0, rv) or {}
    ben_nov = beneficio_nivel(nv1, rv) or {}
    if nv1 > 20:
        avisos.append(
            "Tabela de benefícios cobre níveis 1–20; acima disso use campos manuais."
        )

    talentos_ant = int(ben_ant.get("talentos_totais", 0) or 0)
    talentos_nov = int(ben_nov.get("talentos_totais", 0) or 0)
    talentos_ganho = max(0, talentos_nov - talentos_ant)

    magias_livro_ganho = None
    magias_livro_max_novo = None
    if classe_usa_limite_grimorio_mb(
        slug,
        regra_versao=rv,
        arcanista_caminho=arcanista,
    ):
        o0 = orcamento_magias_grimorio_mb(
            slug,
            nv_conj0,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
            regra_versao=rv,
            arcanista_caminho=arcanista,
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
            regra_versao=rv,
            arcanista_caminho=arcanista,
        )
        if o0 is not None and o1 is not None:
            magias_livro_ganho = max(0, o1 - o0)
            magias_livro_max_novo = o1

    conhecidas_max_novo = None
    if classe_usa_limite_conhecidas_mb(
        slug,
        regra_versao=rv,
        arcanista_caminho=arcanista,
    ):
        conhecidas_max_novo = total_magias_conhecidas_max_mb(
            slug,
            nv_conj1,
            regra_versao=rv,
            arcanista_caminho=arcanista,
        )

    preparadas_teto_novo = None
    if classe_usa_limite_preparadas_mb(
        slug,
        regra_versao=rv,
        arcanista_caminho=arcanista,
    ):
        preparadas_teto_novo = teto_preparadas_mb(
            slug,
            nv_conj1,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
            regra_versao=rv,
            arcanista_caminho=arcanista,
        )

    hab_txt = _habilidade_classe_por_nivel(slug, nv1, regra_versao=rv)

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
        "poderes_gerais_totais_novo": talentos_nov if rv == REGRA_VERSAO_V13 else None,
        "poderes_gerais_ganho": talentos_ganho if rv == REGRA_VERSAO_V13 else None,
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
