"""Migration: convite de campanha Tormenta (RF-T12k)."""

from alembic import op
import sqlalchemy as sa

revision = "p1q2r3s4t5u6"
down_revision = "n0o1p2q3r4s5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tormenta_campanhas" not in inspector.get_table_names():
        return
    cols = {c["name"] for c in inspector.get_columns("tormenta_campanhas")}
    if "convite_token" not in cols:
        op.add_column(
            "tormenta_campanhas",
            sa.Column("convite_token", sa.String(length=64), nullable=True),
        )
    if "convite_ativo" not in cols:
        op.add_column(
            "tormenta_campanhas",
            sa.Column(
                "convite_ativo",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    indexes = {i["name"] for i in inspector.get_indexes("tormenta_campanhas")}
    if "ix_tormenta_campanhas_convite_token" not in indexes:
        op.create_index(
            "ix_tormenta_campanhas_convite_token",
            "tormenta_campanhas",
            ["convite_token"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tormenta_campanhas" not in inspector.get_table_names():
        return
    indexes = {i["name"] for i in inspector.get_indexes("tormenta_campanhas")}
    if "ix_tormenta_campanhas_convite_token" in indexes:
        op.drop_index("ix_tormenta_campanhas_convite_token", table_name="tormenta_campanhas")
    cols = {c["name"] for c in inspector.get_columns("tormenta_campanhas")}
    if "convite_ativo" in cols:
        op.drop_column("tormenta_campanhas", "convite_ativo")
    if "convite_token" in cols:
        op.drop_column("tormenta_campanhas", "convite_token")
