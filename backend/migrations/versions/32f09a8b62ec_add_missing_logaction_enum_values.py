"""add missing logaction enum values

Revision ID: 32f09a8b62ec
Revises: e238af2a90ec
Create Date: 2026-07-13 14:00:04.169527

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32f09a8b62ec'
down_revision = 'e238af2a90ec'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE logaction ADD VALUE IF NOT EXISTS 'REGISTER_APPROVED'")
    op.execute("ALTER TYPE logaction ADD VALUE IF NOT EXISTS 'REGISTER_REJECTED'")
    op.execute("ALTER TYPE logaction ADD VALUE IF NOT EXISTS 'AUDITOR_NOMINATION_REQUESTED'")


def downgrade():
    # Postgres não suporta remover valores de um ENUM existente sem recriar o
    # tipo inteiro e reescrever as colunas dependentes. Nenhuma outra migration
    # deste repositório reverte valores de enum adicionados; downgrade é no-op
    # de propósito.
    pass
