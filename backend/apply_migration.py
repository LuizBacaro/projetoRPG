#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
apply_migration.py
Aplica as migrations ao banco de dados.
"""

import os
import sys
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command

def main():
    print("⬆️ Aplicando migrations...")
    
    try:
        cfg = Config(str(backend_root / "alembic.ini"))
        command.upgrade(cfg, "head")
        print("✅ Migrations aplicadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()