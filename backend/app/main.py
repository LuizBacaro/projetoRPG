"""
main.py
SRP: Entry point da aplicação — orquestra inicialização e rotas
SOLID: Dependency Injection via contexto FastAPI
"""

import asyncio
import logging
import os
import threading
import unicodedata
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    SQLAlchemyError,
    StatementError,
)

from .games.dnd35.api.v1 import armaduras_protecao as dnd35_armaduras_protecao
from .games.dnd35.api.v1 import ataques as dnd35_ataques
from .games.dnd35.api.v1 import campanhas as dnd35_campanhas
from .games.dnd35.api.v1 import combate as dnd35_combate
from .games.dnd35.api.v1 import combatentes as dnd35_combatentes
from .games.dnd35.api.v1 import condicoes as dnd35_condicoes
from .games.dnd35.api.v1 import consumiveis as dnd35_consumiveis
from .games.dnd35.api.v1 import divindades_custom as dnd35_divindades_custom
from .games.dnd35.api.v1 import equipamentos as dnd35_equipamentos
from .games.dnd35.api.v1 import grimorio as dnd35_grimorio
from .games.dnd35.api.v1 import habilidades_especiais as dnd35_habilidades_especiais
from .games.dnd35.api.v1 import magias as dnd35_magias
from .games.dnd35.api.v1 import magias_preparadas as dnd35_magias_preparadas
from .games.dnd35.api.v1 import pericias as dnd35_pericias
from .games.dnd35.api.v1 import racas as dnd35_racas
from .games.dnd35.api.v1 import tabelas_classes as dnd35_tabelas_classes
from .games.dnd35.api.v1 import talentos as dnd35_talentos
from .games.dnd35.legacy_membership import (
    garantir_membership_dnd35_para_usuarios_legados,
)
from .games.dnd35.models import armadura_protecao as armadura_protecao_model
from .games.dnd35.models import ataque as ataque_model
from .games.dnd35.models import campanha as campanha_model
from .games.dnd35.models import combate as combate_model
from .games.dnd35.models import combatente as combatente_model
from .games.dnd35.models import combatente_condicao as pivot_model
from .games.dnd35.models import condicao as condicao_model
from .games.dnd35.models import consumivel as consumivel_model
from .games.dnd35.models import equipamento as equipamento_model
from .games.dnd35.models import grimorio as grimorio_model
from .games.dnd35.models import magia as magia_model
from .games.dnd35.models import pericia as pericia_model
from .games.dnd35.models import sessao_campanha as sessao_campanha_model
from .games.dnd35.models import talento as talento_model
from .games.dnd35.startup_seeds import (
    inicializar_catalogo_magias_se_vazio,
    inicializar_catalogo_tabelas_classes,
    inicializar_consumiveis,
    inicializar_equipamentos,
    inicializar_talentos,
)
from .games.dnd35.sync_progressao_combatentes import (
    sincronizar_bonus_base_ataque_combatentes,
)
from .games.gurps.api.v1 import campanhas as gurps_campanhas
from .games.gurps.api.v1 import combate as gurps_combate
from .games.gurps.api.v1 import personagens as gurps_personagens
from .games.gurps.api.v1 import rolagens as gurps_rolagens
from .games.gurps.models import campanha as gurps_campanha_model
from .games.gurps.models import combate as gurps_combate_model
from .games.gurps.models import personagem as gurps_personagem_model
from .shared.api.v1 import auth, games, usuarios
from .shared.core.config import settings
from .shared.core.database import Base, SessionLocal, engine, get_db
from .shared.core.rate_limit import RateLimitMiddleware
from .shared.core.request_size import RequestSizeLimitMiddleware
from .shared.exceptions.custom_exceptions import ArenaBaseException

# Importar models para criação de tabelas (ordem importa para ForeignKey)
from .shared.models import game as game_model
from .shared.models import usuario as usuario_model
from .shared.startup.admin_default import criar_admin_padrao
from .shared.startup.game_catalog import inicializar_catalogo_jogos

logger = logging.getLogger(__name__)
CRON_PING_TOKEN = os.getenv("CRON_PING_TOKEN", "").strip()

# Inicialização pesada do BD (Alembic + seeds). Em production corre em background
# para o Render não dar timeout no deploy (health check antes do fim do startup).
_db_startup_done = threading.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Inicializa aplicação (migrations, seeds, admin).

    Em **production** o trabalho corre em thread via `asyncio.to_thread` para o
    processo aceitar conexões de imediato — configure no Render o health check
    em `/health/live`. Em development mantém-se síncrono (comportamento anterior).
    """

    def _run_init_sync() -> None:
        db = SessionLocal()
        try:
            _inicializar_banco_critico(db)
            _db_startup_done.set()
            _inicializar_banco_pos_ready(db)
        finally:
            db.close()

    async def _run_init_async() -> None:
        await asyncio.to_thread(_run_init_sync)

    try:
        if settings.ENVIRONMENT == "production":

            def _log_task_fail(t: asyncio.Task) -> None:
                try:
                    exc = t.exception()
                except asyncio.CancelledError:
                    return
                if exc is not None:
                    logger.exception(
                        "❌ Falha na inicialização do banco (background): %s", exc
                    )

            task = asyncio.create_task(_run_init_async())
            task.add_done_callback(_log_task_fail)
            await asyncio.sleep(0)  # dá ao loop uma oportunidade de arrancar a task
            logger.info(
                "Startup production: init crítico em background e pós-ready assíncrono — "
                "health check no Render: /health/live; /api libera após fase crítica."
            )
            print("=" * 60)
            print("✅ API A ACEITAR TRÁFEGO — fase crítica do BD em progresso")
            print("=" * 60)
        else:
            await _run_init_async()
            logger.info("✅ Aplicação inicializada com sucesso")
            print("=" * 60)
            print("✅ API INICIADA COM SUCESSO")
            print("=" * 60)
    except Exception as e:
        logger.error("❌ Erro durante startup: %s", e)
        print(f"❌ Erro durante startup: {str(e)}")
        raise

    yield


# ── Instância FastAPI ────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para gerenciamento de combates TTRPG",
    openapi_url="/api/openapi.json" if settings.ENVIRONMENT != "production" else None,
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)


@app.middleware("http")
async def _readiness_middleware(request: Request, call_next):
    """
    Em production, /api/* fica 503 até a fase crítica de startup concluir.
    OPTIONS passa (CORS preflight). /health/live e /health/ping não passam por /api.

    Também captura qualquer exceção não tratada e devolve um JSON 500
    (em vez de deixar o `ServerErrorMiddleware` do Starlette responder por
    fora do CORS). Sem isto, o navegador receberia a resposta sem o header
    `Access-Control-Allow-Origin` e mostraria apenas "Failed to fetch".
    """
    if settings.ENVIRONMENT == "production" and not _db_startup_done.is_set():
        path = request.url.path or ""
        if path.startswith("/api") and request.method != "OPTIONS":
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Inicialização do banco em curso; tente em instantes."
                },
            )

    try:
        return await call_next(request)
    except HTTPException:
        # Re-levanta — FastAPI/Starlette já tem handler para HTTPException
        # com CORS dentro do escopo de ExceptionMiddleware.
        raise
    except Exception:
        logger.exception(
            "Exceção não tratada em %s %s — convertendo em 500 JSON com CORS",
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Erro interno do servidor. Veja os logs para diagnóstico."
            },
        )


# ── Exception Handlers globais ────────────────────────────────────────────────
# Garante que erros previsíveis (constraint do banco, falha de conexão, regra
# de negócio) sempre voltem como JSON 4xx/5xx — passando pelo CORSMiddleware.
# Sem isso, um IntegrityError não tratado pode chegar ao Render como 500 sem
# `Access-Control-Allow-Origin`, e o navegador mostra apenas "Failed to fetch".


@app.exception_handler(ArenaBaseException)
async def _handle_arena_exception(
    request: Request, exc: ArenaBaseException
) -> JSONResponse:
    """Erro de regra de negócio → respeita o status_code definido pela exceção."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(StatementError)
async def _handle_statement_error(
    request: Request, exc: StatementError
) -> JSONResponse:
    """Erros SQLAlchemy envolvendo o statement (ex.: IntegrityError em `.orig`)."""
    orig = getattr(exc, "orig", None)
    if isinstance(orig, IntegrityError):
        return await _handle_integrity_error(request, orig)  # type: ignore[misc]
    logger.exception("StatementError em %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro ao executar operação no banco. Veja os logs do servidor."
        },
    )


@app.exception_handler(IntegrityError)
async def _handle_integrity_error(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Violação de constraint (CHECK / UNIQUE / FK) → 409 com detalhe seguro.

    Evita 500 sem CORS quando algum dado bate em uma constraint legada (ex.: a
    constraint `ck_combatentes_hp_atual_non_negative` que sobreviveu em bancos
    onde a migration `d5f9a2c1b8e7` rodou em SQLite no-op).
    """
    detalhe_bruto = str(getattr(exc, "orig", exc))
    logger.warning(
        "[%s] IntegrityError em %s %s: %s",
        request.client.host if request.client else "?",
        request.method,
        request.url.path,
        detalhe_bruto[:300],
    )
    detalhe_publico = "Violação de regra de integridade do banco. Tente novamente; se persistir, contate o suporte."
    if "ck_combatentes_hp_atual_non_negative" in detalhe_bruto:
        detalhe_publico = (
            "O servidor ainda tem uma regra antiga que impede HP negativo. "
            "Atualize/redeploy do backend para aplicar a migration mais recente."
        )
    return JSONResponse(
        status_code=409,
        content={"detail": detalhe_publico},
    )


@app.exception_handler(OperationalError)
async def _handle_operational_error(
    request: Request, exc: OperationalError
) -> JSONResponse:
    """Falha de conexão/operação no banco → 503 (não derruba CORS)."""
    detalhe = str(getattr(exc, "orig", exc))
    logger.error(
        "OperationalError em %s %s: %s",
        request.method,
        request.url.path,
        detalhe[:300],
        exc_info=True,
    )
    return JSONResponse(
        status_code=503,
        content={"detail": "Banco indisponível no momento. Tente em instantes."},
    )


@app.exception_handler(SQLAlchemyError)
async def _handle_sqlalchemy_error(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Outras falhas SQLAlchemy → 500 controlado, mas com CORS."""
    logger.exception(
        "SQLAlchemyError em %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno ao acessar o banco. Veja os logs do servidor."
        },
    )


@app.exception_handler(Exception)
async def _handle_uncaught_exception(request: Request, exc: Exception) -> JSONResponse:
    """Última linha de defesa: garante JSON com CORS em qualquer falha não prevista.

    Sem este handler, exceções desconhecidas viram 500 do Starlette
    em texto plano, e em alguns proxies (Render) podem chegar ao
    navegador sem o header `Access-Control-Allow-Origin`, gerando
    apenas "TypeError: Failed to fetch" no console.
    """
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=dict(exc.headers or {}),
        )
    logger.exception(
        "Exceção não tratada em %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Veja os logs para diagnóstico."},
    )


# ── Middleware CORS / limite / gzip / rate limit ─────────────────────────────
# Origens vêm do .env (ALLOWED_ORIGINS) — nunca usar "*" com allow_credentials
#
# Ordem (último add_middleware = mais externo na pilha Starlette):
#   CORS → RateLimit → GZip → RequestSize → … → app
# Assim, respostas geradas *sem* passar pelo restante da pilha (ex.: 429 do
# RateLimitMiddleware que retorna JSON sem `call_next`) ainda passam pelo
# CORSMiddleware e recebem `Access-Control-Allow-Origin` — evita "Failed to
# fetch" no browser por falta de CORS em erros 4xx/5xx.
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if not _allow_all else ["*"],
    allow_credentials=not _allow_all,  # credentials incompatível com wildcard
    allow_methods=["*"],
    # Incluir If-Match: a Arena envia em POST de combate; sem isto o preflight CORS falha (400) em produção.
    allow_headers=[
        "Content-Type",
        "Authorization",
        "If-Match",
        "If-None-Match",
    ],
    expose_headers=["Content-Length"],
    max_age=600,
)

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
DND35_FRONTEND_DIR = FRONTEND_DIR / "games" / "dnd35"
UPLOADS_DIR = settings.UPLOADS_DIR

# ── Static Files ─────────────────────────────────────────────────────────────
if FRONTEND_DIR.exists():
    if DND35_FRONTEND_DIR.is_dir():
        app.mount(
            "/games/dnd35",
            StaticFiles(directory=str(DND35_FRONTEND_DIR)),
            name="dnd35_frontend",
        )
        logger.info("✅ Frontend D&D 3.5 montado em: %s", DND35_FRONTEND_DIR)
    else:
        logger.warning("⚠️  Pasta D&D 3.5 ausente: %s", DND35_FRONTEND_DIR)
    # Cascas "em breve" dos outros jogos (seletor → /games/<slug>/em-breve.html)
    for _slug in ("gurps", "dnd5e"):
        _game_dir = FRONTEND_DIR / "games" / _slug
        if _game_dir.is_dir():
            app.mount(
                f"/games/{_slug}",
                StaticFiles(directory=str(_game_dir)),
                name=f"{_slug}_frontend",
            )
            logger.info("✅ Frontend %s montado em: %s", _slug, _game_dir)
    # Shell global (login, seletor de jogo, redirects legados /pages/*.html)
    app.mount(
        "/pages", StaticFiles(directory=str(FRONTEND_DIR / "pages")), name="pages"
    )
    _js_dir = FRONTEND_DIR / "js"
    if _js_dir.is_dir():
        app.mount("/js", StaticFiles(directory=str(_js_dir)), name="frontend_js")
        logger.info("✅ JS estático montado em /js → %s", _js_dir)
    _assets_dir = FRONTEND_DIR / "assets"
    if _assets_dir.is_dir():
        app.mount(
            "/assets", StaticFiles(directory=str(_assets_dir)), name="frontend_assets"
        )
        logger.info("✅ Assets estáticos montados em /assets → %s", _assets_dir)
    logger.info(f"✅ Frontend raiz: {FRONTEND_DIR}")
else:
    logger.warning(f"⚠️  Frontend não encontrado em: {FRONTEND_DIR}")

app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# ── Rotas da API v1 ──────────────────────────────────────────────────────────
# Ordem importa: dependências primeiro
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(games.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_campanhas.router, prefix=settings.API_V1_PREFIX)
app.include_router(usuarios.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_combatentes.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_combate.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_condicoes.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_ataques.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_pericias.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_magias.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_divindades_custom.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_magias_preparadas.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_grimorio.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_equipamentos.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_consumiveis.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_armaduras_protecao.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_talentos.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_tabelas_classes.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_racas.router, prefix=settings.API_V1_PREFIX)
app.include_router(dnd35_habilidades_especiais.router, prefix=settings.API_V1_PREFIX)
app.include_router(gurps_personagens.router, prefix=settings.API_V1_PREFIX)
app.include_router(gurps_campanhas.router, prefix=settings.API_V1_PREFIX)
app.include_router(gurps_combate.router, prefix=settings.API_V1_PREFIX)
app.include_router(gurps_rolagens.router, prefix=settings.API_V1_PREFIX)

logger.info("✅ Rotas da API v1 registradas com sucesso")

# ── Rotas Frontend ───────────────────────────────────────────────────────────


@app.get("/")
async def root():
    """Raiz redireciona para login."""
    return FileResponse(str(FRONTEND_DIR / "pages" / "login.html"))


@app.get("/selecionar-jogo")
async def selecionar_jogo():
    """Seletor de jogo pós-autenticação (Auth Hub)."""
    return FileResponse(str(FRONTEND_DIR / "pages" / "selecionar-jogo.html"))


@app.get("/dashboard")
async def dashboard():
    """Dashboard após autenticação."""
    return FileResponse(str(DND35_FRONTEND_DIR / "pages" / "dashboard.html"))


@app.get("/arena")
async def arena():
    """Tela da arena de combate."""
    return FileResponse(str(DND35_FRONTEND_DIR / "arena.html"))


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
    return FileResponse(str(DND35_FRONTEND_DIR / "pages" / "pericias.html"))


# ── Health Check ─────────────────────────────────────────────────────────────


@app.get("/health/live", include_in_schema=False)
async def health_live():
    """
    Liveness sem I/O: use como **Health Check Path** no Render para evitar timeout
    no deploy enquanto migrations/seeds correm em background (production).
    """
    return {"status": "live"}


@app.get("/health")
async def health():
    """Verificar saúde da API e conectividade com o banco."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        logger.error("Health check falhou na conexão com banco: %s", exc)
        db_status = "error"
    finally:
        db.close()
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "cors_enabled": True,
    }


@app.get("/health/ping", include_in_schema=False)
async def health_ping(token: str | None = Query(default=None)):
    """
    Endpoint leve para cron externo.
    - Não acessa banco
    - Retorna 204 (sem body)
    - Se CRON_PING_TOKEN estiver configurado, exige ?token=...
    """
    if CRON_PING_TOKEN and token != CRON_PING_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    return Response(status_code=204)


# ── Funções de Inicialização ─────────────────────────────────────────────────


def _obter_revisoes_alembic_atuais() -> list[str]:
    """
    Lê os valores atuais de alembic_version no banco.
    Retorna uma lista de revisões; se a tabela não existir, retorna lista vazia.
    """
    try:
        with engine.connect() as conn:
            resultado = conn.execute(text("SELECT version_num FROM alembic_version"))
            return [row[0] for row in resultado.fetchall()]
    except Exception:
        return []


def _revisao_e_ancestral(script, ancestor: str, descendant: str) -> bool:
    """Verifica se 'ancestor' é ancestral de 'descendant' no grafo Alembic."""
    if ancestor == descendant:
        return True

    visitadas = set()
    pilha = [descendant]

    while pilha:
        atual = pilha.pop()
        if atual in visitadas:
            continue
        visitadas.add(atual)

        rev_obj = script.get_revision(atual)
        if not rev_obj:
            continue

        down_rev = rev_obj.down_revision
        if down_rev is None:
            continue

        if isinstance(down_rev, tuple):
            pilha.extend([rev for rev in down_rev if rev is not None])
        else:
            pilha.append(down_rev)

        if ancestor in visitadas:
            return True

    return False


def _normalizar_alembic_multilinha(cfg, command) -> None:
    """
    Detecta múltiplas linhas em alembic_version e, se seguro, normaliza para o head.
    """
    revisoes = _obter_revisoes_alembic_atuais()
    if len(revisoes) <= 1:
        return

    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    if len(heads) != 1:
        raise RuntimeError(
            "Estado Alembic com várias cabeças no repositório. "
            f"Heads detectados: {heads}."
        )

    head = heads[0]
    if not all(_revisao_e_ancestral(script, rev, head) for rev in revisoes):
        raise RuntimeError(
            "Não foi possível normalizar o estado Alembic com várias revisões atuais. "
            f"Revisões atuais: {revisoes}."
        )

    logger.warning(
        "⚠️  Detectado estado Alembic multi-head em alembic_version: %s",
        revisoes,
    )
    command.stamp(cfg, head)
    logger.warning("✅ Alembic normalizado para head: %s", head)


def _executar_alembic_migrations() -> None:
    """
    Executa as migrations do Alembic automaticamente no startup.
    SRP: Garante que o schema esteja sempre atualizado.

    Quando este passo roda, o schema deve vir **só** do Alembic (não use
    `create_all` antes): senão tabelas novas existem sem `alembic_version` alinhado
    e o próximo `upgrade` tenta `CREATE TABLE` de novo (ex.: gurps_campanhas).

    Em produção/staging, `Settings` já exige DATABASE_URL PostgreSQL; aqui usamos
    `settings.DATABASE_URL` para ficar alinhado ao engine da app.
    """
    try:
        from alembic import command
        from alembic.config import Config

        backend_root = Path(__file__).parent.parent
        ini_path = backend_root / "alembic.ini"

        if not ini_path.exists():
            raise FileNotFoundError(f"alembic.ini não encontrado em {ini_path}")

        # Configurar Alembic
        cfg = Config(str(ini_path))
        database_url = settings.DATABASE_URL
        cfg.set_main_option("sqlalchemy.url", database_url)

        logger.info(f"🔄 Executando migrations Alembic...")

        # Normalizar possíveis múltiplas linhas na tabela alembic_version
        _normalizar_alembic_multilinha(cfg, command)

        # Executar upgrade até head
        try:
            command.upgrade(cfg, "head")
            logger.info("✅ Migrations do Alembic aplicadas com sucesso até HEAD")
        except Exception as migration_error:
            logger.error(
                "❌ Falha ao aplicar migrations do Alembic: %s",
                str(migration_error)[:200],
            )
            raise RuntimeError(
                "Falha ao aplicar migrations do Alembic. "
                "Verifique o estado do banco e o histórico de migrations."
                f"Detalhes: {migration_error}"
            ) from migration_error
    except Exception as e:
        logger.error(
            "❌ Erro ao executar setup de migrations: %s: %s",
            type(e).__name__,
            str(e)[:200],
        )
        raise


def _inicializar_banco_critico(db) -> None:
    """
    SRP: Orquestra a inicialização crítica do banco (gate para liberar /api em produção).

    Ordem importa:
    1. Com `STARTUP_RUN_ALEMBIC`: só Alembic até `head` (fonte de verdade do schema).
       Sem Alembic no startup: `create_all` para bases locais legadas / dev rápido.
    2. Admin + guards de schema + catálogo de jogos + memberships legados

    Args:
        db: Sessão do banco
    """
    if settings.STARTUP_RUN_ALEMBIC:
        passos = [
            ("executar_alembic_migrations", _executar_alembic_migrations),
        ]
    else:
        logger.info(
            "⏭️ Pulando Alembic no startup da app (STARTUP_RUN_ALEMBIC=0); "
            "espera-se migração prévia no processo de deploy (ex.: Procfile)."
        )
        passos = [
            ("criar_tabelas", lambda: Base.metadata.create_all(bind=engine)),
        ]

    passos.extend(
        [
            ("criar_admin_padrao", lambda: criar_admin_padrao(db)),
            ("garantir_coluna_dono_id", _garantir_coluna_dono_id),
            ("garantir_colunas_soft_delete", _garantir_colunas_soft_delete),
            (
                "garantir_colunas_catalogo_equipamentos",
                _garantir_colunas_catalogo_equipamentos,
            ),
            ("garantir_coluna_bonus_base_ataque", _garantir_coluna_bonus_base_ataque),
            (
                "garantir_coluna_habilidades_especiais",
                _garantir_coluna_habilidades_especiais,
            ),
            ("garantir_coluna_campanha_id", _garantir_coluna_campanha_id),
            ("garantir_coluna_raca_slug", _garantir_coluna_raca_slug),
            ("garantir_colunas_resistencia_base", _garantir_colunas_resistencia_base),
            ("garantir_colunas_dinheiro", _garantir_colunas_dinheiro),
            ("garantir_colunas_talentos", _garantir_colunas_talentos),
            (
                "garantir_colunas_armaduras_protecao",
                _garantir_colunas_armaduras_protecao,
            ),
            (
                "garantir_coluna_pericia_destaque_arena",
                _garantir_coluna_pericia_destaque_arena,
            ),
            ("garantir_constraints_item_13", _garantir_constraints_item_13),
            ("inicializar_catalogo_jogos", lambda: inicializar_catalogo_jogos(db)),
            (
                "garantir_membership_dnd35_para_usuarios_legados",
                lambda: garantir_membership_dnd35_para_usuarios_legados(db),
            ),
        ]
    )

    for nome, callback in passos:
        _executar_passo_startup(nome, callback)


def _inicializar_banco_pos_ready(db) -> None:
    """
    Passos não críticos para liberar API de login/negócio.
    Em produção rodam após a fase crítica ter marcado readiness.
    """
    passos = [
        ("seed_condicoes", lambda: _seed_condicoes(db)),
        ("seed_pericias", lambda: _seed_pericias(db)),
        ("seed_pericias_classes", lambda: _seed_pericias_classes(db)),
        ("inicializar_equipamentos", lambda: inicializar_equipamentos(db)),
        ("inicializar_consumiveis", lambda: inicializar_consumiveis(db)),
        ("seed_armaduras_protecao", lambda: _seed_armaduras_protecao(db)),
        ("inicializar_talentos", lambda: inicializar_talentos(db)),
        (
            "inicializar_catalogo_magias_se_vazio",
            lambda: inicializar_catalogo_magias_se_vazio(db),
        ),
        (
            "sincronizar_bonus_base_ataque_combatentes",
            lambda: sincronizar_bonus_base_ataque_combatentes(db),
        ),
        ("inicializar_catalogo_tabelas_classes", inicializar_catalogo_tabelas_classes),
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
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_combatentes_dono_id ON combatentes (dono_id)"
            )
        )

        if engine.dialect.name == "postgresql":
            owner_sql = """
                SELECT id
                FROM usuarios
                WHERE CAST(perfil AS TEXT) ILIKE 'administrador'
                  AND ativo IS TRUE
                ORDER BY id
                LIMIT 1
                """
        else:
            owner_sql = """
                SELECT id
                FROM usuarios
                WHERE perfil = 'administrador' AND ativo = 1
                ORDER BY id
                LIMIT 1
                """
        owner_id = conn.execute(text(owner_sql)).scalar()

        if owner_id is None:
            owner_id = conn.execute(
                text("SELECT id FROM usuarios ORDER BY id LIMIT 1")
            ).scalar()

        if owner_id is not None:
            conn.execute(
                text(
                    "UPDATE combatentes SET dono_id = :owner_id WHERE dono_id IS NULL"
                ),
                {"owner_id": owner_id},
            )


def _garantir_colunas_soft_delete() -> None:
    """Adiciona colunas `deleted_at` em tabelas legadas quando ausentes."""
    tabelas = [
        "pericias",
        "equipamentos",
        "consumiveis",
        "talentos",
        "combatentes",
        "equipamentos_jogador",
        "consumiveis_jogador",
        "talentos_jogador",
        "pericias_jogador",
    ]

    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())

    with engine.begin() as conn:
        for tabela in tabelas:
            if tabela not in tabelas_existentes:
                continue

            colunas = {col["name"] for col in inspector.get_columns(tabela)}
            if "deleted_at" in colunas:
                continue

            logger.warning(
                "⚠️  coluna %s.deleted_at ausente; aplicando schema guard", tabela
            )
            conn.execute(text(f"ALTER TABLE {tabela} ADD COLUMN deleted_at TIMESTAMP"))


def _garantir_constraints_item_13() -> None:
    """Normaliza dados e garante unicidade para item #13 em bases existentes.

    Importante: a partir do release que permite jogadores caírem até -10 HP
    (regra D&D 3.5 — `ck_combatentes_hp_atual_minimum CHECK hp_atual >= -10`),
    NÃO zeramos mais hp_atual negativo. Apenas elevamos valores abaixo do
    piso (< -10) para -10, mantendo o estado de "morto" coerente.
    """
    logger.info("🔧 Aplicando guard de integridade do item #13")
    with engine.begin() as conn:
        # Postgres: remove constraint legada `hp_atual >= 0` se ainda existir
        # (ex.: migration c4e8d2a9f1b3 não aplicada ou deploy parcial). Sem isto,
        # dano que leva PJ a HP negativo gera IntegrityError → 500.
        if engine.dialect.name == "postgresql":
            conn.execute(
                text(
                    "ALTER TABLE combatentes DROP CONSTRAINT IF EXISTS "
                    '"ck_combatentes_hp_atual_non_negative"'
                )
            )

        conn.execute(
            text(
                "UPDATE combatentes SET hp_maximo = 1 WHERE hp_maximo IS NULL OR hp_maximo <= 0"
            )
        )
        conn.execute(text("UPDATE combatentes SET hp_atual = 0 WHERE hp_atual IS NULL"))
        conn.execute(text("UPDATE combatentes SET hp_atual = -10 WHERE hp_atual < -10"))
        conn.execute(
            text(
                "UPDATE combatentes SET hp_atual = hp_maximo WHERE hp_atual > hp_maximo"
            )
        )

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


def _garantir_colunas_catalogo_equipamentos() -> None:
    """
    Garante colunas do catálogo estendido de equipamentos em bases legadas.

    Cenário alvo: banco com alembic_version marcado em revisão avançada,
    mas sem execução efetiva da migration de expansão de `equipamentos`.
    """
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "equipamentos" not in tabelas_existentes:
        return

    colunas_existentes = {col["name"] for col in inspector.get_columns("equipamentos")}
    colunas_esperadas = {
        "categoria": "VARCHAR(50)",
        "subcategoria": "VARCHAR(100)",
        "custo": "VARCHAR(50)",
        "dano_pequeno": "VARCHAR(20)",
        "dano_medio": "VARCHAR(20)",
        "critico": "VARCHAR(20)",
        "alcance_incremento": "VARCHAR(50)",
        "peso": "VARCHAR(20)",
        "tipo_dano": "VARCHAR(50)",
    }

    with engine.begin() as conn:
        for coluna, tipo_sql in colunas_esperadas.items():
            if coluna in colunas_existentes:
                continue

            logger.warning(
                "⚠️  coluna equipamentos.%s ausente; aplicando schema guard",
                coluna,
            )
            conn.execute(
                text(f"ALTER TABLE equipamentos ADD COLUMN {coluna} {tipo_sql}")
            )


def _garantir_colunas_talentos() -> None:
    """Garante colunas de talentos que podem faltar em banco legado ou incompleto."""
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "talentos" not in tabelas_existentes:
        return

    colunas_existentes = {col["name"] for col in inspector.get_columns("talentos")}
    colunas_esperadas = {
        "prerequisitos": "VARCHAR(500)",
        "secao": "VARCHAR(200)",
    }

    with engine.begin() as conn:
        for coluna, tipo_sql in colunas_esperadas.items():
            if coluna in colunas_existentes:
                continue

            logger.warning(
                "⚠️  coluna talentos.%s ausente; aplicando schema guard",
                coluna,
            )
            conn.execute(text(f"ALTER TABLE talentos ADD COLUMN {coluna} {tipo_sql}"))


def _garantir_coluna_bonus_base_ataque() -> None:
    """Garante a coluna `combatentes.bonus_base_ataque` em bancos legados."""
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "combatentes" not in tabelas_existentes:
        return

    colunas_existentes = {col["name"] for col in inspector.get_columns("combatentes")}
    if "bonus_base_ataque" in colunas_existentes:
        return

    logger.warning(
        "⚠️  coluna combatentes.bonus_base_ataque ausente; aplicando schema guard"
    )
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE combatentes ADD COLUMN bonus_base_ataque VARCHAR(30)")
        )


def _garantir_coluna_habilidades_especiais() -> None:
    """Garante a coluna `combatentes.habilidades_especiais` em bancos legados."""
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "combatentes" not in tabelas_existentes:
        return

    colunas_existentes = {col["name"] for col in inspector.get_columns("combatentes")}
    if "habilidades_especiais" in colunas_existentes:
        return

    logger.warning(
        "⚠️  coluna combatentes.habilidades_especiais ausente; aplicando schema guard"
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE combatentes ADD COLUMN habilidades_especiais VARCHAR(2000)"
            )
        )


def _garantir_coluna_campanha_id() -> None:
    """Garante a coluna `combatentes.campanha_id` em bancos legados."""
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "combatentes" not in tabelas_existentes:
        return

    colunas_existentes = {col["name"] for col in inspector.get_columns("combatentes")}
    if "campanha_id" in colunas_existentes:
        return

    logger.warning("⚠️  coluna combatentes.campanha_id ausente; aplicando schema guard")
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE combatentes ADD COLUMN campanha_id INTEGER"))
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_combatentes_campanha_id ON combatentes (campanha_id)"
            )
        )


def _garantir_coluna_raca_slug() -> None:
    """Garante a coluna `combatentes.raca_slug` em bancos legados."""
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "combatentes" not in tabelas_existentes:
        return

    colunas_existentes = {col["name"] for col in inspector.get_columns("combatentes")}
    if "raca_slug" in colunas_existentes:
        return

    logger.warning("⚠️  coluna combatentes.raca_slug ausente; aplicando schema guard")
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE combatentes ADD COLUMN raca_slug VARCHAR(80)"))


def _garantir_colunas_resistencia_base() -> None:
    """Garante colunas base de resistência em bancos legados."""
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "combatentes" not in tabelas_existentes:
        return

    colunas_existentes = {col["name"] for col in inspector.get_columns("combatentes")}
    colunas_esperadas = {
        "fortitude_base": "INTEGER",
        "reflexos_base": "INTEGER",
        "vontade_base": "INTEGER",
    }

    with engine.begin() as conn:
        for coluna, tipo_sql in colunas_esperadas.items():
            if coluna in colunas_existentes:
                continue
            logger.warning(
                "⚠️  coluna combatentes.%s ausente; aplicando schema guard", coluna
            )
            conn.execute(
                text(f"ALTER TABLE combatentes ADD COLUMN {coluna} {tipo_sql}")
            )


def _garantir_colunas_dinheiro() -> None:
    """Garante colunas de moedas em bancos legados."""
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "combatentes" not in tabelas_existentes:
        return

    colunas_existentes = {col["name"] for col in inspector.get_columns("combatentes")}
    colunas_esperadas = {
        "pc": "INTEGER",
        "pp": "INTEGER",
        "po": "INTEGER",
        "pl": "INTEGER",
    }
    with engine.begin() as conn:
        for coluna, tipo_sql in colunas_esperadas.items():
            if coluna in colunas_existentes:
                continue
            logger.warning(
                "⚠️  coluna combatentes.%s ausente; aplicando schema guard", coluna
            )
            conn.execute(
                text(
                    f"ALTER TABLE combatentes ADD COLUMN {coluna} {tipo_sql} DEFAULT 0"
                )
            )


def _garantir_colunas_armaduras_protecao() -> None:
    """Garante colunas da tabela armaduras_protecao em banco legado ou incompleto."""
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "armaduras_protecao" not in tabelas_existentes:
        return

    colunas_existentes = {
        col["name"] for col in inspector.get_columns("armaduras_protecao")
    }
    colunas_esperadas = {
        "nome": "VARCHAR(120)",
        "tipo": "VARCHAR(60)",
        "bonus_ca": "INTEGER",
        "des_max": "VARCHAR(20)",
        "penalidade": "INTEGER",
        "falha_arcana": "VARCHAR(20)",
        "deslocamento": "VARCHAR(40)",
        "peso": "FLOAT",
        "propriedades_especiais": "VARCHAR(600)",
        "ativo": "BOOLEAN",
        "criado_em": "TIMESTAMP",
    }

    with engine.begin() as conn:
        for coluna, tipo_sql in colunas_esperadas.items():
            if coluna in colunas_existentes:
                continue

            logger.warning(
                "⚠️  coluna armaduras_protecao.%s ausente; aplicando schema guard",
                coluna,
            )
            conn.execute(
                text(f"ALTER TABLE armaduras_protecao ADD COLUMN {coluna} {tipo_sql}")
            )


def _garantir_coluna_pericia_destaque_arena() -> None:
    """Garante a coluna de destaque para exibição de perícias na arena."""
    inspector = inspect(engine)
    tabelas_existentes = set(inspector.get_table_names())
    if "pericia_jogadores" not in tabelas_existentes:
        return

    colunas_existentes = {
        col["name"] for col in inspector.get_columns("pericia_jogadores")
    }
    if "destaque_arena" in colunas_existentes:
        return

    logger.warning(
        "⚠️  coluna pericia_jogadores.destaque_arena ausente; aplicando schema guard"
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE pericia_jogadores ADD COLUMN destaque_arena INTEGER DEFAULT 0"
            )
        )


def _seed_pericias(db) -> None:
    """
    Garante que as perícias da Tabela 4-3 (D&D 3.5, Livro do Jogador p. 55) existam no banco.

    Idempotente: insere apenas as perícias canônicas que ainda não estão na tabela,
    usando `scripts.seed_pericias.PERICIAS_DATA` como única fonte de verdade.
    As reconciliações de nomes legados (ex.: "Acrobacia" → "Acrobacias") ficam a
    cargo das migrações Alembic — este seed não renomeia nada.
    """
    from scripts.seed_pericias import PERICIAS_DATA

    from .games.dnd35.models.pericia import Pericia

    try:
        existentes = {nome for (nome,) in db.query(Pericia.nome).all()}
        criadas: list[str] = []

        for pericia_data in PERICIAS_DATA:
            nome = pericia_data["nome"]
            if nome in existentes:
                continue

            atributo_raw = str(pericia_data.get("atributo") or "").strip()
            atributo_norm = atributo_raw[:3].upper() if atributo_raw else "DES"

            db.add(
                Pericia(
                    nome=nome,
                    descricao=pericia_data.get("descricao") or "",
                    atributo=atributo_norm,
                    tipo="comum",
                    especialidade=None,
                    requer_treinamento=0,
                    pode_usar_sem_treinamento=1,
                    sofre_penalidade_armadura=0,
                )
            )
            criadas.append(nome)

        if criadas:
            db.commit()
            logger.info("✅ %s perícias canônicas inseridas (Tabela 4-3)", len(criadas))
            print(f"✅ {len(criadas)} perícias canônicas inseridas (Tabela 4-3)")
        else:
            logger.info(
                "✅ Perícias da Tabela 4-3 já presentes (%s existentes)",
                len(existentes),
            )
            print(
                f"✅ Perícias da Tabela 4-3 já presentes ({len(existentes)} existentes)"
            )

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erro ao popular perícias: {str(e)}")
        print(f"❌ Erro ao popular perícias: {str(e)}")
        raise


def _seed_armaduras_protecao(db) -> None:
    """
    Popula catálogo de armaduras/escudos da Tabela 7-6 se estiver vazio.
    """
    from scripts.seed_armaduras_protecao import seed_armaduras_protecao

    from .games.dnd35.models.armadura_protecao import ArmaduraProtecao

    try:
        count = db.query(ArmaduraProtecao).count()
        if count > 0:
            logger.info("✅ %s armaduras/proteções já existem no banco", count)
            print(f"✅ {count} armaduras/proteções já existem no banco de dados")
            return

        logger.info("🔄 Populando armaduras/proteções (Tabela 7-6)...")
        print("🔄 Populando banco com armaduras/proteções da Tabela 7-6...")
        seed_armaduras_protecao(db)
    except Exception as e:
        db.rollback()
        logger.error("❌ Erro ao popular armaduras/proteções: %s", str(e))
        print(f"❌ Erro ao popular armaduras/proteções: {str(e)}")
        raise


def _normalizar_nome_pericia(valor: str) -> str:
    """Normaliza nomes para casar perícias entre fontes de seed diferentes."""
    if not valor:
        return ""

    texto = unicodedata.normalize("NFKD", valor)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.lower().strip()
    texto = "".join(ch if ch.isalnum() else " " for ch in texto)
    return " ".join(texto.split())


def _seed_pericias_classes(db) -> None:
    """
    Popula `pericias_classes` de forma idempotente para habilitar custo por classe.
    """
    from scripts.seed_pericias import PERICIAS_DATA

    from .games.dnd35.models.pericia import Pericia, PericiaClasse

    try:
        associacoes_antes = db.query(PericiaClasse).count()

        pericias_db = db.query(Pericia.id, Pericia.nome).all()
        if not pericias_db:
            logger.info("ℹ️ Sem perícias cadastradas; seed_pericias_classes ignorado")
            print("ℹ️ Sem perícias cadastradas; seed_pericias_classes ignorado")
            return

        mapa_por_nome = {
            _normalizar_nome_pericia(nome): pericia_id
            for pericia_id, nome in pericias_db
        }

        registros_novos = 0
        nao_mapeadas = 0

        for pericia in PERICIAS_DATA:
            pericia_id = mapa_por_nome.get(
                _normalizar_nome_pericia(pericia.get("nome", ""))
            )
            if pericia_id is None:
                nao_mapeadas += 1
                continue

            for classe_nome in pericia.get("classes", []):
                existente = (
                    db.query(PericiaClasse.id)
                    .filter(
                        PericiaClasse.pericia_id == pericia_id,
                        PericiaClasse.classe_nome == classe_nome,
                        PericiaClasse.is_default == 1,
                    )
                    .first()
                )
                if existente:
                    continue

                db.add(
                    PericiaClasse(
                        pericia_id=pericia_id,
                        classe_nome=classe_nome,
                        is_default=1,
                    )
                )
                registros_novos += 1

        db.commit()
        logger.info(
            "✅ pericias_classes: %s -> %s (+%s), %s perícias sem match",
            associacoes_antes,
            associacoes_antes + registros_novos,
            registros_novos,
            nao_mapeadas,
        )
        print(
            f"✅ pericias_classes: {associacoes_antes} -> {associacoes_antes + registros_novos} "
            f"(+{registros_novos}) "
            f"({nao_mapeadas} perícias sem match)"
        )
    except Exception as e:
        db.rollback()
        logger.error("❌ Erro ao popular pericias_classes: %s", str(e))
        print(f"❌ Erro ao popular pericias_classes: {str(e)}")
        raise


def _seed_combatentes(db) -> None:
    """
    Popula combatentes iniciais se o banco estiver vazio.

    Args:
        db: Sessão do banco
    """
    from .games.dnd35.models.combatente import Combatente
    from .games.dnd35.repositories.combatente_repository import CombatenteRepository

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
    from .games.dnd35.repositories.condicao_repository import CondicaoRepository
    from .games.dnd35.services.condicao_service import CondicaoService

    repo = CondicaoRepository(db)
    service = CondicaoService(condicao_repository=repo, combatente_repository=None)

    service.inicializar_seed()
    logger.info("✅ Seed de condições D&D verificado")
    print("✅ Seed de condições D&D verificado/executado com sucesso!")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
