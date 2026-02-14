"""
Configurações centrais da aplicação
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Projeto
    PROJECT_NAME: str = "Arena de Combate TTRPG API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./rpg_arena.db"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent  # backend/
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    FRONTEND_DIR: Path = BASE_DIR.parent / "frontend"  # projetoRPG/frontend
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]
    
    # Arquivo
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Criar diretórios necessários
settings.UPLOADS_DIR.mkdir(exist_ok=True)