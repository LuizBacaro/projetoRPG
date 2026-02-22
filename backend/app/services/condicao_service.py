"""
Service de Condição (Business Logic)
Princípio SOLID:
  SRP - Apenas lógica de negócio de Condição
  DIP - Depende da abstração CondicaoRepository, não da implementação
"""
from typing import List, Dict
from ..repositories.condicao_repository import CondicaoRepository
from ..repositories.combatente_repository import CombatenteRepository
from ..exceptions.custom_exceptions import CombatenteNaoEncontrado

# ── Seed das 25 condições da planilha Condies-D&D.xlsx ────────────────────────
CONDICOES_SEED = [
    {"nome": "Abalado",        "efeito": "-2 em testes de ataque, saves e verificações de habilidade."},
    {"nome": "Agarrado",       "efeito": "Não pode se mover. -4 CA, -4 em testes de ataque corpo a corpo. Não pode usar ações de ataque à distância exceto armas leves."},
    {"nome": "Apavorado",      "efeito": "Foge do que o apavora. -2 em testes de ataque, saves e verificações de habilidade enquanto a fonte estiver visível."},
    {"nome": "Atordoado",      "efeito": "Não pode agir, perde bônus de Destreza à CA e sofre -2 na CA."},
    {"nome": "Caído",          "efeito": "-4 em ataques corpo a corpo. Ataques à distância impossíveis. +4 CA contra ataques à distância, -4 CA contra corpo a corpo."},
    {"nome": "Cego",           "efeito": "-2 CA, perde bônus de Destreza. Atacantes têm +2 para acertar. -4 em testes de Busca, Observar e outros dependentes de visão."},
    {"nome": "Confuso",        "efeito": "Age aleatoriamente: age normal, fica inativo, ataca aliado mais próximo ou ataca inimigo mais próximo (rolar 1d100 a cada turno)."},
    {"nome": "Cowering",       "efeito": "Paralisado de medo. Perde bônus de Destreza à CA e sofre -2 na CA. Opositores ganham +2 para acertar."},
    {"nome": "Deslumbrado",    "efeito": "-1 em testes de ataque e Observar."},
    {"nome": "Desprevenido",   "efeito": "Perde bônus de Destreza à CA. Não pode fazer ataques de oportunidade."},
    {"nome": "Energizado",     "efeito": "Morre em 1d4 rodadas se não tratado. Perde 1d4 pontos de uma habilidade por rodada."},
    {"nome": "Enjoado",        "efeito": "Pode apenas fazer ação de movimento ou padrão. -2 em testes de ataque, dano, saves e verificações de habilidade."},
    {"nome": "Entorpecido",    "efeito": "-2 em testes de Força e Destreza. Perde 1 ponto de bônus de Destreza à CA (min 0)."},
    {"nome": "Envenenado",     "efeito": "Sofre dano de veneno. Efeito varia conforme o veneno aplicado. Pode exigir saves de Fortitude."},
    {"nome": "Esmorecido",     "efeito": "-2 em testes de ataque, saves e verificações de habilidade."},
    {"nome": "Exausto",        "efeito": "Velocidade reduzida à metade. -6 em Força e Destreza. Não pode correr ou realizar carga."},
    {"nome": "Fascinado",      "efeito": "Para e foca em estímulo. -4 em testes de Observar e Ouvir. Reação a ameaças quebra o efeito."},
    {"nome": "Fatigado",       "efeito": "-2 em Força e Destreza. Não pode correr ou realizar carga."},
    {"nome": "Flanqueado",     "efeito": "Atacantes que flanqueiam ganham +2 nos testes de ataque corpo a corpo."},
    {"nome": "Incorporeo",     "efeito": "Imune a ataques não mágicos. 50% de chance de ignorar dano de ataques mágicos."},
    {"nome": "Invisível",      "efeito": "+2 em testes de ataque. Oponentes perdem bônus de Destreza à CA. -4 nos testes dos opositores para observar."},
    {"nome": "Nauseado",       "efeito": "Apenas ação de movimento por rodada. Não pode atacar, conjurar, usar itens ou habilidades especiais."},
    {"nome": "Paralisado",     "efeito": "Fica rígido e incapaz de agir. CA cerde bônus de Destreza. Opositores têm +4 e podem aplicar golpe de misericórdia."},
    {"nome": "Sangrando",      "efeito": "Perde 1 PV por rodada até receber cura ou ser estabilizado (Primeiros Socorros CD 15)."},
    {"nome": "Surdo",          "efeito": "-4 em testes de iniciativa. 20% de falha em conjuração com componentes verbais."},
]


class CondicaoService:
    """
    Service com lógica de negócio para gerenciamento de condições.
    """

    def __init__(
        self,
        condicao_repository: CondicaoRepository,
        combatente_repository: CombatenteRepository,
    ):
        self.condicao_repo   = condicao_repository
        self.combatente_repo = combatente_repository

    # ── Catálogo ────────────────────────────────────────────────────────────────

    def inicializar_seed(self) -> None:
        """Popula a tabela de condições com as 25 condições D&D 3.5"""
        self.condicao_repo.seed(CONDICOES_SEED)

    def listar_todas(self):
        """Retorna catálogo completo de condições"""
        return self.condicao_repo.get_all()

    # ── Condições por combatente ────────────────────────────────────────────────

    def listar_condicoes_do_combatente(self, combatente_id: int) -> Dict:
        """Retorna condições ativas de um combatente"""
        self._validar_combatente(combatente_id)
        condicoes = self.condicao_repo.get_condicoes_do_combatente(combatente_id)
        return {"combatente_id": combatente_id, "condicoes": condicoes}

    def aplicar_condicao(self, combatente_id: int, condicao_id: int) -> Dict:
        """
        Aplica uma condição a um combatente.
        Idempotente — não gera erro se já existia.
        """
        self._validar_combatente(combatente_id)
        self._validar_condicao(condicao_id)

        self.condicao_repo.aplicar(combatente_id, condicao_id)
        condicoes = self.condicao_repo.get_condicoes_do_combatente(combatente_id)
        return {"combatente_id": combatente_id, "condicoes": condicoes}

    def remover_condicao(self, combatente_id: int, condicao_id: int) -> Dict:
        """Remove uma condição específica de um combatente"""
        self._validar_combatente(combatente_id)
        self.condicao_repo.remover(combatente_id, condicao_id)
        condicoes = self.condicao_repo.get_condicoes_do_combatente(combatente_id)
        return {"combatente_id": combatente_id, "condicoes": condicoes}

    def remover_todas_condicoes(self, combatente_id: int) -> Dict:
        """Remove todas as condições ativas de um combatente"""
        self._validar_combatente(combatente_id)
        self.condicao_repo.remover_todas(combatente_id)
        return {"combatente_id": combatente_id, "condicoes": []}

    # ── Helpers privados ────────────────────────────────────────────────────────

    def _validar_combatente(self, combatente_id: int) -> None:
        combatente = self.combatente_repo.get_by_id(combatente_id)
        if not combatente:
            raise CombatenteNaoEncontrado(combatente_id)

    def _validar_condicao(self, condicao_id: int) -> None:
        condicao = self.condicao_repo.get_by_id(condicao_id)
        if not condicao:
            from ..exceptions.custom_exceptions import DadosInvalidos
            raise DadosInvalidos(f"Condição {condicao_id} não encontrada")