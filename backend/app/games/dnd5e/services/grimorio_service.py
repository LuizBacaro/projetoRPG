"""Service — grimório de magias do personagem D&D 5e."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import HTTPException

from app.games.dnd5e.models.grimorio import (
    Dnd5eGrimorioHistoricoTroca,
    Dnd5eGrimorioMagia,
    Dnd5eGrimorioNotificacao,
)
from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.rules.magia import max_nivel_magia_conjuravel
from app.games.dnd5e.services.conjuracao_shared import (
    classe_slug_ficha,
    contar_magias_conhecidas_grimorio,
    magias_conhecidas_max,
)
from app.games.dnd5e.services.magia_service import _componentes_str


def _normalizar_classe(classe: str) -> str:
    return (classe or "").strip().lower()


# Slug de conjurador (antes do alias de lista de magias)
_CLASSE_REGRAS_MAP = {
    "sorcerer": "feiticeiro",
    "wizard": "mago",
    "bard": "bardo",
    "warlock": "bruxo",
    "cleric": "clerigo",
    "druid": "druida",
    "paladin": "paladino",
    "ranger": "patrulheiro",
}

# PHB 5e: magias conhecidas — troca ao subir de nível (Bardo, Feiticeiro, Bruxo; Mago no grimório)
_CLASSES_TROCA_5E = frozenset({"bardo", "feiticeiro", "mago", "bruxo"})

_SPELL_LIST_ALIASES = {
    "feiticeiro": "mago",
    "sorcerer": "mago",
    "wizard": "mago",
    "cleric": "clerigo",
    "druid": "druida",
    "bard": "bardo",
    "warlock": "bruxo",
    "paladin": "paladino",
    "ranger": "patrulheiro",
}


def _classe_lista_magias(classe: str) -> str:
    slug = _normalizar_classe(classe)
    return _SPELL_LIST_ALIASES.get(slug, slug)


def _classe_conjurador_regras(classe: str) -> str:
    slug = _normalizar_classe(classe)
    return _CLASSE_REGRAS_MAP.get(slug, slug)


def _validar_janela_troca_5e(classe_conj: str, nivel_personagem: int) -> None:
    """Ao subir de nível na classe, uma magia conhecida pode ser trocada (PHB § Magias conhecidas)."""
    if classe_conj not in _CLASSES_TROCA_5E:
        raise HTTPException(
            status_code=400,
            detail="Troca de magia disponível para Bardo, Feiticeiro, Mago e Bruxo",
        )
    if nivel_personagem < 2:
        raise HTTPException(
            status_code=400,
            detail="Só é possível trocar magia a partir do 2º nível de conjurador",
        )


def _ja_trocou_neste_nivel(
    repo: Dnd5eGrimorioRepository,
    personagem_id: int,
    classe_grimorio: str,
    nivel_personagem: int,
) -> bool:
    historico = repo.listar_historico_troca(
        personagem_id, classe=classe_grimorio, limit=50
    )
    return any(int(h.nivel_personagem) == nivel_personagem for h in historico)


class Dnd5eGrimorioService:
    def __init__(
        self,
        grimorio_repo: Dnd5eGrimorioRepository,
        magia_repo: Dnd5eMagiaRepository,
    ):
        self.grimorio_repo = grimorio_repo
        self.magia_repo = magia_repo

    def listar_paginado(
        self,
        personagem_id: int,
        *,
        nome: Optional[str] = None,
        nivel: Optional[int] = None,
        escola: Optional[str] = None,
        classe: Optional[str] = None,
        favorita: Optional[bool] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[int, list[Dnd5eGrimorioMagia]]:
        classe_norm = _normalizar_classe(classe) if classe else None
        return self.grimorio_repo.listar_paginado(
            personagem_id,
            nome=nome,
            nivel=nivel,
            escola=escola,
            classe=classe_norm,
            favorita=favorita,
            skip=skip,
            limit=limit,
        )

    def adicionar_magia(
        self,
        personagem_id: int,
        *,
        magia_id: int,
        classe: str,
        origem: str = "SELECAO_MANUAL",
    ) -> Dnd5eGrimorioMagia:
        classe_norm = _classe_lista_magias(classe)
        magia = self.magia_repo.obter(magia_id)
        if not magia:
            raise HTTPException(status_code=404, detail="Magia não encontrada")

        permitida = any(
            row.classe_slug == classe_norm for row in (magia.classes_niveis or [])
        )
        if not permitida:
            raise HTTPException(
                status_code=422,
                detail=f"Magia não pertence à lista da classe '{classe_norm}'",
            )

        existente = self.grimorio_repo.obter_item(personagem_id, magia_id, classe_norm)
        if existente:
            raise HTTPException(status_code=409, detail="Magia já está no grimório")

        personagem = self.grimorio_repo.obter_personagem(personagem_id)
        if personagem:
            ficha = dict(personagem.ficha_json or {})
            slug = classe_slug_ficha(ficha) or classe_norm
            nivel_pers = int(personagem.nivel or 1)
            maximo = magias_conhecidas_max(slug, nivel_pers)
            if maximo is not None and int(magia.nivel or 0) >= 1:
                _, itens = self.grimorio_repo.listar_paginado(
                    personagem_id, classe=classe_norm, limit=500
                )
                conhecidas = contar_magias_conhecidas_grimorio(itens)
                if conhecidas >= maximo:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Limite de magias conhecidas ({maximo}) atingido",
                    )

        item = Dnd5eGrimorioMagia(
            personagem_id=personagem_id,
            magia_id=magia_id,
            classe=classe_norm,
            origem=origem,
        )
        return self.grimorio_repo.adicionar(item)

    def atualizar_item(
        self,
        personagem_id: int,
        magia_id: int,
        *,
        classe: str,
        favorita: Optional[bool] = None,
        anotacoes: Optional[str] = None,
    ) -> Dnd5eGrimorioMagia:
        classe_norm = _classe_lista_magias(classe)
        item = self.grimorio_repo.obter_item(personagem_id, magia_id, classe_norm)
        if not item:
            raise HTTPException(
                status_code=404, detail="Item do grimório não encontrado"
            )
        if favorita is not None:
            item.favorita = favorita
        if anotacoes is not None:
            item.anotacoes = anotacoes.strip() or None
        return self.grimorio_repo.atualizar(item)

    def remover_magia(self, personagem_id: int, magia_id: int, *, classe: str) -> None:
        classe_norm = _classe_lista_magias(classe)
        item = self.grimorio_repo.obter_item(personagem_id, magia_id, classe_norm)
        if not item:
            raise HTTPException(
                status_code=404, detail="Item do grimório não encontrado"
            )
        self.grimorio_repo.remover(item)

    def listar_historico_troca(
        self, personagem_id: int, *, classe: Optional[str] = None, limit: int = 20
    ) -> list[Dnd5eGrimorioHistoricoTroca]:
        classe_norm = _classe_lista_magias(classe) if classe else None
        return self.grimorio_repo.listar_historico_troca(
            personagem_id, classe=classe_norm, limit=limit
        )

    def trocar_magia(
        self,
        personagem_id: int,
        *,
        classe: str,
        magia_removida_id: int,
        magia_adicionada_id: int,
    ) -> Dnd5eGrimorioHistoricoTroca:
        classe_conj = _classe_conjurador_regras(classe)
        classe_norm = _classe_lista_magias(classe)

        personagem = self.grimorio_repo.obter_personagem(personagem_id)
        if not personagem:
            raise HTTPException(status_code=404, detail="Personagem não encontrado")

        nivel_personagem = int(personagem.nivel or 1)
        _validar_janela_troca_5e(classe_conj, nivel_personagem)
        if _ja_trocou_neste_nivel(
            self.grimorio_repo, personagem_id, classe_norm, nivel_personagem
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Já foi registrada uma troca de magia neste nível de personagem. "
                    "No PHB 5e, ao subir de nível você pode substituir no máximo uma magia conhecida."
                ),
            )

        item_antigo = self.grimorio_repo.obter_item(
            personagem_id, magia_removida_id, classe_norm
        )
        if not item_antigo:
            raise HTTPException(
                status_code=404, detail="Magia removida não está no grimório"
            )

        if self.grimorio_repo.obter_item(
            personagem_id, magia_adicionada_id, classe_norm
        ):
            raise HTTPException(
                status_code=409, detail="Magia nova já está no grimório"
            )

        magia_nova = self.magia_repo.obter(magia_adicionada_id)
        if not magia_nova:
            raise HTTPException(
                status_code=404, detail="Magia adicionada não encontrada"
            )

        nivel_removida = item_antigo.magia.nivel if item_antigo.magia else None
        nivel_nova = magia_nova.nivel
        permitida = any(
            row.classe_slug == classe_norm for row in (magia_nova.classes_niveis or [])
        )
        if not permitida:
            raise HTTPException(
                status_code=422,
                detail="Magia adicionada não pertence à lista da classe",
            )
        max_nivel = max_nivel_magia_conjuravel(classe_conj, nivel_personagem)
        if nivel_nova > max_nivel:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"A magia substituta deve ser de nível ≤ {max_nivel} "
                    "(nível para o qual você tem espaços de magia)"
                ),
            )

        item_novo = Dnd5eGrimorioMagia(
            personagem_id=personagem_id,
            magia_id=magia_adicionada_id,
            classe=classe_norm,
            origem="TROCA",
            favorita=item_antigo.favorita,
            anotacoes=item_antigo.anotacoes,
        )
        historico = Dnd5eGrimorioHistoricoTroca(
            personagem_id=personagem_id,
            classe=classe_norm,
            magia_removida_id=magia_removida_id,
            magia_adicionada_id=magia_adicionada_id,
            nivel_personagem=nivel_personagem,
        )
        return self.grimorio_repo.registrar_troca(
            item_antigo=item_antigo, item_novo=item_novo, historico=historico
        )

    def listar_notificacoes(
        self,
        personagem_id: int,
        *,
        classe: Optional[str] = None,
        apenas_nao_lidas: bool = False,
        limit: int = 30,
        force_sync: bool = True,
    ) -> list[Dnd5eGrimorioNotificacao]:
        classe_norm = _classe_lista_magias(classe) if classe else None
        if force_sync and classe_norm:
            self._garantir_notificacao_nivel(personagem_id, classe_norm)
        return self.grimorio_repo.listar_notificacoes(
            personagem_id,
            classe=classe_norm,
            apenas_nao_lidas=apenas_nao_lidas,
            limit=limit,
        )

    def marcar_notificacao_lida(
        self, personagem_id: int, notificacao_id: int, *, lida: bool = True
    ) -> Dnd5eGrimorioNotificacao:
        notif = self.grimorio_repo.get_notificacao(notificacao_id)
        if not notif or notif.personagem_id != personagem_id:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        notif.lida = bool(lida)
        return self.grimorio_repo.update_notificacao(notif)

    def descartar_notificacao(self, personagem_id: int, notificacao_id: int) -> None:
        notif = self.grimorio_repo.get_notificacao(notificacao_id)
        if not notif or notif.personagem_id != personagem_id:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        self.grimorio_repo.delete_notificacao(notif)

    def _garantir_notificacao_nivel(self, personagem_id: int, classe_norm: str) -> None:
        personagem = self.grimorio_repo.obter_personagem(personagem_id)
        if not personagem:
            return
        nivel = int(personagem.nivel or 1)
        if nivel < 1:
            return
        tipo = "MAGIA_NOVO_NIVEL"
        if self.grimorio_repo.get_notificacao_aberta_por_tipo(
            personagem_id, classe_norm, tipo
        ):
            return
        dados = json.dumps(
            {
                "nivel": nivel,
                "mensagem": f"Você pode escolher magias de até o nível permitido (nível {nivel}).",
            },
            ensure_ascii=False,
        )
        self.grimorio_repo.create_notificacao(
            Dnd5eGrimorioNotificacao(
                personagem_id=personagem_id,
                classe=classe_norm,
                tipo=tipo,
                dados=dados,
                lida=False,
            )
        )


def grimorio_item_para_dict(item: Dnd5eGrimorioMagia) -> dict:
    magia = item.magia
    return {
        "id": item.id,
        "personagem_id": item.personagem_id,
        "magia_id": item.magia_id,
        "classe": item.classe,
        "favorita": item.favorita,
        "anotacoes": item.anotacoes,
        "origem": item.origem,
        "adicionada_em": item.adicionada_em,
        "magia_nome": magia.nome if magia else None,
        "magia_ataque_magico": getattr(magia, "ataque_magico", None) if magia else None,
        "magia_escola": magia.escola if magia else None,
        "magia_nivel": magia.nivel if magia else None,
        "magia_componentes": _componentes_str(magia) if magia else None,
        "descricao": magia.descricao if magia else None,
        "descricao_nivel_superior": magia.descricao_nivel_superior if magia else None,
        "tempo_conjuracao": magia.tempo_conjuracao if magia else None,
        "alcance_texto": magia.alcance_texto if magia else None,
        "duracao": magia.duracao if magia else None,
        "requer_concentracao": bool(magia.requer_concentracao) if magia else False,
        "ritual": bool(magia.ritual) if magia else False,
        "material_consumido": bool(magia.material_consumido) if magia else False,
        "componentes_material": magia.componentes_material if magia else None,
        "teste_resistencia": magia.teste_resistencia if magia else None,
        # Compatibilidade com GrimorioController dnd35
        "combatente_id": item.personagem_id,
        "magia_e_magia_dominio": False,
        "magia_dominios": None,
        "sub_escola": None,
        "area_efeito": None,
        "resistencia_magia": None,
    }
