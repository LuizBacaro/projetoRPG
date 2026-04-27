"""
Migration para adicionar campo rodada_atual
Execute: python migrations/add_rodada.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from app.shared.core.config import settings


def migrate():
    """Adiciona coluna rodada_atual na tabela combates"""
    
    print("🔄 Adicionando campo rodada_atual...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Verificar se tabela existe
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='combates'"))
            if not result.fetchone():
                print("⚠️  Tabela 'combates' não existe ainda. Nada a fazer.")
                return True
            
            # Verificar colunas existentes
            result = conn.execute(text("PRAGMA table_info(combates)"))
            colunas_existentes = [row[1] for row in result]
            
            if 'rodada_atual' not in colunas_existentes:
                try:
                    conn.execute(text("ALTER TABLE combates ADD COLUMN rodada_atual INTEGER DEFAULT 1"))
                    conn.commit()
                    print("✅ Coluna 'rodada_atual' adicionada com sucesso!")
                    return True
                except Exception as e:
                    print(f"❌ Erro ao adicionar coluna: {e}")
                    return False
            else:
                print("⚠️  Coluna 'rodada_atual' já existe.")
                return True
                
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


if __name__ == "__main__":
    print("🛡️  MIGRAÇÃO: Adicionar Rodadas")
    print("=" * 50)
    
    if migrate():
        print("\n✅ Migração concluída!")
        print("Reinicie o servidor: python -m uvicorn app.main:app --reload")
    else:
        print("\n❌ Migração falhou.")
    
    print("=" * 50)