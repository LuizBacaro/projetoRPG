#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
alembic_direct.py
Executa migrações Alembic de forma manual, sem depender do comando externo.
Importa e executa as funções do Alembic diretamente.
"""

import os
import sys
from pathlib import Path

# Configura paths
backend_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(backend_root))
os.chdir(str(backend_root))

# Configuração do PYTHONPATH
os.environ['PYTHONPATH'] = str(backend_root)

print(f"📍 Backend root: {backend_root}")
print(f"📍 Current dir: {os.getcwd()}")
print(f"📍 PYTHONPATH: {os.environ['PYTHONPATH']}")

# Imports
try:
    from alembic.config import Config
    from alembic import command
    print("✅ Alembic importado com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar Alembic: {e}")
    print("\nTentando solução alternativa...")
    sys.exit(1)

import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_config():
    """Retorna configuração do Alembic."""
    ini_path = backend_root / "alembic.ini"
    if not ini_path.exists():
        logger.error(f"❌ alembic.ini não encontrado em {ini_path}")
        sys.exit(1)
    
    cfg = Config(str(ini_path))
    cfg.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL", "sqlite:///./rpg_arena.db"))
    return cfg


def validate_env():
    """Valida ambiente."""
    logger.info("🔍 Validando ambiente...")
    
    checks = {
        "alembic.ini": backend_root / "alembic.ini",
        "alembic_migrations/": backend_root / "alembic_migrations",
        "app/": backend_root / "app",
    }


def cmd_autogenerate(message):
    """Gera migration automática."""
    logger.info(f"✨ Gerando migration automática: '{message}'")
    cfg = get_config()
    
    try:
        command.revision(cfg, autogenerate=True, message=message)
        logger.info("✅ Migration gerada com sucesso!")
        logger.info("📁 Verifique em: alembic/versions/")
    except Exception as e:
        logger.error(f"❌ Erro ao gerar migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_upgrade(target='head'):
    """Aplica migrations."""
    logger.info(f"⬆️  Aplicando migrations até '{target}'...")
    cfg = get_config()
    
    try:
        command.upgrade(cfg, target)
        logger.info("✅ Migrations aplicadas com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao aplicar migrations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_downgrade(target='-1'):
    """Reverte migrations."""
    logger.info(f"⬇️  Revertendo para '{target}'...")
    cfg = get_config()
    
    try:
        command.downgrade(cfg, target)
        logger.info("✅ Migration revertida com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao reverter migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_history():
    """Mostra histórico de migrations."""
    logger.info("📜 Histórico de migrations:")
    cfg = get_config()
    
    try:
        command.history(cfg)
    except Exception as e:
        logger.error(f"❌ Erro ao consultar histórico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_current():
    """Mostra versão atual."""
    logger.info("🔍 Versão atual do banco de dados:")
    cfg = get_config()
    
    try:
        command.current(cfg)
    except Exception as e:
        logger.error(f"❌ Erro ao consultar versão: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_revision(message):
    """Cria migration manual vazia."""
    logger.info(f"📝 Criando migration manual: '{message}'")
    cfg = get_config()
    
    try:
        command.revision(cfg, message=message)
        logger.info("✅ Migration criada com sucesso!")
        logger.info("📁 Verifique em: alembic/versions/")
    except Exception as e:
        logger.error(f"❌ Erro ao criar migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point principal."""
    parser = argparse.ArgumentParser(
        description="🚀 Gerenciador de Migrations Alembic (Direct Python)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python alembic_direct.py autogenerate "add_new_spell_columns"
  python alembic_direct.py upgrade
  python alembic_direct.py downgrade
  python alembic_direct.py history
  python alembic_direct.py current
  python alembic_direct.py revision "minha descricao"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')
    
    # autogenerate
    autogen = subparsers.add_parser('autogenerate', help='Gera migration automática')
    autogen.add_argument('message', help='Descrição da migration')
    
    # upgrade
    upgrade = subparsers.add_parser('upgrade', help='Aplica migrations')
    upgrade.add_argument('target', nargs='?', default='head', help='Versão alvo (padrão: head)')
    
    # downgrade
    downgrade = subparsers.add_parser('downgrade', help='Reverte migrations')
    downgrade.add_argument('target', nargs='?', default='-1', help='Versão alvo (padrão: -1)')
    
    # history
    subparsers.add_parser('history', help='Mostra histórico de migrations')
    
    # current
    subparsers.add_parser('current', help='Mostra versão atual')
    
    # revision
    revision = subparsers.add_parser('revision', help='Cria migration manual')
    revision.add_argument('message', help='Descrição da migration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        validate_env()
        
        if args.command == 'autogenerate':
            cmd_autogenerate(args.message)
        elif args.command == 'upgrade':
            cmd_upgrade(args.target)
        elif args.command == 'downgrade':
            cmd_downgrade(args.target)
        elif args.command == 'history':
            cmd_history()
        elif args.command == 'current':
            cmd_current()
        elif args.command == 'revision':
            cmd_revision(args.message)
    
    except KeyboardInterrupt:
        logger.info("\n👋 Operação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro não previsto: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()