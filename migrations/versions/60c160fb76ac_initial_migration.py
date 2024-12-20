"""Initial migration

Revision ID: 60c160fb76ac
Revises: 
Create Date: 2024-11-05 19:07:32.018926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60c160fb76ac'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), nullable=True),
    sa.Column('hashed_password', sa.VARCHAR(length=255), nullable=True),
    sa.Column('first_name', sa.VARCHAR(length=255), nullable=True),
    sa.Column('last_name', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('vault_entry',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.VARCHAR(length=255), nullable=True),
    sa.Column('url', sa.VARCHAR(length=255), nullable=True),
    sa.Column('encrypted_username', sa.VARCHAR(length=255), nullable=True),
    sa.Column('encrypted_password', sa.VARCHAR(length=255), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'title', name='unique_user_title')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vault_entry')
    op.drop_table('user')
    # ### end Alembic commands ###
