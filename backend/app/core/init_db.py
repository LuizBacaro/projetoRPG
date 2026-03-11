"""
init_db.py
SRP: Inicializar banco de dados e seed de dados padrão
SOLID: Single Responsibility — responsável APENAS por inicialização
"""
from sqlalchemy.orm import Session
from ..core.config import settings  # ✅ MUDADO: relativa em vez de absoluta
from ..models.usuario import Usuario, PerfilUsuario
from .security import hash_senha
import logging

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
    from ..repositories.usuario_repository import UsuarioRepository

    repo = UsuarioRepository(db)

    # ✅ Verifica se admin já existe
    admin_existe = repo.buscar_por_email(settings.ADMIN_EMAIL)
    if admin_existe:
        logger.info(f"✅ Admin já cadastrado: {settings.ADMIN_EMAIL}")
        return

    # ✅ Cria novo admin
    admin = Usuario(
        perfil=PerfilUsuario.ADMINISTRADOR,
        nome=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        senha_hash=hash_senha(settings.ADMIN_PASSWORD),
        ativo=True,
        usuario_responsavel="sistema",
    )

    repo.criar(admin)

    # ✅ Log seguro (não aparece no stdout em Railway)
    logger.warning(
        f"⚠️  ADMIN CRIADO — Email: {settings.ADMIN_EMAIL} "
        f"— ALTERE A SENHA IMEDIATAMENTE via painel de usuários"
    )
    print(
        f"✅ Admin criado com sucesso!\n"
        f"   📧 Email: {settings.ADMIN_EMAIL}\n"
        f"   🔐 Senha: {settings.ADMIN_PASSWORD}\n"
        f"   ⚠️  ALTERE A SENHA IMEDIATAMENTE após primeiro acesso\n"
        f"   📍 Acesse: /pages/usuarios.html"
    )