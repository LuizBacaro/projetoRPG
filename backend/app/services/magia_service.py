"""Service com regras de negócio do catálogo de magias."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from fastapi import HTTPException

from ..models.magia import Magia
from ..repositories.base import commit_with_rollback
from ..repositories.magia_repository import MagiaRepository


class MagiaService:
    def __init__(self, repository: MagiaRepository):
        self.repository = repository

    def listar_magias(self, **kwargs):
        return self.repository.listar_paginado(**kwargs)

    def listar_classes(self) -> list[str]:
        return self.repository.listar_classes()

    def obter_por_id(self, magia_id: int) -> Magia:
        magia = self.repository.get_by_id(magia_id)
        if not magia:
            raise HTTPException(status_code=404, detail="Magia não encontrada")
        return magia

    def criar(self, payload: Any) -> Magia:
        data = self._as_dict(payload)
        self._validar_nome_unico(data["nome"])

        classes_niveis = data.pop("classes_niveis")
        self._validar_classes_niveis(classes_niveis)

        legacy = self._gerar_legacy_classes(classes_niveis)
        data["classe"] = legacy["classe"]
        data["nivel"] = legacy["nivel"]

        magia = Magia(**data)
        self.repository.create(magia)
        self.repository.replace_classes(magia, classes_niveis)
        return self.repository.save(magia)

    def atualizar(self, magia_id: int, payload: Any) -> Magia:
        magia = self.obter_por_id(magia_id)
        data = self._as_dict(payload, exclude_unset=True)

        if "nome" in data and data["nome"] and data["nome"].strip().lower() != magia.nome.strip().lower():
            self._validar_nome_unico(data["nome"])

        classes_niveis = data.pop("classes_niveis", None)

        for key, value in data.items():
            if hasattr(magia, key):
                setattr(magia, key, value)

        if classes_niveis is not None:
            self._validar_classes_niveis(classes_niveis)
            legacy = self._gerar_legacy_classes(classes_niveis)
            magia.classe = legacy["classe"]
            magia.nivel = legacy["nivel"]
            self.repository.replace_classes(magia, classes_niveis)

        commit_with_rollback(self.repository.db)
        return self.repository.save(magia)

    def desativar(self, magia_id: int) -> Magia:
        magia = self.obter_por_id(magia_id)
        magia.ativo = False
        return self.repository.save(magia)

    def reativar(self, magia_id: int) -> Magia:
        magia = self.obter_por_id(magia_id)
        magia.ativo = True
        return self.repository.save(magia)

    def deletar_fisico(self, magia_id: int) -> None:
        magia = self.obter_por_id(magia_id)
        if self.repository.has_dependencias(magia_id):
            raise HTTPException(
                status_code=409,
                detail="Esta magia não pode ser excluída pois está vinculada a grimório/ficha. Use desativar.",
            )
        self.repository.db.delete(magia)
        commit_with_rollback(self.repository.db)

    def _validar_nome_unico(self, nome: str) -> None:
        existente = self.repository.get_by_nome(nome)
        if existente:
            raise HTTPException(status_code=409, detail="Já existe uma magia com este nome")

    @staticmethod
    def _validar_classes_niveis(classes_niveis: list[dict]) -> None:
        if not classes_niveis:
            raise HTTPException(status_code=422, detail="Informe ao menos uma classe com nível")

        classes = set()
        for item in classes_niveis:
            classe = str(item.get("classe", "")).strip().upper()
            nivel = item.get("nivel")
            if not classe:
                raise HTTPException(status_code=422, detail="Classe inválida em classes_niveis")
            if classe in classes:
                raise HTTPException(status_code=422, detail=f"Classe duplicada em classes_niveis: {classe}")
            if not isinstance(nivel, int) or nivel < 0 or nivel > 9:
                raise HTTPException(status_code=422, detail=f"Nível inválido para classe {classe}")
            classes.add(classe)

    @staticmethod
    def _gerar_legacy_classes(classes_niveis: list[dict]) -> dict:
        ordenadas = sorted(classes_niveis, key=lambda x: (x["nivel"], str(x["classe"]).upper()))
        classe_legacy = ",".join(str(item["classe"]).strip().upper() for item in ordenadas)
        nivel_legacy = ordenadas[0]["nivel"]
        return {"classe": classe_legacy, "nivel": nivel_legacy}

    @staticmethod
    def _as_dict(payload: Any, *, exclude_unset: bool = False) -> dict:
        if hasattr(payload, "model_dump"):
            return payload.model_dump(exclude_unset=exclude_unset)
        if is_dataclass(payload):
            return asdict(payload)
        if isinstance(payload, dict):
            return payload
        raise TypeError("Payload inválido")
