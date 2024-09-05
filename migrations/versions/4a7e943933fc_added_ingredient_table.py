""" added Ingredient table

Revision ID: 4a7e943933fc
Revises: e25e4f232faa
Create Date: 2024-08-28 21:21:45.773303

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a7e943933fc'
down_revision = 'e25e4f232faa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('books_instructions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('book_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('instruction_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'instructions', ['instruction_id'], ['id'])
        batch_op.create_foreign_key(None, 'books', ['book_id'], ['id'])

    with op.batch_alter_table('instructions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('instruction', sa.String(length=255), nullable=False))
        batch_op.drop_column('name')

    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.drop_column('preparation')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('preparation', sa.VARCHAR(length=255), autoincrement=False, nullable=True))

    with op.batch_alter_table('instructions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
        batch_op.drop_column('instruction')

    with op.batch_alter_table('books_instructions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('instruction_id')
        batch_op.drop_column('book_id')

    # ### end Alembic commands ###