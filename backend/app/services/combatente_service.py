"""
Service de Combatente (Business Logic)
SRP: Lógica de negócio de Combatente
SOLID: DIP via repository injetado no constructor
"""
import unicodedata
import json

from typing import List, Optional, Dict

from ..repositories.combatente_repository import CombatenteRepository
from ..repositories.condicao_repository import CondicaoRepository
from ..repositories.base import commit_with_rollback
from ..services.file_service import FileService
from ..models.combatente import Combatente
from ..models.ataque import MagiaSlot
from ..models.talento import Talento, TalentoJogador
from ..core.bonus_base_ataque import (
    calcular_bonus_base_ataque,
    calcular_habilidades_especiais,
    calcular_habilidades_especiais_por_nivel,
    calcular_resistencias_base,
)
from ..exceptions.custom_exceptions import (
    ArenaBaseException,
    CombatenteNaoEncontrado,
    DadosInvalidos,
)
from ..models.usuario import PerfilUsuario

# Nomes canônicos das condições automáticas de HP (D&D 3.5)
_CONDICAO_INCONSCIENTE = "Inconsciente"
_CONDICAO_MORRENDO     = "Morrendo"

# Clérigo: magias por dia (Normal) + domínio — Magias por dia clerigo.xlsx (C = nv. 0 só truques; D–E = nv. 1 Normal/Domínio; truques sem slot de domínio)
_CLERIC_SPELLS_PER_DAY_NORMAL = [
    [3, 1, None, None, None, None, None, None, None, None],
    [4, 2, None, None, None, None, None, None, None, None],
    [5, 2, 1, None, None, None, None, None, None, None],
    [5, 3, 2, None, None, None, None, None, None, None],
    [5, 3, 2, 1, None, None, None, None, None, None],
    [6, 3, 3, 2, None, None, None, None, None, None],
    [6, 4, 3, 2, 1, None, None, None, None, None],
    [6, 4, 3, 3, 2, None, None, None, None, None],
    [6, 4, 4, 3, 2, 1, None, None, None, None],
    [6, 4, 4, 3, 3, 2, None, None, None, None],
    [6, 5, 4, 4, 3, 2, 1, None, None, None],
    [6, 5, 4, 4, 3, 3, 2, None, None, None],
    [6, 5, 5, 4, 4, 3, 2, 1, None, None],
    [6, 5, 5, 4, 4, 3, 3, 2, None, None],
    [6, 5, 5, 5, 4, 4, 3, 2, 1, None],
    [6, 5, 5, 5, 4, 4, 3, 3, 2, None],
    [6, 5, 5, 5, 5, 4, 4, 3, 2, 1],
    [6, 5, 5, 5, 5, 4, 4, 3, 3, 2],
    [6, 5, 5, 5, 5, 5, 4, 4, 3, 3],
    [6, 5, 5, 5, 5, 5, 4, 4, 4, 4],
]

_CLERIC_SPELLS_PER_DAY_DOMINIO = [
    [0, 1, None, None, None, None, None, None, None, None],
    [0, 1, None, None, None, None, None, None, None, None],
    [0, 1, 1, None, None, None, None, None, None, None],
    [0, 1, 1, None, None, None, None, None, None, None],
    [0, 1, 1, 1, None, None, None, None, None, None],
    [0, 1, 1, 1, None, None, None, None, None, None],
    [0, 1, 1, 1, 1, None, None, None, None, None],
    [0, 1, 1, 1, 1, None, None, None, None, None],
    [0, 1, 1, 1, 1, 1, None, None, None, None],
    [0, 1, 1, 1, 1, 1, None, None, None, None],
    [0, 1, 1, 1, 1, 1, 1, None, None, None],
    [0, 1, 1, 1, 1, 1, 1, None, None, None],
    [0, 1, 1, 1, 1, 1, 1, 1, None, None],
    [0, 1, 1, 1, 1, 1, 1, 1, None, None],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, None],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, None],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Magias adicionais por modificador do atributo de conjuração (níveis 0–9). Fonte: tabela1-1_mod_habilidades_e_magias.xlsx
_SPELL_BONUS_BY_MODIFIER = {
    -5: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    -4: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    -3: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    -2: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    -1: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    0: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    1: (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    2: (1, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    3: (1, 1, 0, 0, 0, 0, 0, 0, 0, 0),
    4: (1, 1, 1, 0, 0, 0, 0, 0, 0, 0),
    5: (1, 1, 1, 1, 0, 0, 0, 0, 0, 0),
    6: (1, 1, 1, 1, 1, 0, 0, 0, 0, 0),
    7: (1, 1, 1, 1, 1, 1, 0, 0, 0, 0),
    8: (1, 1, 1, 1, 1, 1, 1, 0, 0, 0),
    9: (1, 1, 1, 1, 1, 1, 1, 1, 0, 0),
    10: (1, 1, 1, 1, 1, 1, 1, 1, 1, 0),
    11: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    12: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    13: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    14: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    15: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    16: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    17: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    18: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    19: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    20: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    21: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    22: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    23: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    24: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    25: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    26: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    27: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    28: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    29: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    30: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    31: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    32: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    33: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    34: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    35: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    36: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    37: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    38: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    39: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    40: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    41: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    42: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    43: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    44: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    45: (1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
}


def _bonus_magias_por_modificador(mod: int) -> List[int]:
    m = max(-5, min(45, int(mod)))
    return list(_SPELL_BONUS_BY_MODIFIER[m])


def _linha_slots_clerigo(nivel_personagem: int, modificador_sab: int) -> List[Optional[int]]:
    """Uma linha por nível de magia (0–9): totais = normal + domínio + bônus por atributo (Tabela 1-1)."""
    idx = max(1, min(20, nivel_personagem)) - 1
    n_row = _CLERIC_SPELLS_PER_DAY_NORMAL[idx]
    d_row = _CLERIC_SPELLS_PER_DAY_DOMINIO[idx]
    bonus = _bonus_magias_por_modificador(modificador_sab)

    linha: List[Optional[int]] = [None] * 10
    for sl in range(10):
        raw_n = n_row[sl]
        raw_d = d_row[sl]
        if raw_n is None and raw_d is None:
            continue
        b_attr = bonus[sl] if sl < len(bonus) else 0
        total = (raw_n or 0) + (raw_d or 0) + b_attr
        linha[sl] = total
    return linha


class CombatenteService:

    def __init__(
        self,
        repository: CombatenteRepository,
        file_service: FileService,
        condicao_repository: Optional[CondicaoRepository] = None,
    ):
        self.repository        = repository
        self.file_service      = file_service
        self.condicao_repo     = condicao_repository
        self._condicao_id_cache: Dict[str, int] = {}

    # ── CRUD ─────────────────────────────────────────────

    def listar_todos(
        self,
        tipo: Optional[str] = None,
        usuario=None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Combatente]:
        """Lista todos os combatentes, opcionalmente filtrando por tipo."""
        # Jogador enxerga apenas seus próprios combatentes (qualquer tipo)
        if usuario and usuario.perfil == PerfilUsuario.JOGADOR:
            if tipo:
                combatentes = self.repository.get_by_owner_and_tipo(usuario.id, tipo, skip=skip, limit=limit)
                self._sincronizar_progressao_em_memoria(combatentes)
                return combatentes
            combatentes = self.repository.get_by_owner(usuario.id, skip=skip, limit=limit)
            self._sincronizar_progressao_em_memoria(combatentes)
            return combatentes

        # Mestre/user comum enxerga seus próprios (com filtro de tipo se aplicável)
        if usuario and usuario.perfil != PerfilUsuario.ADMINISTRADOR:
            if tipo:
                combatentes = self.repository.get_by_owner_and_tipo(usuario.id, tipo, skip=skip, limit=limit)
                self._sincronizar_progressao_em_memoria(combatentes)
                return combatentes
            combatentes = self.repository.get_by_owner(usuario.id, skip=skip, limit=limit)
            self._sincronizar_progressao_em_memoria(combatentes)
            return combatentes

        if tipo:
            combatentes = self.repository.get_by_tipo(tipo, skip=skip, limit=limit)
            self._sincronizar_progressao_em_memoria(combatentes)
            return combatentes
        combatentes = self.repository.get_all(skip=skip, limit=limit)
        self._sincronizar_progressao_em_memoria(combatentes)
        return combatentes

    def contar_todos(self, tipo: Optional[str] = None, usuario=None) -> int:
        """Conta combatentes respeitando escopo do usuário e filtro por tipo."""
        # Jogador conta apenas seus próprios combatentes (qualquer tipo)
        if usuario and usuario.perfil == PerfilUsuario.JOGADOR:
            if tipo:
                return self.repository.count_by_owner_and_tipo(usuario.id, tipo)
            return self.repository.count_by_owner(usuario.id)

        # Mestre/user comum conta seus próprios (com filtro de tipo se aplicável)
        if usuario and usuario.perfil != PerfilUsuario.ADMINISTRADOR:
            if tipo:
                return self.repository.count_by_owner_and_tipo(usuario.id, tipo)
            return self.repository.count_by_owner(usuario.id)

        if tipo:
            return self.repository.count_by_tipo(tipo)
        return self.repository.count_all()

    def obter_por_id(self, combatente_id: int) -> Combatente:
        """
        Obtém combatente por ID.
        lazy='selectin' no model garante que ataques, magias_slots
        e magias_preparadas já vêm carregados automaticamente.
        """
        combatente = self.repository.get_by_id(combatente_id)
        if not combatente:
            raise CombatenteNaoEncontrado(combatente_id)
        self._sincronizar_progressao_em_memoria([combatente])
        return combatente

    def criar(self, combatente_data: dict, foto_file=None, dono_id: Optional[int] = None) -> Combatente:
        """Cria um novo combatente com foto opcional."""
        if foto_file and hasattr(foto_file, 'filename') and foto_file.filename:
            combatente_data["foto_url"] = self.file_service.salvar_arquivo(foto_file)

        if dono_id is not None:
            combatente_data["dono_id"] = dono_id

        self._aplicar_regras_dominios_por_classe(
            combatente_data,
            exigir_dois_dominios_clerigo=False,
        )
        self._aplicar_regra_iniciativa_por_tipo(combatente_data)
        self._preencher_bonus_base_ataque(combatente_data)
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

        self._aplicar_regras_dominios_por_classe(
            combatente_data,
            classe_atual=combatente.classe,
            dominios_atuais=combatente.dominios,
            exigir_dois_dominios_clerigo=False,
        )
        self._aplicar_regra_iniciativa_por_tipo(combatente_data, combatente_atual=combatente)
        self._preencher_bonus_base_ataque(combatente_data, combatente_atual=combatente)

        for key, value in combatente_data.items():
            if hasattr(combatente, key) and value is not None:
                setattr(combatente, key, value)

        atualizado = self.repository.update(combatente)
        return self.obter_por_id(atualizado.id)

    def _preencher_bonus_base_ataque(
        self,
        combatente_data: dict,
        combatente_atual: Optional[Combatente] = None,
    ) -> None:
        classe = combatente_data.get("classe")
        nivel = combatente_data.get("nivel")

        if classe is None and combatente_atual is not None:
            classe = combatente_atual.classe
        if nivel is None and combatente_atual is not None:
            nivel = combatente_atual.nivel

        bba = calcular_bonus_base_ataque(classe, nivel)
        combatente_data["bonus_base_ataque"] = bba or ""
        habilidades_grouped = calcular_habilidades_especiais_por_nivel(classe, nivel)
        if habilidades_grouped:
            combatente_data["habilidades_especiais"] = json.dumps(habilidades_grouped, ensure_ascii=False)
        else:
            # Compatibilidade com registros legados sem agrupamento.
            habilidades = calcular_habilidades_especiais(classe, nivel)
            combatente_data["habilidades_especiais"] = " | ".join(habilidades) if habilidades else ""
        saves = calcular_resistencias_base(classe, nivel)
        if saves is not None:
            fortitude, reflexos, vontade = saves
            combatente_data["fortitude_base"] = fortitude
            combatente_data["reflexos_base"] = reflexos
            combatente_data["vontade_base"] = vontade

        self._recalcular_resistencias_totais(combatente_data, combatente_atual=combatente_atual)

    def _recalcular_resistencias_totais(
        self,
        combatente_data: dict,
        combatente_atual: Optional[Combatente] = None,
    ) -> None:
        fort_base = self._obter_valor_int(combatente_data, "fortitude_base", combatente_atual, default=0)
        reflex_base = self._obter_valor_int(combatente_data, "reflexos_base", combatente_atual, default=0)
        vontade_base = self._obter_valor_int(combatente_data, "vontade_base", combatente_atual, default=0)

        con = self._obter_valor_int(combatente_data, "constituicao", combatente_atual, default=10)
        des = self._obter_valor_int(combatente_data, "destreza", combatente_atual, default=10)
        sab = self._obter_valor_int(combatente_data, "sabedoria", combatente_atual, default=10)

        combatente_data["fortitude"] = fort_base + self._modificador_atributo(con)
        combatente_data["reflexos"] = reflex_base + self._modificador_atributo(des)
        combatente_data["vontade"] = vontade_base + self._modificador_atributo(sab)

    @staticmethod
    def _modificador_atributo(valor: int) -> int:
        return (valor - 10) // 2

    @staticmethod
    def _obter_valor_int(
        combatente_data: dict,
        key: str,
        combatente_atual: Optional[Combatente],
        default: int,
    ) -> int:
        if key in combatente_data and combatente_data[key] is not None:
            try:
                return int(combatente_data[key])
            except (TypeError, ValueError):
                return default
        if combatente_atual is not None:
            try:
                return int(getattr(combatente_atual, key))
            except (TypeError, ValueError, AttributeError):
                return default
        return default

    def _sincronizar_progressao_em_memoria(self, combatentes: List[Combatente]) -> None:
        """
        Corrige registros legados em leitura quando progressão ainda não foi persistida.
        Evita exibir BBA '+0' para classes/níveis válidos.
        """
        precisa_commit = False
        for combatente in combatentes:
            payload = {
                "tipo": combatente.tipo,
                "classe": combatente.classe,
                "nivel": combatente.nivel,
                "iniciativa": combatente.iniciativa,
                "constituicao": combatente.constituicao,
                "destreza": combatente.destreza,
                "sabedoria": combatente.sabedoria,
                "fortitude_base": combatente.fortitude_base,
                "reflexos_base": combatente.reflexos_base,
                "vontade_base": combatente.vontade_base,
            }
            self._aplicar_regra_iniciativa_por_tipo(payload, combatente_atual=combatente)
            self._preencher_bonus_base_ataque(payload, combatente_atual=combatente)
            campos = (
                "iniciativa",
                "bonus_base_ataque",
                "habilidades_especiais",
                "fortitude_base",
                "reflexos_base",
                "vontade_base",
                "fortitude",
                "reflexos",
                "vontade",
            )
            for campo in campos:
                novo = payload.get(campo)
                atual = getattr(combatente, campo, None)
                if novo != atual:
                    setattr(combatente, campo, novo)
                    precisa_commit = True
        if precisa_commit:
            commit_with_rollback(self.repository.db)

    def _aplicar_regra_iniciativa_por_tipo(
        self,
        combatente_data: dict,
        combatente_atual: Optional[Combatente] = None,
    ) -> None:
        tipo = (combatente_data.get("tipo") or (combatente_atual.tipo if combatente_atual else "") or "").lower()
        if tipo != "jogador":
            return
        des = self._obter_valor_int(combatente_data, "destreza", combatente_atual, default=10)
        bonus_talento = self._bonus_iniciativa_aprimorada(combatente_atual.id) if combatente_atual else 0
        # Regra base D&D 3.5: Iniciativa = modificador de Destreza.
        # Talento Iniciativa Aprimorada concede +4 adicional.
        combatente_data["iniciativa"] = self._modificador_atributo(des) + bonus_talento

    def _bonus_iniciativa_aprimorada(self, combatente_id: int) -> int:
        nomes = (
            self.repository.db.query(Talento.nome)
            .join(TalentoJogador, TalentoJogador.talento_id == Talento.id)
            .filter(
                TalentoJogador.combatente_id == combatente_id,
                Talento.deleted_at.is_(None),
            )
            .all()
        )
        for (nome,) in nomes:
            chave = unicodedata.normalize("NFD", str(nome or ""))
            chave = "".join(ch for ch in chave if unicodedata.category(ch) != "Mn")
            if chave.strip().upper() == "INICIATIVA APRIMORADA":
                return 4
        return 0

    def deletar(self, combatente_id: int) -> bool:
        """Arquiva combatente via soft delete."""
        combatente = self.obter_por_id(combatente_id)
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
        - Monstros: morrem a 0 HP (não ficam negativos).
        - Jogadores/NPCs: chegam a -10 HP (morte) ou ficam no range -1 a -9 (morrendo).
        Aplica condições automáticas Inconsciente/Morrendo conforme D&D 3.5.
        """
        if valor <= 0:
            raise DadosInvalidos("Valor de dano deve ser maior que zero")

        combatente  = self.obter_por_id(combatente_id)
        hp_anterior = combatente.hp_atual
        # aplicar_dano() no model já respeita as regras por tipo
        novo_hp     = combatente.aplicar_dano(valor)
        self.repository.update(combatente)

        # Atualiza condições automáticas de HP
        self._sincronizar_estado_hp(combatente)

        mensagem = self._mensagem_dano(combatente, hp_anterior, hp_anterior - novo_hp)
        return self._response_dano_cura(combatente, mensagem)

    def aplicar_cura(self, combatente_id: int, valor: int) -> Dict:
        """
        Aplica cura ao combatente.
        Remove condições Morrendo/Inconsciente se HP sobe acima de 0.
        """
        if valor <= 0:
            raise DadosInvalidos("Valor de cura deve ser maior que zero")

        combatente   = self.obter_por_id(combatente_id)
        hp_anterior  = combatente.hp_atual
        novo_hp      = min(combatente.hp_maximo, combatente.hp_atual + valor)
        cura_efetiva = novo_hp - hp_anterior

        combatente.hp_atual = novo_hp
        self.repository.update(combatente)

        # Atualiza condições automáticas de HP
        self._sincronizar_estado_hp(combatente)

        mensagem = (
            f"{combatente.nome} já está com HP máximo"
            if cura_efetiva == 0
            else f"{combatente.nome} recuperou {cura_efetiva} HP"
        )
        return self._response_dano_cura(combatente, mensagem)

    def aplicar_dano_massa(self, combatente_ids: List[int], valor: int, usuario) -> Dict:
        """Aplica dano em lote validando ownership por combatente."""
        if valor <= 0:
            raise DadosInvalidos("Valor de dano deve ser maior que zero")
        if not combatente_ids:
            raise DadosInvalidos("Lista de combatentes não pode ser vazia")

        ids_unicos = list(dict.fromkeys(combatente_ids))
        for combatente_id in ids_unicos:
            combatente = self.obter_por_id(combatente_id)
            self._validar_acesso_combatente(combatente, usuario)

        resultados = [self.aplicar_dano(combatente_id, valor) for combatente_id in ids_unicos]
        return {
            "resultados": resultados,
            "total": len(resultados),
        }

    def aplicar_cura_massa(self, combatente_ids: List[int], valor: int, usuario) -> Dict:
        """Aplica cura em lote validando ownership por combatente."""
        if valor <= 0:
            raise DadosInvalidos("Valor de cura deve ser maior que zero")
        if not combatente_ids:
            raise DadosInvalidos("Lista de combatentes não pode ser vazia")

        ids_unicos = list(dict.fromkeys(combatente_ids))
        for combatente_id in ids_unicos:
            combatente = self.obter_por_id(combatente_id)
            self._validar_acesso_combatente(combatente, usuario)

        resultados = [self.aplicar_cura(combatente_id, valor) for combatente_id in ids_unicos]
        return {
            "resultados": resultados,
            "total": len(resultados),
        }

    def _sincronizar_estado_hp(self, combatente: Combatente) -> None:
        """
        Aplica ou remove condições Inconsciente/Morrendo com base no HP atual.
        Execução silenciosa — falha de lookup de condição não interrompe o fluxo.
        """
        if self.condicao_repo is None:
            return

        hp      = combatente.hp_atual
        tipo    = combatente.tipo
        cid     = combatente.id

        id_inconsciente = self._id_condicao(_CONDICAO_INCONSCIENTE)
        id_morrendo     = self._id_condicao(_CONDICAO_MORRENDO)
        houve_mudanca = False

        if tipo == 'monstro':
            # Monstros não recebem Inconsciente/Morrendo — morrem diretamente.
            if id_inconsciente is not None:
                self.condicao_repo.remover(cid, id_inconsciente, commit=False)
                houve_mudanca = True
            if id_morrendo is not None:
                self.condicao_repo.remover(cid, id_morrendo, commit=False)
                houve_mudanca = True
            if houve_mudanca:
                self.condicao_repo.commit()
            return

        # Jogador / NPC
        if hp > 0:
            # Vivo e consciente — remove ambas as condições
            if id_inconsciente is not None:
                self.condicao_repo.remover(cid, id_inconsciente, commit=False)
                houve_mudanca = True
            if id_morrendo is not None:
                self.condicao_repo.remover(cid, id_morrendo, commit=False)
                houve_mudanca = True
        elif hp == 0:
            # Inconsciente mas estável
            if id_morrendo is not None:
                self.condicao_repo.remover(cid, id_morrendo, commit=False)
                houve_mudanca = True
            if id_inconsciente is not None:
                self.condicao_repo.aplicar(cid, id_inconsciente, duracao_turnos=-1, commit=False)
                houve_mudanca = True
        elif -10 < hp < 0:
            # Morrendo (-1 a -9)
            if id_inconsciente is not None:
                self.condicao_repo.remover(cid, id_inconsciente, commit=False)
                houve_mudanca = True
            if id_morrendo is not None:
                self.condicao_repo.aplicar(cid, id_morrendo, duracao_turnos=-1, commit=False)
                houve_mudanca = True
        else:
            # Morto (hp <= -10) — remove condições de processo
            if id_inconsciente is not None:
                self.condicao_repo.remover(cid, id_inconsciente, commit=False)
                houve_mudanca = True
            if id_morrendo is not None:
                self.condicao_repo.remover(cid, id_morrendo, commit=False)
                houve_mudanca = True

        if houve_mudanca:
            self.condicao_repo.commit()

    def _id_condicao(self, nome: str) -> Optional[int]:
        """Retorna o ID de uma condição pelo nome, ou None se não existir."""
        if nome in self._condicao_id_cache:
            return self._condicao_id_cache[nome]

        try:
            condicao = self.condicao_repo.get_by_nome(nome)
            if condicao:
                self._condicao_id_cache[nome] = condicao.id
                return condicao.id
            return None
        except Exception:
            return None

    def _validar_acesso_combatente(self, combatente: Combatente, usuario) -> None:
        """Garante acesso apenas ao dono, exceto perfil administrador."""
        if usuario is None:
            raise ArenaBaseException("Usuário autenticado é obrigatório", status_code=401)

        perfil = getattr(usuario, "perfil", None)
        if perfil == PerfilUsuario.ADMINISTRADOR or perfil == PerfilUsuario.ADMINISTRADOR.value:
            return

        if combatente.dono_id != getattr(usuario, "id", None):
            raise ArenaBaseException(
                "Sem permissão para alterar este combatente",
                status_code=403,
            )

    def _mensagem_dano(self, combatente: Combatente, hp_anterior: int, dano_efetivo: int) -> str:
        hp = combatente.hp_atual
        tipo = combatente.tipo
        if tipo == 'monstro':
            if hp <= 0:
                return f"{combatente.nome} foi derrotado! 💀"
            return f"{combatente.nome} sofreu {dano_efetivo} de dano"
        # Jogador / NPC
        if hp <= -10:
            return f"{combatente.nome} morreu! ☠️"
        if hp < 0:
            return f"{combatente.nome} está morrendo! ({hp} HP) 🩸"
        if hp == 0:
            return f"{combatente.nome} caiu inconsciente! 😵"
        return f"{combatente.nome} sofreu {dano_efetivo} de dano"

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

    @staticmethod
    def _normalizar_texto(valor: str) -> str:
        texto = str(valor or "").strip()
        return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("ascii").upper()

    def _eh_clerigo(self, classe: str) -> bool:
        return self._normalizar_texto(classe) == "CLERIGO"

    @staticmethod
    def _parse_dominios(dominios_raw: str) -> List[str]:
        itens = [item.strip() for item in str(dominios_raw or "").split(",") if item.strip()]
        vistos = set()
        dominios = []
        for item in itens:
            key = item.lower()
            if key in vistos:
                continue
            vistos.add(key)
            dominios.append(item)
        return dominios

    def _aplicar_regras_dominios_por_classe(
        self,
        combatente_data: dict,
        classe_atual: Optional[str] = None,
        dominios_atuais: Optional[str] = None,
        exigir_dois_dominios_clerigo: bool = True,
    ) -> None:
        classe_final = combatente_data.get("classe", classe_atual or "")

        if not self._eh_clerigo(classe_final):
            combatente_data["dominios"] = ""
            return

        dominios_raw = combatente_data["dominios"] if "dominios" in combatente_data else (dominios_atuais or "")
        dominios = self._parse_dominios(dominios_raw)
        if not dominios and not exigir_dois_dominios_clerigo:
            combatente_data["dominios"] = ""
            return

        if len(dominios) != 2:
            raise DadosInvalidos("Clérigo deve escolher exatamente dois domínios")

        combatente_data["dominios"] = ", ".join(dominios)

    def inicializar_slots_magia(self, combatente_id: int) -> Dict:
        """Inicializa slots de magia para um combatente baseado em sua classe e nível."""
        combatente = self.obter_por_id(combatente_id)
        
        # Magias adicionais (Tabela 1-1): INT Mago; CAR Feiticeiro/Bardo; SAB Clérigo/Druida/Paladino/Ranger
        ATRIBUTO_CHAVE = {
            'Mago': 'inteligencia',
            'Feiticeiro': 'carisma',
            'Clérigo': 'sabedoria',
            'Druida': 'sabedoria',
            'Bardo': 'carisma',
            'Paladino': 'sabedoria',
            'Ranger': 'sabedoria',
        }
        
        # Tabela de slots por classe e nível
        TABELA_SLOTS = {
            'Mago': [
                [3,1,None,None,None,None,None,None,None,None],
                [4,2,None,None,None,None,None,None,None,None],
                [4,2,1,None,None,None,None,None,None,None],
                [4,3,2,None,None,None,None,None,None,None],
                [4,3,2,1,None,None,None,None,None,None],
                [4,3,3,2,None,None,None,None,None,None],
                [4,4,3,2,1,None,None,None,None,None],
                [4,4,3,3,2,None,None,None,None,None],
                [4,4,4,3,2,1,None,None,None,None],
                [4,4,4,3,3,2,None,None,None,None],
                [4,4,4,4,3,2,1,None,None,None],
                [4,4,4,4,3,3,2,None,None,None],
                [4,4,4,4,4,3,2,1,None,None],
                [4,4,4,4,4,3,3,2,None,None],
                [4,4,4,4,4,4,3,2,1,None],
                [4,4,4,4,4,4,3,3,2,None],
                [4,4,4,4,4,4,4,3,2,1],
                [4,4,4,4,4,4,4,3,3,2],
                [4,4,4,4,4,4,4,4,3,3],
                [4,4,4,4,4,4,4,4,4,4],
            ],
            'Feiticeiro': [
                [3,1,None,None,None,None,None,None,None,None],
                [4,2,None,None,None,None,None,None,None,None],
                [4,2,1,None,None,None,None,None,None,None],
                [4,3,2,None,None,None,None,None,None,None],
                [4,3,2,1,None,None,None,None,None,None],
                [4,3,3,2,None,None,None,None,None,None],
                [4,4,3,2,1,None,None,None,None,None],
                [4,4,3,3,2,None,None,None,None,None],
                [4,4,4,3,2,1,None,None,None,None],
                [4,4,4,3,3,2,None,None,None,None],
                [4,4,4,4,3,2,1,None,None,None],
                [4,4,4,4,3,3,2,None,None,None],
                [4,4,4,4,4,3,2,1,None,None],
                [4,4,4,4,4,3,3,2,None,None],
                [4,4,4,4,4,4,3,2,1,None],
                [4,4,4,4,4,4,3,3,2,None],
                [4,4,4,4,4,4,4,3,2,1],
                [4,4,4,4,4,4,4,3,3,2],
                [4,4,4,4,4,4,4,4,3,3],
                [4,4,4,4,4,4,4,4,4,4],
            ],
            'Druida': [
                [3,1,None,None,None,None,None,None,None,None],
                [4,2,None,None,None,None,None,None,None,None],
                [4,2,1,None,None,None,None,None,None,None],
                [5,3,2,None,None,None,None,None,None,None],
                [5,3,2,1,None,None,None,None,None,None],
                [5,3,3,2,None,None,None,None,None,None],
                [6,4,3,2,1,None,None,None,None,None],
                [6,4,3,3,2,None,None,None,None,None],
                [6,4,4,3,2,1,None,None,None,None],
                [6,4,4,3,3,2,None,None,None,None],
                [6,5,4,4,3,2,1,None,None,None],
                [6,5,4,4,3,3,2,None,None,None],
                [6,5,5,4,4,3,2,1,None,None],
                [6,5,5,4,4,3,3,2,None,None],
                [6,5,5,5,4,4,3,2,1,None],
                [6,5,5,5,4,4,3,3,2,None],
                [6,5,5,5,5,4,4,3,2,1],
                [6,5,5,5,5,4,4,3,3,2],
                [6,5,5,5,5,5,4,4,3,3],
                [6,5,5,5,5,5,4,4,4,4],
            ],
            'Bardo': [
                [3,1,None,None,None,None,None,None,None,None],
                [4,2,None,None,None,None,None,None,None,None],
                [4,2,1,None,None,None,None,None,None,None],
                [4,3,2,None,None,None,None,None,None,None],
                [4,3,2,1,None,None,None,None,None,None],
                [4,3,3,2,None,None,None,None,None,None],
                [4,4,3,2,1,None,None,None,None,None],
                [4,4,3,3,2,None,None,None,None,None],
                [4,4,4,3,2,1,None,None,None,None],
                [4,4,4,3,3,2,None,None,None,None],
                [4,4,4,4,3,2,1,None,None,None],
                [4,4,4,4,3,3,2,None,None,None],
                [4,4,4,4,4,3,2,1,None,None],
                [4,4,4,4,4,3,3,2,None,None],
                [4,4,4,4,4,4,3,2,1,None],
                [4,4,4,4,4,4,3,3,2,None],
                [4,4,4,4,4,4,4,3,2,1],
                [4,4,4,4,4,4,4,3,3,2],
                [4,4,4,4,4,4,4,4,3,3],
                [4,4,4,4,4,4,4,4,4,4],
            ],
            'Paladino': [
                [None,None,None,None,None,None,None,None,None,None],
                [None,None,None,None,None,None,None,None,None,None],
                [3,1,None,None,None,None,None,None,None,None],
                [3,1,None,None,None,None,None,None,None,None],
                [4,2,None,None,None,None,None,None,None,None],
                [4,2,1,None,None,None,None,None,None,None],
                [4,2,1,None,None,None,None,None,None,None],
                [4,3,2,None,None,None,None,None,None,None],
                [4,3,2,None,None,None,None,None,None,None],
                [4,3,2,1,None,None,None,None,None,None],
                [4,3,3,2,None,None,None,None,None,None],
                [4,3,3,2,None,None,None,None,None,None],
                [4,4,3,3,None,None,None,None,None,None],
                [4,4,3,3,1,None,None,None,None,None],
                [4,4,3,3,1,None,None,None,None,None],
                [4,4,4,3,2,None,None,None,None,None],
                [4,4,4,3,2,None,None,None,None,None],
                [4,4,4,4,2,1,None,None,None,None],
                [4,4,4,4,3,1,None,None,None,None],
                [4,4,4,4,3,2,None,None,None,None],
            ],
            'Ranger': [
                [None,None,None,None,None,None,None,None,None,None],
                [None,None,None,None,None,None,None,None,None,None],
                [3,1,None,None,None,None,None,None,None,None],
                [3,1,None,None,None,None,None,None,None,None],
                [4,2,None,None,None,None,None,None,None,None],
                [4,2,1,None,None,None,None,None,None,None],
                [4,2,1,None,None,None,None,None,None,None],
                [4,3,2,None,None,None,None,None,None,None],
                [4,3,2,None,None,None,None,None,None,None],
                [4,3,2,1,None,None,None,None,None,None],
                [4,3,3,2,None,None,None,None,None,None],
                [4,3,3,2,None,None,None,None,None,None],
                [4,4,3,3,None,None,None,None,None,None],
                [4,4,3,3,1,None,None,None,None,None],
                [4,4,3,3,1,None,None,None,None,None],
                [4,4,4,3,2,None,None,None,None,None],
                [4,4,4,3,2,None,None,None,None,None],
                [4,4,4,4,2,1,None,None,None,None],
                [4,4,4,4,3,1,None,None,None,None],
                [4,4,4,4,3,2,None,None,None,None],
            ],
        }
        
        classe = combatente.classe
        tabla = TABELA_SLOTS.get(classe)

        nivel = min(max(1, combatente.nivel or 1), 20)

        atributo_chave = ATRIBUTO_CHAVE.get(classe, "inteligencia")
        valor_atributo = getattr(combatente, atributo_chave, 10) or 10
        modificador = (valor_atributo - 10) // 2

        if classe == "Clérigo":
            linha_slots = _linha_slots_clerigo(nivel, modificador)
        else:
            if not tabla:
                raise DadosInvalidos(f"Classe {classe} não suporta slots de magia")
            linha_slots = tabla[nivel - 1]

        # Verificar se a classe tem slots disponíveis neste nível
        tem_slots = any(slot is not None for slot in linha_slots)
        
        if not tem_slots:
            raise DadosInvalidos(f"Classe {classe} não ganha slots de magia até o nível 3. Nível atual: {nivel}")

        bonus_row = _bonus_magias_por_modificador(modificador)

        # Deletar slots existentes
        for slot in combatente.magias_slots:
            self.repository.db.delete(slot)
        
        # Criar novos slots
        slots_criados = []
        for nivel_magia, base in enumerate(linha_slots):
            if base is None:
                continue

            if classe == "Clérigo":
                total_slots = int(base)
            else:
                b = bonus_row[nivel_magia] if nivel_magia < len(bonus_row) else 0
                total_slots = base + b

            novo_slot = MagiaSlot(
                combatente_id=combatente_id,
                nivel=nivel_magia,
                total=total_slots,
                usados=0
            )
            self.repository.db.add(novo_slot)
            slots_criados.append(novo_slot)
        
        commit_with_rollback(self.repository.db)
        self.repository.db.refresh(combatente)
        
        return {
            "id": combatente_id,
            "classe": classe,
            "nivel": nivel,
            "slots_criados": len(slots_criados),
            "message": f"Slots inicializados para {combatente.nome}"
        }