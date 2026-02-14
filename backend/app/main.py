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
from .api.v1 import combatentes, combate

# Importar models para criar tabelas
from .models import combatente as combatente_model
from .models import combate as combate_model

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

# Definir caminhos corretos
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
FRONTEND_DIR = BASE_DIR.parent / "frontend"  # projetoRPG/frontend
UPLOADS_DIR = BASE_DIR / "uploads"

# Criar diretório de uploads se não existir
UPLOADS_DIR.mkdir(exist_ok=True)

# Montar arquivos estáticos
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    print(f"✅ Frontend montado em: {FRONTEND_DIR}")
else:
    print(f"⚠️  Frontend não encontrado em: {FRONTEND_DIR}")

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Incluir routers
app.include_router(combatentes.router, prefix=settings.API_V1_PREFIX)
app.include_router(combate.router, prefix=settings.API_V1_PREFIX)


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
    """Evento de inicialização da aplicação"""
    from .repositories.combatente_repository import CombatenteRepository
    from .models.combatente import Combatente
    
    db = SessionLocal()
    try:
        repo = CombatenteRepository(db)
        
        # Popular banco se estiver vazio
        if repo.count() == 0:
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
                combatente = Combatente(**data)
                repo.create(combatente)
            
            print("✅ Banco de dados populado com sucesso!")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)