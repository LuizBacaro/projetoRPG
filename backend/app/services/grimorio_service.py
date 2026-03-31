"""Regras de negócio do Grimório."""

from __future__ import annotations

import re
import unicodedata
import json
from typing import Optional

from fastapi import HTTPException

from ..models.grimorio import GrimorioHistoricoTroca, GrimorioMagia, GrimorioNotificacao
from ..repositories.grimorio_repository import GrimorioRepository
from ..repositories.magia_repository import MagiaRepository


_CLASSES_DIVINAS = {"CLERIGO", "DRUIDA", "RANGER", "PALADINO"}
_DOMINIOS_BLOQUEADOS_POR_ALINHAMENTO = {
    "BOM": {"MAL", "DESTRUICAO"},
    "MAL": {"BEM", "CURA"},
    "CAOTICO": {"ORDEM", "LEI"},
    "ORDEIRO": {"CAOS"},
    "LEAL": {"CAOS"},
}
_PARES_DOMINIOS_OPOSTOS = (
    frozenset({"MAL", "BEM"}),
    frozenset({"LEI", "CAOS"}),
    frozenset({"ORDEM", "CAOS"}),
    frozenset({"PROTECAO", "DESTRUICAO"}),
)


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
    if "BEM" in texto:
        descritores.add("BEM")
    if "MAL" in texto:
        descritores.add("MAL")
    if "CAOS" in texto:
        descritores.add("CAOS")
    if "LEI" in texto or "ORDEM" in texto:
        descritores.add("LEI")
        descritores.add("ORDEM")
    return descritores


def _alinhamento_do_combatente(combatente) -> str | None:
    valor = getattr(combatente, "alinhamento", None) or getattr(combatente, "tendencia", None)
    normalizado = _normalizar(valor) if valor else ""
    return normalizado or None


def _marcadores_alinhamento(alinhamento_norm: str | None) -> set[str]:
    if not alinhamento_norm:
        return set()

    marcadores = set()
    if "BOM" in alinhamento_norm:
        marcadores.add("BOM")
    if "MAL" in alinhamento_norm:
        marcadores.add("MAL")
    if "CAOT" in alinhamento_norm:
        marcadores.add("CAOTICO")
    if "ORDEIR" in alinhamento_norm or "LEAL" in alinhamento_norm:
        marcadores.add("ORDEIRO")
        marcadores.add("LEAL")
    return marcadores


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


def _dominios_opostos(dominio: str) -> set[str]:
    opostos = set()
    for par in _PARES_DOMINIOS_OPOSTOS:
        if dominio in par:
            opostos.update(par - {dominio})
    return opostos


def _magia_bloqueada_por_alinhamento(magia, alinhamento_norm: str | None) -> bool:
    if not alinhamento_norm:
        return False
    bloqueados = set()
    for marcador in _marcadores_alinhamento(alinhamento_norm):
        bloqueados.update(_DOMINIOS_BLOQUEADOS_POR_ALINHAMENTO.get(marcador, set()))
    if not bloqueados:
        return False

    tags = _dominios_de_magia(magia) | _descritor_de_magia(magia)
    return len(tags & bloqueados) > 0


def _magia_bloqueada_por_dominios_opostos(magia, dominios_personagem: set[str]) -> bool:
    if not bool(getattr(magia, "e_magia_dominio", False)) or not dominios_personagem:
        return False

    dominios_magia = _dominios_de_magia(magia)
    if not dominios_magia:
        return False

    opostos = set()
    for dominio in dominios_personagem:
        opostos.update(_dominios_opostos(dominio))

    return len(dominios_magia & opostos) > 0


def _magia_permitida_por_dominio_de_clerigo(magia, dominios_personagem: set[str]) -> bool:
    if not bool(getattr(magia, "e_magia_dominio", False)):
        return True
    dominios_magia = _dominios_de_magia(magia)
    if not dominios_personagem or not dominios_magia:
        return False
    return len(dominios_magia & dominios_personagem) > 0


def _nivel_por_classe(magia, classe_norm: str) -> Optional[int]:
    for cn in (magia.classes_niveis or []):
        if _normalizar(cn.classe) == classe_norm:
            return int(cn.nivel)

    classes_legacy = [p.strip() for p in re.split(r"[,/;|]", magia.classe or "") if p.strip()]
    for classe in classes_legacy:
        if _normalizar(classe) == classe_norm:
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

    def listar(self, combatente_id: int, classe: Optional[str] = None, favorita: Optional[bool] = None):
        classe_norm = _normalizar(classe) if classe else None
        combatente = self.grimorio_repo.get_combatente(combatente_id)
        if not combatente:
            raise HTTPException(status_code=404, detail="Combatente não encontrado")

        magias_adicionadas = self._sincronizar_magias_automaticas(
            combatente_id,
            classe_norm=classe_norm or _normalizar(combatente.classe),
            nivel_personagem=int(combatente.nivel or 1),
        )
        if magias_adicionadas:
            self._registrar_notificacao_magias_adicionadas(
                combatente_id,
                classe_norm=classe_norm or _normalizar(combatente.classe),
                magias=magias_adicionadas,
            )

        self._reconciliar_magias_invalidas(
            combatente_id,
            classe_norm=classe_norm or _normalizar(combatente.classe),
        )
        return self.grimorio_repo.listar(combatente_id, classe=classe_norm, favorita=favorita)

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
    ):
        combatente = self.grimorio_repo.get_combatente(combatente_id)
        if not combatente:
            raise HTTPException(status_code=404, detail="Combatente não encontrado")

        classe_norm = _normalizar(classe) if classe else _normalizar(combatente.classe)
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

        classes_permitidas = {c.classe for c in (magia.classes_niveis or [])}
        if not classes_permitidas:
            classes_permitidas = _classes_legacy(magia.classe)

        if classe_norm not in classes_permitidas:
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
