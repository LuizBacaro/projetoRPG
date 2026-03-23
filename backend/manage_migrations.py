#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
manage_migrations.py

SRP: Gerenciar comandos do Alembic de forma simplificada e robusta.
Este script atua como um wrapper para o Alembic, configurando o ambiente
e fornecendo uma interface de linha de comando amigável para as operações
de migração do banco de dados. Ele garante que o PYTHONPATH esteja
corretamente configurado para que o Alembic possa encontrar os módulos
da sua aplicação (ex: 'app/models').
"""

import os
import sys
import subprocess
import argparse
import logging

# Configuração básica de logging para o script
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def _validate_directory_structure() -> None:
    """
    Valida se a estrutura de diretórios necessária para o Alembic está presente.
    Verifica a existência de 'alembic.ini', 'alembic/' e 'app/' na raiz do backend.
    """
    logger.info("🔍 Validando estrutura de diretórios...")
    backend_root = os.getcwd()

    if not os.path.exists(os.path.join(backend_root, 'alembic.ini')):
        logger.error("❌ Erro: 'alembic.ini' não encontrado na raiz do backend. Certifique-se de estar no diretório correto.")
        sys.exit(1)

    if not os.path.isdir(os.path.join(backend_root, 'alembic')):
        logger.error("❌ Erro: Diretório 'alembic/' não encontrado. Execute 'alembic init alembic' se ainda não o fez.")
        sys.exit(1)

    if not os.path.isdir(os.path.join(backend_root, 'app')):
        logger.error("❌ Erro: Diretório 'app/' não encontrado. O projeto FastAPI/SQLAlchemy deve estar em 'app/'.")
        sys.exit(1)

    logger.info("✅ Estrutura de diretórios validada com sucesso.")


def _configure_pythonpath() -> None:
    """
    Configura o PYTHONPATH para que o Alembic possa encontrar o módulo 'app'.
    Adiciona o diretório raiz do backend ao sys.path e ao PYTHONPATH do ambiente
    para subprocessos.
    """
    backend_root = os.getcwd()
    
    # Adiciona ao sys.path do processo atual
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)
        logger.info(f"➕ Adicionado '{backend_root}' ao sys.path do processo atual.")

    # Configura o PYTHONPATH para subprocessos (como o comando 'alembic' em si)
    if 'PYTHONPATH' in os.environ:
        # Evita duplicatas e garante que o diretório do backend seja o primeiro
        existing_paths = os.environ['PYTHONPATH'].split(os.pathsep)
        if backend_root not in existing_paths:
            os.environ['PYTHONPATH'] = f"{backend_root}{os.pathsep}{os.environ['PYTHONPATH']}"
            logger.info(f"➕ Adicionado '{backend_root}' ao PYTHONPATH do ambiente para subprocessos.")
    else:
        os.environ['PYTHONPATH'] = backend_root
        logger.info(f"➕ Definido PYTHONPATH do ambiente para '{backend_root}' para subprocessos.")


def _run_alembic_command(command_args: list) -> None:
    """
    Executa um comando do Alembic usando subprocess.
    """
    full_command = ['alembic'] + command_args
    logger.info(f"🚀 Executando comando Alembic: {' '.join(full_command)}")
    
    try:
        # Executa o comando Alembic, passando o ambiente modificado
        process = subprocess.run(full_command, check=True, capture_output=True, text=True, env=os.environ)
        logger.info("✅ Comando Alembic executado com sucesso.")
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(process.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao executar comando Alembic (código de saída {e.returncode}):")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        sys.exit(e.returncode)
    except FileNotFoundError:
        logger.error("❌ Erro: Comando 'alembic' não encontrado. Certifique-se de que o Alembic está instalado e no PATH.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Ocorreu um erro inesperado: {e}")
        sys.exit(1)


def main() -> None:
    """
    Função principal para parsear argumentos e executar comandos Alembic.
    """
    parser = argparse.ArgumentParser(
        description="✨ Gerenciador de Migrações Alembic para o Projeto RPG ✨\nSimplifica a execução de comandos Alembic, garantindo a configuração correta do ambiente.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos de migração disponíveis')

    # Comando 'status'
    status_parser = subparsers.add_parser('status', help='Mostra o histórico e status das migrações.')
    status_parser.set_defaults(func=lambda args: _run_alembic_command(['history']))

    # Comando 'upgrade'
    upgrade_parser = subparsers.add_parser('upgrade', help='Aplica as migrações pendentes.')
    upgrade_parser.add_argument('target', nargs='?', default='head',
                                help='Versão alvo para upgrade (ex: head, <revision_id>). Padrão: head.')
    upgrade_parser.set_defaults(func=lambda args: _run_alembic_command(['upgrade', args.target]))

    # Comando 'downgrade'
    downgrade_parser = subparsers.add_parser('downgrade', help='Reverte a última migração aplicada ou para uma versão específica.')
    downgrade_parser.add_argument('target', nargs='?', default='-1',
                                  help='Versão alvo para downgrade (ex: -1 para a última, <revision_id>). Padrão: -1.')
    downgrade_parser.set_defaults(func=lambda args: _run_alembic_command(['downgrade', args.target]))

    # Comando 'revision' (manual)
    revision_parser = subparsers.add_parser('revision', help='Cria uma nova migração vazia (manual).')
    revision_parser.add_argument('message', type=str,
                                 help='Mensagem descritiva para a nova migração.')
    revision_parser.set_defaults(func=lambda args: _run_alembic_command(['revision', '-m', args.message]))

    # Comando 'autogenerate'
    autogenerate_parser = subparsers.add_parser('autogenerate', help='Cria uma nova migração automaticamente com base nas mudanças do modelo.')
    autogenerate_parser.add_argument('message', type=str,
                                     help='Mensagem descritiva para a nova migração.')
    autogenerate_parser.set_defaults(func=lambda args: _run_alembic_command(['revision', '--autogenerate', '-m', args.message]))

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        _validate_directory_structure()
        _configure_pythonpath()
        args.func(args)  # Chama a função associada ao subcomando
    except KeyboardInterrupt:
        logger.info("\n👋 Operação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Um erro inesperado ocorreu: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()