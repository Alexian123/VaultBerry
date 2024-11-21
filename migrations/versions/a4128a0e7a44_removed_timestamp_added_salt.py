"""removed timestamp, added salt

Revision ID: a4128a0e7a44
Revises: 9f4f0ba30f59
Create Date: 2024-11-21 21:36:12.763478

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a4128a0e7a44'
down_revision = '9f4f0ba30f59'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('salt', sa.VARCHAR(length=16), nullable=True))
        batch_op.drop_column('created_on')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.drop_column('salt')

    # ### end Alembic commands ###