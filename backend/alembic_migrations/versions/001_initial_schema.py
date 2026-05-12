"""
001_initial_schema.py

Migração: schema completo da feature/visualizacao_v2
- Cria tabela `usuarios` (nova)
- Adiciona colunas novas em `combatentes`:
    defesa  : ca, toque, surpresa
    resistências: fortitude, reflexos, vontade
    progressão  : nivel, pontos
    visual      : foto_url
    atributos D&D completos

SRP  : cada upgrade/downgrade faz exatamente uma coisa coesa.
Autor: gerado para branch feature/deploy_migration
"""
from alembic import op
from alembic.operations import Operations
import sqlalchemy as sa


# Revisão gerada — não altere esses valores após o primeiro deploy
revision = "001_initial_schema"
down_revision = None          # primeira migration da cadeia
branch_labels = None
depends_on = None


# 
# Helpers — ISP: funções pequenas e focadas
# 

def _tabela_existe(tabela: str) -> bool:
    """
    Verifica se a tabela já existe (idempotência em re-runs).
    Funciona APENAS em modo online (com conexão real).
    """
    try:
        bind = op.get_bind()
        # Se for MockConnection (modo offline), retorna False (assume que não existe)
        if hasattr(bind, "__class__") and "Mock" in bind.__class__.__name__:
            return False
        inspector = sa.inspect(bind)
        return tabela in inspector.get_table_names()
    except Exception:
        # Se houver qualquer erro (offline, sem inspector), assume que não existe
        return False


def _coluna_existe(tabela: str, coluna: str) -> bool:
    """
    Verifica se uma coluna já existe (idempotência em re-runs).
    Funciona APENAS em modo online (com conexão real).
    """
    try:
        bind = op.get_bind()
        # Se for MockConnection (modo offline), retorna False (assume que não existe)
        if hasattr(bind, "__class__") and "Mock" in bind.__class__.__name__:
            return False
        inspector = sa.inspect(bind)
        colunas = [c["name"] for c in inspector.get_columns(tabela)]
        return coluna in colunas
    except Exception:
        # Se houver qualquer erro, assume que não existe
        return False


# 
# Upgrade
# 

def _ensure_combatentes_raiz() -> None:
    """
    Banco totalmente novo (ex.: CI Postgres vazio, SQLite limpo): antes só havia
    schema legado criado fora do Alembic; esta migration altera `combatentes`.
    """
    if _tabela_existe("combatentes"):
        return
    op.create_table(
        "combatentes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("classe", sa.String(), nullable=False),
        sa.Column("hp_atual", sa.Integer(), nullable=False),
        sa.Column("hp_maximo", sa.Integer(), nullable=False),
        sa.Column("iniciativa", sa.Integer(), nullable=False, server_default="0"),
    )


def upgrade() -> None:
    # 
    # 1. Tabela `usuarios` — nova, não existia na feature/salva
    # 
    if not _tabela_existe("usuarios"):
        op.create_table(
            "usuarios",
            sa.Column("id",    sa.Integer(), primary_key=True, index=True),
            sa.Column("perfil", sa.Enum(
                "administrador", "mestre", "jogador",
                name="perfilusuario"          # nome do tipo ENUM no PostgreSQL
            ), nullable=False),
            sa.Column("nome",       sa.String(100), nullable=False),
            sa.Column("email",      sa.String(150), nullable=False, unique=True, index=True),
            sa.Column("senha_hash", sa.String(255), nullable=False),
            sa.Column("ativo",      sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("usuario_responsavel", sa.String(150), nullable=True),
            sa.Column(
                "data_acao",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
                nullable=True,
            ),
        )

    _ensure_combatentes_raiz()

    # 
    # 2. Colunas novas em `combatentes`
    #    Cada add_column é idempotente: só executa se a coluna não existir.
    # 
    _add_col_if_missing = _add_combatente_column   # alias legível

    # --- Defesa ---
    _add_col_if_missing("ca",       sa.Integer(), server_default="10")
    _add_col_if_missing("toque",    sa.Integer(), server_default="10")
    _add_col_if_missing("surpresa", sa.Integer(), server_default="10")

    # --- Resistências ---
    _add_col_if_missing("fortitude", sa.Integer(), server_default="0")
    _add_col_if_missing("reflexos",  sa.Integer(), server_default="0")
    _add_col_if_missing("vontade",   sa.Integer(), server_default="0")

    # --- Atributos D&D (podem já existir — verifica antes) ---
    _add_col_if_missing("forca",        sa.Integer(), server_default="10")
    _add_col_if_missing("destreza",     sa.Integer(), server_default="10")
    _add_col_if_missing("constituicao", sa.Integer(), server_default="10")
    _add_col_if_missing("inteligencia", sa.Integer(), server_default="10")
    _add_col_if_missing("sabedoria",    sa.Integer(), server_default="10")
    _add_col_if_missing("carisma",      sa.Integer(), server_default="10")

    # --- Progressão ---
    _add_col_if_missing("nivel",  sa.Integer(), server_default="1")
    _add_col_if_missing("pontos", sa.Integer(), server_default="0")

    # --- Visual ---
    _add_col_if_missing("foto_url", sa.String(), nullable=True, server_default=None)

    # --- Raça (pode não existir na salva) ---
    _add_col_if_missing("raca", sa.String(), nullable=True, server_default="''")


# 
# Downgrade — reverte exatamente o que o upgrade fez
# 

def downgrade() -> None:
    # Remove colunas adicionadas em combatentes (ordem inversa)
    _colunas_novas = [
        "raca", "foto_url", "pontos", "nivel",
        "carisma", "sabedoria", "inteligencia",
        "constituicao", "destreza", "forca",
        "vontade", "reflexos", "fortitude",
        "surpresa", "toque", "ca",
    ]
    for col in _colunas_novas:
        if _coluna_existe("combatentes", col):
            op.drop_column("combatentes", col)

    # Remove tabela usuarios
    if _tabela_existe("usuarios"):
        op.drop_table("usuarios")
        # Remove o tipo ENUM do PostgreSQL
        try:
            sa.Enum(name="perfilusuario").drop(op.get_bind(), checkfirst=True)
        except Exception:
            # Se estiver em modo offline ou der erro, ignora
            pass


# 
# Helper interno — SRP: centraliza a lógica de add_column idempotente
# 

def _add_combatente_column(
    nome: str,
    tipo: sa.types.TypeEngine,
    server_default=None,
    nullable: bool = False,
) -> None:
    """
    Adiciona coluna em `combatentes` apenas se não existir.
    Evita erro em re-runs e deploys parciais.
    
    Em modo offline (--sql), tenta adicionar mesmo que a coluna exista
    (o banco/script precisará ignorar a coluna duplicada).
    Em modo online (conexão real), verifica antes.
    """
    if _coluna_existe("combatentes", nome):
        return

    col_kwargs = {"nullable": nullable}
    if server_default is not None:
        col_kwargs["server_default"] = (
            sa.text(str(server_default))
            if not isinstance(server_default, sa.sql.elements.TextClause)
            else server_default
        )

    op.add_column(
        "combatentes",
        sa.Column(nome, tipo, **col_kwargs),
    )