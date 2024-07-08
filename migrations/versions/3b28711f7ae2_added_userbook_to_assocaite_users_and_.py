"""added UserBook to assocaite users and books

Revision ID: 3b28711f7ae2
Revises: 96f9f72f7ba1
Create Date: 2024-06-28 16:49:05.253419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b28711f7ae2'
down_revision = '96f9f72f7ba1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('user_books_recipe_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])
        batch_op.drop_column('recipe_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('recipe_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('user_books_recipe_id_fkey', 'recipes', ['recipe_id'], ['id'])
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###