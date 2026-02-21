"""
Script de migração para adicionar campos CA, TOQUE e SURPRESA
"""
from app.core.database import engine
from sqlalchemy import text


def migrar():
    with engine.connect() as conn:
        colunas = [
            ("ca", "INTEGER DEFAULT 10"),
            ("toque", "INTEGER DEFAULT 10"),
            ("surpresa", "INTEGER DEFAULT 10"),
        ]

        for coluna, definicao in colunas:
            try:
                conn.execute(text(f"ALTER TABLE combatentes ADD COLUMN {coluna} {definicao}"))
                conn.commit()
                print(f"✅ Coluna '{coluna}' adicionada com sucesso")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"⚠️ Coluna '{coluna}' já existe, pulando...")
                else:
                    print(f"❌ Erro: {e}")


if __name__ == "__main__":
    migrar()