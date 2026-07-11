"""add selection_id to audit_log

Revision ID: c4d9f1a6b2e7
Revises: b3c8e2f9a1d4
Create Date: 2026-07-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c4d9f1a6b2e7'
down_revision = 'b3c8e2f9a1d4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('selection_id', sa.UUID(), nullable=True))
        batch_op.create_foreign_key(
            'fk_audit_log_selection_id', 'selection', ['selection_id'], ['id']
        )


def downgrade():
    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.drop_constraint('fk_audit_log_selection_id', type_='foreignkey')
        batch_op.drop_column('selection_id')
