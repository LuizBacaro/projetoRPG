"""
config.py
SRP: Gerenciar todas as configurações da aplicação via variáveis de ambiente
SOLID: Single Responsibility — configuração centralizada
"""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from pathlib import Path
from typing import List
import secrets
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Configurações da aplicação — lidas de variáveis de ambiente e arquivo .env
    SEGURANÇA: Em produção, TODAS essas credenciais devem vir de variáveis de ambiente
    """

    # ── Projeto ──────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "Arena de Combate TTRPG API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development | staging | production

    # ── Segurança ────────────────────────────────────────────────────────────
    # Obrigatório via .env — sem default inseguro
    SECRET_KEY: str = ""

    # ── Admin padrão (credenciais iniciais via .env)
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    ADMIN_USERNAME: str = "Administrador"

    # ── Banco de dados ───────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./rpg_arena.db"

    # ── Caminhos ─────────────────────────────────────────────────────────────
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    FRONTEND_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent / "frontend"
    UPLOADS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "uploads"

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["*"]

    # ── Upload ───────────────────────────────────────────────────────────────
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    class Config:
        """Configuração de leitura do Pydantic"""
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **data):
        """Inicializa e valida configurações"""
        super().__init__(**data)
        self._validar_seguranca()
        self._criar_diretorios()
        self._normalizar_database_url()

    def _validar_seguranca(self) -> None:
        """Valida configurações críticas de segurança"""
        # SECRET_KEY: gerar automaticamente em dev, exigir em produção
        if not self.SECRET_KEY:
            if self.ENVIRONMENT == "production":
                raise ValueError(
                    "SECRET_KEY é obrigatória em produção! "
                    "Gere com: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            self.SECRET_KEY = secrets.token_hex(32)
            logger.warning("⚠️  SECRET_KEY não configurada — gerada automaticamente (apenas dev)")

        # Admin: avisar se credenciais não configuradas
        if not self.ADMIN_EMAIL or not self.ADMIN_PASSWORD:
            if self.ENVIRONMENT == "production":
                raise ValueError(
                    "ADMIN_EMAIL e ADMIN_PASSWORD são obrigatórios em produção! "
                    "Configure via variáveis de ambiente."
                )
            logger.warning(
                "⚠️  ADMIN_EMAIL/ADMIN_PASSWORD não configurados no .env — "
                "admin padrão NÃO será criado"
            )

    def _criar_diretorios(self) -> None:
        """Cria diretórios necessários"""
        self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    def _normalizar_database_url(self) -> None:
        """Railway gera 'postgres://' mas SQLAlchemy >= 2.0 requer 'postgresql://'"""
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)


# Instância global (singleton)
settings = Settings()