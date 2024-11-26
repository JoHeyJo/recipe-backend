"""changed notes attribute in Recipe to hold and array

Revision ID: 501196d6984c
Revises: 3db7e6a01a1c
Create Date: 2024-10-16 11:43:10.296031

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '501196d6984c'
down_revision = '3db7e6a01a1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('notes',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('notes',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###