"""add missing typedocument enum values

Revision ID: d8f3a6c1e9b4
Revises: c4d9f1a6b2e7
Create Date: 2026-07-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'd8f3a6c1e9b4'
down_revision = 'c4d9f1a6b2e7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'RELATORIO_TATICO'")
    op.execute("ALTER TYPE typedocument ADD VALUE IF NOT EXISTS 'ESQUEMA_JOGADAS'")


def downgrade():
    # Postgres não suporta remover valores de um ENUM existente sem recriar o
    # tipo inteiro e reescrever as colunas dependentes. Nenhuma outra migration
    # deste repositório reverte valores de enum adicionados; downgrade é no-op
    # de propósito.
    pass
