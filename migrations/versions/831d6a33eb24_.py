"""empty message

Revision ID: 831d6a33eb24
Revises: 83a0f5a7151f
Create Date: 2018-10-21 11:41:33.713066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '831d6a33eb24'
down_revision = '83a0f5a7151f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('context_session', sa.Column('description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('context_session', 'description')
    # ### end Alembic commands ###