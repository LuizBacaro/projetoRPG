"""
Script para adicionar campos prerequisitos e secao à tabela talentos
"""
from app.core.database import engine
from sqlalchemy import text


def migrar_talentos():
    with engine.connect() as conn:
        colunas = [
            ("prerequisitos", "VARCHAR(500)"),
            ("secao", "VARCHAR(100)"),
        ]

        for coluna, definicao in colunas:
            try:
                conn.execute(text(f"ALTER TABLE talentos ADD COLUMN {coluna} {definicao}"))
                conn.commit()
                print(f"✅ Coluna '{coluna}' adicionada com sucesso")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"⚠️ Coluna '{coluna}' já existe, pulando...")
                else:
                    print(f"❌ Erro: {e}")


if __name__ == "__main__":
    print("🔄 Adicionando campos à tabela talentos...")
    migrar_talentos()
    print("✅ Migration concluída!")
