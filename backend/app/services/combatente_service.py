"""
Service de Combatente (Business Logic)
SRP: Lógica de negócio de Combatente
SOLID: DIP via repository injetado no constructor
"""
from typing import List, Optional, Dict

from ..repositories.combatente_repository import CombatenteRepository
from ..services.file_service import FileService
from ..models.combatente import Combatente
from ..exceptions.custom_exceptions import (
    CombatenteNaoEncontrado,
    DadosInvalidos,
)


class CombatenteService:

    def __init__(self, repository: CombatenteRepository, file_service: FileService):
        self.repository   = repository
        self.file_service = file_service

    # ── CRUD ─────────────────────────────────────────────

    def listar_todos(self, tipo: Optional[str] = None) -> List[Combatente]:
        """Lista todos os combatentes, opcionalmente filtrando por tipo."""
        if tipo:
            return self.repository.get_by_tipo(tipo)
        return self.repository.get_all()

    def obter_por_id(self, combatente_id: int) -> Combatente:
        """
        Obtém combatente por ID.
        lazy='selectin' no model garante que ataques, magias_slots
        e magias_preparadas já vêm carregados automaticamente.
        """
        combatente = self.repository.get_by_id(combatente_id)
        if not combatente:
            raise CombatenteNaoEncontrado(combatente_id)
        return combatente

    def criar(self, combatente_data: dict, foto_file=None) -> Combatente:
        """Cria um novo combatente com foto opcional."""
        if foto_file and hasattr(foto_file, 'filename') and foto_file.filename:
            combatente_data["foto_url"] = self.file_service.salvar_arquivo(foto_file)

        combatente_data["hp_atual"] = combatente_data["hp_maximo"]
        combatente = Combatente(**combatente_data)
        criado = self.repository.create(combatente)

        # Recarrega via get_by_id para garantir relacionamentos no response
        return self.obter_por_id(criado.id)

    def atualizar(
        self,
        combatente_id: int,
        combatente_data: dict,
        foto_file=None,
    ) -> Combatente:
        """Atualiza combatente existente, foto e HP proporcionais."""
        combatente = self.obter_por_id(combatente_id)

        # Troca foto somente se uma nova foi enviada
        if foto_file and hasattr(foto_file, 'filename') and foto_file.filename:
            if combatente.foto_url:
                self.file_service.deletar_arquivo(combatente.foto_url)
            combatente_data["foto_url"] = self.file_service.salvar_arquivo(foto_file)

        # Ajusta HP proporcional se hp_maximo mudou
        if "hp_maximo" in combatente_data and combatente.hp_maximo != combatente_data["hp_maximo"]:
            novo_max = combatente_data["hp_maximo"]
            if "hp_atual" not in combatente_data and combatente.hp_maximo > 0:
                proporcao = combatente.hp_atual / combatente.hp_maximo
                combatente_data["hp_atual"] = int(novo_max * proporcao)

        for key, value in combatente_data.items():
            if hasattr(combatente, key) and value is not None:
                setattr(combatente, key, value)

        atualizado = self.repository.update(combatente)
        return self.obter_por_id(atualizado.id)

    def deletar(self, combatente_id: int) -> bool:
        """Deleta combatente e sua foto se existir."""
        combatente = self.obter_por_id(combatente_id)
        if combatente.foto_url:
            self.file_service.deletar_arquivo(combatente.foto_url)
        return self.repository.delete(combatente)

    # ── HP / Iniciativa ───────────────────────────────────

    def atualizar_hp(self, combatente_id: int, novo_hp: int) -> Combatente:
        """Atualiza HP atual, clampado entre 0 e hp_maximo."""
        combatente = self.obter_por_id(combatente_id)
        combatente.hp_atual = max(0, min(novo_hp, combatente.hp_maximo))
        return self.repository.update(combatente)

    def atualizar_iniciativa(self, combatente_id: int, nova_iniciativa: int) -> Combatente:
        """Atualiza iniciativa, mínimo 0."""
        combatente = self.obter_por_id(combatente_id)
        combatente.iniciativa = max(0, nova_iniciativa)
        return self.repository.update(combatente)

    # ── Dano / Cura ───────────────────────────────────────

    def aplicar_dano(self, combatente_id: int, valor: int) -> Dict:
        """
        Aplica dano ao combatente.
        SRP: validação + cálculo + persistência aqui; serialização em _response_dano_cura.
        """
        if valor <= 0:
            raise DadosInvalidos("Valor de dano deve ser maior que zero")

        combatente   = self.obter_por_id(combatente_id)
        hp_anterior  = combatente.hp_atual
        novo_hp      = max(0, combatente.hp_atual - valor)
        dano_efetivo = hp_anterior - novo_hp

        combatente.hp_atual = novo_hp
        self.repository.db.commit()
        self.repository.db.refresh(combatente)

        mensagem = (
            f"{combatente.nome} foi derrotado! 💀"
            if novo_hp == 0
            else f"{combatente.nome} sofreu {dano_efetivo} de dano"
        )
        return self._response_dano_cura(combatente, mensagem)

    def aplicar_cura(self, combatente_id: int, valor: int) -> Dict:
        """
        Aplica cura ao combatente.
        SRP: validação + cálculo + persistência aqui; serialização em _response_dano_cura.
        """
        if valor <= 0:
            raise DadosInvalidos("Valor de cura deve ser maior que zero")

        combatente   = self.obter_por_id(combatente_id)
        hp_anterior  = combatente.hp_atual
        novo_hp      = min(combatente.hp_maximo, combatente.hp_atual + valor)
        cura_efetiva = novo_hp - hp_anterior

        combatente.hp_atual = novo_hp
        self.repository.db.commit()
        self.repository.db.refresh(combatente)

        mensagem = (
            f"{combatente.nome} já está com HP máximo"
            if cura_efetiva == 0
            else f"{combatente.nome} recuperou {cura_efetiva} HP"
        )
        return self._response_dano_cura(combatente, mensagem)

    # ── Helpers privados ──────────────────────────────────

    def _response_dano_cura(self, combatente: Combatente, mensagem: str) -> Dict:
        """SRP: serialização isolada do response de dano/cura."""
        return {
            "id":        combatente.id,
            "nome":      combatente.nome,
            "hp_atual":  combatente.hp_atual,
            "hp_maximo": combatente.hp_maximo,
            "mensagem":  mensagem,
        }