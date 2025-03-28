"""removed primary key from ingredient

Revision ID: fd2dc4723531
Revises: 553be24eb084
Create Date: 2025-03-17 12:42:19.699021

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fd2dc4723531'
down_revision = '553be24eb084'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('amounts_books', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    with op.batch_alter_table('books_instructions', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('quantity_amount_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('quantity_unit_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('item_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('items_books', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    with op.batch_alter_table('recipes_books', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    with op.batch_alter_table('recipes_instructions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.BIGINT(), nullable=False))
        batch_op.drop_column('created_at')

    with op.batch_alter_table('units_books', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    with op.batch_alter_table('users_books', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False))

    with op.batch_alter_table('units_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False))

    with op.batch_alter_table('recipes_instructions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False))
        batch_op.drop_column('id')

    with op.batch_alter_table('recipes_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False))

    with op.batch_alter_table('items_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False))

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.alter_column('item_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('quantity_unit_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('quantity_amount_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('books_instructions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False))

    with op.batch_alter_table('amounts_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
