"""add auditor nomination rejected enum value

Revision ID: a4e7c25f9b31
Revises: 32f09a8b62ec
Create Date: 2026-07-13 18:32:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4e7c25f9b31'
down_revision = '32f09a8b62ec'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE logaction ADD VALUE IF NOT EXISTS 'AUDITOR_NOMINATION_REJECTED'")


def downgrade():
    # Postgres não suporta remover valores de um ENUM existente sem recriar o
    # tipo inteiro e reescrever as colunas dependentes. Nenhuma outra migration
    # deste repositório reverte valores de enum adicionados; downgrade é no-op
    # de propósito.
    pass
