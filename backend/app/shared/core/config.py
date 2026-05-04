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
import os

logger = logging.getLogger(__name__)

# Produção: front está no Registro.br (apex + www). Mescladas em ALLOWED_ORIGINS se faltarem no Render.
_ARENA_FRONTEND_ORIGINS_PROD: tuple[str, ...] = (
    "https://arena-de-combate-rpg.com.br",
    "https://www.arena-de-combate-rpg.com.br",
)


def _norm_cors_origin(url: str) -> str:
    return (url or "").strip().rstrip("/")


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
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    FRONTEND_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent.parent / "frontend"
    UPLOADS_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
    UPLOADS_BASE_URL: str = "/uploads"

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["*"]

    @model_validator(mode="after")
    def _merge_arena_cors_origins(self):
        """Em produção, garante apex + www do domínio Arena no CORS (evita bloqueio só com `www`)."""
        if "*" in self.ALLOWED_ORIGINS:
            return self
        seen: set[str] = set()
        merged: list[str] = []
        for raw in self.ALLOWED_ORIGINS:
            n = _norm_cors_origin(str(raw))
            if not n or n in seen:
                continue
            seen.add(n)
            merged.append(n)
        if self.ENVIRONMENT == "production":
            for raw in _ARENA_FRONTEND_ORIGINS_PROD:
                n = _norm_cors_origin(raw)
                if n not in seen:
                    seen.add(n)
                    merged.append(n)
                    logger.info("CORS: origem Arena adicionada automaticamente em produção: %s", n)
        self.ALLOWED_ORIGINS = merged
        return self

    # ── Upload ───────────────────────────────────────────────────────────────
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    MAX_REQUEST_SIZE: int = 6 * 1024 * 1024  # 6MB
    MAX_JSON_BODY_SIZE: int = 1 * 1024 * 1024  # 1MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    # ── Cloudinary (armazenamento de imagens em produção) ─────────────────────
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # ── Compressão ───────────────────────────────────────────────────────────
    GZIP_ENABLED: bool = True
    GZIP_MINIMUM_SIZE: int = 1000

    # ── Cache ────────────────────────────────────────────────────────────────
    CACHE_ENABLED: bool = True
    CACHE_CATALOG_TTL_SECONDS: int = 300
    CLASSES_TABLES_CATALOG_ENABLED: bool = False
    CLASSES_TABLES_CATALOG_PATH: str = "docs/dados/tabelas_classes_catalogo.json"

    # ── Rate Limiting ────────────────────────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    API_RATE_LIMIT_PER_MINUTE: int = 180
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 10
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Multi-jogo ───────────────────────────────────────────────────────────
    # Quando True, endpoints específicos do D&D 3.5 exigem `game_slug=dnd35`
    # no token. Quando False (padrão até a Fase 2 estabilizar), apenas registra
    # log sem bloquear — preserva tokens legados durante o rollout.
    MULTI_GAME_STRICT_MODE: bool = False
    # Frontend: permite auto-entrada no último jogo válido ao abrir o seletor.
    AUTO_ENTER_LAST_GAME: bool = True

    # Se True e a tabela `magias` estiver vazia, o startup executa `scripts/seed_magias.py`
    # (PHB completo — pode levar ~30s). Em SQLite vazio o seed roda sempre sem esta flag.
    SEED_MAGIAS_ON_EMPTY: bool = False
    # Controla se a API deve rodar Alembic também no startup da app.
    # Em produção (Render/Procfile), normalmente já roda antes de subir o uvicorn.
    STARTUP_RUN_ALEMBIC: bool = True

    # Catálogo de consumíveis (seed): em produção, se False, não sincroniza pergaminhos
    # (apenas poções/óleos). True = catálogo completo como em desenvolvimento.
    CONSUMIVEIS_SEED_PERGAMINHOS: bool = True

    class Config:
        """Configuração de leitura do Pydantic"""
        # Suporta execução tanto na raiz do repo quanto dentro de backend/
        env_file = (".env", "backend/.env")
        case_sensitive = True

    def __init__(self, **data):
        """Inicializa e valida configurações"""
        super().__init__(**data)
        if "STARTUP_RUN_ALEMBIC" not in os.environ and self.ENVIRONMENT == "production":
            # Em produção padrão seguro para evitar migração duplicada
            # quando o Procfile já executa `alembic upgrade head`.
            self.STARTUP_RUN_ALEMBIC = False
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
        # Resolve caminho relativo SQLite para absoluto baseado em BASE_DIR,
        # evitando apontamento ao diretório de trabalho quando iniciado fora do backend/.
        if self.DATABASE_URL.startswith("sqlite:///./"):
            db_file = self.DATABASE_URL[len("sqlite:///./"):]
            absolute = self.BASE_DIR / db_file
            self.DATABASE_URL = f"sqlite:///{absolute}"


# Instância global (singleton)
settings = Settings()