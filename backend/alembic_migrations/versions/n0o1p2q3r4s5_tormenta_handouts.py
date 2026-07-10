"""Migration: tormenta_handouts — handouts revelados pelo mestre (RF-T12f)."""

from alembic import op
import sqlalchemy as sa

revision = "n0o1p2q3r4s5"
down_revision = "m9n0o1p2q3r4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tormenta_handouts" in inspector.get_table_names():
        return
    op.create_table(
        "tormenta_handouts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campanha_id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("corpo_md", sa.String(length=8000), nullable=False, server_default=""),
        sa.Column("imagem_url", sa.String(length=2048), nullable=True),
        sa.Column(
            "visivel_para_user_ids",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["campanha_id"],
            ["tormenta_campanhas.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_tormenta_handouts_campanha_id"),
        "tormenta_handouts",
        ["campanha_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tormenta_handouts_id"),
        "tormenta_handouts",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tormenta_handouts" not in inspector.get_table_names():
        return
    op.drop_index(op.f("ix_tormenta_handouts_id"), table_name="tormenta_handouts")
    op.drop_index(
        op.f("ix_tormenta_handouts_campanha_id"), table_name="tormenta_handouts"
    )
    op.drop_table("tormenta_handouts")
