"""added keys to useer

Revision ID: 19804513104c
Revises: 3f9e9f80819b
Create Date: 2024-11-21 20:50:21.156218

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19804513104c'
down_revision = '3f9e9f80819b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('vault_key', sa.VARCHAR(length=255), nullable=True))
        batch_op.add_column(sa.Column('recovery_key', sa.VARCHAR(length=255), nullable=True))

    with op.batch_alter_table('vault_entry', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_uuid', sa.VARCHAR(length=36), nullable=True))
        batch_op.drop_constraint('unique_user_title', type_='unique')
        batch_op.create_unique_constraint('unique_user_title', ['user_uuid', 'title'])
        batch_op.drop_constraint('vault_entry_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_uuid'], ['uuid'])
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vault_entry', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('vault_entry_user_id_fkey', 'user', ['user_id'], ['id'])
        batch_op.drop_constraint('unique_user_title', type_='unique')
        batch_op.create_unique_constraint('unique_user_title', ['user_id', 'title'])
        batch_op.drop_column('user_uuid')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('recovery_key')
        batch_op.drop_column('vault_key')

    # ### end Alembic commands ###
