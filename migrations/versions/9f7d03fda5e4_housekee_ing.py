"""housekee[ing

Revision ID: 9f7d03fda5e4
Revises: fd2dc4723531
Create Date: 2025-03-17 15:48:30.947711

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f7d03fda5e4'
down_revision = 'fd2dc4723531'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('amounts_books', schema=None) as batch_op:
        batch_op.alter_column('amount_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('books_instructions', schema=None) as batch_op:
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('instruction_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('quantity_amount_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('quantity_unit_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('item_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('items_books', schema=None) as batch_op:
        batch_op.alter_column('item_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('recipes_books', schema=None) as batch_op:
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('recipes_instructions', schema=None) as batch_op:
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('instruction_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('units_books', schema=None) as batch_op:
        batch_op.alter_column('unit_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('users_books', schema=None) as batch_op:
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users_books', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('units_books', schema=None) as batch_op:
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('unit_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('recipes_instructions', schema=None) as batch_op:
        batch_op.alter_column('instruction_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('recipes_books', schema=None) as batch_op:
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('items_books', schema=None) as batch_op:
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('item_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.alter_column('item_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('quantity_unit_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('quantity_amount_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('books_instructions', schema=None) as batch_op:
        batch_op.alter_column('instruction_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('amounts_books', schema=None) as batch_op:
        batch_op.alter_column('book_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('amount_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###
