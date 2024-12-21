"""ajout account

Revision ID: e7fc8f09528b
Revises: 876e4db7c26b
Create Date: 2021-07-04 16:46:32.474200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7fc8f09528b'
down_revision = '876e4db7c26b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('positions', sa.Column('account', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('positions', 'account')
    # ### end Alembic commands ###
