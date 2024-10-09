"""changed RecipeIngredient col ingredient_id to item_id

Revision ID: 23665af94eb4
Revises: 6c1cf522471c
Create Date: 2024-10-09 16:51:48.131822

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23665af94eb4'
down_revision = '6c1cf522471c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes_ingredients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('item_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('recipes_ingredients_ingredient_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'items', ['item_id'], ['id'])
        batch_op.drop_column('ingredient_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes_ingredients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ingredient_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('recipes_ingredients_ingredient_id_fkey', 'items', ['ingredient_id'], ['id'])
        batch_op.drop_column('item_id')

    # ### end Alembic commands ###