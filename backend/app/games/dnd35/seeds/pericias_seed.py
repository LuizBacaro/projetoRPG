"""
Seed para popular perícias do Excel: Perícias.xlsx (D&D 3.5)

Módulo canónico: `app.games.dnd35.seeds.pericias_seed`.
"""

import sys
from pathlib import Path

from sqlalchemy.orm import Session

# backend/scripts (5 níveis: seeds → dnd35 → games → app → backend)
_SCRIPTS = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from pericias_loader import carregar_pericias  # noqa: E402

from app.games.dnd35.models.combatente import (  # noqa: F401 — resolve relacionamentos
    Combatente,
)
from app.games.dnd35.models.pericia import Pericia, PericiaClasse


def seed_pericias(db: Session):
    """
    Popula a tabela de perícias a partir do Excel
    Criar perícias + associações com classes
    """
    if db.query(Pericia).first():
        print("✅ Perícias já existem no banco de dados, pulando seed")
        return

    caminho_excel = (
        Path(__file__).resolve().parent.parent.parent.parent.parent.parent
        / "Perícias.xlsx"
    )
    print(f"📚 Carregando perícias de {caminho_excel}...")

    dados = carregar_pericias(str(caminho_excel))
    pericias_data = dados["pericias"]
    pericia_classe_map = dados["pericia_classe"]

    print(f"📝 Criando {len(pericias_data)} perícias...")
    pericias_criadas = {}

    for pericia_data in pericias_data:
        pericia = Pericia(
            nome=pericia_data["nome"],
            descricao=pericia_data["descricao"],
            atributo=pericia_data["atributo"],
            tipo=pericia_data["tipo"],
            especialidade=pericia_data["especialidade"],
            requer_treinamento=pericia_data["requer_treinamento"],
            pode_usar_sem_treinamento=pericia_data["pode_usar_sem_treinamento"],
            sofre_penalidade_armadura=pericia_data["sofre_penalidade_armadura"],
        )
        db.add(pericia)
        pericias_criadas[pericia_data["nome"]] = pericia

    db.flush()

    print("🔗 Criando associações classe-perícia...")
    total_associacoes = 0

    for pericia_nome, classes_dict in pericia_classe_map.items():
        pericia = pericias_criadas.get(pericia_nome)
        if not pericia:
            print(f"⚠️ Perícia não encontrada: {pericia_nome}")
            continue

        for classe_nome, é_default in classes_dict.items():
            if é_default:
                pericia_classe = PericiaClasse(
                    pericia_id=pericia.id,
                    classe_nome=classe_nome,
                    is_default=1,
                )
                db.add(pericia_classe)
                total_associacoes += 1

    db.commit()
    print(f"✅ {len(pericias_criadas)} perícias criadas!")
    print(f"✅ {total_associacoes} associações classe-perícia criadas!")
    print("✅ Seed de perícias concluído com sucesso!")
