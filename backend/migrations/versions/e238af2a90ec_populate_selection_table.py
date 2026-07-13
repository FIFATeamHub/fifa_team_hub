"""populate_selection_table

Revision ID: e238af2a90ec
Revises: 18f4f078464b
Create Date: 2026-07-13 10:12:16.283378

"""
from alembic import op
import sqlalchemy as sa

revision = 'e238af2a90ec' 
down_revision = '18f4f078464b'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    count = bind.execute(sa.text("SELECT COUNT(*) FROM selection")).scalar()

    if count == 0:
        bind.execute(sa.text("""
            INSERT INTO selection (id, name, code, created_at) VALUES
            (gen_random_uuid(), 'Brazil', 'BRA', now()),
            (gen_random_uuid(), 'Argentina', 'ARG', now()),
            (gen_random_uuid(), 'France', 'FRA', now())
        """))

def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("""
        DELETE FROM selection WHERE code IN ('BRA', 'ARG', 'FRA')
    """))