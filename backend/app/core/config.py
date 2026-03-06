"""
Configurações centrais da aplicação
SRP: única responsabilidade — centralizar configurações via variáveis de ambiente
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """Configurações da aplicação — lidas do ambiente ou .env"""

    # Projeto
    PROJECT_NAME:  str = "Arena de Combate TTRPG API"
    VERSION:       str = "1.0.0"
    API_V1_PREFIX: str = "/api"

    # ── Segurança ─────────────────────────────────────────────────────────
    # Lida do .env ou variável de ambiente no Railway
    # NUNCA deixe o valor padrão em produção
    SECRET_KEY: str = "rpg-arena-secret-key-change-in-production"

    # ── Banco de dados ────────────────────────────────────────────────────
    # Railway injeta DATABASE_URL automaticamente ao adicionar plugin PostgreSQL
    DATABASE_URL: str = "sqlite:///./rpg_arena.db"

    # Paths
    BASE_DIR:     Path = Path(__file__).resolve().parent.parent.parent
    UPLOADS_DIR:  Path = Path(__file__).resolve().parent.parent.parent / "uploads"
    FRONTEND_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent / "frontend"

    # ── CORS ──────────────────────────────────────────────────────────────
    # Railway: defina ALLOWED_ORIGINS=https://arena-de-combate-rpg.com.br
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Arquivo
    MAX_FILE_SIZE:      int = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    class Config:
        env_file       = ".env"
        case_sensitive = True


settings = Settings()

# Railway gera 'postgres://' mas SQLAlchemy exige 'postgresql://'
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace(
        "postgres://", "postgresql://", 1
    )

# Criar diretórios necessários
settings.UPLOADS_DIR.mkdir(exist_ok=True)