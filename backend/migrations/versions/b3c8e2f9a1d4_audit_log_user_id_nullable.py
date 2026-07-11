
from alembic import op
import sqlalchemy as sa


revision = 'b3c8e2f9a1d4'
down_revision = '439b6c5d42ce'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.UUID(),
               nullable=True)



def downgrade():
    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.UUID(),
               nullable=False)

