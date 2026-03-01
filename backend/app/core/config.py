"""
Configurações centrais da aplicação
SRP: única responsabilidade — centralizar configurações via variáveis de ambiente
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import os


class Settings(BaseSettings):
    """Configurações da aplicação — lidas do ambiente ou .env"""

    # Projeto
    PROJECT_NAME: str = "Arena de Combate TTRPG API"
    VERSION:      str = "1.0.0"
    API_V1_PREFIX: str = "/api"

    # ✅ Database — SQLite local em dev, PostgreSQL no Railway em prod
    # Railway injeta DATABASE_URL automaticamente ao adicionar o plugin PostgreSQL
    DATABASE_URL: str = "sqlite:///./rpg_arena.db"

    # Paths
    BASE_DIR:     Path = Path(__file__).resolve().parent.parent.parent  # backend/
    UPLOADS_DIR:  Path = BASE_DIR / "uploads"
    FRONTEND_DIR: Path = BASE_DIR.parent / "frontend"

    # ✅ CORS — em prod aceita apenas a URL do GitHub Pages
    # Defina ALLOWED_ORIGINS no Railway: https://luizbacaro.github.io
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Arquivo
    MAX_FILE_SIZE:      int = 5 * 1024 * 1024   # 5MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    class Config:
        env_file       = ".env"
        case_sensitive = True


settings = Settings()

# ✅ Corrige URL do Railway: 'postgres://' → 'postgresql://' (exigido pelo SQLAlchemy)
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace(
        "postgres://", "postgresql://", 1
    )

# Criar diretórios necessários
settings.UPLOADS_DIR.mkdir(exist_ok=True)