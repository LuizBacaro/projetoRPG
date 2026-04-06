"""
Service de Condição (Business Logic)
Princípio SOLID: SRP - lógica de negócio de Condição + duração
DIP - Depende da abstração CondicaoRepository
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
    # ── Condições automáticas de HP (D&D 3.5) ─────────────────────────────
    {"nome": "Inconsciente",   "efeito": "HP igual a 0. Incapaz de agir. Estável, mas inconsciente — sem perder HP por rodada. Pode ser acordado com cura."},
    {"nome": "Morrendo",       "efeito": "HP entre -1 e -9. Incapacitado e sangrando — perde 1 PV por rodada sem socorro. Pode ser estabilizado com Primeiros Socorros (CD 15) ou cura mágica. Morre ao atingir -10 HP."},
]


class CondicaoService:
    """
    Service com lógica de negócio para gerenciamento de condições com duração.
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
        """Retorna condições ativas de um combatente com duração"""
        self._validar_combatente(combatente_id)
        condicoes = self.condicao_repo.get_condicoes_do_combatente(combatente_id)
        return {
            "combatente_id": combatente_id,
            "condicoes": condicoes  # Inclui duracao_turnos de cada condição
        }

    def aplicar_condicao(self, combatente_id: int, condicao_id: int, duracao_turnos: int = -1) -> Dict:
        """
        Aplica uma condição a um combatente com duração opcional.
        
        Args:
            combatente_id: ID do combatente
            condicao_id: ID da condição
            duracao_turnos: Duração em turnos (-1 = permanente, 0+ = número de turnos)
        
        Retorna: Dict com combatente_id e lista de condições ativas
        """
        self._validar_combatente(combatente_id)
        self._validar_condicao(condicao_id)

        # ✅ NOVO: passa duração para o repository
        self.condicao_repo.aplicar(combatente_id, condicao_id, duracao_turnos)
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

    # ── NOVO: Decremento de duração (arena) ──────────────────────────────────────

    def decrementar_duracao_todas(self, combatente_id: int) -> Dict:
        """
        Decrementa a duração de TODAS as condições ativas de um combatente em 1 turno.
        Remove automaticamente condições que expirarem (duracao_turnos = 0).
        
        ✅ Trata valores NULL/undefined como permanentes (-1)
        """
        self._validar_combatente(combatente_id)

        condicoes_ativas = self.condicao_repo.get_condicoes_do_combatente(combatente_id)
        
        for condicao in condicoes_ativas:
            duracao = condicao.get('duracao_turnos')
            
            # ✅ Tratar NULL como permanente
            if duracao is None:
                duracao = -1
            
            # Se permanente (-1), não decrementa
            if duracao == -1:
                continue
            
            # Decrementar
            nova_duracao = duracao - 1
            
            if nova_duracao <= 0:
                # Expirou — remover
                self.condicao_repo.remover(
                    combatente_id,
                    condicao.get('condicao_id')
                )
                print(f"⏰ Condição '{condicao.get('nome')}' expirou para combatente {combatente_id}")
            else:
                # Atualizar duração
                self.condicao_repo.atualizar_duracao(
                    combatente_id,
                    condicao.get('condicao_id'),
                    nova_duracao
                )
                print(f"⏰ Condição '{condicao.get('nome')}' decrementada: {nova_duracao} turno(s)")

        # Retornar estado atualizado
        condicoes = self.condicao_repo.get_condicoes_do_combatente(combatente_id)
        return {"combatente_id": combatente_id, "condicoes": condicoes}

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