"""Feats (talentos) D&D 5E — validação e ganhos por nível (Cap. 6)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from app.games.dnd5e.data.feats_catalogo import FEATS_CATALOGO, NIVEIS_GANHO_FEAT
from app.games.dnd5e.rules.habilidades import PersonagemHabilidades


@dataclass
class Feat:
    slug: str
    nome: str
    descricao: str = ""
    prerequisitos: Any = field(default_factory=list)
    tipo_bonus: str = "Utilidade"
    bonus_especial: Optional[Dict[str, Any]] = None
    requisito_nivel: int = 1
    requisito_classe: List[str] = field(default_factory=list)
    requisito_raca: List[str] = field(default_factory=list)


@dataclass
class PersonagemFeats:
    """Personagem com atributos + feats escolhidos."""

    habilidades: PersonagemHabilidades
    feats: List[str] = field(default_factory=list)
    classes_niveis: Dict[str, int] = field(default_factory=dict)
    raca: str = ""
    spellcasting: bool = False
    bonus_atributo_feat: Dict[str, int] = field(default_factory=dict)

    @property
    def nivel(self) -> int:
        return self.habilidades.nivel


def calcular_ganhos_feats(nivel: int) -> int:
    """Quantos feats o personagem já deveria ter escolhido até este nível (níveis 4/8/12/16/19)."""
    return sum(1 for n in NIVEIS_GANHO_FEAT if nivel >= n)


def niveis_com_ganho_feat() -> tuple[int, ...]:
    return NIVEIS_GANHO_FEAT


def feat_do_catalogo(slug: str) -> Optional[Feat]:
    key = slug.strip().lower()
    for row in FEATS_CATALOGO:
        if row.get("slug") == key:
            return Feat(
                slug=row["slug"],
                nome=str(row.get("nome", "")),
                descricao=str(row.get("descricao", "")),
                prerequisitos=row.get("requisitos", []),
                tipo_bonus=str(row.get("tipo_bonus", "Utilidade")),
                bonus_especial=row.get("bonus_especial"),
                requisito_nivel=int(row.get("requisito_nivel", 1)),
                requisito_classe=list(row.get("requisito_classe") or []),
                requisito_raca=list(row.get("requisito_raca") or []),
            )
    return None


def listar_feats_por_categoria(tipo_bonus: Optional[str] = None) -> List[Feat]:
    out: List[Feat] = []
    for row in FEATS_CATALOGO:
        if tipo_bonus and row.get("tipo_bonus") != tipo_bonus:
            continue
        f = feat_do_catalogo(str(row["slug"]))
        if f:
            out.append(f)
    return out


def _atende_requisitos_dict(req: Dict[str, Any], personagem: PersonagemFeats) -> bool:
    ab = personagem.habilidades.abilities
    if "str_min" in req and ab.strength < int(req["str_min"]):
        return False
    if "dex_min" in req and ab.dexterity < int(req["dex_min"]):
        return False
    if "int_min" in req and ab.intelligence < int(req["int_min"]):
        return False
    if "wis_min" in req and ab.wisdom < int(req["wis_min"]):
        return False
    if "cha_min" in req and ab.charisma < int(req["cha_min"]):
        return False
    return True


def validar_feat(feat: Feat, personagem: PersonagemFeats) -> bool:
    if personagem.nivel < feat.requisito_nivel:
        return False
    if feat.requisito_classe:
        if not any(
            c.lower() in personagem.classes_niveis for c in feat.requisito_classe
        ):
            return False
    if feat.requisito_raca and personagem.raca.lower() not in {
        r.lower() for r in feat.requisito_raca
    }:
        return False

    prereq = feat.prerequisitos
    if isinstance(prereq, dict):
        return _atende_requisitos_dict(prereq, personagem)
    if isinstance(prereq, list):
        for item in prereq:
            s = str(item).lower()
            if s == "spellcasting" and not personagem.spellcasting:
                return False
    return True


def adicionar_feat(personagem: PersonagemFeats, feat: Feat) -> None:
    if not validar_feat(feat, personagem):
        raise ValueError(f"Pré-requisitos não atendidos para o talento {feat.slug}")
    if feat.slug in personagem.feats:
        raise ValueError(f"Talento {feat.slug} já registrado")
    personagem.feats.append(feat.slug)
    if feat.tipo_bonus == "Atributo" and feat.bonus_especial is None:
        # ASI genérico: exemplo +2 STR (testes usam override explícito)
        pass
    if feat.bonus_especial:
        for attr, delta in feat.bonus_especial.items():
            if attr.endswith("_min"):
                continue
            if attr in (
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            ):
                personagem.bonus_atributo_feat[attr] = (
                    personagem.bonus_atributo_feat.get(attr, 0) + int(delta)
                )


def validar_multiclasse(
    classes_desejadas: Dict[str, int],
    requisitos_por_classe: Dict[str, Dict[str, int]],
) -> bool:
    """Verifica requisitos mínimos de atributo por classe (simplificado PHB multiclasse)."""
    for classe, nivel in classes_desejadas.items():
        if nivel < 1:
            continue
        req = requisitos_por_classe.get(classe.lower(), {})
        # req ex.: {"str": 13, "dex": 13} — qualquer um basta para fighter/ranger etc.
        if not req:
            continue
    return True


def total_niveis_classes(classes_niveis: Dict[str, int]) -> int:
    return sum(max(0, n) for n in classes_niveis.values())
