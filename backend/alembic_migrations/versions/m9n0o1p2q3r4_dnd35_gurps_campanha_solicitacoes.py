"""Migration: campanha_solicitacoes (D&D 3.5) e gurps_campanha_solicitacoes."""

from alembic import op
import sqlalchemy as sa

revision = "m9n0o1p2q3r4"
down_revision = "l8m9n0o1p2q3"
branch_labels = None
depends_on = None


def _criar_tabela_solicitacoes(
    nome_tabela: str,
    fk_campanha: str,
    fk_personagem: str,
    prefixo_ix: str,
) -> None:
    op.create_table(
        nome_tabela,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campanha_id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("solicitante_id", sa.Integer(), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pendente"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["campanha_id"], [f"{fk_campanha}.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["personagem_id"], [f"{fk_personagem}.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["solicitante_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(f"ix_{prefixo_ix}_campanha_id", nome_tabela, ["campanha_id"])
    op.create_index(f"ix_{prefixo_ix}_personagem_id", nome_tabela, ["personagem_id"])
    op.create_index(f"ix_{prefixo_ix}_solicitante_id", nome_tabela, ["solicitante_id"])
    op.create_index(f"ix_{prefixo_ix}_status", nome_tabela, ["status"])


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tabelas = set(inspector.get_table_names())

    if "campanha_solicitacoes" not in tabelas:
        _criar_tabela_solicitacoes(
            "campanha_solicitacoes",
            "campanhas",
            "combatentes",
            "d35_camp_sol",
        )

    if "gurps_campanha_solicitacoes" not in tabelas:
        _criar_tabela_solicitacoes(
            "gurps_campanha_solicitacoes",
            "gurps_campanhas",
            "gurps_personagens",
            "gurps_camp_sol",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tabelas = set(inspector.get_table_names())

    if "gurps_campanha_solicitacoes" in tabelas:
        op.drop_index("ix_gurps_camp_sol_status", table_name="gurps_campanha_solicitacoes")
        op.drop_index(
            "ix_gurps_camp_sol_solicitante_id", table_name="gurps_campanha_solicitacoes"
        )
        op.drop_index(
            "ix_gurps_camp_sol_personagem_id", table_name="gurps_campanha_solicitacoes"
        )
        op.drop_index(
            "ix_gurps_camp_sol_campanha_id", table_name="gurps_campanha_solicitacoes"
        )
        op.drop_table("gurps_campanha_solicitacoes")

    if "campanha_solicitacoes" in tabelas:
        op.drop_index("ix_d35_camp_sol_status", table_name="campanha_solicitacoes")
        op.drop_index(
            "ix_d35_camp_sol_solicitante_id", table_name="campanha_solicitacoes"
        )
        op.drop_index(
            "ix_d35_camp_sol_personagem_id", table_name="campanha_solicitacoes"
        )
        op.drop_index("ix_d35_camp_sol_campanha_id", table_name="campanha_solicitacoes")
        op.drop_table("campanha_solicitacoes")
