"""Migration: tormenta_campanha_solicitacoes — pedidos de entrada na mesa."""

from alembic import op
import sqlalchemy as sa

revision = "l8m9n0o1p2q3"
down_revision = "k7l8m9n0o1p2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tormenta_campanha_solicitacoes" in inspector.get_table_names():
        return
    op.create_table(
        "tormenta_campanha_solicitacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campanha_id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("solicitante_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pendente"),
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
        sa.ForeignKeyConstraint(["campanha_id"], ["tormenta_campanhas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["personagem_id"], ["tormenta_personagens.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["solicitante_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_tormenta_camp_sol_campanha_id",
        "tormenta_campanha_solicitacoes",
        ["campanha_id"],
    )
    op.create_index(
        "ix_tormenta_camp_sol_personagem_id",
        "tormenta_campanha_solicitacoes",
        ["personagem_id"],
    )
    op.create_index(
        "ix_tormenta_camp_sol_solicitante_id",
        "tormenta_campanha_solicitacoes",
        ["solicitante_id"],
    )
    op.create_index(
        "ix_tormenta_camp_sol_status",
        "tormenta_campanha_solicitacoes",
        ["status"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tormenta_campanha_solicitacoes" not in inspector.get_table_names():
        return
    op.drop_index("ix_tormenta_camp_sol_status", table_name="tormenta_campanha_solicitacoes")
    op.drop_index(
        "ix_tormenta_camp_sol_solicitante_id", table_name="tormenta_campanha_solicitacoes"
    )
    op.drop_index(
        "ix_tormenta_camp_sol_personagem_id", table_name="tormenta_campanha_solicitacoes"
    )
    op.drop_index("ix_tormenta_camp_sol_campanha_id", table_name="tormenta_campanha_solicitacoes")
    op.drop_table("tormenta_campanha_solicitacoes")
