"""
main.py
SRP: Entry point da aplicação — orquestra inicialização e rotas
SOLID: Dependency Injection via contexto FastAPI
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from .core.config import settings
from .core.database import engine, Base, SessionLocal
from .core.init_db import criar_admin_padrao
from .api.v1 import combatentes, combate, condicoes, usuarios, auth, ataques

# Importar models para criação de tabelas (ordem importa para ForeignKey)
from .models import usuario as usuario_model
from .models import combatente as combatente_model
from .models import combate as combate_model
from .models import condicao as condicao_model
from .models import combatente_condicao as pivot_model
from .models import ataque as ataque_model

logger = logging.getLogger(__name__)

# ── Criar tabelas ────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Instância FastAPI ────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para gerenciamento de combates TTRPG",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ── Middleware CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
UPLOADS_DIR = settings.UPLOADS_DIR

# ── Static Files ─────────────────────────────────────────────────────────────
if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
    app.mount("/pages", StaticFiles(directory=str(FRONTEND_DIR / "pages")), name="pages")
    logger.info(f"✅ Frontend montado em: {FRONTEND_DIR}")
else:
    logger.warning(f"⚠️  Frontend não encontrado em: {FRONTEND_DIR}")

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# ── Rotas da API v1 ──────────────────────────────────────────────────────────
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(usuarios.router, prefix=settings.API_V1_PREFIX)
app.include_router(combatentes.router, prefix=settings.API_V1_PREFIX)
app.include_router(combate.router, prefix=settings.API_V1_PREFIX)
app.include_router(condicoes.router, prefix=settings.API_V1_PREFIX)
app.include_router(ataques.router, prefix=settings.API_V1_PREFIX)

# ── Rotas Frontend ───────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Raiz redireciona para login."""
    return FileResponse(str(FRONTEND_DIR / "pages" / "login.html"))


@app.get("/dashboard")
async def dashboard():
    """Dashboard após autenticação."""
    return FileResponse(str(FRONTEND_DIR / "pages" / "dashboard.html"))


@app.get("/arena")
async def arena():
    """Tela da arena de combate."""
    return FileResponse(str(FRONTEND_DIR / "index.html"))


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Verificar saúde da API."""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }


# ── Startup Event ────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """
    Inicializa aplicação:
    1. Cria admin padrão
    2. Popula combatentes iniciais
    3. Popula condições D&D
    """
    db = SessionLocal()
    try:
        _inicializar_banco(db)
        logger.info("✅ Aplicação inicializada com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro durante startup: {str(e)}")
        raise
    finally:
        db.close()


# ── Funções de Inicialização ─────────────────────────────────────────────────

def _inicializar_banco(db) -> None:
    """
    SRP: Orquestra a inicialização completa do banco.

    Args:
        db: Sessão do banco
    """
    criar_admin_padrao(db)
    _seed_combatentes(db)
    _seed_condicoes(db)


def _seed_combatentes(db) -> None:
    """
    Popula combatentes iniciais se o banco estiver vazio.

    Args:
        db: Sessão do banco
    """
    from .repositories.combatente_repository import CombatenteRepository
    from .models.combatente import Combatente

    repo = CombatenteRepository(db)
    if repo.count() > 0:
        return

    logger.info("🔄 Populando combatentes iniciais...")
    print("🔄 Populando banco de dados com combatentes iniciais...")

    combatentes_iniciais = [
        {
            "nome": "Theron",
            "tipo": "jogador",
            "classe": "Guerreiro",
            "hp_maximo": 85,
            "hp_atual": 85,
            "iniciativa": 15,
            "forca": 16,
            "destreza": 12,
            "constituicao": 14,
            "inteligencia": 10,
            "sabedoria": 11,
            "carisma": 13,
            "nivel": 5,
            "pontos": 1200,
        },
        {
            "nome": "Lyra",
            "tipo": "jogador",
            "classe": "Mago",
            "hp_maximo": 45,
            "hp_atual": 45,
            "iniciativa": 18,
            "forca": 8,
            "destreza": 14,
            "constituicao": 10,
            "inteligencia": 18,
            "sabedoria": 15,
            "carisma": 12,
            "nivel": 5,
            "pontos": 1150,
        },
        {
            "nome": "Garrick",
            "tipo": "jogador",
            "classe": "Clérigo",
            "hp_maximo": 65,
            "hp_atual": 65,
            "iniciativa": 12,
            "forca": 14,
            "destreza": 10,
            "constituicao": 13,
            "inteligencia": 12,
            "sabedoria": 16,
            "carisma": 14,
            "nivel": 5,
            "pontos": 980,
        },
        {
            "nome": "Zara",
            "tipo": "jogador",
            "classe": "Ladino",
            "hp_maximo": 55,
            "hp_atual": 55,
            "iniciativa": 20,
            "forca": 10,
            "destreza": 18,
            "constituicao": 12,
            "inteligencia": 14,
            "sabedoria": 13,
            "carisma": 15,
            "nivel": 5,
            "pontos": 1350,
        },
        {
            "nome": "Goblin Arqueiro",
            "tipo": "monstro",
            "classe": "Arqueiro",
            "hp_maximo": 30,
            "hp_atual": 30,
            "iniciativa": 14,
            "forca": 8,
            "destreza": 14,
            "constituicao": 10,
            "inteligencia": 10,
            "sabedoria": 8,
            "carisma": 8,
            "nivel": 2,
            "pontos": 0,
        },
        {
            "nome": "Orc Guerreiro",
            "tipo": "monstro",
            "classe": "Guerreiro",
            "hp_maximo": 60,
            "hp_atual": 60,
            "iniciativa": 10,
            "forca": 16,
            "destreza": 12,
            "constituicao": 16,
            "inteligencia": 7,
            "sabedoria": 11,
            "carisma": 10,
            "nivel": 3,
            "pontos": 0,
        },
    ]

    for data in combatentes_iniciais:
        repo.create(Combatente(**data))

    logger.info("✅ Combatentes iniciais inseridos")
    print("✅ Combatentes iniciais inseridos com sucesso!")


def _seed_condicoes(db) -> None:
    """
    Popula as 25 condições D&D se não existirem.

    Args:
        db: Sessão do banco
    """
    from .repositories.condicao_repository import CondicaoRepository
    from .services.condicao_service import CondicaoService

    repo = CondicaoRepository(db)
    service = CondicaoService(condicao_repository=repo, combatente_repository=None)

    try:
        service.inicializar_seed()
        logger.info("✅ Seed de condições D&D verificado")
        print("✅ Seed de condições D&D verificado/executado com sucesso!")
    except Exception as e:
        logger.warning(f"⚠️  Erro ao popular condições: {str(e)}")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )