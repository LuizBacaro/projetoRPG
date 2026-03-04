"""
Entry Point da Aplicação
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from .core.config import settings
from .core.database import engine, Base, SessionLocal
from .api.v1 import combatentes, combate, condicoes, usuarios

# Importar models para criar tabelas (ordem importa para FK)
from .models import usuario as usuario_model
from .models import combatente as combatente_model
from .models import combate as combate_model
from .models import condicao as condicao_model
from .models import combatente_condicao as pivot_model

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para gerenciamento de combates TTRPG"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir caminhos
BASE_DIR     = Path(__file__).resolve().parent.parent  # backend/
FRONTEND_DIR = BASE_DIR.parent / "frontend"            # projetoRPG/frontend
UPLOADS_DIR  = BASE_DIR / "uploads"

# Criar diretório de uploads se não existir
UPLOADS_DIR.mkdir(exist_ok=True)

# Montar arquivos estáticos
if FRONTEND_DIR.exists():
    app.mount("/css",    StaticFiles(directory=str(FRONTEND_DIR / "css")),    name="css")
    app.mount("/js",     StaticFiles(directory=str(FRONTEND_DIR / "js")),     name="js")
    app.mount("/pages",  StaticFiles(directory=str(FRONTEND_DIR / "pages")),  name="pages")
    print(f"✅ Frontend montado em: {FRONTEND_DIR}")
else:
    print(f"⚠️  Frontend não encontrado em: {FRONTEND_DIR}")

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Incluir routers
app.include_router(usuarios.router,    prefix=settings.API_V1_PREFIX)  
app.include_router(combatentes.router, prefix=settings.API_V1_PREFIX)
app.include_router(combate.router,     prefix=settings.API_V1_PREFIX)
app.include_router(condicoes.router,   prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Redireciona para o frontend"""
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/frontend/{file_path:path}")
async def serve_frontend(file_path: str):
    """Serve arquivos do frontend"""
    file = FRONTEND_DIR / file_path
    if file.exists() and file.is_file():
        return FileResponse(file)
    return {"error": "File not found"}


@app.on_event("startup")
async def startup_event():
    """
    Evento de inicialização da aplicação.
    Responsabilidades:
      1. Popular combatentes iniciais (se banco vazio)
      2. Seed das 25 condições D&D (idempotente)
    """
    db = SessionLocal()
    try:
        _seed_combatentes(db)
        _seed_condicoes(db)
    finally:
        db.close()


# ── Helpers de seed ────────────────────────────────────────────────────────────

def _seed_combatentes(db) -> None:
    """Popula combatentes iniciais se o banco estiver vazio."""
    from .repositories.combatente_repository import CombatenteRepository
    from .models.combatente import Combatente

    repo = CombatenteRepository(db)
    if repo.count() > 0:
        return

    print("🔄 Populando banco de dados com combatentes iniciais...")

    combatentes_iniciais = [
        {
            "nome": "Theron", "tipo": "jogador", "classe": "Guerreiro",
            "hp_maximo": 85, "hp_atual": 85, "iniciativa": 15,
            "forca": 16, "destreza": 12, "constituicao": 14,
            "inteligencia": 10, "sabedoria": 11, "carisma": 13,
            "nivel": 5, "pontos": 1200
        },
        {
            "nome": "Lyra", "tipo": "jogador", "classe": "Mago",
            "hp_maximo": 45, "hp_atual": 45, "iniciativa": 18,
            "forca": 8, "destreza": 14, "constituicao": 10,
            "inteligencia": 18, "sabedoria": 15, "carisma": 12,
            "nivel": 5, "pontos": 1150
        },
        {
            "nome": "Garrick", "tipo": "jogador", "classe": "Clérigo",
            "hp_maximo": 65, "hp_atual": 65, "iniciativa": 12,
            "forca": 14, "destreza": 10, "constituicao": 13,
            "inteligencia": 12, "sabedoria": 16, "carisma": 14,
            "nivel": 5, "pontos": 980
        },
        {
            "nome": "Zara", "tipo": "jogador", "classe": "Ladino",
            "hp_maximo": 55, "hp_atual": 55, "iniciativa": 20,
            "forca": 10, "destreza": 18, "constituicao": 12,
            "inteligencia": 14, "sabedoria": 13, "carisma": 15,
            "nivel": 5, "pontos": 1350
        },
        {
            "nome": "Goblin Arqueiro", "tipo": "monstro", "classe": "Arqueiro",
            "hp_maximo": 30, "hp_atual": 30, "iniciativa": 14,
            "forca": 8, "destreza": 14, "constituicao": 10,
            "inteligencia": 10, "sabedoria": 8, "carisma": 8,
            "nivel": 2, "pontos": 0
        },
        {
            "nome": "Orc Guerreiro", "tipo": "monstro", "classe": "Guerreiro",
            "hp_maximo": 60, "hp_atual": 60, "iniciativa": 10,
            "forca": 16, "destreza": 12, "constituicao": 16,
            "inteligencia": 7, "sabedoria": 11, "carisma": 10,
            "nivel": 3, "pontos": 0
        },
    ]

    for data in combatentes_iniciais:
        repo.create(Combatente(**data))

    print("✅ Combatentes iniciais inseridos com sucesso!")


def _seed_condicoes(db) -> None:
    """
    Popula as 25 condições D&D 3.5 se a tabela estiver vazia.
    Idempotente — seguro de chamar sempre no startup.
    """
    from .repositories.condicao_repository import CondicaoRepository
    from .services.condicao_service import CondicaoService

    repo    = CondicaoRepository(db)
    service = CondicaoService(
        condicao_repository=repo,
        combatente_repository=None   # não necessário para seed
    )
    service.inicializar_seed()
    print("✅ Seed de condições D&D verificado/executado com sucesso!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)