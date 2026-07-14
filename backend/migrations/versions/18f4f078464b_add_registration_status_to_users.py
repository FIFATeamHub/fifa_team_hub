"""add registration_status to users

Revision ID: 18f4f078464b
Revises: d8f3a6c1e9b4
Create Date: 2026-07-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '18f4f078464b'
down_revision = 'd8f3a6c1e9b4'
branch_labels = None
depends_on = None

registration_status_enum = sa.Enum(
    'PENDING', 'APPROVED', 'REJECTED', name='registrationstatus'
)


def upgrade():
    bind = op.get_bind()
    registration_status_enum.create(bind, checkfirst=True)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'registration_status',
                sa.Enum(
                    'PENDING', 'APPROVED', 'REJECTED',
                    name='registrationstatus', create_type=False
                ),
                nullable=False,
                server_default='PENDING',
            )
        )

    op.execute("UPDATE users SET registration_status = 'APPROVED'")


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('registration_status')

    registration_status_enum.drop(op.get_bind(), checkfirst=True)
