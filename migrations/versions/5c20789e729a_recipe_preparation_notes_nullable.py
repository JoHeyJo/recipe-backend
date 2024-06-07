"""Recipe - preparation & notes, nullable

Revision ID: 5c20789e729a
Revises: 3851c47c1d19
Create Date: 2024-06-07 09:43:05.967611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c20789e729a'
down_revision = '3851c47c1d19'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe_ingredients', schema=None) as batch_op:
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('preparation',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
        batch_op.alter_column('notes',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('notes',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
        batch_op.alter_column('preparation',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)

    with op.batch_alter_table('recipe_ingredients', schema=None) as batch_op:
        batch_op.alter_column('recipe_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
