"""07_add_category_limits

Revision ID: 96401c1d8e4e
Revises: ceaf687eeb55
Create Date: 2023-12-02 15:27:41.475687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96401c1d8e4e'
down_revision = 'ceaf687eeb55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('limits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'category')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('limits')
    # ### end Alembic commands ###
