"""
Criação idempotente do usuário administrador a partir das variáveis de ambiente.
"""

from __future__ import annotations

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.shared.core.config import settings
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario, Usuario

logger = logging.getLogger(__name__)


def criar_admin_padrao(db: Session) -> None:
    """
    Cria o usuário administrador padrão se não existir.

    SEGURANÇA:
    - Apenas via logger (não aparece no stdout em produção)
    - Credenciais vêm do config.py (variáveis de ambiente em prod)
    - Aviso forçado para trocar a senha no primeiro acesso

    Args:
        db: Sessão do banco de dados
    """
    from app.shared.repositories.usuario_repository import UsuarioRepository

    repo = UsuarioRepository(db)

    admin_email = (settings.ADMIN_EMAIL or "").strip().lower()
    admin_password = (settings.ADMIN_PASSWORD or "").strip()
    admin_username = (
        settings.ADMIN_USERNAME or "Administrador"
    ).strip() or "Administrador"

    # Se credenciais não configuradas, pular criação
    if not admin_email or not admin_password:
        logger.info(
            "ℹ️  Credenciais de admin não configuradas no .env — pulando criação"
        )
        return

    # ✅ Verifica se admin já existe
    admin_existe = repo.buscar_por_email(admin_email)
    if admin_existe:
        logger.info(f"✅ Admin já cadastrado: {admin_email}")
        return

    # ✅ Cria novo admin
    admin = Usuario(
        perfil=PerfilUsuario.ADMINISTRADOR,
        nome=admin_username,
        email=admin_email,
        senha_hash=hash_senha(admin_password),
        ativo=True,
        usuario_responsavel="sistema",
    )

    try:
        repo.criar(admin)
    except IntegrityError:
        # Idempotência em cenários de corrida: outro processo criou o admin no intervalo.
        admin_existe = repo.buscar_por_email(admin_email)
        if admin_existe:
            logger.info(f"✅ Admin já cadastrado por outra transação: {admin_email}")
            return
        raise

    # ✅ Log seguro — NÃO exibir a senha
    logger.warning(
        f"⚠️  ADMIN CRIADO — Email: {admin_email} "
        f"— ALTERE A SENHA IMEDIATAMENTE via painel de usuários"
    )
    print(
        f"✅ Admin criado com sucesso!\n"
        f"   📧 Email: {admin_email}\n"
        f"   ⚠️  ALTERE A SENHA IMEDIATAMENTE após primeiro acesso\n"
        f"   📍 Acesse: /pages/usuarios.html"
    )
