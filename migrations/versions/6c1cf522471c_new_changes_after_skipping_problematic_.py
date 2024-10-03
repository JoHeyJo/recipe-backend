"""New changes after skipping problematic migration & adding book_id to user to hold default book info

Revision ID: 6c1cf522471c
Revises: b6e2651ad689
Create Date: 2024-10-03 11:55:44.187328

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c1cf522471c'
down_revision = 'b6e2651ad689'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('book_id', sa.BIGINT(), nullable=True))
        batch_op.create_foreign_key(None, 'books', ['book_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('book_id')

    # ### end Alembic commands ###
