"""
Migration para adicionar campos de resistências
Execute: python migrations/add_resistencias.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings


def migrate():
    """Adiciona colunas de resistências na tabela combatentes"""
    
    print("🔄 Adicionando campos de resistências...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Verificar colunas existentes
            result = conn.execute(text("PRAGMA table_info(combatentes)"))
            colunas_existentes = [row[1] for row in result]
            
            campos_adicionados = []
            
            # Adicionar fortitude
            if 'fortitude' not in colunas_existentes:
                conn.execute(text("ALTER TABLE combatentes ADD COLUMN fortitude INTEGER DEFAULT 0"))
                campos_adicionados.append('fortitude')
                print("✅ Campo 'fortitude' adicionado")
            
            # Adicionar reflexos
            if 'reflexos' not in colunas_existentes:
                conn.execute(text("ALTER TABLE combatentes ADD COLUMN reflexos INTEGER DEFAULT 0"))
                campos_adicionados.append('reflexos')
                print("✅ Campo 'reflexos' adicionado")
            
            # Adicionar vontade
            if 'vontade' not in colunas_existentes:
                conn.execute(text("ALTER TABLE combatentes ADD COLUMN vontade INTEGER DEFAULT 0"))
                campos_adicionados.append('vontade')
                print("✅ Campo 'vontade' adicionado")
            
            if campos_adicionados:
                conn.commit()
                print(f"\n🎉 {len(campos_adicionados)} campo(s) adicionado(s) com sucesso!")
            else:
                print("\n⚠️  Todos os campos já existem.")
            
            return True
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🛡️  MIGRAÇÃO: Adicionar Resistências")
    print("=" * 50)
    
    if migrate():
        print("\n✅ Migração concluída!")
        print("Reinicie o servidor: python -m uvicorn app.main:app --reload")
    else:
        print("\n❌ Migração falhou.")
    
    print("=" * 50)