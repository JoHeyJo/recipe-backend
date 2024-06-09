"""add UserRecipe title

Revision ID: 1eb67852a71f
Revises: 366ebed06cb5
Create Date: 2024-06-06 11:51:32.306773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1eb67852a71f'
down_revision = '366ebed06cb5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_recipes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(length=255), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_recipes', schema=None) as batch_op:
        batch_op.drop_column('title')

    # ### end Alembic commands ###