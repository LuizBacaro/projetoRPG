"""Service com regras de negócio do catálogo de magias (D&D 3.5).

Localização: `app.games.dnd35.services.magia_service`. Shim em
`app.services.magia_service` durante a reorganização multi-jogo.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from fastapi import HTTPException

from app.games.dnd35.catalogs import divindades_catalogo as _divindades_catalogo
from app.games.dnd35.models.magia import Magia
from app.games.dnd35.ports import MagiaRepositoryProtocol
from app.games.dnd35.text_utils import normalizar_classe as _normalizar_classe
from app.repositories.base import commit_with_rollback

DOMINIOS_FIXOS = {
    "AR": "Ar",
    "BEM": "Bem",
    "CAOS": "Caos",
    "CONHECIMENTO": "Conhecimento",
    "CURA": "Cura",
    "DESTRUICAO": "Destruicao",
    "ENGANACAO": "Enganacao",
    "FOGO": "Fogo",
    "FORCA": "Forca",
    "GUERRA": "Guerra",
    "MAGIA": "Magia",
    "MAL": "Mal",
    "MORTE": "Morte",
    "PROTECAO": "Protecao",
    "SOL": "Sol",
    "SORTE": "Sorte",
    "TERRA": "Terra",
    "VIAGEM": "Viagem",
}


class MagiaService:
    def __init__(self, repository: MagiaRepositoryProtocol):
        self.repository = repository

    def listar_magias(self, **kwargs):
        sort_by = kwargs.get("sort_by")
        sort_dir = kwargs.get("sort_dir")

        if sort_by is not None:
            sort_by = str(sort_by).strip().lower()
            if sort_by not in {"nome", "escola", "nivel"}:
                raise HTTPException(
                    status_code=422, detail="Campo de ordenacao invalido"
                )
            kwargs["sort_by"] = sort_by

        if sort_dir is not None:
            sort_dir = str(sort_dir).strip().lower()
            if sort_dir not in {"asc", "desc"}:
                raise HTTPException(
                    status_code=422, detail="Direcao de ordenacao invalida"
                )
            kwargs["sort_dir"] = sort_dir

        return self.repository.listar_paginado(**kwargs)

    def listar_classes(self) -> list[str]:
        return self.repository.listar_classes()

    def listar_dominios(self) -> list[str]:
        return list(DOMINIOS_FIXOS.values())

    def listar_divindades_sugeridas(self) -> list[str]:
        """Nomes canonicos das divindades (retrocompatibilidade com /magias/divindades)."""
        return _divindades_catalogo.listar_nomes()

    def listar_divindades_catalogo(self) -> list[dict]:
        """Catalogo rico (nome, titulo, label, tendencia, dominios, descricao)."""
        return _divindades_catalogo.listar_catalogo()

    def obter_por_id(self, magia_id: int) -> Magia:
        magia = self.repository.get_by_id(magia_id)
        if not magia:
            raise HTTPException(status_code=404, detail="Magia não encontrada")
        return magia

    def criar(self, payload: Any, *, usuario_id: int | None = None) -> Magia:
        data = self._as_dict(payload)
        self._validar_nome_unico(data["nome"])
        self._aplicar_regras_dominios(data)

        classes_niveis = data.pop("classes_niveis")
        self._validar_classes_niveis(classes_niveis)

        legacy = self._gerar_legacy_classes(classes_niveis)
        data["classe"] = legacy["classe"]
        data["nivel"] = legacy["nivel"]

        magia = Magia(**data)
        self.repository.create(magia)
        self.repository.replace_classes(magia, classes_niveis)
        magia = self.repository.save(magia)
        self.repository.registrar_historico(
            magia_id=magia.id,
            usuario_id=usuario_id,
            acao="CRIACAO",
            dados_anteriores=None,
            dados_novos=self._snapshot_magia(magia),
        )
        return magia

    def atualizar(
        self, magia_id: int, payload: Any, *, usuario_id: int | None = None
    ) -> Magia:
        magia = self.obter_por_id(magia_id)
        dados_anteriores = self._snapshot_magia(magia)
        data = self._as_dict(payload, exclude_unset=True)

        if (
            "nome" in data
            and data["nome"]
            and data["nome"].strip().lower() != magia.nome.strip().lower()
        ):
            self._validar_nome_unico(data["nome"])

        self._aplicar_regras_dominios(data, magia_atual=magia)

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
        magia = self.repository.save(magia)
        self.repository.registrar_historico(
            magia_id=magia.id,
            usuario_id=usuario_id,
            acao="EDICAO",
            dados_anteriores=dados_anteriores,
            dados_novos=self._snapshot_magia(magia),
        )
        return magia

    def desativar(self, magia_id: int, *, usuario_id: int | None = None) -> Magia:
        magia = self.obter_por_id(magia_id)
        dados_anteriores = self._snapshot_magia(magia)
        magia.ativo = False
        magia = self.repository.save(magia)
        self.repository.registrar_historico(
            magia_id=magia.id,
            usuario_id=usuario_id,
            acao="DESATIVACAO",
            dados_anteriores=dados_anteriores,
            dados_novos=self._snapshot_magia(magia),
        )
        return magia

    def reativar(self, magia_id: int, *, usuario_id: int | None = None) -> Magia:
        magia = self.obter_por_id(magia_id)
        dados_anteriores = self._snapshot_magia(magia)
        magia.ativo = True
        magia = self.repository.save(magia)
        self.repository.registrar_historico(
            magia_id=magia.id,
            usuario_id=usuario_id,
            acao="REATIVACAO",
            dados_anteriores=dados_anteriores,
            dados_novos=self._snapshot_magia(magia),
        )
        return magia

    def deletar_fisico(self, magia_id: int, *, usuario_id: int | None = None) -> None:
        magia = self.obter_por_id(magia_id)
        dados_anteriores = self._snapshot_magia(magia)
        if self.repository.has_dependencias(magia_id):
            raise HTTPException(
                status_code=409,
                detail="Esta magia não pode ser excluída pois está vinculada a grimório/ficha. Use desativar.",
            )
        magia_id_deleted = magia.id
        self.repository.db.delete(magia)
        commit_with_rollback(self.repository.db)
        self.repository.registrar_historico(
            magia_id=magia_id_deleted,
            usuario_id=usuario_id,
            acao="EXCLUSAO",
            dados_anteriores=dados_anteriores,
            dados_novos=None,
        )

    def listar_historico(self, magia_id: int, *, limit: int = 50):
        self.obter_por_id(magia_id)
        return self.repository.listar_historico(magia_id, limit=limit)

    def _validar_nome_unico(self, nome: str) -> None:
        existente = self.repository.get_by_nome(nome)
        if existente:
            raise HTTPException(
                status_code=409, detail="Já existe uma magia com este nome"
            )

    @staticmethod
    def _validar_classes_niveis(classes_niveis: list[dict]) -> None:
        if not classes_niveis:
            raise HTTPException(
                status_code=422, detail="Informe ao menos uma classe com nível"
            )

        classes = set()
        for item in classes_niveis:
            classe = _normalizar_classe(str(item.get("classe", "")))
            nivel = item.get("nivel")
            if not classe:
                raise HTTPException(
                    status_code=422, detail="Classe inválida em classes_niveis"
                )
            if classe in classes:
                raise HTTPException(
                    status_code=422,
                    detail=f"Classe duplicada em classes_niveis: {classe}",
                )
            if not isinstance(nivel, int) or nivel < 0 or nivel > 9:
                raise HTTPException(
                    status_code=422, detail=f"Nível inválido para classe {classe}"
                )
            classes.add(classe)

    @staticmethod
    def _normalizar_texto(value: str) -> str:
        return _normalizar_classe(value)

    @classmethod
    def normalizar_dominios(cls, dominios_raw: str) -> str:
        itens = [
            item.strip() for item in str(dominios_raw or "").split(",") if item.strip()
        ]
        if not itens:
            raise HTTPException(
                status_code=422,
                detail="Para magia de dominio, informe ao menos um dominio",
            )

        vistos = set()
        canonical = []
        invalidos = []
        for item in itens:
            key = cls._normalizar_texto(item)
            if key not in DOMINIOS_FIXOS:
                invalidos.append(item)
                continue
            if key in vistos:
                continue
            vistos.add(key)
            canonical.append(DOMINIOS_FIXOS[key])

        if invalidos:
            permitidos = ", ".join(DOMINIOS_FIXOS.values())
            raise HTTPException(
                status_code=422,
                detail=f"Dominio invalido: {', '.join(invalidos)}. Permitidos: {permitidos}",
            )

        return ", ".join(canonical)

    def _aplicar_regras_dominios(
        self, data: dict, *, magia_atual: Magia | None = None
    ) -> None:
        flag_final = bool(
            data.get(
                "e_magia_dominio", magia_atual.e_magia_dominio if magia_atual else False
            )
        )

        if not flag_final:
            data["dominios"] = None
            return

        dominios_raw = data.get(
            "dominios", magia_atual.dominios if magia_atual else None
        )
        data["e_magia_dominio"] = True
        data["dominios"] = self.normalizar_dominios(dominios_raw or "")

    @staticmethod
    def _gerar_legacy_classes(classes_niveis: list[dict]) -> dict:
        ordenadas = sorted(
            classes_niveis,
            key=lambda x: (x["nivel"], _normalizar_classe(str(x["classe"]))),
        )
        classe_legacy = ",".join(
            _normalizar_classe(str(item["classe"])) for item in ordenadas
        )
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

    @staticmethod
    def _snapshot_magia(magia: Magia) -> dict:
        classes_niveis = [
            {"classe": item.classe, "nivel": item.nivel}
            for item in sorted(
                (magia.classes_niveis or []),
                key=lambda x: (int(x.nivel), str(x.classe)),
            )
        ]
        return {
            "id": magia.id,
            "nome": magia.nome,
            "nome_en": magia.nome_en,
            "nivel": magia.nivel,
            "classe": magia.classe,
            "escola": magia.escola,
            "sub_escola": magia.sub_escola,
            "descritor": magia.descritor,
            "componentes": magia.componentes,
            "componente_extra": magia.componente_extra,
            "alcance": magia.alcance,
            "area_efeito": magia.area_efeito,
            "duracao": magia.duracao,
            "tempo_conjuracao": magia.tempo_conjuracao,
            "dano": magia.dano,
            "teste_resistencia": magia.teste_resistencia,
            "resistencia_magica": magia.resistencia_magica,
            "resistencia_magia_texto": magia.resistencia_magia_texto,
            "descricao": magia.descricao,
            "descricao_en": magia.descricao_en,
            "ativo": magia.ativo,
            "e_magia_dominio": magia.e_magia_dominio,
            "dominios": magia.dominios,
            "pagina_referencia": magia.pagina_referencia,
            "classes_niveis": classes_niveis,
        }
