"""fixed associations

Revision ID: b414120511f4
Revises: 3b28711f7ae2
Create Date: 2024-06-28 17:24:31.684118

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b414120511f4'
down_revision = '3b28711f7ae2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('book_recipers')
    op.drop_table('book_recipes')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('book_recipes',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('book_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recipe_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['recipe_books.id'], name='book_recipes_book_id_fkey'),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name='book_recipes_recipe_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='book_recipes_pkey')
    )
    op.create_table('book_recipers',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('book_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recipe_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['recipe_books.id'], name='book_recipers_book_id_fkey'),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], name='book_recipers_recipe_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='book_recipers_pkey')
    )
    # ### end Alembic commands ###
