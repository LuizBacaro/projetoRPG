"""Regras de negócio do Grimório."""

from __future__ import annotations

import csv
import re
import unicodedata
import json
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

from fastapi import HTTPException

from ..models.grimorio import GrimorioHistoricoTroca, GrimorioMagia, GrimorioNotificacao
from ..repositories.grimorio_repository import GrimorioRepository
from ..repositories.magia_repository import MagiaRepository


_CLASSES_DIVINAS = {"CLERIGO", "DRUIDA", "PALADINO"}

# Intervalo mínimo entre sincronizações automáticas do grimório por combatente (segundos).
# Evita rodar 2-3 queries extras a cada GET /notificações em chamadas rápidas consecutivas.
_SYNC_INTERVAL_SECONDS = 30
_sync_last: dict[int, datetime] = {}  # combatente_id → última sincronização

# Em D&D 3.5, Feiticeiro usa a mesma lista de magias do Mago.
# O banco de dados armazena as magias com class="MAGO"; este alias
# resolve a compatibilidade sem precisar re-seeder todas as magias.
_SPELL_LIST_ALIASES: dict[str, str] = {
    "FEITICEIRO": "MAGO",
}


def _alias_lista_magias(classe_norm: str) -> str:
    """Retorna a classe canônica da lista de magias (ex: FEITICEIRO → MAGO)."""
    return _SPELL_LIST_ALIASES.get(classe_norm, classe_norm)
_PARES_DOMINIOS_OPOSTOS = (
    frozenset({"MAL", "BEM"}),
    frozenset({"LEI", "CAOS"}),
    frozenset({"ORDEM", "CAOS"}),
    frozenset({"PROTECAO", "DESTRUICAO"}),
)

_DIVINDADES_CURAR_SEMPRE = {
    "ST CUTHBERT",
    "ST. CUTHBERT",
    "SAO CUTHBERT",
    "SAINT CUTHBERT",
}

_DIVINDADES_INFLIGIR_SEMPRE_SE_LEAL_OU_NEUTRO = {
    "WEE JAS",
}

_DIVINDADES_CURAR_SEMPRE_NEUTRO_OU_BOM = {
    "OBAD HAI",
    "OBAD-HAI",
}

_CSV_REGRAS_COMPLETO = Path(__file__).resolve().parents[3] / "restricoes_clerigo_completo.csv"
_RULES_BY_NAME_LEVEL: dict[tuple[str, int], list[dict]] | None = None


def _bool_sim(valor: str | None) -> bool:
    return _normalizar(valor or "") == "SIM"


def _carregar_regras_clerigo_csv() -> dict[tuple[str, int], list[dict]]:
    global _RULES_BY_NAME_LEVEL
    if _RULES_BY_NAME_LEVEL is not None:
        return _RULES_BY_NAME_LEVEL

    index: dict[tuple[str, int], list[dict]] = {}
    if not _CSV_REGRAS_COMPLETO.exists():
        _RULES_BY_NAME_LEVEL = index
        return index

    with _CSV_REGRAS_COMPLETO.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nome = str(row.get("nome_magia") or "").strip()
            nivel_raw = str(row.get("nivel") or "").strip()
            if not nome or not nivel_raw:
                continue
            try:
                nivel = int(nivel_raw)
            except ValueError:
                continue

            row_data = dict(row)
            row_data["_nome_norm"] = _normalizar(nome)
            row_data["_dominio_norm"] = _normalizar(row.get("dominio") or "")
            row_data["_eh_dominio"] = _bool_sim(row.get("eh_magia_dominio"))

            key = (row_data["_nome_norm"], nivel)
            index.setdefault(key, []).append(row_data)

    _RULES_BY_NAME_LEVEL = index
    return index


def _alinhamento_para_coluna_csv(alinhamento_norm: str | None) -> str | None:
    if not alinhamento_norm:
        return None

    a = _normalizar(alinhamento_norm)
    has_leal = "LEAL" in a or "ORDEIR" in a
    has_caotico = "CAOT" in a
    has_bom = "BOM" in a
    has_mau = "MAU" in a or "MAL" in a
    has_neutro = "NEUTRO" in a

    if has_leal and has_bom:
        return "pode_leal_bom"
    if has_leal and has_neutro:
        return "pode_leal_neutro"
    if has_leal and has_mau:
        return "pode_leal_mau"

    if has_caotico and has_bom:
        return "pode_caotico_bom"
    if has_caotico and has_neutro:
        return "pode_caotico_neutro"
    if has_caotico and has_mau:
        return "pode_caotico_mau"

    if has_neutro and has_bom:
        return "pode_neutro_bom"
    if has_neutro and has_mau:
        return "pode_neutro_mau"
    if has_neutro:
        return "pode_neutro"

    return None


def _csv_rule_for_magia(magia) -> dict | None:
    try:
        nivel = int(getattr(magia, "nivel", 0) or 0)
    except (TypeError, ValueError):
        nivel = 0

    nome_norm = _normalizar(getattr(magia, "nome", ""))
    if not nome_norm:
        return None

    candidatos = _carregar_regras_clerigo_csv().get((nome_norm, nivel), [])
    if not candidatos:
        return None

    eh_dominio_magia = bool(getattr(magia, "e_magia_dominio", False))
    dominios_magia = _dominios_de_magia(magia)

    if eh_dominio_magia:
        dominio_match = [
            r for r in candidatos
            if r.get("_eh_dominio") and (
                not dominios_magia or r.get("_dominio_norm") in dominios_magia
            )
        ]
        if dominio_match:
            return dominio_match[0]

    base_match = [r for r in candidatos if not r.get("_eh_dominio")]
    if base_match:
        return base_match[0]

    return candidatos[0]


def _normalizar(valor: str) -> str:
    normalizado = unicodedata.normalize("NFD", str(valor or ""))
    sem_acentos = "".join(ch for ch in normalizado if unicodedata.category(ch) != "Mn")
    return sem_acentos.strip().upper()


def _classes_legacy(valor: str) -> set[str]:
    partes = [p.strip() for p in re.split(r"[,/;|]", valor or "") if p.strip()]
    return {_normalizar(parte) for parte in partes}


def _partes_csv(valor: str | None) -> list[str]:
    return [p.strip() for p in re.split(r"[,/;|]", str(valor or "")) if p.strip()]


def _dominios_de_magia(magia) -> set[str]:
    dominios = set()
    for parte in _partes_csv(getattr(magia, "dominios", None)):
        norm = _normalizar(parte)
        if norm:
            dominios.add(norm)
    return dominios


def _descritor_de_magia(magia) -> set[str]:
    descritores = set()
    texto = _normalizar(getattr(magia, "descritor", ""))
    nome = _normalizar(getattr(magia, "nome", ""))

    if "BEM" in texto:
        descritores.add("BEM")
    if "MAL" in texto:
        descritores.add("MAL")
    if "CAOS" in texto:
        descritores.add("CAOS")
    if "LEI" in texto or "ORDEM" in texto:
        descritores.add("LEI")
        descritores.add("ORDEM")

    # Fallback semântico para catálogos com domínio/descritor ausentes.
    if "CURA" in nome or "CURAR" in nome:
        descritores.add("BEM")
    if "INFLIGIR" in nome:
        descritores.add("MAL")

    return descritores


def _alinhamento_do_combatente(combatente) -> str | None:
    valor = getattr(combatente, "alinhamento", None) or getattr(combatente, "tendencia", None)
    normalizado = _normalizar(valor) if valor else ""
    return normalizado or None


def _eixo_moral(alinhamento_norm: str | None) -> str | None:
    if not alinhamento_norm:
        return None
    if "BOM" in alinhamento_norm:
        return "BOM"
    if "MAL" in alinhamento_norm or "MAU" in alinhamento_norm:
        return "MAL"
    return "NEUTRO"


def _eixo_etico(alinhamento_norm: str | None) -> str | None:
    if not alinhamento_norm:
        return None
    if "CAOT" in alinhamento_norm:
        return "CAOTICO"
    if "ORDEIR" in alinhamento_norm or "LEAL" in alinhamento_norm:
        return "LEAL"
    return "NEUTRO"


def _dominios_do_combatente(combatente) -> set[str]:
    dominios = set()
    candidatos = [
        getattr(combatente, "dominios", None),
        getattr(combatente, "dominio", None),
        getattr(combatente, "dominio_1", None),
        getattr(combatente, "dominio_2", None),
        getattr(combatente, "dominio1", None),
        getattr(combatente, "dominio2", None),
    ]
    for valor in candidatos:
        for parte in _partes_csv(valor):
            norm = _normalizar(parte)
            if norm:
                dominios.add(norm)
    return dominios


def _divindade_do_combatente(combatente) -> str | None:
    candidatos = (
        getattr(combatente, "divindade", None),
        getattr(combatente, "deidade", None),
        getattr(combatente, "deus", None),
        getattr(combatente, "patrono", None),
    )
    for valor in candidatos:
        texto = str(valor or "").strip()
        if texto:
            return texto
    return None


def _dominios_opostos(dominio: str) -> set[str]:
    opostos = set()
    for par in _PARES_DOMINIOS_OPOSTOS:
        if dominio in par:
            opostos.update(par - {dominio})
    return opostos


def _magia_bloqueada_por_alinhamento(magia, alinhamento_norm: str | None) -> bool:
    regra_csv = _csv_rule_for_magia(magia)
    coluna_alinhamento = _alinhamento_para_coluna_csv(alinhamento_norm)
    bloqueada_por_csv = False
    if regra_csv and coluna_alinhamento and coluna_alinhamento in regra_csv:
        bloqueada_por_csv = not _bool_sim(regra_csv.get(coluna_alinhamento))

    if not alinhamento_norm:
        return bloqueada_por_csv

    moral = _eixo_moral(alinhamento_norm)
    etico = _eixo_etico(alinhamento_norm)

    bloqueados = set()

    if moral == "BOM":
        bloqueados.add("MAL")
    elif moral == "MAL":
        bloqueados.add("BEM")
    elif moral == "NEUTRO":
        bloqueados.update({"BEM", "MAL"})

    if etico == "LEAL":
        bloqueados.add("CAOS")
    elif etico == "CAOTICO":
        bloqueados.update({"ORDEM", "LEI"})
    elif etico == "NEUTRO":
        bloqueados.update({"ORDEM", "LEI", "CAOS"})

    if not bloqueados:
        return False

    tags = _dominios_de_magia(magia) | _descritor_de_magia(magia)
    bloqueada_por_tags = len(tags & bloqueados) > 0
    return bloqueada_por_csv or bloqueada_por_tags


def _magia_bloqueada_por_dominios_opostos(magia, dominios_personagem: set[str]) -> bool:
    regra_csv = _csv_rule_for_magia(magia)
    if regra_csv:
        opostos_csv = {
            _normalizar(parte)
            for parte in _partes_csv(regra_csv.get("dominios_opostos_bloqueiam"))
            if _normalizar(parte)
        }
        if opostos_csv and dominios_personagem:
            return len(opostos_csv & dominios_personagem) > 0

    if not dominios_personagem:
        return False

    dominios_magia = _dominios_de_magia(magia) | _descritor_de_magia(magia)
    if not dominios_magia:
        return False

    opostos = set()
    for dominio in dominios_personagem:
        opostos.update(_dominios_opostos(dominio))

    return len(dominios_magia & opostos) > 0


def _magia_permitida_por_dominio_de_clerigo(magia, dominios_personagem: set[str]) -> bool:
    regra_csv = _csv_rule_for_magia(magia)
    if regra_csv:
        exige_dominio = _bool_sim(regra_csv.get("requer_dominio_escolhido"))
        if not exige_dominio:
            return True

        dominio_regra = {
            _normalizar(parte)
            for parte in _partes_csv(regra_csv.get("dominio"))
            if _normalizar(parte)
        }
        if not dominio_regra:
            dominio_regra = _dominios_de_magia(magia)
        if not dominio_regra:
            return False
        return len(dominio_regra & dominios_personagem) > 0

    if not bool(getattr(magia, "e_magia_dominio", False)):
        return True
    dominios_magia = _dominios_de_magia(magia)
    if not dominios_personagem or not dominios_magia:
        return False
    return len(dominios_magia & dominios_personagem) > 0


def _politica_conversao_clerigo(combatente) -> dict:
    alinhamento_norm = _alinhamento_do_combatente(combatente)
    eixo_moral = _eixo_moral(alinhamento_norm)
    eixo_etico = _eixo_etico(alinhamento_norm)

    divindade = _divindade_do_combatente(combatente)
    divindade_norm = _normalizar(divindade)

    if divindade_norm in _DIVINDADES_CURAR_SEMPRE:
        return {
            "modo": "CURAR_OBRIGATORIO",
            "fonte": "DIVINDADE",
            "regra": "St. Cuthbert: clérigos sempre convertem para Curar.",
            "alinhamento": alinhamento_norm or "",
            "divindade": divindade or "",
        }

    if (
        divindade_norm in _DIVINDADES_INFLIGIR_SEMPRE_SE_LEAL_OU_NEUTRO
        and eixo_etico in {"LEAL", "NEUTRO"}
    ):
        return {
            "modo": "INFLIGIR_OBRIGATORIO",
            "fonte": "DIVINDADE",
            "regra": "Wee Jas: clérigos leais ou neutros convertem para Infligir.",
            "alinhamento": alinhamento_norm or "",
            "divindade": divindade or "",
        }

    if (
        divindade_norm in _DIVINDADES_CURAR_SEMPRE_NEUTRO_OU_BOM
        and eixo_moral in {"BOM", "NEUTRO"}
    ):
        return {
            "modo": "CURAR_OBRIGATORIO",
            "fonte": "DIVINDADE",
            "regra": "Obad-Hai: clérigos neutros ou bons convertem para Curar.",
            "alinhamento": alinhamento_norm or "",
            "divindade": divindade or "",
        }

    if eixo_moral == "BOM":
        modo = "CURAR_OBRIGATORIO"
    elif eixo_moral == "MAL":
        modo = "INFLIGIR_OBRIGATORIO"
    else:
        modo = "ESCOLHER_CURAR_OU_INFLIGIR"

    return {
        "modo": modo,
        "fonte": "ALINHAMENTO",
        "regra": "Conversão divina definida pelo alinhamento do clérigo.",
        "alinhamento": alinhamento_norm or "",
        "divindade": divindade or "",
    }


def _nivel_por_classe(magia, classe_norm: str) -> Optional[int]:
    alias = _SPELL_LIST_ALIASES.get(classe_norm)
    buscar_em = [classe_norm] if not alias else [classe_norm, alias]

    for busca in buscar_em:
        for cn in (magia.classes_niveis or []):
            if _normalizar(cn.classe) == busca:
                return int(cn.nivel)

    classes_legacy = [p.strip() for p in re.split(r"[,/;|]", magia.classe or "") if p.strip()]
    for busca in buscar_em:
        for classe in classes_legacy:
            if _normalizar(classe) == busca:
                return int(magia.nivel)
    return None


def _max_nivel_magia_conjuravel(classe_norm: str, nivel_personagem: int) -> int:
    if classe_norm in {"CLERIGO", "DRUIDA", "MAGO"}:
        nivel = max(1, int(nivel_personagem or 1))
        return min(9, (nivel + 1) // 2)

    if classe_norm in {"RANGER", "PALADINO"}:
        nivel = max(1, int(nivel_personagem or 1))
        if nivel < 4:
            return 0
        return min(4, (nivel - 1) // 3)

    if classe_norm == "FEITICEIRO":
        progressao = {
            1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5,
            11: 6, 12: 6, 13: 7, 14: 7, 15: 8, 16: 8, 17: 9, 18: 9, 19: 9, 20: 9,
        }
        return progressao.get(max(1, min(20, nivel_personagem)), 1)

    if classe_norm == "BARDO":
        progressao = {
            1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 3, 8: 3, 9: 4, 10: 4,
            11: 4, 12: 5, 13: 5, 14: 5, 15: 6, 16: 6, 17: 6, 18: 6, 19: 6, 20: 6,
        }
        return progressao.get(max(1, min(20, nivel_personagem)), 0)

    return 0


_LIMITES_CONHECIDAS_BARDO = {
    1: [6, 4, 0, 0, 0, 0, 0],
    2: [6, 4, 0, 0, 0, 0, 0],
    3: [6, 4, 0, 0, 0, 0, 0],
    4: [6, 4, 0, 0, 0, 0, 0],
    5: [6, 4, 3, 0, 0, 0, 0],
    6: [6, 4, 4, 0, 0, 0, 0],
    7: [6, 4, 4, 2, 0, 0, 0],
    8: [6, 4, 4, 3, 0, 0, 0],
    9: [6, 4, 4, 4, 0, 0, 0],
    10: [6, 4, 4, 4, 2, 0, 0],
    11: [6, 4, 4, 4, 3, 0, 0],
    12: [6, 4, 4, 4, 4, 0, 0],
    13: [6, 4, 4, 4, 4, 2, 0],
    14: [6, 4, 4, 4, 4, 3, 0],
    15: [6, 4, 4, 4, 4, 4, 0],
    16: [6, 4, 4, 4, 4, 4, 2],
    17: [6, 4, 4, 4, 4, 4, 3],
    18: [6, 4, 4, 4, 4, 4, 4],
    19: [6, 4, 4, 4, 4, 4, 4],
    20: [6, 4, 4, 4, 4, 4, 4],
}

_LIMITES_CONHECIDAS_FEITICEIRO = {
    1: [4, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [5, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [5, 3, 0, 0, 0, 0, 0, 0, 0, 0],
    4: [6, 3, 1, 0, 0, 0, 0, 0, 0, 0],
    5: [6, 4, 2, 0, 0, 0, 0, 0, 0, 0],
    6: [7, 4, 2, 1, 0, 0, 0, 0, 0, 0],
    7: [7, 5, 3, 2, 0, 0, 0, 0, 0, 0],
    8: [8, 5, 3, 2, 1, 0, 0, 0, 0, 0],
    9: [8, 5, 4, 3, 2, 0, 0, 0, 0, 0],
    10: [9, 5, 4, 3, 2, 1, 0, 0, 0, 0],
    11: [9, 5, 5, 4, 3, 2, 0, 0, 0, 0],
    12: [9, 5, 5, 4, 3, 2, 1, 0, 0, 0],
    13: [9, 5, 5, 4, 4, 3, 2, 0, 0, 0],
    14: [9, 5, 5, 4, 4, 3, 2, 1, 0, 0],
    15: [9, 5, 5, 4, 4, 4, 3, 2, 0, 0],
    16: [9, 5, 5, 4, 4, 4, 3, 2, 1, 0],
    17: [9, 5, 5, 4, 4, 4, 4, 3, 2, 0],
    18: [9, 5, 5, 4, 4, 4, 4, 3, 3, 0],
    19: [9, 5, 5, 4, 4, 4, 4, 4, 3, 0],
    20: [9, 5, 5, 4, 4, 4, 4, 4, 4, 0],
}

# Politica G03: Mago usa grimorio aberto por aprendizado (sem teto de conhecidas por nivel).
# O controle de progressao para Mago permanece apenas no nivel maximo conjuravel.
_CLASSES_COM_LIMITE_CONHECIDAS = {"BARDO", "FEITICEIRO"}


def _limite_magias_conhecidas(classe_norm: str, nivel_personagem: int, nivel_magia: int) -> Optional[int]:
    if nivel_magia < 0:
        return 0

    if classe_norm not in _CLASSES_COM_LIMITE_CONHECIDAS:
        return None

    nivel_personagem = max(1, min(20, int(nivel_personagem or 1)))
    if classe_norm == "BARDO":
        tabela = _LIMITES_CONHECIDAS_BARDO.get(nivel_personagem, _LIMITES_CONHECIDAS_BARDO[1])
        if nivel_magia >= len(tabela):
            return 0
        return int(tabela[nivel_magia])

    if classe_norm == "FEITICEIRO":
        tabela = _LIMITES_CONHECIDAS_FEITICEIRO.get(nivel_personagem, _LIMITES_CONHECIDAS_FEITICEIRO[1])
        if nivel_magia >= len(tabela):
            return 0
        return int(tabela[nivel_magia])

    return None


class GrimorioService:
    def __init__(self, grimorio_repo: GrimorioRepository, magia_repo: MagiaRepository):
        self.grimorio_repo = grimorio_repo
        self.magia_repo = magia_repo

    def _preparar_listagem(self, combatente_id: int, classe: Optional[str] = None) -> Optional[str]:
        classe_norm = _normalizar(classe) if classe else None
        combatente = self.grimorio_repo.get_combatente(combatente_id)
        if not combatente:
            raise HTTPException(status_code=404, detail="Combatente não encontrado")

        classe_referencia = classe_norm or _normalizar(combatente.classe)
        nivel_personagem = int(combatente.nivel or 1)

        magias_adicionadas = self._sincronizar_magias_automaticas(
            combatente_id,
            classe_norm=classe_referencia,
            nivel_personagem=nivel_personagem,
        )
        if magias_adicionadas:
            self._registrar_notificacao_magias_adicionadas(
                combatente_id,
                classe_norm=classe_referencia,
                magias=magias_adicionadas,
            )

        self._reconciliar_magias_invalidas(
            combatente_id,
            classe_norm=classe_referencia,
        )
        return classe_norm

    def listar(self, combatente_id: int, classe: Optional[str] = None, favorita: Optional[bool] = None):
        classe_norm = self._preparar_listagem(combatente_id, classe=classe)
        return self.grimorio_repo.listar(combatente_id, classe=classe_norm, favorita=favorita)

    def listar_paginado(
        self,
        combatente_id: int,
        *,
        nome: Optional[str] = None,
        nivel: Optional[int] = None,
        escola: Optional[str] = None,
        componentes: Optional[str] = None,
        magia_ids: Optional[list[int]] = None,
        classe: Optional[str] = None,
        favorita: Optional[bool] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[int, list[GrimorioMagia]]:
        classe_norm = self._preparar_listagem(combatente_id, classe=classe)
        return self.grimorio_repo.listar_paginado(
            combatente_id,
            nome=nome,
            nivel=nivel,
            escola=escola,
            componentes=componentes,
            magia_ids=magia_ids,
            classe=classe_norm,
            favorita=favorita,
            skip=skip,
            limit=limit,
        )

    def diagnosticar_regras_divinas(self, combatente_id: int, *, classe: Optional[str] = None) -> dict:
        combatente = self.grimorio_repo.get_combatente(combatente_id)
        if not combatente:
            raise HTTPException(status_code=404, detail="Combatente não encontrado")

        classe_norm = _normalizar(classe) if classe else _normalizar(combatente.classe)
        if classe_norm not in _CLASSES_DIVINAS:
            raise HTTPException(
                status_code=400,
                detail="Diagnóstico disponível apenas para classes divinas (Clérigo, Druida e Paladino)",
            )

        nivel_personagem = int(combatente.nivel or 1)
        max_nivel = _max_nivel_magia_conjuravel(classe_norm, nivel_personagem)
        alinhamento_norm = _alinhamento_do_combatente(combatente)
        dominios_personagem = _dominios_do_combatente(combatente)

        _, magias_classe = self.magia_repo.listar_paginado(
            classe=classe_norm,
            nivel=None,
            escola=None,
            nome=None,
            componentes=None,
            dominio=None,
            ativo=True,
            sort_by=None,
            sort_dir=None,
            skip=0,
            limit=500,
        )

        ids_no_grimorio = {
            item.magia_id
            for item in self.grimorio_repo.listar(combatente_id, classe=classe_norm, favorita=None)
        }

        itens: list[dict] = []
        for magia in magias_classe:
            nivel_magia = _nivel_por_classe(magia, classe_norm)
            if nivel_magia is None or nivel_magia > max_nivel:
                continue

            bloqueada_por_alinhamento = _magia_bloqueada_por_alinhamento(magia, alinhamento_norm)
            bloqueada_por_dominio = False
            bloqueada_por_dominio_oposto = False

            if classe_norm == "CLERIGO":
                bloqueada_por_dominio = not _magia_permitida_por_dominio_de_clerigo(magia, dominios_personagem)
                bloqueada_por_dominio_oposto = _magia_bloqueada_por_dominios_opostos(magia, dominios_personagem)

            motivos = []
            if bloqueada_por_alinhamento:
                motivos.append("alinhamento")
            if bloqueada_por_dominio:
                motivos.append("dominio_nao_selecionado")
            if bloqueada_por_dominio_oposto:
                motivos.append("dominio_oposto")

            permitida = not (bloqueada_por_alinhamento or bloqueada_por_dominio or bloqueada_por_dominio_oposto)
            itens.append(
                {
                    "magia_id": int(magia.id),
                    "magia_nome": str(magia.nome or f"Magia {magia.id}"),
                    "magia_nivel": int(nivel_magia),
                    "classe": classe_norm,
                    "magia_e_magia_dominio": bool(getattr(magia, "e_magia_dominio", False)),
                    "magia_dominios": getattr(magia, "dominios", None),
                    "ja_no_grimorio": int(magia.id) in ids_no_grimorio,
                    "bloqueada_por_alinhamento": bool(bloqueada_por_alinhamento),
                    "bloqueada_por_dominio": bool(bloqueada_por_dominio),
                    "bloqueada_por_dominio_oposto": bool(bloqueada_por_dominio_oposto),
                    "permitida": bool(permitida),
                    "motivos_bloqueio": motivos,
                }
            )

        itens.sort(key=lambda item: (int(item["magia_nivel"]), _normalizar(item["magia_nome"])))

        total_permitidas = sum(1 for item in itens if item["permitida"])
        total_bloqueadas = len(itens) - total_permitidas
        return {
            "combatente_id": int(combatente_id),
            "classe": classe_norm,
            "alinhamento": alinhamento_norm,
            "dominios_personagem": sorted(dominios_personagem),
            "total_magias_avaliadas": len(itens),
            "total_permitidas": int(total_permitidas),
            "total_bloqueadas": int(total_bloqueadas),
            "itens": itens,
        }

    def listar_historico_troca(self, combatente_id: int, classe: Optional[str] = None, limit: int = 20):
        classe_norm = _normalizar(classe) if classe else None
        return self.grimorio_repo.listar_historico_troca(combatente_id, classe=classe_norm, limit=limit)

    def listar_notificacoes(
        self,
        combatente_id: int,
        *,
        classe: Optional[str] = None,
        apenas_nao_lidas: bool = False,
        limit: int = 30,
        force_sync: bool = True,
    ):
        combatente = self.grimorio_repo.get_combatente(combatente_id)
        if not combatente:
            raise HTTPException(status_code=404, detail="Combatente não encontrado")

        classe_norm = _normalizar(classe) if classe else _normalizar(combatente.classe)

        # Só sincroniza se force_sync=True ou se o intervalo mínimo passou
        agora = datetime.now(timezone.utc)
        ultima = _sync_last.get(combatente_id)
        deve_sincronizar = force_sync or (
            ultima is None
            or (agora - ultima).total_seconds() >= _SYNC_INTERVAL_SECONDS
        )

        if deve_sincronizar:
            _sync_last[combatente_id] = agora
            magias_adicionadas = self._sincronizar_magias_automaticas(
                combatente_id,
                classe_norm=classe_norm,
                nivel_personagem=int(combatente.nivel or 1),
            )
            if magias_adicionadas:
                self._registrar_notificacao_magias_adicionadas(
                    combatente_id,
                    classe_norm=classe_norm,
                    magias=magias_adicionadas,
                )
            self._reconciliar_magias_invalidas(combatente_id, classe_norm=classe_norm)
            self._garantir_notificacoes_sistema(combatente_id, classe_norm, int(combatente.nivel or 1))

        return self.grimorio_repo.listar_notificacoes(
            combatente_id,
            classe=classe_norm,
            apenas_nao_lidas=apenas_nao_lidas,
            limit=limit,
        )

    def _reconciliar_magias_invalidas(self, combatente_id: int, *, classe_norm: str) -> int:
        if classe_norm not in _CLASSES_DIVINAS:
            return 0

        combatente = self.grimorio_repo.get_combatente(combatente_id)
        if not combatente:
            return 0

        alinhamento_norm = _alinhamento_do_combatente(combatente)
        dominios_personagem = _dominios_do_combatente(combatente)
        itens = self.grimorio_repo.listar(combatente_id, classe=classe_norm, favorita=None)

        removidas = 0
        for item in itens:
            magia = item.magia
            if not magia:
                continue

            invalida_por_alinhamento = _magia_bloqueada_por_alinhamento(magia, alinhamento_norm)
            invalida_por_dominio = False
            invalida_por_dominio_oposto = False

            if classe_norm == "CLERIGO":
                invalida_por_dominio = not _magia_permitida_por_dominio_de_clerigo(magia, dominios_personagem)
                invalida_por_dominio_oposto = _magia_bloqueada_por_dominios_opostos(magia, dominios_personagem)

            if invalida_por_alinhamento or invalida_por_dominio or invalida_por_dominio_oposto:
                self.grimorio_repo.delete(item)
                removidas += 1

        return removidas

    def _calcular_selecao_pendente_por_nivel(
        self,
        combatente_id: int,
        *,
        classe_norm: str,
        nivel_personagem: int,
    ) -> tuple[int, dict[str, int]]:
        if classe_norm not in {"FEITICEIRO", "BARDO"}:
            return 0, {}

        _, magias_classe = self.magia_repo.listar_paginado(
            classe=_alias_lista_magias(classe_norm),
            nivel=None,
            escola=None,
            nome=None,
            componentes=None,
            dominio=None,
            ativo=True,
            sort_by=None,
            sort_dir=None,
            skip=0,
            limit=500,
        )

        max_nivel = _max_nivel_magia_conjuravel(classe_norm, nivel_personagem)
        catalogo_por_nivel = {}
        for magia in magias_classe:
            nivel_magia = _nivel_por_classe(magia, classe_norm)
            if nivel_magia is None or nivel_magia > max_nivel:
                continue
            catalogo_por_nivel[nivel_magia] = catalogo_por_nivel.get(nivel_magia, 0) + 1

        conhecidas = self.grimorio_repo.listar(combatente_id, classe=classe_norm, favorita=None)
        conhecidas_por_nivel = {}
        for item in conhecidas:
            nivel_magia = _nivel_por_classe(item.magia, classe_norm)
            if nivel_magia is None or nivel_magia > max_nivel:
                continue
            conhecidas_por_nivel[nivel_magia] = conhecidas_por_nivel.get(nivel_magia, 0) + 1

        por_nivel = {}
        total = 0
        for nivel_magia in sorted(catalogo_por_nivel.keys()):
            limite = _limite_magias_conhecidas(classe_norm, nivel_personagem, nivel_magia)
            if limite is None:
                continue

            disponiveis_catalogo = int(catalogo_por_nivel.get(nivel_magia, 0))
            conhecidas_nivel = int(conhecidas_por_nivel.get(nivel_magia, 0))
            max_escolhiveis = min(int(limite), disponiveis_catalogo)
            pendente_nivel = max(max_escolhiveis - conhecidas_nivel, 0)
            if pendente_nivel <= 0:
                continue

            por_nivel[str(nivel_magia)] = pendente_nivel
            total += pendente_nivel

        return total, por_nivel

    def _registrar_notificacao_magias_adicionadas(
        self,
        combatente_id: int,
        *,
        classe_norm: str,
        magias: list[dict],
    ) -> None:
        if not magias:
            return

        quantidade = len(magias)
        nomes_novas = [
            str(item.get("nome") or "").strip()
            for item in magias
            if str(item.get("nome") or "").strip()
        ]

        existente = self.grimorio_repo.get_notificacao_aberta_por_tipo(
            combatente_id,
            classe_norm,
            "MAGIAS_ADICIONADAS",
        )
        if existente:
            dados = {}
            if existente.dados:
                try:
                    dados = json.loads(existente.dados)
                except Exception:
                    dados = {}
            atual = int(dados.get("quantidade", 0))
            dados["quantidade"] = atual + int(quantidade)

            nomes_existentes = dados.get("magias_nomes")
            if not isinstance(nomes_existentes, list):
                nomes_existentes = []
            nomes_mesclados = []
            for nome in [*nomes_existentes, *nomes_novas]:
                texto = str(nome or "").strip()
                if not texto or texto in nomes_mesclados:
                    continue
                nomes_mesclados.append(texto)
            dados["magias_nomes"] = nomes_mesclados[:20]

            existente.dados = json.dumps(dados)
            self.grimorio_repo.update_notificacao(existente)
            return

        self.grimorio_repo.create_notificacao(
            GrimorioNotificacao(
                combatente_id=combatente_id,
                classe=classe_norm,
                tipo="MAGIAS_ADICIONADAS",
                dados=json.dumps(
                    {
                        "quantidade": int(quantidade),
                        "magias_nomes": nomes_novas[:20],
                    }
                ),
                lida=False,
            )
        )

    def _sincronizar_magias_automaticas(
        self,
        combatente_id: int,
        *,
        classe_norm: str,
        nivel_personagem: int,
    ) -> list[dict]:
        if classe_norm not in {"CLERIGO", "DRUIDA", "RANGER", "PALADINO"}:
            return []

        max_nivel = _max_nivel_magia_conjuravel(classe_norm, nivel_personagem)
        if max_nivel <= 0:
            return []

        _, magias_classe = self.magia_repo.listar_paginado(
            classe=classe_norm,
            nivel=None,
            escola=None,
            nome=None,
            componentes=None,
            dominio=None,
            ativo=True,
            sort_by=None,
            sort_dir=None,
            skip=0,
            limit=500,
        )

        existentes = {
            item.magia_id
            for item in self.grimorio_repo.listar(combatente_id, classe=classe_norm, favorita=None)
        }

        combatente = self.grimorio_repo.get_combatente(combatente_id)
        alinhamento_norm = _alinhamento_do_combatente(combatente)
        dominios_personagem = _dominios_do_combatente(combatente)

        adicionadas = []
        for magia in magias_classe:
            nivel_magia = _nivel_por_classe(magia, classe_norm)
            if nivel_magia is None or nivel_magia > max_nivel:
                continue

            if classe_norm in _CLASSES_DIVINAS and _magia_bloqueada_por_alinhamento(magia, alinhamento_norm):
                continue

            if classe_norm == "CLERIGO":
                if not _magia_permitida_por_dominio_de_clerigo(magia, dominios_personagem):
                    continue
                if _magia_bloqueada_por_dominios_opostos(magia, dominios_personagem):
                    continue

            if magia.id in existentes:
                continue

            self.grimorio_repo.create(
                GrimorioMagia(
                    combatente_id=combatente_id,
                    magia_id=magia.id,
                    classe=classe_norm,
                    origem="AUTO_NIVEL",
                )
            )
            existentes.add(magia.id)
            adicionadas.append(
                {
                    "id": int(magia.id),
                    "nome": str(magia.nome or f"Magia {magia.id}"),
                    "nivel": int(nivel_magia),
                }
            )

        return adicionadas

    def marcar_notificacao_lida(self, combatente_id: int, notificacao_id: int, *, lida: bool = True):
        notificacao = self.grimorio_repo.get_notificacao(notificacao_id)
        if not notificacao or notificacao.combatente_id != combatente_id:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        notificacao.lida = bool(lida)
        return self.grimorio_repo.update_notificacao(notificacao)

    def descartar_notificacao(self, combatente_id: int, notificacao_id: int) -> None:
        notificacao = self.grimorio_repo.get_notificacao(notificacao_id)
        if not notificacao or notificacao.combatente_id != combatente_id:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        self.grimorio_repo.delete_notificacao(notificacao)

    def adicionar_magia(self, combatente_id: int, magia_id: int, classe: str, origem: str = "SELECAO_MANUAL"):
        classe_norm = _normalizar(classe)
        combatente = self.grimorio_repo.get_combatente(combatente_id)
        if not combatente:
            raise HTTPException(status_code=404, detail="Combatente não encontrado")

        if classe_norm in {"RANGER", "PALADINO"} and int(combatente.nivel or 1) < 4:
            raise HTTPException(
                status_code=400,
                detail="Ranger e Paladino so tem acesso a magias a partir do nivel 4",
            )

        magia = self.magia_repo.get_by_id(magia_id)
        if not magia:
            raise HTTPException(status_code=404, detail="Magia não encontrada")

        classes_permitidas = {_normalizar(c.classe) for c in (magia.classes_niveis or [])}
        if not classes_permitidas:
            classes_permitidas = _classes_legacy(magia.classe)

        alias = _SPELL_LIST_ALIASES.get(classe_norm)
        if classe_norm not in classes_permitidas and not (alias and alias in classes_permitidas):
            raise HTTPException(status_code=400, detail="Magia incompatível com a classe informada")

        nivel_personagem = int(combatente.nivel or 1)
        nivel_magia = _nivel_por_classe(magia, classe_norm)
        if nivel_magia is None:
            raise HTTPException(status_code=400, detail="Magia incompatível com a classe informada")

        if classe_norm in _CLASSES_DIVINAS:
            alinhamento_norm = _alinhamento_do_combatente(combatente)
            if _magia_bloqueada_por_alinhamento(magia, alinhamento_norm):
                raise HTTPException(status_code=400, detail="Magia incompatível com o alinhamento do personagem")

        if classe_norm == "CLERIGO":
            dominios_personagem = _dominios_do_combatente(combatente)
            if not _magia_permitida_por_dominio_de_clerigo(magia, dominios_personagem):
                raise HTTPException(status_code=400, detail="Magia de domínio incompatível com os domínios do clérigo")
            if _magia_bloqueada_por_dominios_opostos(magia, dominios_personagem):
                raise HTTPException(status_code=400, detail="Magia de domínio bloqueada por domínio oposto")

        max_nivel = _max_nivel_magia_conjuravel(classe_norm, nivel_personagem)
        if nivel_magia > max_nivel:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Magia acima do nível máximo conjurável para a classe/nível atual "
                    f"(máximo: {max_nivel})"
                ),
            )

        limite_conhecidas = _limite_magias_conhecidas(classe_norm, nivel_personagem, int(nivel_magia))
        if limite_conhecidas is not None:
            itens_classe = self.grimorio_repo.listar(combatente_id, classe=classe_norm, favorita=None)
            conhecidas_no_nivel = sum(
                1 for item in itens_classe
                if _nivel_por_classe(item.magia, classe_norm) == int(nivel_magia)
            )
            if conhecidas_no_nivel >= limite_conhecidas:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Limite de magias conhecidas atingido para este nível de magia "
                        f"({limite_conhecidas} no nível {nivel_magia})"
                    ),
                )

        existente = self.grimorio_repo.get_item(combatente_id, magia_id, classe_norm)
        if existente:
            raise HTTPException(status_code=409, detail="Esta magia já está no grimório")

        item = GrimorioMagia(
            combatente_id=combatente_id,
            magia_id=magia_id,
            classe=classe_norm,
            origem=(origem or "SELECAO_MANUAL").strip().upper(),
        )
        return self.grimorio_repo.create(item)

    def atualizar_item(self, combatente_id: int, magia_id: int, classe: str, favorita: Optional[bool], anotacoes: Optional[str]):
        classe_norm = _normalizar(classe)
        item = self.grimorio_repo.get_item(combatente_id, magia_id, classe_norm)
        if not item:
            raise HTTPException(status_code=404, detail="Magia não encontrada no grimório")

        if favorita is not None:
            item.favorita = favorita
        if anotacoes is not None:
            item.anotacoes = anotacoes

        return self.grimorio_repo.update(item)

    def remover_magia(self, combatente_id: int, magia_id: int, classe: str):
        classe_norm = _normalizar(classe)
        item = self.grimorio_repo.get_item(combatente_id, magia_id, classe_norm)
        if not item:
            raise HTTPException(status_code=404, detail="Magia não encontrada no grimório")
        self.grimorio_repo.delete(item)

    def trocar_magia(self, combatente_id: int, classe: str, magia_removida_id: int, magia_adicionada_id: int):
        classe_norm = _normalizar(classe)
        if classe_norm not in {"BARDO", "FEITICEIRO"}:
            raise HTTPException(status_code=400, detail="Troca de magia disponível apenas para Bardo e Feiticeiro")

        combatente = self.grimorio_repo.get_combatente(combatente_id)
        if not combatente:
            raise HTTPException(status_code=404, detail="Combatente não encontrado")

        nivel_personagem = int(combatente.nivel or 1)
        if classe_norm == "FEITICEIRO" and (nivel_personagem < 4 or nivel_personagem % 2 != 0):
            raise HTTPException(status_code=400, detail="Feiticeiro só pode trocar magia em níveis pares a partir do 4º")
        if classe_norm == "BARDO" and nivel_personagem not in {5, 8, 11, 14, 17, 20}:
            raise HTTPException(status_code=400, detail="Bardo só pode trocar magia nos níveis 5, 8, 11, 14, 17 e 20")

        item_antigo = self.grimorio_repo.get_item(combatente_id, magia_removida_id, classe_norm)
        if not item_antigo:
            raise HTTPException(status_code=404, detail="Magia removida não encontrada no grimório")

        if self.grimorio_repo.get_item(combatente_id, magia_adicionada_id, classe_norm):
            raise HTTPException(status_code=409, detail="A magia adicionada já existe no grimório")

        magia_nova = self.magia_repo.get_by_id(magia_adicionada_id)
        if not magia_nova:
            raise HTTPException(status_code=404, detail="Magia adicionada não encontrada")

        nivel_removida = _nivel_por_classe(item_antigo.magia, classe_norm)
        nivel_nova = _nivel_por_classe(magia_nova, classe_norm)
        if nivel_removida is None or nivel_nova is None:
            raise HTTPException(status_code=400, detail="Magia incompatível com a classe informada")

        max_nivel = _max_nivel_magia_conjuravel(classe_norm, nivel_personagem)
        limite_troca = max_nivel - 1
        if limite_troca < 0:
            raise HTTPException(status_code=400, detail="Nível insuficiente para troca de magia")

        if nivel_nova > nivel_removida or nivel_nova > limite_troca:
            raise HTTPException(
                status_code=400,
                detail=(
                    "A nova magia deve ter nível <= magia removida e <= "
                    f"{limite_troca} (um nível abaixo do máximo conjurável)"
                ),
            )

        item_novo = GrimorioMagia(
            combatente_id=combatente_id,
            magia_id=magia_adicionada_id,
            classe=classe_norm,
            origem="TROCA",
            favorita=False,
        )
        historico = GrimorioHistoricoTroca(
            combatente_id=combatente_id,
            classe=classe_norm,
            magia_removida_id=magia_removida_id,
            magia_adicionada_id=magia_adicionada_id,
            nivel_personagem=nivel_personagem,
        )
        return self.grimorio_repo.trocar_magia(
            item_antigo=item_antigo,
            item_novo=item_novo,
            historico=historico,
        )

    def _garantir_notificacoes_sistema(self, combatente_id: int, classe_norm: str, nivel_personagem: int) -> None:
        combatente = self.grimorio_repo.get_combatente(combatente_id)
        if not combatente:
            return

        if classe_norm == "CLERIGO":
            self._garantir_notificacao_conversao_divina(combatente_id, classe_norm, combatente)

        if classe_norm in {"RANGER", "PALADINO"} and nivel_personagem < 4:
            if not self.grimorio_repo.get_notificacao_aberta_por_tipo(
                combatente_id, classe_norm, "SEM_MAGIAS_ATE_NIVEL_4"
            ):
                self.grimorio_repo.create_notificacao(
                    GrimorioNotificacao(
                        combatente_id=combatente_id,
                        classe=classe_norm,
                        tipo="SEM_MAGIAS_ATE_NIVEL_4",
                        dados=json.dumps({"nivel_minimo": 4}),
                        lida=False,
                    )
                )

        if classe_norm in {"FEITICEIRO", "BARDO"}:
            troca_disponivel = (
                (classe_norm == "FEITICEIRO" and nivel_personagem >= 4 and nivel_personagem % 2 == 0)
                or (classe_norm == "BARDO" and nivel_personagem in {5, 8, 11, 14, 17, 20})
            )
            if troca_disponivel and not self.grimorio_repo.get_notificacao_aberta_por_tipo(
                combatente_id, classe_norm, "TROCA_DISPONIVEL"
            ):
                self.grimorio_repo.create_notificacao(
                    GrimorioNotificacao(
                        combatente_id=combatente_id,
                        classe=classe_norm,
                        tipo="TROCA_DISPONIVEL",
                        dados=json.dumps({"nivel_personagem": nivel_personagem}),
                        lida=False,
                    )
                )

        if classe_norm in {"FEITICEIRO", "BARDO"}:
            pendentes, por_nivel = self._calcular_selecao_pendente_por_nivel(
                combatente_id,
                classe_norm=classe_norm,
                nivel_personagem=nivel_personagem,
            )
            notif_pendente = self.grimorio_repo.get_notificacao_aberta_por_tipo(
                combatente_id,
                classe_norm,
                "SELECAO_PENDENTE",
            )

            if pendentes > 0:
                dados_payload = {
                    "quantidade_pendente": int(pendentes),
                    "por_nivel": por_nivel,
                }
                if notif_pendente:
                    notif_pendente.dados = json.dumps(dados_payload)
                    self.grimorio_repo.update_notificacao(notif_pendente)
                else:
                    self.grimorio_repo.create_notificacao(
                        GrimorioNotificacao(
                            combatente_id=combatente_id,
                            classe=classe_norm,
                            tipo="SELECAO_PENDENTE",
                            dados=json.dumps(dados_payload),
                            lida=False,
                        )
                    )
            elif notif_pendente:
                notif_pendente.lida = True
                self.grimorio_repo.update_notificacao(notif_pendente)

    def _garantir_notificacao_conversao_divina(self, combatente_id: int, classe_norm: str, combatente) -> None:
        politica = _politica_conversao_clerigo(combatente)
        payload = {
            "modo": politica.get("modo"),
            "fonte": politica.get("fonte"),
            "regra": politica.get("regra"),
            "alinhamento": politica.get("alinhamento") or "",
            "divindade": politica.get("divindade") or "",
        }

        existente = self.grimorio_repo.get_notificacao_aberta_por_tipo(
            combatente_id,
            classe_norm,
            "CONVERSAO_DIVINA",
        )

        if existente:
            try:
                dados_existentes = json.loads(existente.dados or "{}")
            except Exception:
                dados_existentes = {}
            if dados_existentes == payload:
                return
            existente.dados = json.dumps(payload)
            self.grimorio_repo.update_notificacao(existente)
            return

        self.grimorio_repo.create_notificacao(
            GrimorioNotificacao(
                combatente_id=combatente_id,
                classe=classe_norm,
                tipo="CONVERSAO_DIVINA",
                dados=json.dumps(payload),
                lida=False,
            )
        )
