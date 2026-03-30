"""
main.py
SRP: Entry point da aplicação — orquestra inicialização e rotas
SOLID: Dependency Injection via contexto FastAPI
"""
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import logging
from sqlalchemy import inspect, text

from .core.config import settings
from .core.database import engine, Base, SessionLocal, get_db
from .core.init_db import criar_admin_padrao, inicializar_equipamentos, inicializar_talentos
from .core.rate_limit import RateLimitMiddleware
from .core.request_size import RequestSizeLimitMiddleware
from .api.v1 import combatentes, combate, condicoes, usuarios, auth, ataques, pericias, magias, magias_preparadas, equipamentos, talentos

# Importar models para criação de tabelas (ordem importa para ForeignKey)
from .models import usuario as usuario_model
from .models import equipamento as equipamento_model
from .models import talento as talento_model
from .models import combatente as combatente_model
from .models import combate as combate_model
from .models import condicao as condicao_model
from .models import combatente_condicao as pivot_model
from .models import ataque as ataque_model
from .models import pericia as pericia_model
from .models import magia as magia_model

logger = logging.getLogger(__name__)

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
# Origens vêm do .env (ALLOWED_ORIGINS) — nunca usar "*" com allow_credentials
_origins = settings.ALLOWED_ORIGINS
_allow_all = "*" in _origins

app.add_middleware(
    RequestSizeLimitMiddleware,
    max_request_size=settings.MAX_REQUEST_SIZE,
    max_json_body_size=settings.MAX_JSON_BODY_SIZE,
)

if settings.GZIP_ENABLED:
    app.add_middleware(
        GZipMiddleware,
        minimum_size=settings.GZIP_MINIMUM_SIZE,
    )
    logger.info("✅ GZip ativo: minimum_size=%s bytes", settings.GZIP_MINIMUM_SIZE)
else:
    logger.warning("⚠️  GZip desativado")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if not _allow_all else ["*"],
    allow_credentials=not _allow_all,  # credentials incompatível com wildcard
    allow_methods=["*"],
    allow_headers=[
        "Content-Type",
        "Authorization"
    ],
    expose_headers=["Content-Length"],
    max_age=600,
)

if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        api_limit_per_minute=settings.API_RATE_LIMIT_PER_MINUTE,
        login_limit_per_minute=settings.LOGIN_RATE_LIMIT_PER_MINUTE,
    )
    logger.info(
        "✅ Rate limiting ativo: api=%s/min, login=%s/min",
        settings.API_RATE_LIMIT_PER_MINUTE,
        settings.LOGIN_RATE_LIMIT_PER_MINUTE,
    )
else:
    logger.warning("⚠️  Rate limiting desativado")

logger.info(
    "✅ Request size limits ativos: request=%s bytes, json=%s bytes",
    settings.MAX_REQUEST_SIZE,
    settings.MAX_JSON_BODY_SIZE,
)

if _allow_all:
    logger.warning("⚠️  CORS com wildcard '*' — NÃO usar em produção!")
else:
    logger.info(f"✅ CORS configurado para: {_origins}")

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
# Ordem importa: dependências primeiro
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(usuarios.router, prefix=settings.API_V1_PREFIX)
app.include_router(combatentes.router, prefix=settings.API_V1_PREFIX)
app.include_router(combate.router, prefix=settings.API_V1_PREFIX)
app.include_router(condicoes.router, prefix=settings.API_V1_PREFIX)
app.include_router(ataques.router, prefix=settings.API_V1_PREFIX)
app.include_router(pericias.router, prefix=settings.API_V1_PREFIX)
app.include_router(magias.router, prefix=settings.API_V1_PREFIX)
app.include_router(magias_preparadas.router, prefix=settings.API_V1_PREFIX)
app.include_router(equipamentos.router, prefix=settings.API_V1_PREFIX)
app.include_router(talentos.router, prefix=settings.API_V1_PREFIX)

logger.info("✅ Rotas da API v1 registradas com sucesso")

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


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon quando disponível; evita 404 em desenvolvimento."""
    favicon_path = FRONTEND_DIR / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    return Response(status_code=204)


@app.get("/pericias")
async def pericias_page():
    """Tela de perícias do personagem."""
    return FileResponse(str(FRONTEND_DIR / "pages" / "pericias.html"))


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Verificar saúde da API."""
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "cors_enabled": True
    }


# ── Startup Event ────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """
    Inicializa aplicação:
    1. Cria admin padrão
    2. Popula combatentes iniciais
    3. Popula condições D&D
    4. Popula perícias D&D
    """
    db = SessionLocal()
    try:
        _inicializar_banco(db)
        logger.info("✅ Aplicação inicializada com sucesso")
        print("=" * 60)
        print("✅ API INICIADA COM SUCESSO")
        print("=" * 60)
    except Exception as e:
        logger.error(f"❌ Erro durante startup: {str(e)}")
        print(f"❌ Erro durante startup: {str(e)}")
        raise
    finally:
        db.close()


# ── Funções de Inicialização ─────────────────────────────────────────────────

def _inicializar_banco(db) -> None:
    """
    SRP: Orquestra a inicialização completa do banco.
    Ordem importa:
    1. Admin (dependência de tudo)
    2. Condições (globais)
    3. Perícias (globais)
    4. Equipamentos (globais)
    5. Combatentes (usam condições)

    Args:
        db: Sessão do banco
    """
    passos = [
        ("criar_tabelas", lambda: Base.metadata.create_all(bind=engine)),
        ("criar_admin_padrao", lambda: criar_admin_padrao(db)),
        ("garantir_coluna_dono_id", _garantir_coluna_dono_id),
        ("garantir_constraints_item_13", _garantir_constraints_item_13),
        ("seed_condicoes", lambda: _seed_condicoes(db)),
        ("inicializar_equipamentos", lambda: inicializar_equipamentos(db)),
        ("inicializar_talentos", lambda: inicializar_talentos(db)),
        ("seed_combatentes", lambda: _seed_combatentes(db)),
    ]

    for nome, callback in passos:
        _executar_passo_startup(nome, callback)


def _executar_passo_startup(nome: str, callback) -> None:
    """Executa um passo de startup com logging consistente e falha explícita."""
    logger.info("🔄 Startup step: %s", nome)
    try:
        callback()
        logger.info("✅ Startup step concluído: %s", nome)
    except Exception as exc:
        logger.exception("❌ Falha no passo de startup '%s'", nome)
        raise RuntimeError(f"Falha no startup em '{nome}': {exc}") from exc


def _garantir_coluna_dono_id() -> None:
    """Adiciona `combatentes.dono_id` em bases antigas quando a migração não foi aplicada."""
    inspector = inspect(engine)
    colunas = {col["name"] for col in inspector.get_columns("combatentes")}
    if "dono_id" in colunas:
        return

    logger.warning("⚠️  coluna combatentes.dono_id ausente; aplicando schema guard")
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE combatentes ADD COLUMN dono_id INTEGER"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_combatentes_dono_id ON combatentes (dono_id)"))

        owner_id = conn.execute(
            text(
                """
                SELECT id
                FROM usuarios
                WHERE perfil = 'administrador' AND ativo = 1
                ORDER BY id
                LIMIT 1
                """
            )
        ).scalar()

        if owner_id is None:
            owner_id = conn.execute(
                text("SELECT id FROM usuarios ORDER BY id LIMIT 1")
            ).scalar()

        if owner_id is not None:
            conn.execute(
                text("UPDATE combatentes SET dono_id = :owner_id WHERE dono_id IS NULL"),
                {"owner_id": owner_id},
            )


def _garantir_constraints_item_13() -> None:
    """Normaliza dados e garante unicidade para item #13 em bases existentes."""
    logger.info("🔧 Aplicando guard de integridade do item #13")
    with engine.begin() as conn:
        # Normaliza limites de HP
        conn.execute(text("UPDATE combatentes SET hp_maximo = 1 WHERE hp_maximo IS NULL OR hp_maximo <= 0"))
        conn.execute(text("UPDATE combatentes SET hp_atual = 0 WHERE hp_atual IS NULL OR hp_atual < 0"))
        conn.execute(text("UPDATE combatentes SET hp_atual = hp_maximo WHERE hp_atual > hp_maximo"))

        # Normaliza tipo para conjunto fechado permitido
        conn.execute(
            text(
                """
                UPDATE combatentes
                SET tipo = LOWER(COALESCE(tipo, 'npc'))
                WHERE tipo IS NULL OR LOWER(tipo) NOT IN ('jogador', 'monstro', 'npc')
                """
            )
        )

        # Remove duplicatas de magias preparadas mantendo o menor ID
        conn.execute(
            text(
                """
                DELETE FROM magias_preparadas
                WHERE id IN (
                    SELECT id FROM (
                        SELECT
                            id,
                            ROW_NUMBER() OVER (
                                PARTITION BY combatente_id, magia_id
                                ORDER BY id
                            ) AS rn
                        FROM magias_preparadas
                    ) t
                    WHERE t.rn > 1
                )
                """
            )
        )

        # SQLite/PostgreSQL: índice único para prevenir duplicatas futuras
        conn.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS uq_magias_preparadas_combatente_magia
                ON magias_preparadas (combatente_id, magia_id)
                """
            )
        )


def _seed_pericias(db) -> None:
    """
    Popula as perícias D&D 3.5 se não existirem.
    
    SRP: Apenas popula perícias
    
    Args:
        db: Sessão do banco
    """
    from .models.pericia import Pericia
    
    try:
        # Verificar se já existem perícias
        pericia_count = db.query(Pericia).count()
        if pericia_count > 0:
            logger.info(f"✅ {pericia_count} perícias já existem no banco")
            print(f"✅ {pericia_count} perícias já existem no banco de dados")
            return
        
        logger.info("🔄 Populando perícias D&D 3.5...")
        print("🔄 Populando banco de dados com perícias D&D 3.5...")
        
        # Lista completa de perícias D&D 3.5
        pericias_iniciais = [
            # ========== DESTREZA ==========
            {"nome": "Acrobacia", "descricao": "Equilibrar-se, saltar, cambalhotas.", "atributo": "DES", "tipo": "comum"},
            {"nome": "Abrir Fechaduras", "descricao": "Usar ferramentas de ladino.", "atributo": "DES", "tipo": "comum", "requer_treinamento": 1},
            {"nome": "Cavalgar", "descricao": "Controlar montarias.", "atributo": "DES", "tipo": "comum"},
            {"nome": "Esconder-se", "descricao": "Ficar fora de vista.", "atributo": "DES", "tipo": "comum"},
            {"nome": "Furtividade", "descricao": "Mover-se silenciosamente.", "atributo": "DES", "tipo": "comum"},
            {"nome": "Equilíbrio", "descricao": "Manter-se em pé em superfícies instáveis.", "atributo": "DES", "tipo": "comum"},
            {"nome": "Usar Cordas", "descricao": "Amarrar e soltar nós.", "atributo": "DES", "tipo": "comum"},
            
            # ========== FORÇA ==========
            {"nome": "Escalar", "descricao": "Subir paredes e obstáculos.", "atributo": "FOR", "tipo": "comum"},
            {"nome": "Natação", "descricao": "Nadar.", "atributo": "FOR", "tipo": "comum"},
            {"nome": "Saltar", "descricao": "Distância de salto.", "atributo": "FOR", "tipo": "comum"},
            
            # ========== INTELIGÊNCIA ==========
            {"nome": "Alquimia", "descricao": "Criar itens alquímicos.", "atributo": "INT", "tipo": "comum", "requer_treinamento": 1},
            {"nome": "Apreciar", "descricao": "Avaliar o valor de itens.", "atributo": "INT", "tipo": "comum"},
            {"nome": "Decifrar Escrita", "descricao": "Traduzir línguas antigas ou códigos.", "atributo": "INT", "tipo": "comum", "requer_treinamento": 1},
            {"nome": "Falsificação", "descricao": "Criar documentos falsos.", "atributo": "INT", "tipo": "comum"},
            {"nome": "Identificar Magia", "descricao": "Reconhecer efeitos mágicos.", "atributo": "INT", "tipo": "comum"},
            {"nome": "Operar Mecanismo", "descricao": "Desativar armadilhas ou dispositivos.", "atributo": "INT", "tipo": "comum", "requer_treinamento": 1},
            {"nome": "Pesquisa", "descricao": "Encontrar informações em bibliotecas.", "atributo": "INT", "tipo": "comum"},
            {"nome": "Procurar", "descricao": "Achar itens escondidos ou armadilhas.", "atributo": "INT", "tipo": "comum"},
            
            # ========== CONHECIMENTO (INT) ==========
            {"nome": "Conhecimento: Arcano", "descricao": "Magia, monstros mágicos.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
            {"nome": "Conhecimento: Arquitetura", "descricao": "Construções e engenharia.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
            {"nome": "Conhecimento: Geografia", "descricao": "Terras, climas.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
            {"nome": "Conhecimento: História", "descricao": "Eventos passados.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
            {"nome": "Conhecimento: Local", "descricao": "Notícias, fofocas.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
            {"nome": "Conhecimento: Natureza", "descricao": "Animais, plantas, clima.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
            {"nome": "Conhecimento: Nobreza", "descricao": "Linhas de sangue, títulos.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
            {"nome": "Conhecimento: Plano", "descricao": "Outras dimensões.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
            {"nome": "Conhecimento: Religião", "descricao": "Divindades, ritos.", "atributo": "INT", "tipo": "conhecimento", "requer_treinamento": 1},
            
            # ========== SABEDORIA ==========
            {"nome": "Cura", "descricao": "Tratar ferimentos e doenças.", "atributo": "SAB", "tipo": "comum"},
            {"nome": "Intuição", "descricao": "Perceber mentiras e intenções.", "atributo": "SAB", "tipo": "comum"},
            {"nome": "Navegação", "descricao": "Orientar-se.", "atributo": "SAB", "tipo": "comum"},
            {"nome": "Ouvir", "descricao": "Detectar sons.", "atributo": "SAB", "tipo": "comum"},
            {"nome": "Sobrevivência", "descricao": "Rastrear e viver na natureza.", "atributo": "SAB", "tipo": "comum"},
            {"nome": "Profissão", "descricao": "Ofício específico.", "atributo": "SAB", "tipo": "profissao"},
            
            # ========== CARISMA ==========
            {"nome": "Adestrar Animais", "descricao": "Treinar e controlar animais.", "atributo": "CAR", "tipo": "comum", "requer_treinamento": 1},
            {"nome": "Atuação", "descricao": "Canto, dança, oratória, instrumentos.", "atributo": "CAR", "tipo": "performance"},
            {"nome": "Diplomacia", "descricao": "Negociar e influenciar.", "atributo": "CAR", "tipo": "comum"},
            {"nome": "Disfarce", "descricao": "Mudar a aparência.", "atributo": "CAR", "tipo": "comum"},
            {"nome": "Intimidação", "descricao": "Ameaçar e coagir.", "atributo": "CAR", "tipo": "comum"},
            {"nome": "Uso de Dispositivos Mágicos", "descricao": "Usar itens de classes diferentes.", "atributo": "CAR", "tipo": "comum", "requer_treinamento": 1},
        ]
        
        # Inserir perícias
        for pericia_data in pericias_iniciais:
            pericia = Pericia(**pericia_data)
            db.add(pericia)
        
        db.commit()
        logger.info(f"✅ {len(pericias_iniciais)} perícias D&D 3.5 inseridas com sucesso")
        print(f"✅ {len(pericias_iniciais)} perícias D&D 3.5 inseridas com sucesso!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao popular perícias: {str(e)}")
        print(f"❌ Erro ao popular perícias: {str(e)}")
        raise


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
        logger.info(f"✅ {repo.count()} combatentes já existem no banco")
        print(f"✅ {repo.count()} combatentes já existem no banco de dados")
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

    service.inicializar_seed()
    logger.info("✅ Seed de condições D&D verificado")
    print("✅ Seed de condições D&D verificado/executado com sucesso!")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )