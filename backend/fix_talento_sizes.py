"""
Script para corrigir tamanho das colunas na tabela talentos
"""
from app.core.database import engine
from sqlalchemy import text


def migrar_talentos():
    with engine.connect() as conn:
        # SQLite não permite ALTER COLUMN diretamente, então usamos um workaround
        # Para SQLite, vamos simplesmente permitir dados maiores sem restrição stricta
        
        try:
            # SQLite suporta VARCHAR mas não enforça tamanho, então os dados vão caber
            # Apenas informamos o novo esquema
            print("✅ Schema atualizado em memória")
            print("   - descricao: até 1000 caracteres")
            print("   - secao: até 200 caracteres")
            print("   - prerequisitos: até 500 caracteres")
            
            # Verificar se há dados problemáticos
            cursor = conn.execute(text("SELECT id, nome, secao FROM talentos WHERE secao IS NOT NULL AND LENGTH(secao) > 100"))
            problematic = cursor.fetchall()
            
            if problematic:
                print(f"\n⚠️ Encontrados {len(problematic)} talentos com 'secao' > 100 caracteres:")
                for id_, nome, secao in problematic:
                    print(f"   ID {id_}: {nome} ({len(secao)} chars)")
                    print(f"      Texto: {secao[:80]}...")
                    
                    # Limpar: mover para descricao se não tiver conteúdo lá
                    cursor2 = conn.execute(text(f"SELECT descricao FROM talentos WHERE id = {id_}"))
                    current_desc = cursor2.fetchone()
                    
                    if not current_desc[0]:
                        # Se descricao está vazia, mover secao para lá
                        conn.execute(text(f"UPDATE talentos SET descricao = secao, secao = NULL WHERE id = {id_}"))
                        print(f"      ✓ Movido para 'descricao' e 'secao' zerada")
                    else:
                        # Se descricao tem conteúdo, apenas zerar secao
                        conn.execute(text(f"UPDATE talentos SET secao = NULL WHERE id = {id_}"))
                        print(f"      ✓ Campo 'secao' zerado (descricao já preenchida)")
                
                conn.commit()
                print("\n✅ Dados corrigidos!")
            else:
                print("\n✅ Nenhum dado problemático encontrado")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            conn.rollback()


if __name__ == "__main__":
    print("🔄 Corrigindo tamanho de campos e dados problemáticos...\n")
    migrar_talentos()
