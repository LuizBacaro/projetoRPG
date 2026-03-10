"""
config.py
SRP: Gerenciar todas as configurações da aplicação via variáveis de ambiente
SOLID: Single Responsibility — configuração centralizada
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """
    Configurações da aplicação — lidas de variáveis de ambiente e arquivo .env
    SEGURANÇA: Em produção, TODAS essas credenciais devem vir de variáveis de ambiente
    """

    # ── Projeto ──────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "Arena de Combate TTRPG API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"  # development | staging | production

    # ── Segurança ────────────────────────────────────────────────────────────
    SECRET_KEY: str = "rpg-arena-secret-key-change-in-production"

    # ── Admin padrão (credenciais iniciais)
    # ⚠️  NUNCA deixar credenciais em código — usar variáveis de ambiente
    ADMIN_EMAIL: str = "admin@arena-rpg.com.br"
    ADMIN_PASSWORD: str = "Admin@123456"  # MUDE IMEDIATAMENTE APÓS PRIMEIRO ACESSO
    ADMIN_USERNAME: str = "Administrador Sistema"

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
        self._criar_diretorios()
        self._normalizar_database_url()

    def _criar_diretorios(self) -> None:
        """Cria diretórios necessários"""
        self.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    def _normalizar_database_url(self) -> None:
        """Railway gera 'postgres://' mas SQLAlchemy >= 2.0 requer 'postgresql://'"""
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)


# Instância global (singleton)
settings = Settings()