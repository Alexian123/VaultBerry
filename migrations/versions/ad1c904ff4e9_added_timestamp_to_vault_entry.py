"""added timestamp to vault entry

Revision ID: ad1c904ff4e9
Revises: 3d867abeafd7
Create Date: 2024-12-08 00:05:51.921126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad1c904ff4e9'
down_revision = '3d867abeafd7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vault_entry', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timestamp', sa.BigInteger(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vault_entry', schema=None) as batch_op:
        batch_op.drop_column('timestamp')

    # ### end Alembic commands ###
