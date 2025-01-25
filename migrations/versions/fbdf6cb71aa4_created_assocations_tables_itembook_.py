"""created assocations tables ItemBook UnitBook AmountBook and added relationships to Book Items QuantityAmount QuantityUnit

Revision ID: fbdf6cb71aa4
Revises: fa7f383ef4c2
Create Date: 2025-01-24 15:35:21.585531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbdf6cb71aa4'
down_revision = 'fa7f383ef4c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('amounts_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('amount_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('book_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'books', ['book_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'quantity_amounts', ['amount_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('items_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('items_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('book_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'items', ['items_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'books', ['book_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('units_books', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unit_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('book_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'books', ['book_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'quantity_units', ['unit_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('units_books', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('book_id')
        batch_op.drop_column('unit_id')

    with op.batch_alter_table('items_books', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('book_id')
        batch_op.drop_column('items_id')

    with op.batch_alter_table('amounts_books', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('book_id')
        batch_op.drop_column('amount_id')

    # ### end Alembic commands ###
