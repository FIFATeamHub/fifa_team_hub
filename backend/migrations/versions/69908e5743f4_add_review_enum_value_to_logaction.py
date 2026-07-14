"""add review enum value to logaction

Revision ID: 69908e5743f4
Revises: 65ce39187789
Create Date: 2026-07-14 01:59:01.721418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69908e5743f4'
down_revision = '65ce39187789'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE logaction ADD VALUE IF NOT EXISTS 'REVIEW'")


def downgrade():
    # Postgres não suporta remover valores de um ENUM existente sem recriar o
    # tipo inteiro e reescrever as colunas dependentes. Nenhuma outra migration
    # deste repositório reverte valores de enum adicionados; downgrade é no-op
    # de propósito.
    pass
