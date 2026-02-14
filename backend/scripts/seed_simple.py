"""
Seed simplificado - popula banco de dados
"""
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

print(f"📁 Backend dir: {backend_dir}")

try:
    from app.core.database import SessionLocal, Base, engine
    from app.models.combatente import Combatente
    import app.models.combate  # Importar para criar tabela
    
    print("✅ Imports bem-sucedidos!")
    
    # Criar tabelas
    print("🔧 Criando tabelas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas!")
    
    # Popular banco
    db = SessionLocal()
    
    try:
        # Verificar se já tem dados
        count = db.query(Combatente).count()
        print(f"📊 Combatentes existentes: {count}")
        
        if count > 0:
            print("\n⚠️  Banco já possui dados!")
            print("Continuando sem limpar (mantenha os dados existentes)")
            print("Se quiser resetar, delete o arquivo rpg_arena.db e rode novamente\n")
        else:
            print("\n🌱 Populando banco de dados...")
            
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
                    "nome": "Comerciante Anão", "tipo": "npc", "classe": "Civil",
                    "hp_maximo": 40, "hp_atual": 40, "iniciativa": 8,
                    "forca": 12, "destreza": 10, "constituicao": 14,
                    "inteligencia": 12, "sabedoria": 13, "carisma": 11,
                    "nivel": 1, "pontos": 0
                }
            ]
            
            for data in combatentes_iniciais:
                combatente = Combatente(**data)
                db.add(combatente)
                print(f"  ✅ {data['nome']} ({data['tipo']}) - Nível {data['nivel']}")
            
            db.commit()
            print(f"\n🎉 {len(combatentes_iniciais)} combatentes criados com sucesso!")
        
        print("\n" + "=" * 50)
        print("Para iniciar o servidor:")
        print("  python -m uvicorn app.main:app --reload")
        print("=" * 50)
        
    finally:
        db.close()
        
except ImportError as e:
    print(f"\n❌ Erro de importação: {e}")
    print("\n🔍 Verificações necessárias:")
    print(f"  1. Verifique se existe: {backend_dir}/app/models/combatente.py")
    print(f"  2. Verifique se existe: {backend_dir}/app/models/__init__.py")
    print(f"  3. Verifique se existe: {backend_dir}/app/__init__.py")
    print(f"  4. Verifique se existe: {backend_dir}/app/core/database.py")
    print("\nExecute para diagnosticar:")
    print("  find app -name '*.py' | head -20")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)