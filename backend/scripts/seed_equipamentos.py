"""
Seed de equipamentos D&D 3.5 padrão
"""

EQUIPAMENTOS_PADRAO = [
    # ── ARMAS ──
    ("Adaga", "Arma simples de melee", "PHB p.120"),
    ("Espada Longa", "Arma marcial de melee", "PHB p.124"),
    ("Espada Curta", "Arma simples de melee", "PHB p.120"),
    ("Machado Grande", "Arma marcial de melee", "PHB p.124"),
    ("Maça", "Arma simples de melee", "PHB p.120"),
    ("Bastão", "Arma simples de melee", "PHB p.120"),
    ("Arco Longo", "Arma marcial à distância", "PHB p.124"),
    ("Arco Curto", "Arma simples à distância", "PHB p.120"),
    ("Besta Pesada", "Arma simples à distância", "PHB p.120"),
    ("Besta Leve", "Arma simples à distância", "PHB p.120"),
    ("Lança", "Arma simples de melee", "PHB p.120"),
    ("Espada Bastarda", "Arma exótica", "PHB p.126"),
    ("Katana", "Arma exótica", "PHB p.126"),
    
    # ── ARMADURAS ──
    ("Courça de Couro", "Armadura leve", "PHB p.125"),
    ("Armadura de Couro", "Armadura leve", "PHB p.125"),
    ("Corrente de Malha", "Armadura média", "PHB p.125"),
    ("Armadura de Placas", "Armadura pesada", "PHB p.125"),
    ("Escudo de Madeira", "Escudo leve", "PHB p.125"),
    ("Escudo de Aço", "Escudo pesado", "PHB p.125"),
    
    # ── EQUIPAMENTOS AVENTUREIROS ──
    ("Mochila de Aventureiro", "Mochila de viagem", "PHB p.128"),
    ("Moeda (Ouro)", "Moeda de ouro", "PHB p.128"),
    ("Corda (15 pés)", "Corda de sisal", "PHB p.128"),
    ("Lanterna", "Fonte de luz", "PHB p.128"),
    ("Óleo para Lanterna", "Combustível para lanterna", "PHB p.128"),
    ("Marmita", "Utensílio de cozinha", "PHB p.128"),
    ("Tenda", "Abrigo portátil", "PHB p.128"),
    ("Saco de Dormir", "Abrigo para dormir", "PHB p.128"),
    ("Cantil", "Recipiente para água", "PHB p.128"),
    ("Picareta", "Ferramenta de escavação", "PHB p.128"),
    ("Pá", "Ferramenta de escavação", "PHB p.128"),
    ("Martelo", "Ferramenta de trabalho", "PHB p.128"),
    ("Pregos (10)", "Fixadores", "PHB p.128"),
    ("Cadeado", "Segurança", "PHB p.128"),
    ("Chave para Cadeado", "Chave mestre", "PHB p.128"),
    ("Jogo de Ferramentas de Ladrão", "Ferramentas especializadas", "PHB p.128"),
    ("Jogo de Cura", "Kit médico", "PHB p.128"),
    ("Tochas (10)", "Fonte de luz", "PHB p.128"),
    ("Bebida Alcoólica", "Bebida alcóolica", "PHB p.128"),
    ("Pergaminho", "Material de escrita", "PHB p.128"),
    ("Tinta", "Tinta para escrita", "PHB p.128"),
    ("Pena", "Ferramenta de escrita", "PHB p.128"),
    
    # ── POÇÕES E CONSUMÍVEIS ──
    ("Poção de Cura Menor", "Restaura 1d8+1 PV", "PHB p.182"),
    ("Poção de Cura Moderada", "Restaura 2d8+3 PV", "PHB p.182"),
    ("Poção de Cura Séria", "Restaura 3d8+5 PV", "PHB p.182"),
    ("Poção de Resistência", "Aumenta resistências", "PHB p.182"),
    ("Poção de Força do Gigante", "Aumenta FOR", "PHB p.182"),
    ("Poção de Velocidade", "Aumenta DES", "PHB p.182"),
    
    # ── ITENS MÁGICOS MUNDANOS ──
    ("Sacola de Manutenção Eterna", "Bolsa infinita", "DMG p.246"),
    ("Corda de Entanglement", "Corda mágica", "DMG p.246"),
    ("Botas de Leveza", "Reduz peso", "DMG p.246"),
    ("Capa de Invisibilidade", "Torna invisível", "DMG p.246"),
    ("Anel de Proteção", "Aumenta CA", "DMG p.246"),
    ("Amuleto de Proteção", "Aumenta resistências", "DMG p.246"),
    ("Anel da Verdade", "Detecta mentira", "DMG p.246"),
    ("Varinha de Magia de Míssil", "Dispara Magic Missile", "DMG p.246"),
    ("Varinha de Cura", "Cura ferimentos", "DMG p.246"),
]


def seed_equipamentos(db):
    """
    Popula a tabela de equipamentos com dados padrão.
    """
    from app.models.equipamento import Equipamento
    from datetime import datetime, timezone
    
    # Verificar se já existem equipamentos
    count = db.query(Equipamento).count()
    if count > 0:
        print(f"✅ Equipamentos já existem ({count}). Pulando seed.")
        return
    
    print("📦 Iniciando seed de equipamentos...")
    
    for nome, descricao, pag_ref in EQUIPAMENTOS_PADRAO:
        equipamento = Equipamento(
            nome=nome,
            descricao=descricao,
            pagina_referencia=pag_ref,
            ativo=True,
            criado_em=datetime.now(timezone.utc)
        )
        db.add(equipamento)
    
    db.commit()
    print(f"✅ {len(EQUIPAMENTOS_PADRAO)} equipamentos inseridos com sucesso!")


if __name__ == "__main__":
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        seed_equipamentos(db)
    finally:
        db.close()
