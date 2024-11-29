"""Add user activity tracking and password reset fields

Revision ID: 075a9666eac5
Revises: ce14a7ba77f7
Create Date: 2024-11-29 14:50:41.388051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '075a9666eac5'
down_revision = 'ce14a7ba77f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_login', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('login_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('failed_login_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('last_failed_login', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('uix_user_reset_token', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('reset_token_expiry', sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint(None, ['uix_user_reset_token'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('reset_token_expiry')
        batch_op.drop_column('uix_user_reset_token')
        batch_op.drop_column('last_failed_login')
        batch_op.drop_column('failed_login_count')
        batch_op.drop_column('login_count')
        batch_op.drop_column('last_login')

    # ### end Alembic commands ###