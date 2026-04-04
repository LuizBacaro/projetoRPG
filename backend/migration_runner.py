#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
migration_runner.py
Executa migrações Alembic via Python puro, sem depender do comando externo 'alembic'.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Configura sys.path
backend_root = os.path.dirname(os.path.abspath(__file__))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Imports do Alembic
from alembic.config import Config
from alembic import command


def _validate_structure():
    """Valida estrutura de diretórios."""
    logger.info("🔍 Validando estrutura...")
    
    required = ['alembic.ini', 'alembic', 'app']
    for item in required:
        path = Path(backend_root) / item
        if not path.exists():
            logger.error(f"❌ {item} não encontrado em {backend_root}")
            sys.exit(1)
    
    logger.info("✅ Estrutura validada.")


def _get_alembic_config():
    """Retorna a configuração do Alembic."""
    alembic_ini = Path(backend_root) / "alembic.ini"
    return Config(str(alembic_ini))


def cmd_autogenerate(message):
    """Cria migration automática."""
    logger.info(f"✨ Gerando migration: {message}")
    cfg = _get_alembic_config()
    try:
        command.revision(cfg, autogenerate=True, message=message)
        logger.info("✅ Migration gerada com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao gerar migration: {e}")
        sys.exit(1)


def cmd_upgrade(target='head'):
    """Aplica migrations."""
    logger.info(f"⬆️ Aplicando migrations até {target}...")
    cfg = _get_alembic_config()
    try:
        command.upgrade(cfg, target)
        logger.info("✅ Migrations aplicadas com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao aplicar migrations: {e}")
        sys.exit(1)


def cmd_downgrade(target='-1'):
    """Reverte migrations."""
    logger.info(f"⬇️ Revertendo para {target}...")
    cfg = _get_alembic_config()
    try:
        command.downgrade(cfg, target)
        logger.info("✅ Migration revertida com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao reverter migration: {e}")
        sys.exit(1)


def cmd_status():
    """Mostra status das migrations."""
    logger.info("🔍 Histórico de migrations:")
    cfg = _get_alembic_config()
    try:
        command.history(cfg)
    except Exception as e:
        logger.error(f"❌ Erro ao consultar histórico: {e}")
        sys.exit(1)


def cmd_revision(message):
    """Cria migration manual."""
    logger.info(f"📝 Criando migration manual: {message}")
    cfg = _get_alembic_config()
    try:
        command.revision(cfg, message=message)
        logger.info("✅ Migration criada com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao criar migration: {e}")
        sys.exit(1)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="🚀 Gerenciador de Migrations (Python Puro)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # autogenerate
    autogen = subparsers.add_parser('autogenerate', help='Gera migration automática')
    autogen.add_argument('message', help='Descrição da migration')
    
    # upgrade
    upgrade = subparsers.add_parser('upgrade', help='Aplica migrations')
    upgrade.add_argument('target', nargs='?', default='head', help='Versão alvo (padrão: head)')
    
    # downgrade
    downgrade = subparsers.add_parser('downgrade', help='Reverte migration')
    downgrade.add_argument('target', nargs='?', default='-1', help='Versão alvo (padrão: -1)')
    
    # status
    subparsers.add_parser('status', help='Mostra histórico de migrations')
    
    # revision
    revision = subparsers.add_parser('revision', help='Cria migration manual')
    revision.add_argument('message', help='Descrição da migration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        _validate_structure()
        
        if args.command == 'autogenerate':
            cmd_autogenerate(args.message)
        elif args.command == 'upgrade':
            cmd_upgrade(args.target)
        elif args.command == 'downgrade':
            cmd_downgrade(args.target)
        elif args.command == 'status':
            cmd_status()
        elif args.command == 'revision':
            cmd_revision(args.message)
    
    except KeyboardInterrupt:
        logger.info("\n👋 Cancelado pelo usuário.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()