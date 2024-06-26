"""trying again

Revision ID: 8812ca14522b
Revises: 95dfb437b3a1
Create Date: 2024-04-27 16:20:08.327916

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8812ca14522b'
down_revision = '95dfb437b3a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipe')
    op.drop_table('quantity_unit')
    op.drop_table('user')
    op.drop_table('recipe_ingredient')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe_ingredient',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='recipe_ingredient_pkey')
    )
    op.create_table('user',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('last_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('password', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('user_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('email', name='user_email_key'),
    sa.UniqueConstraint('user_name', name='user_user_name_key')
    )
    op.create_table('quantity_unit',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('unit', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='quantity_unit_pkey'),
    sa.UniqueConstraint('unit', name='quantity_unit_unit_key')
    )
    op.create_table('recipe',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('preparation', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('notes', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='recipe_pkey')
    )
    # ### end Alembic commands ###
