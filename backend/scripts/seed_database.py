"""
Script para popular o banco de dados com dados iniciais
Execute: python scripts/seed_database.py
"""
import sys
from pathlib import Path

# Adicionar app ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.models.combatente import Combatente


def seed():
    """Popula o banco com combatentes iniciais"""
    db = SessionLocal()
    repo = CombatenteRepository(db)
    
    try:
        # Verificar se já tem dados
        if repo.count() > 0:
            print("⚠️  Banco já possui dados!")
            resposta = input("Deseja limpar e repopular? (s/n): ")
            if resposta.lower() != 's':
                print("❌ Operação cancelada.")
                return
            
            # Deletar todos
            for c in repo.get_all():
                repo.delete(c)
            print("🗑️  Dados antigos removidos.")
        
        print("🌱 Populando banco de dados...")
        print("=" * 50)
        
        combatentes_iniciais = [
            {
                "nome": "Theron", "tipo": "jogador", "classe": "Guerreiro",
                "hp_maximo": 85, "hp_atual": 85, "iniciativa": 15,
                "forca": 16, "destreza": 12, "constituicao": 14,
                "inteligencia": 10, "sabedoria": 11, "carisma": 13,
                "nivel": 5, "pontos": 1200
            },
            {
                "nome": "Lyra", "tipo": "jogador", "classe": "Mago",
                "hp_maximo": 45, "hp_atual": 45, "iniciativa": 18,
                "forca": 8, "destreza": 14, "constituicao": 10,
                "inteligencia": 18, "sabedoria": 15, "carisma": 12,
                "nivel": 5, "pontos": 1150
            },
            {
                "nome": "Garrick", "tipo": "jogador", "classe": "Clérigo",
                "hp_maximo": 65, "hp_atual": 65, "iniciativa": 12,
                "forca": 14, "destreza": 10, "constituicao": 13,
                "inteligencia": 12, "sabedoria": 16, "carisma": 14,
                "nivel": 5, "pontos": 980
            },
            {
                "nome": "Zara", "tipo": "jogador", "classe": "Ladino",
                "hp_maximo": 55, "hp_atual": 55, "iniciativa": 20,
                "forca": 10, "destreza": 18, "constituicao": 12,
                "inteligencia": 14, "sabedoria": 13, "carisma": 15,
                "nivel": 5, "pontos": 1350
            },
            {
                "nome": "Goblin Arqueiro", "tipo": "monstro", "classe": "Arqueiro",
                "hp_maximo": 30, "hp_atual": 30, "iniciativa": 14,
                "forca": 8, "destreza": 14, "constituicao": 10,
                "inteligencia": 10, "sabedoria": 8, "carisma": 8,
                "nivel": 2, "pontos": 0
            },
            {
                "nome": "Orc Guerreiro", "tipo": "monstro", "classe": "Guerreiro",
                "hp_maximo": 60, "hp_atual": 60, "iniciativa": 10,
                "forca": 16, "destreza": 12, "constituicao": 16,
                "inteligencia": 7, "sabedoria": 11, "carisma": 10,
                "nivel": 3, "pontos": 0
            },
            {
                "nome": "Esqueleto Mago", "tipo": "monstro", "classe": "Mago",
                "hp_maximo": 35, "hp_atual": 35, "iniciativa": 16,
                "forca": 8, "destreza": 14, "constituicao": 10,
                "inteligencia": 14, "sabedoria": 10, "carisma": 6,
                "nivel": 3, "pontos": 0
            },
            {
                "nome": "Comerciante Anão", "tipo": "npc", "classe": "Civil",
                "hp_maximo": 40, "hp_atual": 40, "iniciativa": 8,
                "forca": 12, "destreza": 10, "constituicao": 14,
                "inteligencia": 12, "sabedoria": 13, "carisma": 11,
                "nivel": 1, "pontos": 0
            }
        ]
        
        for data in combatentes_iniciais:
            combatente = Combatente(**data)
            repo.create(combatente)
            print(f"  ✅ {data['nome']} ({data['tipo']}) - Nível {data['nivel']}")
        
        print("=" * 50)
        print(f"🎉 {len(combatentes_iniciais)} combatentes criados com sucesso!")
        print()
        print("Para iniciar o servidor:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Erro ao popular banco: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🛡️  SEED DO BANCO DE DADOS - Arena TTRPG")
    print()
    seed()