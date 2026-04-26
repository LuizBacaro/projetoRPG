#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
create_migration.py
Cria arquivo de migration manualmente sem depender do Alembic CLI.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

# Imports dos models
from app.core.database import Base
from app.models.usuario import Usuario
from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.magia import Magia
from app.games.dnd35.models.combate import Combate
from app.games.dnd35.models.pericia import Pericia
from app.games.dnd35.models.condicao import Condicao
from app.games.dnd35.models.combatente_condicao import CombatenteCondicao

from sqlalchemy import inspect, MetaData, create_engine
import sqlite3

def get_migration_template(message, operations):
    """Gera template de migration."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    template = f'''"""
{timestamp}_{message}

Revision ID: {timestamp}
Revises: 
Create Date: {datetime.now().isoformat()}
"""
from alembic import op
import sqlalchemy as sa


revision = '{timestamp}'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    \"\"\"Aplicar migration.\"\"\"
{operations}


def downgrade() -> None:
    \"\"\"Reverter migration.\"\"\"
    pass
'''
    return template, timestamp

def compare_with_db():
    """Compara modelos com banco de dados."""
    db_path = backend_root / "rpg_arena.db"
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado. Criando do zero...")
        return "create_all"
    
    # Conecta ao banco
    engine = create_engine(f"sqlite:///{db_path}")
    
    # Metadata do banco
    inspector = inspect(engine)
    db_tables = inspector.get_table_names()
    
    # Metadata dos modelos
    model_tables = Base.metadata.tables.keys()
    
    print(f"📊 Tabelas no banco: {db_tables}")
    print(f"📊 Tabelas nos modelos: {model_tables}")
    
    # Verifica tabela de magias
    if 'magias' in db_tables:
        existing_cols = {col['name'] for col in inspector.get_columns('magias')}
        print(f"✅ Colunas existentes em magias: {existing_cols}")
        
        # Colunas esperadas do modelo
        magia_model = Base.metadata.tables['magias']
        expected_cols = {col.name for col in magia_model.columns}
        print(f"📋 Colunas esperadas em magias: {expected_cols}")
        
        # Diferença
        missing_cols = expected_cols - existing_cols
        if missing_cols:
            print(f"⚠️  Colunas faltando: {missing_cols}")
            return "add_columns"
    
    return "no_changes"

def create_add_columns_migration():
    """Cria migration para adicionar colunas faltantes."""
    ops = []
    
    # Conecta ao banco
    db_path = backend_root / "rpg_arena.db"
    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    
    if 'magias' in inspector.get_table_names():
        existing_cols = {col['name'] for col in inspector.get_columns('magias')}
        magia_model = Base.metadata.tables['magias']
        expected_cols = magia_model.columns
        
        for col in expected_cols:
            if col.name not in existing_cols:
                col_type = str(col.type)
                nullable = "nullable=True" if col.nullable else "nullable=False"
                ops.append(f"    op.add_column('magias', sa.Column('{col.name}', sa.{col_type}(), {nullable}))")
    
    operations = "\n".join(ops) if ops else "    pass  # Nenhuma coluna para adicionar"
    
    template, ts = get_migration_template("add_new_spell_columns", operations)
    
    return template, ts

def save_migration(template, timestamp):
    """Salva arquivo de migration."""
    versions_dir = backend_root / "alembic" / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{timestamp}_add_new_spell_columns.py"
    filepath = versions_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"✅ Migration criada: {filepath}")
    return filepath

def main():
    print("🔍 Analisando banco de dados...")
    
    status = compare_with_db()
    print(f"\n📌 Status: {status}")
    
    if status == "add_columns":
        print("\n✨ Criando migration para adicionar colunas...")
        template, ts = create_add_columns_migration()
        filepath = save_migration(template, ts)
        
        print(f"\n✅ Pronto!")
        print(f"📁 Arquivo: {filepath}")
        print(f"\nAgora você pode:")
        print(f"  1. Revisar o arquivo criado")
        print(f"  2. Executar: python apply_migration.py")
    else:
        print("✅ Banco de dados já está atualizado!")

if __name__ == '__main__':
    main()