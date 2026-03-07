"""add raca to combatente

Revision ID: add_raca_001
Revises: 
Create Date: 2026-03-07
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('combatentes', sa.Column('raca', sa.String(), nullable=True, server_default=''))

def downgrade():
    op.drop_column('combatentes', 'raca')