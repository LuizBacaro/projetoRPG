"""
DivindadeCustomService (D&D 3.5)
SRP: regras de negocio das divindades customizadas (campanhas caseiras).

Responsabilidades:
  * Validar entrada (nome unico, tendencia conhecida, dominios conhecidos).
  * Serializar no mesmo formato do catalogo oficial (DivindadeCatalogo),
    acrescentando campos id/origem/criado_por_id/criado_em para a UI.
  * Unificar catalogo (oficial + customizadas) para expor em /magias/divindades.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ....shared.exceptions.custom_exceptions import DadosInvalidos
from ..catalogs import divindades_catalogo as _divindades_catalogo
from ..models.divindade_custom import DivindadeCustom
from ..ports.divindade_custom import DivindadeCustomRepositoryProtocol
from ..repositories.divindade_custom_repository import DivindadeCustomRepository
from .magia_service import DOMINIOS_FIXOS

TENDENCIAS_VALIDAS = {
    "Leal e Bom",
    "Neutro e Bom",
    "Caotico e Bom",
    "Caótico e Bom",
    "Leal e Neutro",
    "Neutro",
    "Caotico e Neutro",
    "Caótico e Neutro",
    "Leal e Mau",
    "Leal e Mal",
    "Neutro e Mau",
    "Neutro e Mal",
    "Caotico e Mau",
    "Caotico e Mal",
    "Caótico e Mau",
    "Caótico e Mal",
}


class DivindadeCustomService:
    def __init__(self, repository: DivindadeCustomRepositoryProtocol):
        self.repository = repository

    # ─── Leitura ────────────────────────────────────────────────────────────

    def listar(self) -> List[DivindadeCustom]:
        return self.repository.listar()

    def serializar(self, entidade: DivindadeCustom) -> Dict[str, Any]:
        """Converte entidade ORM em dict no formato usado pelo frontend."""
        dominios = [
            item.strip()
            for item in str(entidade.dominios or "").split(",")
            if item.strip()
        ]
        titulo = (entidade.titulo or "").strip()
        label = f"{entidade.nome}, {titulo}" if titulo else entidade.nome
        return {
            "id": entidade.id,
            "nome": entidade.nome,
            "titulo": titulo,
            "label": label,
            "tendencia": entidade.tendencia,
            "dominios": dominios,
            "descricao": (entidade.descricao or "").strip(),
            "criado_por_id": entidade.criado_por_id,
            "criado_em": entidade.criado_em,
            "origem": "custom",
        }

    def listar_catalogo_unificado(self) -> List[Dict[str, Any]]:
        """Catalogo oficial + customizadas, com campo `origem` em cada item."""
        oficial = [
            {**item, "origem": "oficial"}
            for item in _divindades_catalogo.listar_catalogo()
        ]
        customizadas = [self.serializar(item) for item in self.repository.listar()]
        chaves_oficiais = {item["nome"].strip().lower() for item in oficial}
        filtradas_custom = [
            item
            for item in customizadas
            if str(item["nome"]).strip().lower() not in chaves_oficiais
        ]
        return oficial + filtradas_custom

    # ─── Escrita ────────────────────────────────────────────────────────────

    def criar(
        self,
        payload: Dict[str, Any],
        usuario_id: Optional[int] = None,
    ) -> DivindadeCustom:
        nome = str(payload.get("nome", "") or "").strip()
        titulo = str(payload.get("titulo", "") or "").strip()
        tendencia = str(payload.get("tendencia", "") or "").strip()
        descricao = str(payload.get("descricao", "") or "").strip() or None
        dominios_in = payload.get("dominios") or []

        if not nome:
            raise DadosInvalidos("O nome da divindade é obrigatório.")
        if len(nome) > 100:
            raise DadosInvalidos("Nome da divindade deve ter no máximo 100 caracteres.")

        if not tendencia:
            raise DadosInvalidos("A tendência/alinhamento é obrigatória.")
        if tendencia not in TENDENCIAS_VALIDAS:
            raise DadosInvalidos(
                "Tendência inválida. Use uma das combinações D&D 3.5 "
                "(ex.: 'Leal e Bom', 'Neutro', 'Caótico e Mau')."
            )

        dominios_normalizados = self._normalizar_dominios(dominios_in)
        if not dominios_normalizados:
            raise DadosInvalidos(
                "Informe pelo menos um domínio válido para a divindade."
            )

        if _divindades_catalogo.buscar_por_nome(nome) is not None:
            raise DadosInvalidos(
                f"Já existe uma divindade oficial chamada '{nome}' no catálogo (Tabela 3-7)."
            )
        if self.repository.get_by_nome_case_insensitive(nome) is not None:
            raise DadosInvalidos(
                f"Já existe uma divindade customizada chamada '{nome}'."
            )

        dominios_csv = ", ".join(dominios_normalizados)
        return self.repository.criar(
            nome=nome,
            titulo=titulo,
            tendencia=tendencia,
            dominios_csv=dominios_csv,
            descricao=descricao,
            criado_por_id=usuario_id,
        )

    def deletar(self, divindade_id: int) -> None:
        removido = self.repository.deletar(divindade_id)
        if not removido:
            raise DadosInvalidos(
                f"Divindade customizada {divindade_id} não encontrada."
            )

    # ─── Helpers privados ───────────────────────────────────────────────────

    def _dominios_permitidos_canonicos(self) -> Dict[str, str]:
        """Mapa chave-normalizada -> nome canonico, unindo DOMINIOS_FIXOS
        (magia service) aos dominios que aparecem nas divindades oficiais
        (ex.: Animal, Planta, Ordem, Agua). Usa o _key do catalogo para
        normalizacao tolerante a acento."""
        from ..catalogs.divindades_catalogo import _key

        mapa: Dict[str, str] = {}
        for canonico in DOMINIOS_FIXOS.values():
            mapa[_key(canonico)] = canonico
        for item in _divindades_catalogo.listar_catalogo():
            for dominio in item.get("dominios", []):
                chave = _key(dominio)
                if chave not in mapa:
                    mapa[chave] = dominio
        return mapa

    def _normalizar_dominios(self, dominios_in: Any) -> List[str]:
        from ..catalogs.divindades_catalogo import _key

        if isinstance(dominios_in, str):
            bruto = [item.strip() for item in dominios_in.split(",")]
        elif isinstance(dominios_in, (list, tuple, set)):
            bruto = [str(item).strip() for item in dominios_in]
        else:
            bruto = []

        bruto = [item for item in bruto if item]
        seen: set[str] = set()
        resultado: List[str] = []
        permitidos_canonicos = self._dominios_permitidos_canonicos()

        invalidos: List[str] = []
        for item in bruto:
            chave = _key(item)
            canonico = permitidos_canonicos.get(chave)
            if not canonico:
                invalidos.append(item)
                continue
            if canonico in seen:
                continue
            seen.add(canonico)
            resultado.append(canonico)

        if invalidos:
            lista = ", ".join(sorted(set(permitidos_canonicos.values())))
            raise DadosInvalidos(
                f"Domínio(s) desconhecido(s): {', '.join(invalidos)}. "
                f"Use um dos seguintes: {lista}."
            )

        return resultado


def build_divindade_custom_service(db: Session) -> DivindadeCustomService:
    """Factory conveniente (usada nas dependencies do FastAPI)."""
    return DivindadeCustomService(DivindadeCustomRepository(db))
