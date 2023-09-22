"""01_initial-db

Revision ID: bd9df9b665ed
Revises: 
Create Date: 2023-09-18 20:41:44.535165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd9df9b665ed'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('banks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('in_system', sa.Boolean(), nullable=True),
    sa.Column('allow_cashback_choose', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('cashbacks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_type', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('surname', sa.String(length=100), nullable=False),
    sa.Column('ebs', sa.Boolean(), nullable=True),
    sa.Column('gender', sa.String(length=1), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=False),
    sa.Column('sitizenship', sa.String(length=50), nullable=False),
    sa.Column('birth_place', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('bank_id', sa.Integer(), nullable=False),
    sa.Column('card_number', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['bank_id'], ['banks.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('card_number')
    )
    op.create_table('usercashbacks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('card_id', sa.Integer(), nullable=False),
    sa.Column('cashback_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('month', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ),
    sa.ForeignKeyConstraint(['cashback_id'], ['cashbacks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('usercashbacks')
    op.drop_table('cards')
    op.drop_table('users')
    op.drop_table('cashbacks')
    op.drop_table('banks')
    # ### end Alembic commands ###