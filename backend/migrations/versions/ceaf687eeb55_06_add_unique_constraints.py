"""06_add_unique_constraints

Revision ID: ceaf687eeb55
Revises: ee4c58a7312f
Create Date: 2023-10-12 22:59:10.019632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ceaf687eeb55'
down_revision = 'ee4c58a7312f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'accounts', ['number'])
    op.create_unique_constraint(None, 'usercashbacks', ['account_id', 'cashback_id', 'month'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'usercashbacks', type_='unique')
    op.drop_constraint(None, 'accounts', type_='unique')
    # ### end Alembic commands ###
