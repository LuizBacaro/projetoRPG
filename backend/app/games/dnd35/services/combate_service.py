"""
Service de Combate (Business Logic)
Princípio SOLID: SRP - Lógica de negócio de Combate
"""

from typing import Any, Dict, List, Optional

from app.games.dnd35.models.combate import Combate, CombateHistorico
from app.games.dnd35.ports import (
    CombatenteRepositoryForCombateProtocol,
    CombateRepositoryProtocol,
)
from app.shared.exceptions.custom_exceptions import (
    ArenaBaseException,
    CombateFinalizadoError,
    CombateJaAtivoError,
    CombateNotFoundError,
    ConcurrencyConflictError,
)


class CombateService:
    """
    Service contendo lógica de negócio para Combate
    """

    def __init__(
        self,
        combate_repository: CombateRepositoryProtocol,
        combatente_repository: CombatenteRepositoryForCombateProtocol,
    ):
        self.combate_repo = combate_repository
        self.combatente_repo = combatente_repository

    def iniciar_combate(self, combatente_ids: List[int]) -> Combate:
        """
        Inicia um novo combate com os combatentes selecionados
        """
        # Validar se já existe combate ativo
        if self.combate_repo.existe_combate_ativo():
            raise CombateJaAtivoError(
                "Já existe um combate ativo. Finalize-o antes de iniciar outro."
            )

        # Buscar combatentes
        combatentes = self.combatente_repo.get_by_ids(combatente_ids)

        if len(combatentes) != len(combatente_ids):
            raise ValueError("Alguns combatentes não foram encontrados")

        # Ordenar por iniciativa
        combatentes_ordenados = self.combatente_repo.ordenar_por_iniciativa(combatentes)
        ids_ordenados = [c.id for c in combatentes_ordenados]

        # Criar combate
        combate = Combate(
            combatentes_ids=ids_ordenados,
            turno_atual=0,
            ativo=True,
        )

        return self.combate_repo.create(combate)

    def obter_combate_ativo(self) -> Optional[Combate]:
        """Obtém o combate ativo atual"""
        return self.combate_repo.get_ativo()

    @staticmethod
    def gerar_versao(combate: Combate) -> str:
        """Gera token de versão determinístico para controle de concorrência."""
        return f"{combate.id}:{combate.rodada_atual}:{combate.turno_atual}:{int(bool(combate.ativo))}"

    def validar_versao(self, expected_version: Optional[str], combate: Combate) -> None:
        """Valida precondição de concorrência (If-Match) para mutações de combate."""
        if not expected_version:
            raise ArenaBaseException(
                "Cabeçalho If-Match é obrigatório para mutações de combate",
                status_code=428,
            )

        current_version = self.gerar_versao(combate)
        if expected_version != current_version:
            raise ConcurrencyConflictError(
                f"Conflito de concorrência: versão atual é {current_version}. Atualize o estado e tente novamente."
            )

    @staticmethod
    def _calcular_total_turnos(combate: Combate) -> int:
        if not combate.combatentes_ids:
            return 0
        rodada_atual = combate.rodada_atual or 1
        turno_atual = combate.turno_atual or 0
        return max(
            1, ((rodada_atual - 1) * len(combate.combatentes_ids)) + turno_atual + 1
        )

    def _registrar_historico(
        self, combate: Combate, motivo_encerramento: str
    ) -> CombateHistorico:
        combatentes = self.combatente_repo.get_by_ids(combate.combatentes_ids)
        vivos = [c for c in combatentes if c.esta_vivo()]
        mortos = [c for c in combatentes if not c.esta_vivo()]

        vencedor = vivos[0] if len(vivos) == 1 else None
        historico = CombateHistorico(
            combate_id=combate.id,
            combatentes_ids=combate.combatentes_ids,
            total_combatentes=len(combatentes),
            total_vivos=len(vivos),
            total_rodadas=combate.rodada_atual,
            total_turnos=self._calcular_total_turnos(combate),
            vencedor_id=vencedor.id if vencedor else None,
            vencedor_nome=vencedor.nome if vencedor else None,
            vencedor_tipo=vencedor.tipo if vencedor else None,
            motivo_encerramento=motivo_encerramento,
            estatisticas={
                "vivos": len(vivos),
                "mortos": len(mortos),
                "hp_total_restante": sum(c.hp_atual for c in combatentes),
                "combatentes": [
                    {
                        "id": c.id,
                        "nome": c.nome,
                        "tipo": c.tipo,
                        "hp_atual": c.hp_atual,
                        "hp_maximo": c.hp_maximo,
                        "vivo": c.esta_vivo(),
                    }
                    for c in combatentes
                ],
            },
        )

        return self.combate_repo.criar_historico(historico)

    def montar_status_combate(
        self, combate: Optional[Combate], incluir_combatentes: bool = True
    ) -> Dict[str, Any]:
        """Monta payload de status com base em um combate já carregado."""
        if not combate:
            return {
                "ativo": False,
                "message": "Nenhum combate ativo",
                "resumido": not incluir_combatentes,
            }

        payload = {
            "id": combate.id,
            "combatentes_ids": combate.combatentes_ids,
            "turno_atual": combate.turno_atual,
            "rodada_atual": combate.rodada_atual,
            "versao": self.gerar_versao(combate),
            "ativo": combate.ativo,
            "combatente_ativo_id": combate.obter_combatente_ativo_id(),
        }

        if incluir_combatentes:
            payload["combatentes"] = self.combatente_repo.get_by_ids(
                combate.combatentes_ids
            )

        payload["resumido"] = not incluir_combatentes
        return payload

    def obter_status_combate(self, incluir_combatentes: bool = True) -> Dict[str, Any]:
        """
        Obtém o status completo do combate ativo
        """
        combate = self.obter_combate_ativo()
        return self.montar_status_combate(
            combate, incluir_combatentes=incluir_combatentes
        )

    def avancar_turno(
        self, expected_version: Optional[str], condicao_service: Optional[Any] = None
    ) -> Combate:
        """
        Avança para o próximo turno
        """
        combate = self.obter_combate_ativo()

        if not combate:
            raise CombateNotFoundError("Nenhum combate ativo")

        self.validar_versao(expected_version, combate)

        combatente_ativo_id = combate.obter_combatente_ativo_id()
        if condicao_service and combatente_ativo_id is not None:
            condicao_service.decrementar_duracao_todas(combatente_ativo_id)

        # Verificar se todos estão mortos
        combatentes_vivos = self.combatente_repo.get_vivos_by_ids(
            combate.combatentes_ids
        )

        if len(combatentes_vivos) == 0:
            combate.finalizar()
            combate = self.combate_repo.update(combate)
            self._registrar_historico(combate, motivo_encerramento="todos_mortos")
            raise CombateFinalizadoError(
                "Todos os combatentes estão mortos. Combate finalizado."
            )

        # Avançar turno
        combate.avancar_turno()
        return self.combate_repo.update(combate)

    def finalizar_combate(
        self,
        expected_version: Optional[str] = None,
        motivo_encerramento: str = "manual",
    ) -> bool:
        """
        Finaliza o combate ativo
        """
        combate = self.obter_combate_ativo()

        if not combate:
            raise CombateNotFoundError("Nenhum combate ativo")

        self.validar_versao(expected_version, combate)

        combate.finalizar()
        combate = self.combate_repo.update(combate)
        self._registrar_historico(combate, motivo_encerramento=motivo_encerramento)
        return True

    def listar_historico(self, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        itens = self.combate_repo.listar_historico(skip=skip, limit=limit)
        return {
            "total": self.combate_repo.contar_historico(),
            "skip": skip,
            "limit": limit,
            "itens": itens,
        }

    def resetar_combate(self) -> Dict[str, Any]:
        """
        Reseta todos os combatentes e finaliza o combate
        """
        # Finalizar combate ativo se houver
        combate_ativo = self.obter_combate_ativo()
        if combate_ativo:
            self.finalizar_combate(
                expected_version=self.gerar_versao(combate_ativo),
                motivo_encerramento="reset",
            )

        # Resetar HP de todos
        count = self.combatente_repo.resetar_todos_hp()

        return {
            "message": "Combate resetado com sucesso",
            "combatentes_resetados": count,
        }
