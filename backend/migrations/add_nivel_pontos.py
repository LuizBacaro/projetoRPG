"""
Migration para adicionar campos nivel e pontos
Execute: python migrations/add_nivel_pontos.py
"""
import sys
from pathlib import Path

# Adicionar app ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings


def verificar_tabela_existe(conn):
    """Verifica se a tabela combatentes existe"""
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='combatentes'"))
    return result.fetchone() is not None


def criar_tabelas():
    """Cria as tabelas se não existirem"""
    print("🔍 Verificando se tabelas existem...")
    
    try:
        from app.core.database import Base, engine
        import app.models.combatente
        import app.models.combate
        
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/verificadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        return False


def migrate():
    """Adiciona colunas nivel e pontos na tabela combatentes"""
    
    print("🔄 Iniciando migração do banco de dados...")
    print("=" * 50)
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Verificar se tabela existe
            if not verificar_tabela_existe(conn):
                print("⚠️  Tabela 'combatentes' não existe!")
                print("🔧 Criando tabelas do banco de dados...")
                if not criar_tabelas():
                    print("❌ Falha ao criar tabelas. Abortando.")
                    return False
                print()
            
            # Verificar colunas existentes
            result = conn.execute(text("PRAGMA table_info(combatentes)"))
            colunas_existentes = [row[1] for row in result]
            
            print(f"📊 Colunas existentes: {colunas_existentes}")
            print()
            
            migracoes_aplicadas = []
            
            # Adicionar coluna nivel
            if 'nivel' not in colunas_existentes:
                try:
                    conn.execute(text("ALTER TABLE combatentes ADD COLUMN nivel INTEGER DEFAULT 1"))
                    conn.commit()
                    print("✅ Coluna 'nivel' adicionada com sucesso!")
                    migracoes_aplicadas.append("nivel")
                except Exception as e:
                    print(f"❌ Erro ao adicionar coluna 'nivel': {e}")
                    conn.rollback()
                    return False
            else:
                print("⚠️  Coluna 'nivel' já existe, pulando...")
            
            # Adicionar coluna pontos
            if 'pontos' not in colunas_existentes:
                try:
                    conn.execute(text("ALTER TABLE combatentes ADD COLUMN pontos INTEGER DEFAULT 0"))
                    conn.commit()
                    print("✅ Coluna 'pontos' adicionada com sucesso!")
                    migracoes_aplicadas.append("pontos")
                except Exception as e:
                    print(f"❌ Erro ao adicionar coluna 'pontos': {e}")
                    conn.rollback()
                    return False
            else:
                print("⚠️  Coluna 'pontos' já existe, pulando...")
            
            print()
            print("=" * 50)
            
            # Verificar resultado final
            result = conn.execute(text("PRAGMA table_info(combatentes)"))
            colunas_finais = [row[1] for row in result]
            
            print(f"📊 Colunas após migração: {colunas_finais}")
            print()
            
            if 'nivel' in colunas_finais and 'pontos' in colunas_finais:
                print("🎉 Migração concluída com sucesso!")
                if migracoes_aplicadas:
                    print(f"✅ Migrações aplicadas: {', '.join(migracoes_aplicadas)}")
                else:
                    print("ℹ️  Nenhuma migração necessária (já estava atualizado)")
                return True
            else:
                print("⚠️  Migração parcial - verifique os erros acima")
                return False
                
    except Exception as e:
        print(f"❌ Erro fatal na migração: {e}")
        import traceback
        traceback.print_exc()
        return False


def verificar_dados():
    """Verifica alguns dados após migração"""
    print()
    print("🔍 Verificando dados existentes...")
    print("=" * 50)
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, nome, nivel, pontos FROM combatentes LIMIT 5"))
            rows = result.fetchall()
            
            if rows:
                print("Primeiros 5 combatentes:")
                for row in rows:
                    print(f"  ID: {row[0]} | Nome: {row[1]} | Nível: {row[2]} | Pontos: {row[3]}")
            else:
                print("  📭 Nenhum combatente cadastrado ainda.")
        
        print("=" * 50)
    except Exception as e:
        print(f"⚠️  Erro ao verificar dados: {e}")


if __name__ == "__main__":
    print("🛡️  MIGRAÇÃO DE BANCO DE DADOS - Arena TTRPG")
    print()
    
    sucesso = migrate()
    
    if sucesso:
        verificar_dados()
        print()
        print("✅ Tudo pronto! Reinicie o servidor FastAPI.")
        print("   Comando: cd backend && python -m uvicorn app.main:app --reload")
        sys.exit(0)
    else:
        print()
        print("❌ Migração falhou. Verifique os erros acima.")
        sys.exit(1)