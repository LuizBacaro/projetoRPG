"""Utilitarios para snapshot e restauracao de personagens."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import selectinload


BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app.models  # noqa: F401
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.armadura_protecao import ArmaduraProtecao, ArmaduraProtecaoJogador
from app.models.ataque import Ataque, MagiaPreparada, MagiaSlot
from app.models.combatente import Combatente
from app.models.combatente_condicao import CombatenteCondicao
from app.models.condicao import Condicao
from app.models.equipamento import Equipamento, EquipamentoJogador
from app.models.grimorio import GrimorioHistoricoTroca, GrimorioMagia, GrimorioNotificacao
from app.models.magia import Magia
from app.models.pericia import Pericia, PericiaJogador
from app.models.talento import Talento, TalentoJogador


SNAPSHOT_VERSION = 1
GENERATED_DIR = BACKEND_DIR / "scripts" / "generated"

COMBATENTE_FIELDS = [
    "dono_id",
    "nome",
    "tipo",
    "classe",
    "raca",
    "divindade",
    "alinhamento",
    "dominios",
    "pagina_referencia",
    "hp_atual",
    "hp_maximo",
    "iniciativa",
    "ca",
    "toque",
    "surpresa",
    "foto_url",
    "forca",
    "destreza",
    "constituicao",
    "inteligencia",
    "sabedoria",
    "carisma",
    "fortitude",
    "reflexos",
    "vontade",
    "nivel",
    "pontos",
]

MAGIA_FIELDS = [
    "nome",
    "nome_en",
    "nivel",
    "classe",
    "escola",
    "sub_escola",
    "descritor",
    "componentes",
    "componente_extra",
    "alcance",
    "area_efeito",
    "duracao",
    "tempo_conjuracao",
    "dano",
    "teste_resistencia",
    "resistencia_magica",
    "resistencia_magia_texto",
    "descricao",
    "descricao_en",
    "ativo",
    "e_magia_dominio",
    "dominios",
    "pagina_referencia",
]

PERICIA_FIELDS = [
    "nome",
    "descricao",
    "atributo",
    "tipo",
    "especialidade",
    "requer_treinamento",
    "pode_usar_sem_treinamento",
    "sofre_penalidade_armadura",
    "pagina_livro",
]

CONDICAO_FIELDS = ["nome", "efeito"]
EQUIPAMENTO_FIELDS = ["nome", "descricao", "pagina_referencia", "ativo"]
TALENTO_FIELDS = ["nome", "descricao", "pagina_referencia", "ativo"]
ARMADURA_FIELDS = [
    "nome",
    "tipo",
    "bonus_ca",
    "des_max",
    "penalidade",
    "falha_arcana",
    "deslocamento",
    "peso",
    "propriedades_especiais",
    "ativo",
]


def ensure_generated_dir() -> Path:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    return GENERATED_DIR


def default_snapshot_path() -> Path:
    ensure_generated_dir()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return GENERATED_DIR / f"personagens_snapshot_{timestamp}.json"


def redact_database_url(database_url: str) -> str:
    if "://" not in database_url:
        return database_url
    protocol, rest = database_url.split("://", 1)
    if "@" not in rest:
        return f"{protocol}://{rest}"
    credentials, host = rest.split("@", 1)
    username = credentials.split(":", 1)[0]
    return f"{protocol}://{username}:***@{host}"


def isoformat_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _pick_fields(instance: Any, field_names: list[str]) -> dict[str, Any]:
    return {field_name: getattr(instance, field_name) for field_name in field_names}


def _serialize_magia(magia: Magia) -> dict[str, Any]:
    data = _pick_fields(magia, MAGIA_FIELDS)
    data["id_origem"] = magia.id
    data["data_criacao"] = isoformat_or_none(magia.data_criacao)
    return data


def _serialize_pericia(pericia: Pericia) -> dict[str, Any]:
    data = _pick_fields(pericia, PERICIA_FIELDS)
    data["id_origem"] = pericia.id
    data["deleted_at"] = isoformat_or_none(pericia.deleted_at)
    return data


def _serialize_condicao(condicao: Condicao) -> dict[str, Any]:
    data = _pick_fields(condicao, CONDICAO_FIELDS)
    data["id_origem"] = condicao.id
    return data


def _serialize_equipamento(equipamento: Equipamento) -> dict[str, Any]:
    data = _pick_fields(equipamento, EQUIPAMENTO_FIELDS)
    data["id_origem"] = equipamento.id
    data["criado_em"] = isoformat_or_none(equipamento.criado_em)
    data["deleted_at"] = isoformat_or_none(equipamento.deleted_at)
    return data


def _serialize_talento(talento: Talento) -> dict[str, Any]:
    data = _pick_fields(talento, TALENTO_FIELDS)
    data["id_origem"] = talento.id
    data["criado_em"] = isoformat_or_none(talento.criado_em)
    data["deleted_at"] = isoformat_or_none(talento.deleted_at)
    return data


def _serialize_armadura(item: ArmaduraProtecao) -> dict[str, Any]:
    data = _pick_fields(item, ARMADURA_FIELDS)
    data["id_origem"] = item.id
    data["criado_em"] = isoformat_or_none(item.criado_em)
    return data


def build_snapshot(include_deleted: bool = False, tipos: list[str] | None = None) -> dict[str, Any]:
    session = SessionLocal()
    try:
        query = session.query(Combatente).options(
            selectinload(Combatente.ataques),
            selectinload(Combatente.magias_slots),
            selectinload(Combatente.pericias).selectinload(PericiaJogador.pericia),
            selectinload(Combatente.magias_preparadas).selectinload(MagiaPreparada.magia),
            selectinload(Combatente.equipamentos).selectinload(EquipamentoJogador.equipamento),
            selectinload(Combatente.armaduras_protecao).selectinload(ArmaduraProtecaoJogador.item),
        )

        if not include_deleted:
            query = query.filter(Combatente.deleted_at.is_(None))
        if tipos:
            query = query.filter(Combatente.tipo.in_(tipos))

        combatentes = query.order_by(Combatente.id).all()
        combatente_ids = [combatente.id for combatente in combatentes]

        condicoes_por_combatente: dict[int, list[dict[str, Any]]] = defaultdict(list)
        grimorio_por_combatente: dict[int, list[dict[str, Any]]] = defaultdict(list)
        historico_por_combatente: dict[int, list[dict[str, Any]]] = defaultdict(list)
        notificacoes_por_combatente: dict[int, list[dict[str, Any]]] = defaultdict(list)
        talentos_por_combatente: dict[int, list[dict[str, Any]]] = defaultdict(list)

        if combatente_ids:
            condicoes_rows = (
                session.query(CombatenteCondicao, Condicao)
                .join(Condicao, Condicao.id == CombatenteCondicao.condicao_id)
                .filter(CombatenteCondicao.combatente_id.in_(combatente_ids))
                .order_by(CombatenteCondicao.combatente_id, CombatenteCondicao.id)
                .all()
            )
            for vinculo, condicao in condicoes_rows:
                condicoes_por_combatente[vinculo.combatente_id].append(
                    {
                        "id_origem": vinculo.id,
                        "duracao_turnos": vinculo.duracao_turnos,
                        "condicao": _serialize_condicao(condicao),
                    }
                )

            grimorio_rows = (
                session.query(GrimorioMagia)
                .filter(GrimorioMagia.combatente_id.in_(combatente_ids))
                .order_by(GrimorioMagia.combatente_id, GrimorioMagia.id)
                .all()
            )
            for grimorio in grimorio_rows:
                grimorio_por_combatente[grimorio.combatente_id].append(
                    {
                        "id_origem": grimorio.id,
                        "classe": grimorio.classe,
                        "favorita": grimorio.favorita,
                        "anotacoes": grimorio.anotacoes,
                        "origem": grimorio.origem,
                        "adicionada_em": isoformat_or_none(grimorio.adicionada_em),
                        "magia": _serialize_magia(grimorio.magia),
                    }
                )

            historico_rows = (
                session.query(GrimorioHistoricoTroca)
                .filter(GrimorioHistoricoTroca.combatente_id.in_(combatente_ids))
                .order_by(GrimorioHistoricoTroca.combatente_id, GrimorioHistoricoTroca.id)
                .all()
            )
            for historico in historico_rows:
                historico_por_combatente[historico.combatente_id].append(
                    {
                        "id_origem": historico.id,
                        "classe": historico.classe,
                        "nivel_personagem": historico.nivel_personagem,
                        "realizada_em": isoformat_or_none(historico.realizada_em),
                        "magia_removida": _serialize_magia(historico.magia_removida),
                        "magia_adicionada": _serialize_magia(historico.magia_adicionada),
                    }
                )

            notificacoes_rows = (
                session.query(GrimorioNotificacao)
                .filter(GrimorioNotificacao.combatente_id.in_(combatente_ids))
                .order_by(GrimorioNotificacao.combatente_id, GrimorioNotificacao.id)
                .all()
            )
            for notificacao in notificacoes_rows:
                notificacoes_por_combatente[notificacao.combatente_id].append(
                    {
                        "id_origem": notificacao.id,
                        "classe": notificacao.classe,
                        "tipo": notificacao.tipo,
                        "dados": notificacao.dados,
                        "lida": notificacao.lida,
                        "criada_em": isoformat_or_none(notificacao.criada_em),
                    }
                )

            talentos_rows = (
                session.query(TalentoJogador)
                .filter(TalentoJogador.combatente_id.in_(combatente_ids))
                .order_by(TalentoJogador.combatente_id, TalentoJogador.id)
                .all()
            )
            for talento_jogador in talentos_rows:
                talentos_por_combatente[talento_jogador.combatente_id].append(
                    {
                        "id_origem": talento_jogador.id,
                        "adicionado_em": isoformat_or_none(talento_jogador.adicionado_em),
                        "talento": _serialize_talento(talento_jogador.talento),
                    }
                )

        snapshot_combatentes: list[dict[str, Any]] = []
        for combatente in combatentes:
            combatente_data = _pick_fields(combatente, COMBATENTE_FIELDS)
            combatente_data.update(
                {
                    "id_origem": combatente.id,
                    "deleted_at": isoformat_or_none(combatente.deleted_at),
                    "ataques": [
                        {
                            "id_origem": ataque.id,
                            "nome": ataque.nome,
                            "bonus_ataque": ataque.bonus_ataque,
                            "dano": ataque.dano,
                            "tipo_dano": ataque.tipo_dano,
                        }
                        for ataque in combatente.ataques
                    ],
                    "magias_slots": [
                        {
                            "id_origem": magia_slot.id,
                            "nivel": magia_slot.nivel,
                            "total": magia_slot.total,
                            "usados": magia_slot.usados,
                        }
                        for magia_slot in combatente.magias_slots
                    ],
                    "pericias": [
                        {
                            "id_origem": pericia_jogador.id,
                            "graduacao": pericia_jogador.graduacao,
                            "custo_total": pericia_jogador.custo_total,
                            "modificador_atributo": pericia_jogador.modificador_atributo,
                            "bonus_outros": pericia_jogador.bonus_outros,
                            "pericia": _serialize_pericia(pericia_jogador.pericia),
                        }
                        for pericia_jogador in combatente.pericias
                    ],
                    "magias_preparadas": [
                        {
                            "id_origem": magia_preparada.id,
                            "nivel_slot": magia_preparada.nivel_slot,
                            "quantidade": magia_preparada.quantidade,
                            "usos_realizados": magia_preparada.usos_realizados,
                            "usada": magia_preparada.usada,
                            "preparada_em": isoformat_or_none(magia_preparada.preparada_em),
                            "magia": _serialize_magia(magia_preparada.magia),
                        }
                        for magia_preparada in combatente.magias_preparadas
                    ],
                    "equipamentos": [
                        {
                            "id_origem": equipamento_jogador.id,
                            "quantidade": equipamento_jogador.quantidade,
                            "adicionado_em": isoformat_or_none(equipamento_jogador.adicionado_em),
                            "equipamento": _serialize_equipamento(equipamento_jogador.equipamento),
                        }
                        for equipamento_jogador in combatente.equipamentos
                    ],
                    "talentos": talentos_por_combatente.get(combatente.id, []),
                    "armaduras_protecao": [
                        {
                            "id_origem": armadura_jogador.id,
                            "adicionado_em": isoformat_or_none(armadura_jogador.adicionado_em),
                            "item": _serialize_armadura(armadura_jogador.item),
                        }
                        for armadura_jogador in combatente.armaduras_protecao
                    ],
                    "condicoes": condicoes_por_combatente.get(combatente.id, []),
                    "grimorio_magias": grimorio_por_combatente.get(combatente.id, []),
                    "grimorio_historico_troca": historico_por_combatente.get(combatente.id, []),
                    "grimorio_notificacoes": notificacoes_por_combatente.get(combatente.id, []),
                }
            )
            snapshot_combatentes.append(combatente_data)

        return {
            "snapshot_version": SNAPSHOT_VERSION,
            "gerado_em": datetime.utcnow().isoformat() + "Z",
            "database_url_redacted": redact_database_url(settings.DATABASE_URL),
            "include_deleted": include_deleted,
            "tipos": tipos or [],
            "total_combatentes": len(snapshot_combatentes),
            "combatentes": snapshot_combatentes,
        }
    finally:
        session.close()


def write_snapshot(snapshot: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")


def load_snapshot(input_path: Path) -> dict[str, Any]:
    return json.loads(input_path.read_text(encoding="utf-8"))


def _apply_deleted_at(instance: Any, deleted_at: str | None) -> None:
    instance.deleted_at = parse_datetime(deleted_at)


def _upsert_magia(session: Any, magia_data: dict[str, Any]) -> Magia:
    magia = (
        session.query(Magia)
        .filter(
            Magia.nome == magia_data["nome"],
            Magia.classe == magia_data["classe"],
            Magia.nivel == magia_data["nivel"],
        )
        .one_or_none()
    )
    if magia is None:
        magia = Magia(**{field_name: magia_data.get(field_name) for field_name in MAGIA_FIELDS})
        session.add(magia)
        session.flush()
        return magia

    for field_name in MAGIA_FIELDS:
        setattr(magia, field_name, magia_data.get(field_name))
    return magia


def _upsert_pericia(session: Any, pericia_data: dict[str, Any]) -> Pericia:
    pericia = session.query(Pericia).filter(Pericia.nome == pericia_data["nome"]).one_or_none()
    if pericia is None:
        pericia = Pericia(**{field_name: pericia_data.get(field_name) for field_name in PERICIA_FIELDS})
        session.add(pericia)
        session.flush()
    else:
        for field_name in PERICIA_FIELDS:
            setattr(pericia, field_name, pericia_data.get(field_name))

    _apply_deleted_at(pericia, pericia_data.get("deleted_at"))
    return pericia


def _upsert_condicao(session: Any, condicao_data: dict[str, Any]) -> Condicao:
    condicao = session.query(Condicao).filter(Condicao.nome == condicao_data["nome"]).one_or_none()
    if condicao is None:
        condicao = Condicao(**{field_name: condicao_data.get(field_name) for field_name in CONDICAO_FIELDS})
        session.add(condicao)
        session.flush()
        return condicao

    for field_name in CONDICAO_FIELDS:
        setattr(condicao, field_name, condicao_data.get(field_name))
    return condicao


def _upsert_equipamento(session: Any, equipamento_data: dict[str, Any]) -> Equipamento:
    equipamento = session.query(Equipamento).filter(Equipamento.nome == equipamento_data["nome"]).one_or_none()
    if equipamento is None:
        equipamento = Equipamento(**{field_name: equipamento_data.get(field_name) for field_name in EQUIPAMENTO_FIELDS})
        session.add(equipamento)
        session.flush()
    else:
        for field_name in EQUIPAMENTO_FIELDS:
            setattr(equipamento, field_name, equipamento_data.get(field_name))

    equipamento.criado_em = parse_datetime(equipamento_data.get("criado_em")) or equipamento.criado_em
    _apply_deleted_at(equipamento, equipamento_data.get("deleted_at"))
    return equipamento


def _upsert_talento(session: Any, talento_data: dict[str, Any]) -> Talento:
    talento = session.query(Talento).filter(Talento.nome == talento_data["nome"]).one_or_none()
    if talento is None:
        talento = Talento(**{field_name: talento_data.get(field_name) for field_name in TALENTO_FIELDS})
        session.add(talento)
        session.flush()
    else:
        for field_name in TALENTO_FIELDS:
            setattr(talento, field_name, talento_data.get(field_name))

    talento.criado_em = parse_datetime(talento_data.get("criado_em")) or talento.criado_em
    _apply_deleted_at(talento, talento_data.get("deleted_at"))
    return talento


def _upsert_armadura(session: Any, item_data: dict[str, Any]) -> ArmaduraProtecao:
    armadura = (
        session.query(ArmaduraProtecao)
        .filter(ArmaduraProtecao.nome == item_data["nome"], ArmaduraProtecao.tipo == item_data["tipo"])
        .one_or_none()
    )
    if armadura is None:
        armadura = ArmaduraProtecao(**{field_name: item_data.get(field_name) for field_name in ARMADURA_FIELDS})
        session.add(armadura)
        session.flush()
    else:
        for field_name in ARMADURA_FIELDS:
            setattr(armadura, field_name, item_data.get(field_name))

    armadura.criado_em = parse_datetime(item_data.get("criado_em")) or armadura.criado_em
    return armadura


def _find_existing_combatente(session: Any, combatente_data: dict[str, Any]) -> Combatente | None:
    query = session.query(Combatente).filter(
        Combatente.nome == combatente_data["nome"],
        Combatente.tipo == combatente_data["tipo"],
        Combatente.classe == combatente_data["classe"],
    )

    if combatente_data.get("dono_id") is None:
        query = query.filter(Combatente.dono_id.is_(None))
    else:
        query = query.filter(Combatente.dono_id == combatente_data["dono_id"])

    encontrados = query.all()
    if not encontrados:
        return None
    if len(encontrados) > 1:
        raise ValueError(
            f"Mais de um combatente encontrado para {combatente_data['nome']} ({combatente_data['tipo']}/{combatente_data['classe']})."
        )
    return encontrados[0]


def _replace_combatente_data(session: Any, combatente: Combatente, combatente_data: dict[str, Any]) -> None:
    for field_name in COMBATENTE_FIELDS:
        setattr(combatente, field_name, combatente_data.get(field_name))
    _apply_deleted_at(combatente, combatente_data.get("deleted_at"))
    session.flush()

    session.query(Ataque).filter(Ataque.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(MagiaSlot).filter(MagiaSlot.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(PericiaJogador).filter(PericiaJogador.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(MagiaPreparada).filter(MagiaPreparada.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(EquipamentoJogador).filter(EquipamentoJogador.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(TalentoJogador).filter(TalentoJogador.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(ArmaduraProtecaoJogador).filter(ArmaduraProtecaoJogador.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(CombatenteCondicao).filter(CombatenteCondicao.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(GrimorioMagia).filter(GrimorioMagia.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(GrimorioHistoricoTroca).filter(GrimorioHistoricoTroca.combatente_id == combatente.id).delete(synchronize_session=False)
    session.query(GrimorioNotificacao).filter(GrimorioNotificacao.combatente_id == combatente.id).delete(synchronize_session=False)
    session.flush()


def restore_snapshot(input_path: Path, replace_existing: bool = False) -> dict[str, int]:
    snapshot = load_snapshot(input_path)
    session = SessionLocal()
    created_count = 0
    updated_count = 0

    try:
        combatentes_data = snapshot.get("combatentes", [])
        for combatente_data in combatentes_data:
            combatente = _find_existing_combatente(session, combatente_data)
            if combatente is not None and not replace_existing:
                raise ValueError(
                    f"Combatente ja existe no banco: {combatente.nome} ({combatente.tipo}/{combatente.classe}). Use --replace-existing para sobrescrever os relacionamentos." 
                )

            if combatente is None:
                combatente = Combatente(**{field_name: combatente_data.get(field_name) for field_name in COMBATENTE_FIELDS})
                _apply_deleted_at(combatente, combatente_data.get("deleted_at"))
                session.add(combatente)
                session.flush()
                created_count += 1
            else:
                _replace_combatente_data(session, combatente, combatente_data)
                updated_count += 1

            for ataque_data in combatente_data.get("ataques", []):
                session.add(
                    Ataque(
                        combatente_id=combatente.id,
                        nome=ataque_data["nome"],
                        bonus_ataque=ataque_data.get("bonus_ataque", "+0"),
                        dano=ataque_data.get("dano", "1d6"),
                        tipo_dano=ataque_data.get("tipo_dano", ""),
                    )
                )

            for magia_slot_data in combatente_data.get("magias_slots", []):
                session.add(
                    MagiaSlot(
                        combatente_id=combatente.id,
                        nivel=magia_slot_data["nivel"],
                        total=magia_slot_data.get("total", 0),
                        usados=magia_slot_data.get("usados", 0),
                    )
                )

            for pericia_jogador_data in combatente_data.get("pericias", []):
                pericia = _upsert_pericia(session, pericia_jogador_data["pericia"])
                session.add(
                    PericiaJogador(
                        combatente_id=combatente.id,
                        pericia_id=pericia.id,
                        graduacao=pericia_jogador_data.get("graduacao", 0),
                        custo_total=pericia_jogador_data.get("custo_total", 0),
                        modificador_atributo=pericia_jogador_data.get("modificador_atributo", 0),
                        bonus_outros=pericia_jogador_data.get("bonus_outros", 0),
                    )
                )

            for magia_preparada_data in combatente_data.get("magias_preparadas", []):
                magia = _upsert_magia(session, magia_preparada_data["magia"])
                session.add(
                    MagiaPreparada(
                        combatente_id=combatente.id,
                        magia_id=magia.id,
                        nivel_slot=magia_preparada_data["nivel_slot"],
                        quantidade=magia_preparada_data.get("quantidade", 1),
                        usos_realizados=magia_preparada_data.get("usos_realizados", 0),
                        usada=magia_preparada_data.get("usada", False),
                        preparada_em=parse_datetime(magia_preparada_data.get("preparada_em")),
                    )
                )

            for equipamento_jogador_data in combatente_data.get("equipamentos", []):
                equipamento = _upsert_equipamento(session, equipamento_jogador_data["equipamento"])
                session.add(
                    EquipamentoJogador(
                        combatente_id=combatente.id,
                        equipamento_id=equipamento.id,
                        quantidade=equipamento_jogador_data.get("quantidade", 1),
                        adicionado_em=parse_datetime(equipamento_jogador_data.get("adicionado_em")),
                    )
                )

            for talento_jogador_data in combatente_data.get("talentos", []):
                talento = _upsert_talento(session, talento_jogador_data["talento"])
                session.add(
                    TalentoJogador(
                        combatente_id=combatente.id,
                        talento_id=talento.id,
                        adicionado_em=parse_datetime(talento_jogador_data.get("adicionado_em")),
                    )
                )

            for armadura_jogador_data in combatente_data.get("armaduras_protecao", []):
                armadura = _upsert_armadura(session, armadura_jogador_data["item"])
                session.add(
                    ArmaduraProtecaoJogador(
                        combatente_id=combatente.id,
                        item_id=armadura.id,
                        adicionado_em=parse_datetime(armadura_jogador_data.get("adicionado_em")),
                    )
                )

            for condicao_data in combatente_data.get("condicoes", []):
                condicao = _upsert_condicao(session, condicao_data["condicao"])
                session.add(
                    CombatenteCondicao(
                        combatente_id=combatente.id,
                        condicao_id=condicao.id,
                        duracao_turnos=condicao_data.get("duracao_turnos", -1),
                    )
                )

            for grimorio_data in combatente_data.get("grimorio_magias", []):
                magia = _upsert_magia(session, grimorio_data["magia"])
                session.add(
                    GrimorioMagia(
                        combatente_id=combatente.id,
                        magia_id=magia.id,
                        classe=grimorio_data["classe"],
                        favorita=grimorio_data.get("favorita", False),
                        anotacoes=grimorio_data.get("anotacoes"),
                        origem=grimorio_data.get("origem", "SELECAO_MANUAL"),
                        adicionada_em=parse_datetime(grimorio_data.get("adicionada_em")),
                    )
                )

            for historico_data in combatente_data.get("grimorio_historico_troca", []):
                magia_removida = _upsert_magia(session, historico_data["magia_removida"])
                magia_adicionada = _upsert_magia(session, historico_data["magia_adicionada"])
                session.add(
                    GrimorioHistoricoTroca(
                        combatente_id=combatente.id,
                        classe=historico_data["classe"],
                        magia_removida_id=magia_removida.id,
                        magia_adicionada_id=magia_adicionada.id,
                        nivel_personagem=historico_data["nivel_personagem"],
                        realizada_em=parse_datetime(historico_data.get("realizada_em")),
                    )
                )

            for notificacao_data in combatente_data.get("grimorio_notificacoes", []):
                session.add(
                    GrimorioNotificacao(
                        combatente_id=combatente.id,
                        classe=notificacao_data["classe"],
                        tipo=notificacao_data["tipo"],
                        dados=notificacao_data.get("dados"),
                        lida=notificacao_data.get("lida", False),
                        criada_em=parse_datetime(notificacao_data.get("criada_em")),
                    )
                )

        session.commit()
        return {
            "total_snapshot": len(combatentes_data),
            "criados": created_count,
            "atualizados": updated_count,
        }
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()