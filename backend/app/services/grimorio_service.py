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


def _normalizar(valor: str) -> str:
    normalizado = unicodedata.normalize("NFD", str(valor or ""))
    sem_acentos = "".join(ch for ch in normalizado if unicodedata.category(ch) != "Mn")
    return sem_acentos.strip().upper()


def _classes_legacy(valor: str) -> set[str]:
    partes = [p.strip() for p in re.split(r"[,/;|]", valor or "") if p.strip()]
    return {_normalizar(parte) for parte in partes}


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


class GrimorioService:
    def __init__(self, grimorio_repo: GrimorioRepository, magia_repo: MagiaRepository):
        self.grimorio_repo = grimorio_repo
        self.magia_repo = magia_repo

    def listar(self, combatente_id: int, classe: Optional[str] = None, favorita: Optional[bool] = None):
        return self.grimorio_repo.listar(combatente_id, classe=classe, favorita=favorita)

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
        self._garantir_notificacoes_sistema(combatente_id, classe_norm, int(combatente.nivel or 1))
        return self.grimorio_repo.listar_notificacoes(
            combatente_id,
            classe=classe_norm,
            apenas_nao_lidas=apenas_nao_lidas,
            limit=limit,
        )

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
        magia = self.magia_repo.get_by_id(magia_id)
        if not magia:
            raise HTTPException(status_code=404, detail="Magia não encontrada")

        classes_permitidas = {c.classe for c in (magia.classes_niveis or [])}
        if not classes_permitidas:
            classes_permitidas = _classes_legacy(magia.classe)

        if classe_norm not in classes_permitidas:
            raise HTTPException(status_code=400, detail="Magia incompatível com a classe informada")

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

        if classe_norm in {"MAGO", "FEITICEIRO", "BARDO"}:
            magias_classe = self.magia_repo.listar_paginado(
                classe=classe_norm,
                nivel=None,
                escola=None,
                nome=None,
                componentes=None,
                dominio=None,
                ativo=True,
                skip=0,
                limit=500,
            )[1]
            total_catalogo = len(magias_classe)
            total_grimorio = len(self.grimorio_repo.listar(combatente_id, classe=classe_norm, favorita=None))
            pendentes = max(total_catalogo - total_grimorio, 0)
            if pendentes > 0 and not self.grimorio_repo.get_notificacao_aberta_por_tipo(
                combatente_id, classe_norm, "SELECAO_PENDENTE"
            ):
                self.grimorio_repo.create_notificacao(
                    GrimorioNotificacao(
                        combatente_id=combatente_id,
                        classe=classe_norm,
                        tipo="SELECAO_PENDENTE",
                        dados=json.dumps({"quantidade_pendente": pendentes}),
                        lida=False,
                    )
                )
