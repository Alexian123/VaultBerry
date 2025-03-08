"""MFA status

Revision ID: bca2f7ec3833
Revises: 9c772aef6556
Create Date: 2025-03-08 16:14:38.879523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bca2f7ec3833'
down_revision = '9c772aef6556'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mfa_enabled', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('mfa_enabled')

    # ### end Alembic commands ###
